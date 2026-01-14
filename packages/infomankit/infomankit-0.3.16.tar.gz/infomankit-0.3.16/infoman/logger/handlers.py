# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/12/23 18:02
# Author     ：Maxwell
# Description：
"""
import orjson
import time
from pathlib import Path
from typing import Dict, List, Optional
from threading import Thread, Lock, Event
from queue import Queue, Empty

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class LokiHandler:
    """
    Loki 日志处理器

    功能：
    1. 批量推送（减少网络请求）
    2. 异步推送（不阻塞主线程）
    3. 自动重试（网络异常时）
    4. 降级策略（Loki 不可用时写备份文件）
    """

    def __init__(
            self,
            url: str,
            labels: Dict[str, str],
            batch_size: int = 100,
            flush_interval: float = 5.0,
            timeout: float = 10.0,
            retry_times: int = 3,
            retry_backoff: float = 2.0,
            enable_fallback: bool = True,
            fallback_file: Optional[Path] = None,
    ):
        """
        初始化 Loki 处理器

        Args:
            url: Loki 服务地址
            labels: Loki Labels
            batch_size: 批量推送大小
            flush_interval: 刷新间隔（秒）
            timeout: 推送超时（秒）
            retry_times: 重试次数
            retry_backoff: 重试退避系数
            enable_fallback: 启用降级策略
            fallback_file: 备份文件路径
        """
        if not HTTPX_AVAILABLE:
            raise ImportError("LokiHandler 需要 httpx: pip install httpx")

        self.url = f"{url}/loki/api/v1/push"
        self.labels = labels
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.timeout = timeout
        self.retry_times = retry_times
        self.retry_backoff = retry_backoff
        self.enable_fallback = enable_fallback
        self.fallback_file = fallback_file

        # 日志队列
        self.queue: Queue = Queue(maxsize=10000)
        self.batch: List[Dict] = []
        self.lock = Lock()

        # 后台线程
        self.stop_event = Event()
        self.worker_thread = Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

        # HTTP 客户端
        self.client = httpx.Client(timeout=timeout)

        # 统计信息
        self.sent_count = 0
        self.failed_count = 0
        self.fallback_count = 0

    def write(self, message):
        """
        写入日志（Loguru 调用）

        Args:
            message: 日志消息对象
        """
        try:
            record = message.record

            # 构造日志条目
            entry = {
                "timestamp": int(record["time"].timestamp() * 1e9),  # 纳秒时间戳
                "line": self._format_line(record),
            }

            # 放入队列
            self.queue.put_nowait(entry)

        except Exception as e:
            # 避免日志处理器本身抛出异常
            print(f"LokiHandler 写入失败: {e}")

    def _format_line(self, record: Dict) -> str:
        """格式化日志行"""
        return orjson.dumps({
            "level": record["level"].name,
            "logger": record["name"],
            "function": record["function"],
            "line": record["line"],
            "message": record["message"],
            "extra": record.get("extra", {}),
        }).decode('utf-8')

    def _worker(self):
        """后台工作线程"""
        last_flush_time = time.time()

        while not self.stop_event.is_set():
            try:
                # 从队列获取日志
                try:
                    entry = self.queue.get(timeout=1.0)

                    with self.lock:
                        self.batch.append(entry)

                except Empty:
                    pass

                # 检查是否需要刷新
                current_time = time.time()
                should_flush = (
                        len(self.batch) >= self.batch_size or
                        (self.batch and current_time - last_flush_time >= self.flush_interval)
                )

                if should_flush:
                    self._flush()
                    last_flush_time = current_time

            except Exception as e:
                print(f"LokiHandler 工作线程异常: {e}")

        # 线程退出前，刷新剩余日志
        self._flush()

    def _flush(self):
        """刷新日志批次"""
        with self.lock:
            if not self.batch:
                return

            batch_to_send = self.batch.copy()
            self.batch.clear()

        # 推送到 Loki
        success = self._push_to_loki(batch_to_send)

        if success:
            self.sent_count += len(batch_to_send)
        else:
            self.failed_count += len(batch_to_send)

            # 降级策略：写备份文件
            if self.enable_fallback:
                self._write_fallback(batch_to_send)

    def _push_to_loki(self, batch: List[Dict]) -> bool:
        """
        推送日志到 Loki

        Args:
            batch: 日志批次

        Returns:
            True: 成功
            False: 失败
        """
        # 构造 Loki 请求体
        payload = {
            "streams": [
                {
                    "stream": self.labels,
                    "values": [
                        [str(entry["timestamp"]), entry["line"]]
                        for entry in batch
                    ]
                }
            ]
        }

        # 重试推送
        for attempt in range(self.retry_times + 1):
            try:
                response = self.client.post(
                    self.url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code == 204:
                    return True

                print(
                    f"Loki 推送失败 [尝试 {attempt + 1}/{self.retry_times + 1}]: "
                    f"HTTP {response.status_code} - {response.text}"
                )

            except Exception as e:
                print(
                    f"Loki 推送异常 [尝试 {attempt + 1}/{self.retry_times + 1}]: {e}"
                )

            # 退避重试
            if attempt < self.retry_times:
                time.sleep(self.retry_backoff ** attempt)

        return False

    def _write_fallback(self, batch: List[Dict]):
        """
        写入备份文件

        Args:
            batch: 日志批次
        """
        if not self.fallback_file:
            return

        try:
            with open(self.fallback_file, "a", encoding="utf-8") as f:
                for entry in batch:
                    f.write(entry["line"] + "\n")

            self.fallback_count += len(batch)

        except Exception as e:
            print(f"写入备份文件失败: {e}")

    def flush(self):
        """手动刷新"""
        self._flush()

    def close(self):
        """关闭处理器"""
        # 停止工作线程
        self.stop_event.set()
        self.worker_thread.join(timeout=5.0)

        # 关闭 HTTP 客户端
        self.client.close()

        print(
            f"LokiHandler 已关闭 "
            f"[发送={self.sent_count}, 失败={self.failed_count}, "
            f"备份={self.fallback_count}]"
        )

    def __del__(self):
        """析构函数"""
        try:
            self.close()
        except:
            pass
