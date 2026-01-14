# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/12/23 17:57
# Author     ：Maxwell
# Description：
"""
import re
from typing import List, Set
from loguru import logger
import time
from collections import deque


class ModuleFilter:
    """模块过滤器"""

    def __init__(self, excluded_modules: List[str]):
        self.excluded_modules = set(excluded_modules)

    def __call__(self, record) -> bool:
        """
        过滤指定模块的日志

        Returns:
            True: 保留日志
            False: 过滤日志
        """
        logger_name = record["name"]

        # 精确匹配
        if logger_name in self.excluded_modules:
            return False

        # 前缀匹配
        for module in self.excluded_modules:
            if logger_name.startswith(f"{module}."):
                return False

        return True


class KeywordFilter:

    def __init__(self, excluded_keywords: List[str]):
        self.excluded_keywords = [kw.lower() for kw in excluded_keywords]

    def __call__(self, record) -> bool:
        message = record["message"].lower()

        for keyword in self.excluded_keywords:
            if keyword in message:
                return False

        return True


class LevelFilter:

    def __init__(self, min_level: str):
        self.min_level = min_level

    def __call__(self, record) -> bool:
        return record["level"].name >= self.min_level


class RateLimitFilter:

    def __init__(self, max_messages_per_second: int):
        self.max_messages = max_messages_per_second
        self.timestamps = deque(maxlen=max_messages_per_second)
        self.dropped_count = 0

    def __call__(self, record) -> bool:
        current_time = time.time()
        while self.timestamps and current_time - self.timestamps[0] > 1.0:
            self.timestamps.popleft()

        # 检查是否超过限制
        if len(self.timestamps) >= self.max_messages:
            self.dropped_count += 1

            # 每丢弃 100 条日志，记录一次警告
            if self.dropped_count % 100 == 0:
                logger.warning(
                    f"日志速率限制触发，已丢弃 {self.dropped_count} 条日志"
                )

            return False

        self.timestamps.append(current_time)
        return True


class SanitizeFilter:
    """敏感信息脱敏过滤器"""

    def __init__(self, sensitive_fields: List[str], pattern: str = "***REDACTED***"):
        """
        Args:
            sensitive_fields: 敏感字段列表
            pattern: 替换模式
        """
        self.sensitive_fields = [field.lower() for field in sensitive_fields]
        self.pattern = pattern

    def __call__(self, record) -> bool:
        """
        脱敏处理

        Returns:
            True: 始终返回 True（不过滤，只修改）
        """
        # 脱敏消息
        record["message"] = self._sanitize_text(record["message"])

        # 脱敏 extra 字段
        if record.get("extra"):
            record["extra"] = self._sanitize_dict(record["extra"])

        return True

    def _sanitize_text(self, text: str) -> str:
        """脱敏文本"""
        for field in self.sensitive_fields:
            # 匹配 key=value 或 "key":"value" 格式
            patterns = [
                rf'{field}["\']?\s*[:=]\s*["\']?([^"\',\s}}]+)',
                rf'"{field}"\s*:\s*"([^"]+)"',
            ]

            for pattern in patterns:
                text = re.sub(
                    pattern,
                    lambda m: m.group(0).replace(m.group(1), self.pattern),
                    text,
                    flags=re.IGNORECASE
                )

        return text

    def _sanitize_dict(self, data: dict) -> dict:
        """脱敏字典"""
        sanitized = {}

        for key, value in data.items():
            if key.lower() in self.sensitive_fields:
                sanitized[key] = self.pattern
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            elif isinstance(value, str):
                sanitized[key] = self._sanitize_text(value)
            else:
                sanitized[key] = value

        return sanitized
