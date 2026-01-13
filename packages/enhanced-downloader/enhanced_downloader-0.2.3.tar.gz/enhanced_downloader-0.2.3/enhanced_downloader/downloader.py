import hashlib
import json
import logging
import os
import platform
import queue
import re
import tempfile
import threading
import time
import uuid

import psutil
import requests
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3.util.retry import Retry

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)


def get_largest_free_space_disk():
    """
    获取剩余空间最大的磁盘

    Returns:
        tuple: (磁盘路径, 剩余空间大小(字节))
    """
    system = platform.system()

    try:
        if system == 'Windows':
            drives = psutil.disk_partitions()
            max_free_space = 0
            max_free_drive = None

            for drive in drives:
                if 'fixed' in drive.opts.lower():
                    try:
                        usage = psutil.disk_usage(drive.mountpoint)
                        if usage.free > max_free_space:
                            max_free_space = usage.free
                            max_free_drive = drive.mountpoint
                    except (PermissionError, FileNotFoundError):
                        continue

            if max_free_drive:
                return max_free_drive, max_free_space
            else:
                return None, 0

        elif system == 'Linux':
            partitions = psutil.disk_partitions(all=True)
            max_free_space = 0
            max_free_mount = None
            checked_mounts = set()

            for partition in partitions:
                if not partition.mountpoint or partition.mountpoint in checked_mounts:
                    continue
                excluded_fstypes = ['tmpfs', 'devtmpfs', 'sysfs', 'proc', 'cgroup', 'devpts', 'overlay', 'aufs']
                if partition.fstype in excluded_fstypes:
                    continue

                try:
                    if os.path.isdir(partition.mountpoint):
                        usage = psutil.disk_usage(partition.mountpoint)
                        checked_mounts.add(partition.mountpoint)

                        if usage.free > max_free_space:
                            max_free_space = usage.free
                            max_free_mount = partition.mountpoint
                except (PermissionError, FileNotFoundError, OSError):
                    continue
            if not max_free_mount:
                common_mounts = ['/', '/data', '/home', '/opt', '/var']
                for mount_point in common_mounts:
                    if os.path.isdir(mount_point) and mount_point not in checked_mounts:
                        try:
                            usage = psutil.disk_usage(mount_point)
                            if usage.free > max_free_space:
                                max_free_space = usage.free
                                max_free_mount = mount_point
                        except (PermissionError, FileNotFoundError, OSError):
                            continue

            if max_free_mount:
                return max_free_mount, max_free_space
            else:
                return None, 0

        else:
            log.error(f"不支持的操作系统: {system}")
            return None, 0

    except Exception as e:
        log.error(f"获取磁盘信息时出错: {str(e)}")
        return None, 0


def format_bytes(bytes_value):
    """
    将字节数格式化为人类可读的单位

    Args:
        bytes_value: 字节数

    Returns:
        str: 格式化后的字符串
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    unit_index = 0
    size = float(bytes_value)

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f"{size:.2f} {units[unit_index]}"


def get_url_hash(url):
    """
    根据URL生成唯一哈希值用于识别下载文件
    
    Args:
        url (str): 下载URL
        
    Returns:
        str: URL的MD5哈希值（16字符）
    """
    return hashlib.md5(url.encode()).hexdigest()[:16]


def load_resume_state(state_file):
    """
    从状态文件加载断点续传信息
    
    Args:
        state_file (str): 状态文件路径
        
    Returns:
        dict: 包含已完成范围和元数据的字典，若文件不存在则返回空字典
    """
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log.warning(f"加载状态文件失败: {str(e)}，将重新开始下载")
            return {}
    return {}


def save_resume_state(state_file, completed_ranges, file_size, url, num_threads=30, partial_ranges=None):
    """
    保存断点续传信息到状态文件
    
    Args:
        state_file (str): 状态文件路径
        completed_ranges (set): 已完成的范围集合
        file_size (int): 文件总大小
        url (str): 下载URL
        num_threads (int): 分片线程数
        partial_ranges (dict): 部分下载的范围 {(start, end): downloaded_bytes}
    """
    try:
        # 将集合转换为列表以便JSON序列化
        completed_list = sorted([list(r) for r in completed_ranges])
        
        # 转换部分下载范围（只保存有实际进度的）
        partial_list = []
        if partial_ranges:
            # log.info(f"downloaded_bytes 字典大小: {len(partial_ranges)}, 内容: {[(k, v) for k, v in list(partial_ranges.items())[:3]]}...")  # 只显示前3个
            for (start, end), downloaded in partial_ranges.items():
                if downloaded > 0 and (start, end) not in completed_ranges:
                    partial_list.append({
                        'start': start,
                        'end': end,
                        'downloaded': downloaded
                    })
                    # log.info(f"添加部分分片: {start}-{end}, 已下载 {downloaded / 1024 / 1024:.2f}MB")
        else:
            log.info("partial_ranges 为空或 None")
        
        state_data = {
            'url': url,
            'file_size': file_size,
            'completed_ranges': completed_list,
            'partial_ranges': partial_list,  # 新增：部分下载的范围
            'num_threads': num_threads,
            'timestamp': int(time.time())
        }
        
        # 确保状态文件所在目录存在（转换为绝对路径）
        state_file_abs = os.path.abspath(state_file)
        state_dir = os.path.dirname(state_file_abs)
        
        log.debug(f"准备保存状态文件: {state_file_abs}")
        log.debug(f"状态文件目录: {state_dir}")
        
        if state_dir:  # 创建目录
            try:
                os.makedirs(state_dir, exist_ok=True)
                log.debug(f"目录已创建或已存在: {state_dir}")
            except Exception as dir_err:
                log.error(f"创建目录失败: {state_dir}, 错误: {dir_err}")
                raise
        
        # 使用绝对路径写入文件
        try:
            with open(state_file_abs, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2)
            # log.info(f"状态文件已保存: {state_file_abs}, 完成分片: {len(completed_list)}, 部分分片: {len(partial_list)}")
            
            # 验证文件是否真的存在
            if os.path.exists(state_file_abs):
                file_size_kb = os.path.getsize(state_file_abs) / 1024
                log.debug(f"状态文件验证成功，大小: {file_size_kb:.2f}KB")
            else:
                log.error(f"状态文件保存后未找到: {state_file_abs}")
        except Exception as write_err:
            log.error(f"写入状态文件失败: {state_file_abs}, 错误: {write_err}")
            raise
            
    except Exception as e:
        log.error(f"保存状态文件失败: {str(e)}, 类型: {type(e).__name__}")
        import traceback
        log.error(f"详细错误: {traceback.format_exc()}")


class EnhancedDownloader:
    """增强型下载器，支持单线程和多线程下载，自动检测服务器是否支持分片"""

    def __init__(self, proxy=None):
        """
        初始化下载器

        Args:
            proxy (str, optional): 代理地址，格式如 'http://127.0.0.1:7890' 或 'socks5://127.0.0.1:1080'
        """
        self._default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self._proxy = None
        self._proxy_checked = False
        self._proxy_available = False
        if proxy:
            self.set_proxy(proxy)

    def set_proxy(self, proxy):
        """
        设置代理，会自动验证代理可用性

        Args:
            proxy (str): 代理地址，格式如 'http://127.0.0.1:7890' 或 'socks5://127.0.0.1:1080'
        """
        self._proxy = proxy
        self._proxy_checked = False
        self._proxy_available = False
        # 立即验证代理可用性
        self._check_proxy_available()

    def _get_proxies(self):
        """获取代理配置字典"""
        if self._proxy and self._proxy_available:
            return {
                'http': self._proxy,
                'https': self._proxy
            }
        return None

    def _check_proxy_available(self):
        """检查代理是否可用"""
        if not self._proxy:
            self._proxy_available = False
            self._proxy_checked = True
            return False

        if self._proxy_checked:
            return self._proxy_available

        log.info(f"正在检测代理可用性: {self._proxy}")
        proxies = {
            'http': self._proxy,
            'https': self._proxy
        }

        test_urls = [
            'https://www.google.com',
            'https://www.baidu.com',
            'https://httpbin.org/ip'
        ]

        for test_url in test_urls:
            try:
                response = requests.get(
                    test_url,
                    proxies=proxies,
                    timeout=10,
                    headers=self._default_headers
                )
                if response.status_code == 200:
                    self._proxy_available = True
                    self._proxy_checked = True
                    log.info(f"代理可用: {self._proxy}")
                    return True
            except Exception as e:
                log.debug(f"代理测试 {test_url} 失败: {str(e)}")
                continue

        self._proxy_available = False
        self._proxy_checked = True
        log.warning(f"代理不可用，将使用直连: {self._proxy}")
        return False

    def create_session(self, retries=3, backoff_factor=3, use_proxy=True):
        """创建带重试策略的会话

        Args:
            retries (int): 重试次数
            backoff_factor (int): 退避因子
            use_proxy (bool): 是否使用代理
        """
        session = requests.Session()
        session.headers.update(self._default_headers)

        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504, 520, 522, 524],
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # 设置代理
        if use_proxy:
            proxies = self._get_proxies()
            if proxies:
                session.proxies.update(proxies)

        return session

    def check_range_support(self, url, session=None):
        """检查服务器是否支持分片下载"""
        use_session = session if session else self.create_session()
        try:
            head_response = use_session.head(url)
            head_response.raise_for_status()

            accept_ranges = head_response.headers.get('accept-ranges', 'none')
            if accept_ranges.lower() == 'bytes':
                try:
                    range_response = use_session.get(url, headers={'Range': 'bytes=0-1'}, stream=True)
                    if range_response.status_code == 206:
                        return True, int(head_response.headers.get('content-length', 0))
                except Exception as e:
                    log.warning(f"Range请求验证失败: {str(e)}")
                    pass

            # 获取文件大小
            content_length = int(head_response.headers.get('content-length', 0))
            return False, content_length
        except Exception as e:
            log.warning(f"检查分片支持时出错: {str(e)}")
            return False, 0
        finally:
            if not session:
                use_session.close()

    def _worker(self, task_queue, filename, pbar, completed_ranges, stop_event, downloaded_bytes, url, max_retries=3,
                use_proxy=True, speed_stats=None, resume_info=None, periodic_save_interval=10):
        """工作线程函数，处理队列中的下载任务
        
        Args:
            periodic_save_interval (int): 定期保存状态的间隔（秒），默认10秒
        """
        success_count = 0  # 连续成功下载计数
        last_save_time = time.time()  # 上次保存状态的时间
        while not stop_event.is_set():
            try:
                start, end = task_queue.get(timeout=1)
                range_key = (start, end)
                if range_key in completed_ranges:
                    task_queue.task_done()
                    continue

                retry_count = task_queue.retries.get(range_key, 0)

                # 如果超过最大重试次数，则放弃任务
                if retry_count >= max_retries:
                    log.error(f"下载块 {start}-{end} 已达到最大重试次数 {max_retries}，放弃下载")
                    task_queue.task_done()
                    continue

                # 执行下载任务
                chunk_start_time = time.time()
                session = self.create_session(use_proxy=use_proxy)
                try:
                    headers = {'Range': f'bytes={start}-{end}'}
                    # 动态调整下载chunk_size：
                    # 1. 当失败次数增加时，温和减小（不能过激）
                    # 2. 当長時間沒有失敗時，逐步增加chunk_size以利用好网絡
                    base_chunk_size = 8192

                    # 减小逻辑：当有失败时
                    if retry_count > 0:
                        reduction_factor = min(retry_count, 3)
                        chunk_size = max(1024, base_chunk_size >> reduction_factor)
                    else:
                        # 增大逻辑：沒有失败時，逐步增大
                        if success_count >= 30:  # 連纃30次成功下载了，可以想考增大分片
                            # 逐步增大chunk_size，最大到128KB
                            amplification_factor = min(success_count // 30, 4)  # 最多放大4倍
                            chunk_size = min(base_chunk_size << amplification_factor, 128 * 1024)
                            if amplification_factor > 0:
                                log.debug(f"连续成功(success_count={success_count})，增批chunk_size至{chunk_size}")
                        else:
                            chunk_size = base_chunk_size

                    log.debug(f"第 {retry_count} 次重试，连续成功次数: {success_count}，使用chunk_size: {chunk_size}")
                    response = session.get(url, headers=headers, stream=True, timeout=120)
                    response.raise_for_status()

                    with open(filename, 'r+b') as f:
                        f.seek(start)
                        downloaded = downloaded_bytes[range_key]
                        expected_size = end - start + 1

                        # 更新进度条：减去之前已下载但失败的部分
                        if downloaded > 0:
                            pbar.update(-downloaded)

                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                chunk_len = len(chunk)
                                prev_downloaded = downloaded
                                downloaded += chunk_len
                                downloaded_bytes[range_key] = downloaded

                                actual_new_bytes = min(chunk_len, expected_size - prev_downloaded)
                                if actual_new_bytes > 0:
                                    pbar.update(actual_new_bytes)

                                    # 记录下载速度
                                    if speed_stats is not None:
                                        speed_stats['bytes_downloaded'] += actual_new_bytes
                                        speed_stats['chunk_count'] += 1
                                
                                # 定期保存部分下载进度（每隔一定时间）
                                current_time = time.time()
                                if resume_info is not None and (current_time - last_save_time) >= periodic_save_interval:
                                    # 【关键】强制刷新数据到磁盘，确保数据一致性
                                    f.flush()  # 刷新Python缓冲区到OS
                                    os.fsync(f.fileno())  # 强制OS将数据写入磁盘
                                    
                                    with resume_info['lock']:
                                        try:
                                            save_resume_state(
                                                resume_info['state_file'],
                                                resume_info['completed_ranges'],
                                                resume_info['file_size'],
                                                resume_info['url'],
                                                resume_info['num_threads'],
                                                downloaded_bytes  # 传递部分下载进度
                                            )
                                            last_save_time = current_time
                                        except Exception as save_err:
                                            log.error(f"定期保存进度失败: {save_err}")

                    # 分片下载完成，强制刷新到磁盘后再保存状态
                    # 确保状态文件记录的进度与实际磁盘数据一致
                    if resume_info is not None:
                        # 重新打开文件并刷新（因为with块已结束）
                        with open(filename, 'r+b') as f:
                            f.flush()
                            os.fsync(f.fileno())
                        
                        with resume_info['lock']:
                            completed_ranges.add(range_key)
                            try:
                                save_resume_state(
                                    resume_info['state_file'],
                                    resume_info['completed_ranges'],
                                    resume_info['file_size'],
                                    resume_info['url'],
                                    resume_info['num_threads'],
                                    downloaded_bytes  # 传递部分下载进度
                                )
                            except Exception as save_err:
                                log.error(f"保存断点续传状态失败: {save_err}")
                    else:
                        completed_ranges.add(range_key)
                    
                    # 成功了，记录这个块的下载时间，增加成功计数
                    if speed_stats is not None:
                        with speed_stats['lock']:
                            if range_key in speed_stats['block_times']:
                                # 计算下载时间并记录
                                block_duration = time.time() - speed_stats['block_times'][range_key]
                                speed_stats['block_durations'].append(block_duration)
                                # 只保留最新20个块的时间记录，用于计算平均值
                                if len(speed_stats['block_durations']) > 20:
                                    speed_stats['block_durations'].pop(0)
                                del speed_stats['block_times'][range_key]
                    success_count += 1

                except Exception as e:
                    log.info(f"下载块 {start}-{end} 时出错: {e}")
                    # 成功计数下降，失败后应该羀介多次
                    success_count = max(0, success_count - 5)
                    # 更新进度条：减去已下载但失败的部分
                    if downloaded_bytes[range_key] > 0:
                        pbar.update(-downloaded_bytes[range_key])
                    downloaded_bytes[range_key] = 0

                    # 增加重试次数
                    new_retry_count = retry_count + 1
                    task_queue.retries[range_key] = new_retry_count

                    # 记录需要减小块大小的信息（表现为连接中断）
                    if "IncompleteRead" in str(e) or "Connection broken" in str(e) or "SSLEOFError" in str(e):
                        if speed_stats is not None:
                            with speed_stats['lock']:
                                if 'failed_retries' not in speed_stats:
                                    speed_stats['failed_retries'] = 0
                                speed_stats['failed_retries'] += 1

                    # 【核心逻辑】当块多次失败且块过大时，分割成小块提高成功率
                    block_size = end - start + 1
                    max_block_size_for_split = 50 * 1024 * 1024  # 50MB
                    min_retry_for_split = 2  # 至少失败2次才考虑分割

                    if new_retry_count >= min_retry_for_split and block_size > max_block_size_for_split:
                        # 分割成更小的块，每块约25MB
                        target_size = 25 * 1024 * 1024
                        num_splits = (block_size + target_size - 1) // target_size
                        num_splits = max(2, min(num_splits, 8))  # 最少2份，最大8份

                        log.warning(
                            f"块 {start}-{end} ({block_size / 1024 / 1024:.1f}MB) 已失败 {new_retry_count} 次，自动分割成 {num_splits} 个子块提高成功率")

                        block_step = (block_size + num_splits - 1) // num_splits
                        for i in range(num_splits):
                            sub_start = start + i * block_step
                            sub_end = min(start + (i + 1) * block_step - 1, end)
                            if sub_start <= sub_end:
                                sub_key = (sub_start, sub_end)
                                task_queue.put(sub_key)
                                downloaded_bytes[sub_key] = 0
                                # 子块重试次数从0开始
                                task_queue.retries[sub_key] = 0

                        # 删除原块的僵尸键，防止内存泄漏
                        if (start, end) in downloaded_bytes:
                            del downloaded_bytes[(start, end)]
                        if (start, end) in task_queue.retries:
                            del task_queue.retries[(start, end)]
                        # 从慢块追踪中删除（如果存在）
                        if speed_stats and (start, end) in speed_stats['block_times']:
                            del speed_stats['block_times'][(start, end)]
                        # 不再重新放入原块
                    else:
                        # 正常重试：重新放入队列
                        task_queue.put((start, end))
                finally:
                    session.close()
                    # 记录这个块的下载时间
                    if speed_stats is not None:
                        chunk_time = time.time() - chunk_start_time
                        with speed_stats['lock']:
                            speed_stats['total_time'] += chunk_time
                    task_queue.task_done()

            except queue.Empty:
                # 队列为空，继续等待
                continue
            except Exception as e:
                log.error(f"工作线程出错: {str(e)}")

    def _optimize_download_performance(self, speed_stats, workers, task_queue, completed_ranges, stop_event):
        """
        优化线程函数：定期检查下载速度和失败率，根据情况自动调整线程数和块大小（均衡策略）
        
        Args:
            speed_stats (dict): 速度统计信息
            workers (list): 工作线程列表
            task_queue (Queue): 任务队列
            completed_ranges (set): 已完成的范围
            stop_event (Event): 停止事件
        """
        check_interval = 5  # 每5秒检查一次
        low_speed_threshold = 1024 * 100  # 100KB/s以下认为速度低
        high_speed_threshold = 1024 * 1024 * 10  # 10MB/s以上认为速度高
        min_threads = 4  # 最少4个线程，避免过度集中
        max_threads = 50  # 最多50个线程，避免系统过载
        ideal_thread_range = (8, 30)  # 理想线程数范围8-30

        previous_speed = 0
        low_speed_count = 0
        high_speed_count = 0
        previous_chunk_count = 0

        while not stop_event.is_set():
            try:
                time.sleep(check_interval)

                with speed_stats['lock']:
                    if speed_stats['total_time'] <= 0:
                        continue

                    # 计算当前速度（字节/秒）
                    current_speed = speed_stats['bytes_downloaded'] / speed_stats['total_time']
                    current_threads = speed_stats['current_threads']
                    current_chunk_count = speed_stats['chunk_count']
                    failed_retries = speed_stats.get('failed_retries', 0)

                    # 计算增长率
                    if previous_speed > 0:
                        speed_growth = (current_speed - previous_speed) / previous_speed
                    else:
                        speed_growth = 0

                    # 计算块大小指标
                    chunk_delta = current_chunk_count - previous_chunk_count
                    if speed_stats['total_time'] > 0 and chunk_delta > 0:
                        avg_chunk_size = speed_stats['bytes_downloaded'] / max(chunk_delta, 1)

                    log.debug(
                        f"当前速度: {current_speed / 1024:.2f}KB/s, 线程数: {current_threads}, 速度增长率: {speed_growth * 100:.1f}%, 块数: {current_chunk_count}, 失败次数: {failed_retries}")

                    # 计算新增失败次数（相对于上次调整）
                    new_failed_count = failed_retries - speed_stats.get('last_failed_retries', 0)

                    # 均衡调整策略：线程数调整要温和，不能过激
                    new_threads = current_threads

                    # 【优先级1】检查线程数是否在安全范围内
                    # 不超过max_threads（系统最大值），不低于min_threads（最小并发）
                    if current_threads >= max_threads:
                        # 已达系统上限，不再增加
                        if failed_retries >= 5:
                            # 失败多但线程已满，问题可能不是并发不足
                            log.warning(f"检测到多次失败 ({failed_retries} 次)，但线程已达上限({max_threads})，不再增加")
                    elif current_threads > ideal_thread_range[1]:
                        # 超过理想范围上限，逐步降回范围内（不强制一次性降30）
                        new_threads = current_threads - 1
                        log.info(
                            f"线程数({current_threads})超过理想范围上限({ideal_thread_range[1]})，温和降至 {new_threads}")

                    # 【优先级2】失败驱动调整（只有新增失败次数达到阈值才调整一次）
                    elif new_failed_count >= speed_stats.get('failed_retries_threshold',
                                                             3) and current_threads < max_threads:
                        # 新增失败次数超过阈值才调整，防止重复对同一批失败做反应
                        new_threads = min(current_threads + 1, max_threads)
                        speed_stats['last_failed_retries'] = failed_retries  # 更新基准值
                        log.warning(
                            f"检测到了 {new_failed_count} 次新增失败(总计{failed_retries}次)，增加线程数至 {new_threads} 以提高并发能力")

                    # 【优先级3】基于速度的温和调整
                    elif current_speed < low_speed_threshold and current_threads < ideal_thread_range[1]:
                        # 速度过低，温和增加线程（最多到理想范围上限）
                        low_speed_count += 1
                        high_speed_count = 0

                        if low_speed_count >= 2:  # 连续2次低速
                            new_threads = min(current_threads + 1, ideal_thread_range[1])
                            low_speed_count = 0
                            log.info(f"检测到低速下载 ({current_speed / 1024:.2f}KB/s)，温和增加线程数至 {new_threads}")

                    elif current_speed > high_speed_threshold and current_threads > ideal_thread_range[0]:
                        # 速度很高，温和减少线程（最多到理想范围下限）
                        high_speed_count += 1
                        low_speed_count = 0

                        if high_speed_count >= 3:  # 连续3次高速
                            new_threads = max(current_threads - 1, ideal_thread_range[0])
                            high_speed_count = 0
                            log.info(
                                f"检测到高速下载 ({current_speed / 1024 / 1024:.2f}MB/s)，温和减少线程数至 {new_threads}")

                    # 【优先级4】如果未在任何条件下调整，检查是否需要向理想范围靠拢
                    elif current_threads < ideal_thread_range[0]:
                        # 低于理想范围，逐步增加
                        new_threads = current_threads + 1
                        log.info(
                            f"线程数({current_threads})低于理想范围下限({ideal_thread_range[0]})，温和增至 {new_threads}")
                        low_speed_count = 0
                        high_speed_count = 0

                    previous_speed = current_speed
                    previous_chunk_count = current_chunk_count

                    # 如果需要调整线程数
                    if new_threads != current_threads:
                        speed_stats['current_threads'] = new_threads
                        speed_stats['optimal_threads'] = new_threads
                        log.info(f"线程数已调整: {current_threads} -> {new_threads}")

                    # 检测并处理慢块：根据平均下载时间动态调整阈值
                    current_time = time.time()
                    # 计算平均下载时间，应对整个下载都慢的情况
                    if speed_stats['block_durations']:
                        avg_duration = sum(speed_stats['block_durations']) / len(speed_stats['block_durations'])
                        slow_block_factor = speed_stats.get('slow_block_factor', 1.5)
                        slow_block_threshold = avg_duration * slow_block_factor  # 动态配置阈值
                    else:
                        # 没有足够的数据，使用10秒作为阈值
                        slow_block_threshold = 10
                        avg_duration = 0

                    blocks_to_split = []  # 需要细分的块

                    # 扫描所有未完成的块，检查是否是慢块
                    for block_range, start_time in list(speed_stats['block_times'].items()):
                        elapsed_time = current_time - start_time
                        if elapsed_time > slow_block_threshold and block_range not in completed_ranges:
                            start, end = block_range
                            block_size = end - start + 1
                            # 只有较大的块才能细分（例如：低于100KB的块不细分）
                            if block_size > 102400:  # > 100KB
                                blocks_to_split.append((block_range, elapsed_time))

                    # 处理需要细分的块
                    if blocks_to_split:
                        for (start, end), elapsed_time in blocks_to_split:
                            if (start, end) in speed_stats['block_times']:  # 再次确认是否仍在处理
                                log.warning(
                                    f"检测到慢块 ({start}-{end})，耗时{elapsed_time:.1f}s > {slow_block_threshold:.1f}s(平均{avg_duration:.1f}s*{slow_block_factor})")
                                log.warning(f"对该块进行二次细分以加速")
                                mid = (start + end) // 2
                                new_blocks = [(start, mid), (mid + 1, end)]
                                log.info(f"将慢块 {start}-{end} 细分为 {start}-{mid} 和 {mid + 1}-{end}")
                                for new_block in new_blocks:
                                    task_queue.put(new_block)
                                    speed_stats['block_times'][new_block] = current_time
                                # 删除旧块的时间记录
                                del speed_stats['block_times'][(start, end)]

            except Exception as e:
                log.debug(f"优化线程出错: {str(e)}")
                continue

    def multi_thread_download(self, url, filename, file_size, num_threads=30, temp_dir=None, use_proxy=True,
                              adaptive=True, enable_resume=True):
        """
        多线程下载文件，支持断点续传
        
        Args:
            url (str): 下载链接
            filename (str): 保存文件名
            file_size (int): 文件大小
            num_threads (int): 线程数
            temp_dir (str): 临时目录
            use_proxy (bool): 是否使用代理
            adaptive (bool): 是否启用自適應优化
            enable_resume (bool): 是否启用断点续传
        """
        # 确定临时文件路径（使用URL哈希以支持断点续传）
        url_hash = get_url_hash(url)
        if temp_dir:
            os.makedirs(temp_dir, exist_ok=True)
            temp_filename = os.path.join(temp_dir, f"download_{url_hash}.tmp")
            state_file = os.path.join(temp_dir, f"download_{url_hash}.state")
        else:
            # 确保目标文件路径是绝对路径
            target_path = os.path.abspath(filename)
            target_dir = os.path.dirname(target_path)
            os.makedirs(target_dir, exist_ok=True)
            # 使用目标目录作为临时文件的存储位置
            temp_filename = os.path.join(target_dir, f"download_{url_hash}.tmp")
            state_file = os.path.join(target_dir, f"download_{url_hash}.state")

        try:
            # 加载断点续传状态
            resumed_ranges = set()
            resumed_bytes = 0
            partial_downloads = {}  # 部分下载的分片 {(start, end): downloaded_bytes}
            saved_num_threads = num_threads  # 默认使用传入的线程数
            
            if enable_resume and os.path.exists(state_file) and os.path.exists(temp_filename):
                resume_state = load_resume_state(state_file)
                if resume_state.get('file_size') == file_size and resume_state.get('url') == url:
                    # 恢复已完成的分片
                    resumed_ranges = set(tuple(r) for r in resume_state.get('completed_ranges', []))
                    resumed_bytes = sum(r[1] - r[0] + 1 for r in resumed_ranges)
                    
                    # 恢复部分下载的分片
                    partial_ranges = resume_state.get('partial_ranges', [])
                    for partial in partial_ranges:
                        start = partial['start']
                        end = partial['end']
                        downloaded = partial['downloaded']
                        partial_key = (start, end)
                        partial_downloads[partial_key] = downloaded
                        resumed_bytes += downloaded
                    
                    # 使用保存的线程数以确保分片一致
                    saved_num_threads = resume_state.get('num_threads', num_threads)
                    log.info(f"断点续传: 已完成 {resumed_bytes / 1024 / 1024:.2f}MB / {file_size / 1024 / 1024:.2f}MB (完成分片: {len(resumed_ranges)}, 部分分片: {len(partial_downloads)})")
                    if saved_num_threads != num_threads:
                        log.info(f"使用保存的分片数 {saved_num_threads}（原请求 {num_threads}）以确保断点续传正确")
                        num_threads = saved_num_threads
                else:
                    log.info("状态文件与当前下载不匹配，重新开始下载")
                    resumed_ranges = set()
                    partial_downloads = {}
            
            # 创建或验证临时文件
            if not os.path.exists(temp_filename) or os.path.getsize(temp_filename) != file_size:
                # 创建与文件大小相同的空文件
                with open(temp_filename, 'wb') as f:
                    f.seek(file_size - 1)
                    f.write(b'\0')
                resumed_ranges = set()  # 文件重建，清空已完成记录
                resumed_bytes = 0

            with tqdm(total=file_size, unit='B', unit_scale=True, desc='下载进度', initial=resumed_bytes) as pbar:
                task_queue = queue.Queue()
                completed_ranges = set(resumed_ranges)  # 使用已恢复的范围初始化
                downloaded_bytes = {}
                stop_event = threading.Event()
                
                # 创建断点续传信息字典（用于实时保存状态）
                resume_info = None
                if enable_resume:
                    resume_info = {
                        'state_file': state_file,
                        'file_size': file_size,
                        'url': url,
                        'num_threads': num_threads,
                        'lock': threading.Lock(),
                        'completed_ranges': completed_ranges  # 引用同一个集合
                    }

                # 初始化速度统计
                speed_stats = None
                optimization_thread = None
                if adaptive:
                    speed_stats = {
                        'bytes_downloaded': 0,
                        'total_time': 0,
                        'chunk_count': 0,
                        'lock': threading.Lock(),
                        'last_check_time': time.time(),
                        'last_bytes': 0,
                        'current_threads': 0,
                        'task_queue': task_queue,
                        'stop_event': stop_event,
                        'block_times': {},  # 跟踪每个块的开始时间
                        'block_durations': [],  # 记录已完成块的下载时间（用于计算平均值）
                        'slow_block_factor': 1.5,  # 平均时间的1.5倍认为是慢块
                        'last_failed_retries': 0,  # 上次调整线程时的失败数，用于追踪新增失败
                        'failed_retries_threshold': 3  # 新增3次失败时调整一次线程数
                    }

                # 初始化任务队列：计算未完成的字节范围
                bytes_per_thread = file_size // num_threads
                pending_count = 0
                for i in range(num_threads):
                    start = i * bytes_per_thread
                    end = start + bytes_per_thread - 1 if i < num_threads - 1 else file_size - 1
                    range_key = (start, end)
                    
                    # 检查该分片是否已完成（断点续传）
                    if range_key in completed_ranges:
                        log.debug(f"分片 {start}-{end} 已完成，跳过")
                        continue
                    
                    # 检查是否有部分下载的进度
                    if range_key in partial_downloads:
                        partial_downloaded = partial_downloads[range_key]
                        downloaded_bytes[range_key] = partial_downloaded
                        # 计算剩余未下载的部分
                        remaining_start = start + partial_downloaded
                        if remaining_start <= end:
                            # 只下载剩余部分
                            remaining_key = (remaining_start, end)
                            task_queue.put(remaining_key)
                            # 继承原有的下载进度
                            downloaded_bytes[remaining_key] = 0
                            pending_count += 1
                            # log.info(f"分片 {start}-{end} 部分完成 ({partial_downloaded / 1024 / 1024:.2f}MB)，继续下载 {remaining_start}-{end}")
                        else:
                            # 已完成，添加到已完成集合
                            completed_ranges.add(range_key)
                            log.debug(f"分片 {start}-{end} 实际已完成")
                        continue
                    
                    # 检查是否有子分片已完成（处理分片被分割的情况）
                    # 计算该范围内已完成的字节数
                    completed_in_range = 0
                    sub_ranges_completed = []
                    for cr in completed_ranges:
                        cr_start, cr_end = cr
                        # 检查是否是该范围的子分片
                        if cr_start >= start and cr_end <= end:
                            completed_in_range += cr_end - cr_start + 1
                            sub_ranges_completed.append(cr)
                    
                    if completed_in_range > 0:
                        # 有部分子分片已完成，需要计算剩余未完成的部分
                        # 将子分片按起始位置排序
                        sub_ranges_completed.sort(key=lambda x: x[0])
                        
                        # 计算未完成的间隙
                        current_pos = start
                        for sr_start, sr_end in sub_ranges_completed:
                            if current_pos < sr_start:
                                # 有未完成的间隙
                                gap_key = (current_pos, sr_start - 1)
                                task_queue.put(gap_key)
                                downloaded_bytes[gap_key] = 0
                                pending_count += 1
                            current_pos = sr_end + 1
                        
                        # 检查最后一段是否有未完成
                        if current_pos <= end:
                            gap_key = (current_pos, end)
                            task_queue.put(gap_key)
                            downloaded_bytes[gap_key] = 0
                            pending_count += 1
                        
                        log.debug(f"分片 {start}-{end} 部分完成，已拆分剩余未完成部分")
                    else:
                        # 整个分片未完成
                        task_queue.put(range_key)
                        downloaded_bytes[range_key] = 0
                        pending_count += 1
                
                if pending_count == 0:
                    log.info("所有分片已完成，无需下载")
                else:
                    log.info(f"待下载分片数: {pending_count}")

                # 初始化重试计数字典
                task_queue.retries = {}

                # 启动工作线程
                workers = []
                # 根据文件大小和系统资源动态调整实际线程数
                actual_threads = min(num_threads, 30)
                if speed_stats is not None:
                    speed_stats['current_threads'] = actual_threads

                for _ in range(actual_threads):
                    w = threading.Thread(target=self._worker,
                                         args=(task_queue, temp_filename, pbar, completed_ranges, stop_event,
                                               downloaded_bytes, url, 3, use_proxy, speed_stats, resume_info))
                    w.daemon = True
                    w.start()
                    workers.append(w)

                # 启动优化线程（定期检查下载速度并调整）
                if adaptive:
                    optimization_thread = threading.Thread(
                        target=self._optimize_download_performance,
                        args=(speed_stats, workers, task_queue, completed_ranges, stop_event)
                    )
                    optimization_thread.daemon = True
                    optimization_thread.start()

                # 等待所有任务完成
                task_queue.join()

                # 通知所有线程停止
                stop_event.set()

                # 等待优化线程结束
                if optimization_thread:
                    optimization_thread.join(timeout=5)

                # 等待所有工作线程结束
                for w in workers:
                    w.join(timeout=5)

                # 输出最终速度统计
                if speed_stats is not None and speed_stats['total_time'] > 0:
                    avg_speed = speed_stats['bytes_downloaded'] / speed_stats['total_time'] / 1024 / 1024
                    log.info(
                        f"下载完成。最终平均速度: {avg_speed:.2f}MB/s，最优线程数: {speed_stats.get('optimal_threads', actual_threads)}")

            # 如果指定了目标文件名，则将临时文件移动到目标位置
            if filename != temp_filename:
                # 确保目标文件所在目录存在
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                # 先删除可能存在的目标文件
                if os.path.exists(filename):
                    os.remove(filename)
                # 尝试重命名文件，如果跨磁盘则复制后删除
                try:
                    os.rename(temp_filename, filename)
                except OSError as e:
                    if e.winerror == 17:  # 系统无法将文件移到不同的磁盘驱动器
                        # 跨磁盘复制文件
                        import shutil
                        shutil.copy2(temp_filename, filename)
                        # 删除临时文件
                        os.remove(temp_filename)
                    else:
                        raise

            # 下载完成，删除状态文件
            if os.path.exists(state_file):
                try:
                    os.remove(state_file)
                except:
                    pass

            log.info(f"文件已保存至: {filename}")
            return filename

        except Exception as e:
            log.error(f"多线程下载失败: {str(e)}")
            # 先强制刷新所有未写入的数据，再保存状态
            try:
                if os.path.exists(temp_filename):
                    with open(temp_filename, 'r+b') as f:
                        f.flush()
                        os.fsync(f.fileno())
                    log.info("已强制刷新所有数据到磁盘")
            except Exception as flush_err:
                log.warning(f"刷新数据失败: {flush_err}")
            
            # 保存断点续传进度（而不是删除临时文件）
            if enable_resume and 'completed_ranges' in locals() and 'downloaded_bytes' in locals():
                try:
                    save_resume_state(state_file, completed_ranges, file_size, url, num_threads, downloaded_bytes)
                    log.info(f"已保存断点续传进度，下次启动可继续下载")
                except Exception as save_err:
                    log.error(f"保存失败: {save_err}")
            raise
        except KeyboardInterrupt:
            log.warning("用户中断下载")
            try:
                if os.path.exists(temp_filename):
                    with open(temp_filename, 'r+b') as f:
                        f.flush()
                        os.fsync(f.fileno())
                    log.info("已强制刷新所有数据到磁盘")
            except Exception as flush_err:
                log.warning(f"刷新数据失败: {flush_err}")
            
            # 保存断点续传进度
            if enable_resume and 'completed_ranges' in locals() and 'downloaded_bytes' in locals():
                try:
                    save_resume_state(state_file, completed_ranges, file_size, url, num_threads, downloaded_bytes)
                    log.info(f"已保存断点续传进度 ({len(completed_ranges)} 个分片)，下次启动可继续下载")
                except Exception as save_err:
                    log.error(f"保存断点续传进度失败: {save_err}")
            raise

    def single_thread_download(self, url, save_path, return_content=False, chunk_size=8192, timeout=30, max_retries=3,
                               speed_limit=None, use_proxy=True):
        """单线程下载文件，支持断点续传和速度限制"""
        retry_count = 0
        last_exception = None

        while retry_count <= max_retries:
            try:
                if return_content:
                    log.info("正在下载内容...")
                    content = bytearray()

                    # 使用会话下载内容
                    session = self.create_session(use_proxy=use_proxy)
                    try:
                        response = session.get(url, stream=True, timeout=timeout)
                        response.raise_for_status()

                        # 获取文件总大小
                        total_size = int(response.headers.get('content-length', 0))

                        with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                            # 下载速度控制
                            if speed_limit:
                                max_chunk_time = chunk_size / speed_limit  # 字节/秒
                                chunk_start_time = time.time()
                            else:
                                max_chunk_time = 0

                            for chunk in response.iter_content(chunk_size=chunk_size):
                                if chunk:
                                    content.extend(chunk)
                                    pbar.update(len(chunk))

                                    # 速度限制逻辑
                                    if speed_limit:
                                        elapsed = time.time() - chunk_start_time
                                        if elapsed < max_chunk_time:
                                            time.sleep(max_chunk_time - elapsed)
                                        chunk_start_time = time.time()
                        return bytes(content)
                    finally:
                        session.close()
                else:
                    # 确保目录存在
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)

                    # 检查是否已存在部分文件（断点续传）
                    resume_header = {}
                    initial_size = 0

                    if os.path.exists(save_path):
                        initial_size = os.path.getsize(save_path)
                        if initial_size > 0:
                            log.info(f"检测到部分下载的文件，从 {initial_size} 字节处继续下载")
                            resume_header = {'Range': f'bytes={initial_size}-'}

                    # 获取文件总大小
                    session = self.create_session(use_proxy=use_proxy)
                    try:
                        # 获取文件总大小
                        head_response = session.head(url, timeout=timeout)
                        head_response.raise_for_status()

                        total_size = int(head_response.headers.get('content-length', 0))

                        # 处理已下载完成的情况
                        if initial_size >= total_size > 0:
                            log.info(f"文件已下载完成，大小: {initial_size} 字节")
                            return save_path

                        # 计算需要下载的剩余大小
                        remaining_size = total_size - initial_size if total_size > 0 else 0
                        log.info(
                            f"文件总大小: {total_size / 1024 / 1024:.2f}MB, 已下载: {initial_size / 1024 / 1024:.2f}MB, 剩余: {remaining_size / 1024 / 1024:.2f}MB")

                        # 使用追加模式打开文件进行断点续传
                        mode = 'ab' if initial_size > 0 else 'wb'
                        with open(save_path, mode) as file, tqdm(
                                total=remaining_size if remaining_size > 0 else None,  # 如果不知道总大小，显示为None
                                initial=0,
                                unit='B',
                                unit_scale=True,
                                unit_divisor=1024,
                                desc=os.path.basename(save_path)
                        ) as pbar:

                            # 发送请求，设置较大的超时时间
                            response = session.get(url, headers=resume_header, stream=True, timeout=timeout)
                            response.raise_for_status()

                            # 验证Range请求是否成功
                            if initial_size > 0 and response.status_code != 206:
                                log.warning(f"服务器不支持断点续传，将从头开始下载")
                                # 关闭当前文件并重新以写入模式打开
                                file.close()
                                with open(save_path, 'wb') as new_file, tqdm(
                                        total=total_size if total_size > 0 else None,
                                        unit='B',
                                        unit_scale=True,
                                        unit_divisor=1024,
                                        desc=os.path.basename(save_path)
                                ) as new_pbar:
                                    # 重新下载整个文件
                                    # 下载速度控制
                                    if speed_limit:
                                        max_chunk_time = chunk_size / speed_limit
                                        chunk_start_time = time.time()
                                    else:
                                        max_chunk_time = 0

                                    for chunk in response.iter_content(chunk_size=chunk_size):
                                        if chunk:
                                            new_file.write(chunk)
                                            new_file.flush()
                                            new_pbar.update(len(chunk))

                                            # 速度限制逻辑
                                            if speed_limit:
                                                elapsed = time.time() - chunk_start_time
                                                if elapsed < max_chunk_time:
                                                    time.sleep(max_chunk_time - elapsed)
                                                chunk_start_time = time.time()
                                return save_path

                            # 下载速度控制
                            if speed_limit:
                                max_chunk_time = chunk_size / speed_limit  # 字节/秒
                                chunk_start_time = time.time()
                            else:
                                max_chunk_time = 0

                            # 下载数据
                            for chunk in response.iter_content(chunk_size=chunk_size):
                                if chunk:
                                    file.write(chunk)
                                    file.flush()  # 确保数据写入磁盘
                                    pbar.update(len(chunk))

                                    # 速度限制逻辑
                                    if speed_limit:
                                        elapsed = time.time() - chunk_start_time
                                        if elapsed < max_chunk_time:
                                            time.sleep(max_chunk_time - elapsed)
                                        chunk_start_time = time.time()

                        # 验证下载是否完成
                        downloaded_size = os.path.getsize(save_path)
                        if total_size > 0 and downloaded_size < total_size:
                            log.warning(f"下载未完成，已下载: {downloaded_size} 字节，期望: {total_size} 字节")
                            raise Exception(f"下载未完成，大小不匹配")

                        log.info(f"下载完成! 文件保存至: {save_path}")
                        return save_path

                    except requests.exceptions.RequestException as e:
                        log.error(f"下载请求失败: {str(e)}")
                        raise
                    except IOError as e:
                        log.error(f"文件保存失败: {str(e)}")
                        raise
                    finally:
                        session.close()

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                # 针对连接错误和超时进行特殊处理
                last_exception = e
                retry_count += 1
                if retry_count <= max_retries:
                    wait_time = min(2 ** (retry_count - 1) * 2, 60)  # 针对网络错误使用更长的退避时间
                    log.warning(f"网络错误，将在 {wait_time} 秒后重试 ({retry_count}/{max_retries}): {str(e)}")
                    time.sleep(wait_time)
                else:
                    log.error(f"达到最大重试次数 {max_retries}，下载失败")
                    raise last_exception
            except Exception as e:
                # 其他错误直接抛出
                raise
        return None

    def download(self, url, save_path=None, return_content=False, chunk_size=8192, base_timeout=30,
                 num_threads=30, temp_dir=None, force_single_thread=False, min_size_for_multithread=10 * 1024 * 1024,
                 max_retries=5, speed_limit=None, proxy=None, adaptive=True, enable_resume=True):
        """
        智能下载函数，根据服务器支持和文件大小自动选择下载方式

        Args:
            url (str): 下载链接
            save_path (str, optional): 保存文件的路径，如果为None且return_content为False，则自动生成文件名；如果是目录路径，则使用服务器返回的原始文件名
            return_content (bool, optional): 是否返回文件内容而不是保存到本地
            chunk_size (int, optional): 下载块大小
            base_timeout (int, optional): 请求基础超时时间（秒）
            num_threads (int, optional): 多线程下载时的线程数
            temp_dir (str, optional): 临时文件目录，用于多线程下载和返回内容时的缓存
            force_single_thread (bool, optional): 是否强制使用单线程下载
            min_size_for_multithread (int, optional): 启用多线程下载的最小文件大小（默认10MB）
            max_retries (int, optional): 下载失败时的最大重试次数（默认5次）
            speed_limit (int, optional): 下载速度限制（字节/秒），默认无限制
            proxy (str, optional): 代理地址，格式如 'http://127.0.0.1:7890'，传入即使用，不可用则自动降级
            adaptive (bool, optional): 是否启用自適應优化，根据实时速度自动调整线程数（默认是True）
            enable_resume (bool, optional): 是否启用断点续传（默认是True），仅对多线程下载有效

        Returns:
            str or bytes: 如果return_content为True，返回文件内容(bytes)；否则返回保存的文件路径(str)
        """
        # 如果传入了代理参数，设置代理
        if proxy is not None:
            self.set_proxy(proxy)

        # 判断是否使用代理
        use_proxy = self._proxy_available

        # 动态调整超时时间函数
        def get_dynamic_timeout(file_size):
            # 基础超时30秒，每增加100MB增加10秒超时，最大1200秒
            if file_size <= 0:
                return base_timeout
            return min(base_timeout + int(file_size / (100 * 1024 * 1024)) * 10, 1200)

        # 记录下载开始时间
        start_time = time.time()

        # 如果需要返回内容，先检查是否可以使用多线程下载
        if return_content:
            # 检查服务器是否支持分片下载
            range_support, file_size = self.check_range_support(url)

            # 动态计算超时时间
            timeout = get_dynamic_timeout(file_size)
            log.info(f"文件大小: {file_size / 1024 / 1024:.2f}MB, 动态设置超时时间: {timeout}秒")

            # 如果支持分片且文件大小超过阈值，并且不强制单线程，使用多线程下载到临时文件
            if range_support and file_size >= min_size_for_multithread and not force_single_thread:
                log.info(f"大文件内容返回，使用多线程下载，文件大小: {file_size / 1024 / 1024:.2f}MB")

                # 生成临时文件路径
                effective_temp_dir = temp_dir
                if not effective_temp_dir:
                    # 获取最大空闲磁盘作为临时文件的存储位置，而不是系统临时目录
                    disk_dir, _ = get_largest_free_space_disk()
                    if disk_dir:
                        effective_temp_dir = os.path.join(disk_dir, "enh_temp")
                        os.makedirs(effective_temp_dir, exist_ok=True)
                    else:
                        # 如果无法获取空闲磁盘，回退到系统临时目录
                        effective_temp_dir = tempfile.gettempdir()
                        os.makedirs(effective_temp_dir, exist_ok=True)
                
                temp_filename = os.path.join(effective_temp_dir, f"temp_{uuid.uuid4().hex}")

                try:
                    # 使用多线程下载到临时文件
                    self.multi_thread_download(url, temp_filename, file_size, num_threads, effective_temp_dir,
                                               use_proxy=use_proxy, adaptive=adaptive, enable_resume=enable_resume)

                    # 读取临时文件内容
                    with open(temp_filename, 'rb') as f:
                        content = f.read()

                    # 计算下载统计信息
                    end_time = time.time()
                    total_time = end_time - start_time
                    if total_time > 0:
                        speed = len(content) / total_time / 1024 / 1024  # MB/s
                        log.info(
                            f"下载完成! 总大小: {len(content) / 1024 / 1024:.2f}MB, 总时间: {total_time:.2f}秒, 平均速度: {speed:.2f}MB/s")

                    return content

                finally:
                    # 清理临时文件
                    if os.path.exists(temp_filename):
                        try:
                            os.remove(temp_filename)
                            log.info(f"已清理临时文件: {temp_filename}")
                        except Exception as e:
                            log.warning(f"清理临时文件失败: {str(e)}")
            else:
                # 小文件或不支持分片或强制单线程，使用单线程下载
                if not range_support:
                    log.info("服务器不支持分片下载，使用单线程下载返回内容")
                elif force_single_thread:
                    log.info("强制使用单线程下载返回内容")
                else:
                    log.info(f"文件大小小于{min_size_for_multithread / 1024 / 1024:.2f}MB，使用单线程下载返回内容")

                result = self.single_thread_download(url, None, return_content=True, chunk_size=chunk_size,
                                                     timeout=timeout, max_retries=max_retries, speed_limit=speed_limit,
                                                     use_proxy=use_proxy)

                # 计算下载统计信息
                end_time = time.time()
                total_time = end_time - start_time
                if total_time > 0:
                    speed = len(result) / total_time / 1024 / 1024  # MB/s
                    log.info(
                        f"下载完成! 总大小: {len(result) / 1024 / 1024:.2f}MB, 总时间: {total_time:.2f}秒, 平均速度: {speed:.2f}MB/s")

                return result

        # 确定保存路径
        if save_path is None:
            # 如果没有指定保存路径，使用脚本所在目录
            disk_dir, disk_size = get_largest_free_space_disk()
            file_dir = os.path.join(disk_dir, "enh_downloads")
            save_path = file_dir
            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)

            log.info(f"未指定保存路径，使用设备空闲磁盘所在目录: {save_path}")
        # 如果save_path是一个目录，则使用服务器返回的原始文件名
        if os.path.isdir(save_path):
            # 发送HEAD请求获取文件名和内容类型
            session = self.create_session()
            try:
                head_response = session.head(url)
                head_response.raise_for_status()

                # 尝试从Content-Disposition头中获取原始文件名
                content_disposition = head_response.headers.get('Content-Disposition', '')
                filename = None

                # 从Content-Disposition中提取文件名
                if 'filename=' in content_disposition:
                    match = re.findall(r'filename="?([^";]+)', content_disposition)
                    if match:
                        filename = match[0]

                # 如果Content-Disposition中没有，则从URL中获取文件名
                if not filename:
                    filename = os.path.basename(url.split('?')[0])

                # 如果文件名无效，生成时间戳文件名
                if not filename or '.' not in filename:
                    # 生成时间戳文件名
                    timestamp = int(time.time())
                    content_type = head_response.headers.get('content-type', 'application/octet-stream')
                    # 简单的内容类型到文件扩展名的映射
                    ext_map = {
                        'application/pdf': '.pdf',
                        'application/zip': '.zip',
                        'application/xml': '.xml',
                        'text/xml': '.xml',
                        'application/json': '.json',
                        'text/plain': '.txt'
                    }
                    extension = ext_map.get(content_type, '.bin')
                    filename = f"download_{timestamp}{extension}"

                # 根据是否提供了目录路径来决定保存位置
                save_path = os.path.join(save_path, filename)

                log.info(f"将使用服务器原始文件名: {filename}")
            finally:
                session.close()

        if len(save_path) > 0 and '\\' not in save_path and '/' not in save_path:
            log.warning(f"仅指定了文件名: {save_path}")
            disk_dir, disk_size = get_largest_free_space_disk()
            file_dir = os.path.join(disk_dir, "enh_downloads")
            save_path = os.path.join(file_dir, save_path)
            log.warning(f"将文件保存到设备空闲磁盘所在位置: {save_path}")

        # 检查是否需要使用多线程下载
        if not force_single_thread:
            # 检查服务器是否支持分片下载
            range_support, file_size = self.check_range_support(url)

            # 动态计算超时时间
            timeout = get_dynamic_timeout(file_size)
            log.info(f"文件大小: {file_size / 1024 / 1024:.2f}MB, 动态设置超时时间: {timeout}秒")

            # 如果支持分片且文件大小超过阈值，使用多线程下载
            if range_support and file_size >= min_size_for_multithread:
                log.info(f"服务器支持分片下载，文件大小: {file_size / 1024 / 1024:.2f}MB，使用多线程下载")
                try:
                    # 如果没有指定临时目录，自动使用目标文件所在的磁盘作为临时文件的存储位置
                    effective_temp_dir = temp_dir
                    if not effective_temp_dir:
                        save_dir = os.path.dirname(os.path.abspath(save_path))
                        effective_temp_dir = save_dir
                    result = self.multi_thread_download(url, save_path, file_size, num_threads, effective_temp_dir,
                                                        use_proxy=use_proxy, adaptive=adaptive, enable_resume=enable_resume)

                    # 计算下载统计信息
                    end_time = time.time()
                    total_time = end_time - start_time
                    if total_time > 0:
                        speed = os.path.getsize(result) / total_time / 1024 / 1024  # MB/s
                        log.info(
                            f"下载完成! 总大小: {os.path.getsize(result) / 1024 / 1024:.2f}MB, 总时间: {total_time:.2f}秒, 平均速度: {speed:.2f}MB/s")

                    return result
                except Exception as e:
                    log.warning(f"多线程下载失败: {str(e)}，切换到单线程下载")
            else:
                if not range_support:
                    log.info("服务器不支持分片下载，使用单线程下载")
                else:
                    log.info(f"文件大小小于{min_size_for_multithread / 1024 / 1024:.2f}MB，使用单线程下载")
        else:
            log.info("强制使用单线程下载")
            # 检查服务器是否支持分片下载并获取文件大小用于动态超时
            _, file_size = self.check_range_support(url)
            timeout = get_dynamic_timeout(file_size)
            log.info(f"文件大小: {file_size / 1024 / 1024:.2f}MB, 动态设置超时时间: {timeout}秒")

        # 使用单线程下载，添加重试逻辑
        retry_count = 0
        last_exception = None

        while retry_count <= max_retries:
            try:
                result = self.single_thread_download(url, save_path, return_content=False, chunk_size=chunk_size,
                                                     timeout=timeout, max_retries=max_retries, speed_limit=speed_limit,
                                                     use_proxy=use_proxy)

                # 计算下载统计信息
                end_time = time.time()
                total_time = end_time - start_time
                if total_time > 0:
                    speed = os.path.getsize(result) / total_time / 1024 / 1024  # MB/s
                    log.info(
                        f"下载完成! 总大小: {os.path.getsize(result) / 1024 / 1024:.2f}MB, 总时间: {total_time:.2f}秒, 平均速度: {speed:.2f}MB/s")

                return result
            except Exception as e:
                last_exception = e
                retry_count += 1
                if retry_count <= max_retries:
                    wait_time = min(2 ** (retry_count - 1), 60)  # 指数退避，但最大等待60秒
                    log.warning(f"下载失败，将在 {wait_time} 秒后重试 ({retry_count}/{max_retries}): {str(e)}")
                    time.sleep(wait_time)
                else:
                    log.error(f"达到最大重试次数 {max_retries}，下载失败")
                    raise last_exception

        return None


# 创建全局下载器实例
downloader = EnhancedDownloader()


# 提供便捷函数
def download_file(url, save_path=None, return_content=False, chunk_size=8192, base_timeout=30,
                  num_threads=30, temp_dir=None, force_single_thread=False, min_size_for_multithread=10 * 1024 * 1024,
                  max_retries=5, speed_limit=None, proxy=None, adaptive=True, enable_resume=True):
    """
    便捷下载函数，使用全局下载器实例

    Args:
        url (str): 下载链接
        save_path (str, optional): 保存文件的路径，如果为None且return_content为False，则自动采用当前设备最大盘符所在位置
        return_content (bool, optional): 是否返回文件内容而不是保存到本地
        chunk_size (int, optional): 下载块大小
        base_timeout (int, optional): 请求基础超时时间（秒）
        num_threads (int, optional): 多线程下载时的线程数
        temp_dir (str, optional): 临时文件目录
        force_single_thread (bool, optional): 是否强制使用单线程下载
        min_size_for_multithread (int, optional): 启用多线程下载的最小文件大小（默认10MB）
        max_retries (int, optional): 下载失败时的最大重试次数（默认5次）
        speed_limit (int, optional): 下载速度限制（字节/秒），默认无限制
        proxy (str, optional): 代理地址，格式如 'http://127.0.0.1:7890'，传入即使用，不可用则自动降级
        adaptive (bool, optional): 是否启用自適應优化，默认是True
        enable_resume (bool, optional): 是否启用断点续传，默认是True，仅对多线程下载有效

    Returns:
        str or bytes: 如果return_content为True，返回文件内容(bytes)；否则返回保存的文件路径(str)
    """
    return downloader.download(
        url=url,
        save_path=save_path,
        return_content=return_content,
        chunk_size=chunk_size,
        base_timeout=base_timeout,
        num_threads=num_threads,
        temp_dir=temp_dir,
        force_single_thread=force_single_thread,
        min_size_for_multithread=min_size_for_multithread,
        max_retries=max_retries,
        speed_limit=speed_limit,
        proxy=proxy,
        adaptive=adaptive,
        enable_resume=enable_resume
    )


# 示例用法
if __name__ == "__main__":
    # 要下载的URL
    target_url = "https://publication-bdds.apps.epo.org/bdds/bdds-bff-service/prod/api/public/products/32/delivery/2887/item/8270/download"

    try:
        # 示例1: 下载并保存到指定路径
        # download_path = download_file(target_url, save_path="E:\work\demo",
        #                               base_timeout=600, max_retries=10, chunk_size=2 * 1024 * 1024)
        # print(f"文件保存路径: {download_path}")
        url = 'https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref100/uniref100.xml.gz'
        download_file(url, enable_resume=True)

        # 示例2: 下载并返回内容
        # file_content = download_file(target_url, return_content=True)
        # print(f"获取到文件内容，大小: {len(file_content)} 字节")

        # 示例3: 下载到自动生成的路径
        # download_path = download_file(target_url)
        # print(f"自动保存路径: {download_path}")

        # 示例4: 强制使用单线程下载
        # download_path = download_file(target_url, force_single_thread=True)
        # print(f"强制单线程下载路径: {download_path}")

        # 示例5: 限制下载速度为1MB/s
        # download_path = download_file(target_url, speed_limit=1024*1024)
        # print(f"限速下载路径: {download_path}")

    except Exception as e:
        print(f"操作失败: {str(e)}")
