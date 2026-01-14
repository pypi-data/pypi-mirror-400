# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/12/23 17:58
# Author     ：Maxwell
# Description：
"""

"""日志指标统计"""

import time
from collections import defaultdict, deque
from typing import Dict, Optional
from threading import Lock


class LogMetrics:
    """日志指标统计器"""

    def __init__(self, window_size: int = 60):
        """
        Args:
            window_size: 统计窗口大小（秒）
        """
        self.window_size = window_size
        self.lock = Lock()

        # 日志计数（按级别）
        self.counts: Dict[str, int] = defaultdict(int)

        # 时间序列（用于速率计算）
        self.timestamps: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )

        # 错误统计
        self.error_count = 0
        self.error_timestamps = deque(maxlen=1000)

    def record(self, level: str):
        """
        记录日志

        Args:
            level: 日志级别
        """
        with self.lock:
            current_time = time.time()

            # 更新计数
            self.counts[level] += 1
            self.timestamps[level].append(current_time)

            # 记录错误
            if level in ("ERROR", "CRITICAL"):
                self.error_count += 1
                self.error_timestamps.append(current_time)

    def get_counts(self) -> Dict[str, int]:
        """获取日志计数"""
        with self.lock:
            return dict(self.counts)

    def get_rate(self, level: str) -> float:
        """
        获取日志速率（每秒）

        Args:
            level: 日志级别

        Returns:
            每秒日志数
        """
        with self.lock:
            timestamps = self.timestamps[level]
            if not timestamps:
                return 0.0

            current_time = time.time()

            # 过滤窗口内的时间戳
            recent = [
                ts for ts in timestamps
                if current_time - ts <= self.window_size
            ]

            if not recent:
                return 0.0

            duration = current_time - recent[0]
            return len(recent) / duration if duration > 0 else 0.0

    def get_error_rate(self) -> float:
        """获取错误速率（每秒）"""
        with self.lock:
            if not self.error_timestamps:
                return 0.0

            current_time = time.time()

            # 过滤窗口内的时间戳
            recent = [
                ts for ts in self.error_timestamps
                if current_time - ts <= self.window_size
            ]

            if not recent:
                return 0.0

            duration = current_time - recent[0]
            return len(recent) / duration if duration > 0 else 0.0

    def check_error_threshold(self, threshold: int, window: int) -> bool:
        """
        检查错误阈值

        Args:
            threshold: 错误阈值
            window: 时间窗口（秒）

        Returns:
            True: 超过阈值
            False: 未超过阈值
        """
        with self.lock:
            current_time = time.time()

            # 统计窗口内的错误数
            recent_errors = sum(
                1 for ts in self.error_timestamps
                if current_time - ts <= window
            )

            return recent_errors >= threshold

    def get_summary(self) -> Dict[str, any]:
        """获取统计摘要"""
        with self.lock:
            return {
                "total_counts": dict(self.counts),
                "error_count": self.error_count,
                "error_rate": round(self.get_error_rate(), 2),
                "rates": {
                    level: round(self.get_rate(level), 2)
                    for level in self.counts.keys()
                },
            }


# 全局指标实例
_metrics_instance: Optional[LogMetrics] = None


def get_metrics() -> LogMetrics:
    """获取指标实例"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = LogMetrics()
    return _metrics_instance
