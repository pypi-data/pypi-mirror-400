# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
日志格式化器

使用 orjson 提升 JSON 序列化性能
"""

import orjson
import traceback
from typing import Dict, Any

# =================================================================
# 控制台格式（带颜色）
# =================================================================

CONSOLE_FORMATS = {
    "simple": (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    ),

    "detailed": (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    ),

    "debug": (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<magenta>{process}</magenta>:<magenta>{thread}</magenta> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    ),

    "json": "{message}",  # JSON 格式由 serialize 参数处理

    "pro": (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "{extra[hostname]} | "
        "{extra[app_name]} | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan> | "
        "<level>{message}</level>"
    ),
}

# =================================================================
# 文件格式（无颜色）
# =================================================================

FILE_FORMATS = {
    "simple": (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{message}"
    ),

    "detailed": (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    ),

    "debug": (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{process}:{thread} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    ),

    "json": "{message}",

    "pro": (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{extra[hostname]} | "
        "{extra[app_name]} | "
        "{level: <8} | "
        "{name}:{function} | "
        "{message}"
    ),
}


def get_console_format(format_type: str) -> str:
    return CONSOLE_FORMATS.get(format_type, CONSOLE_FORMATS["detailed"])


def get_file_format(format_type: str) -> str:
    return FILE_FORMATS.get(format_type, FILE_FORMATS["detailed"])


def serialize_json(record: Dict[str, Any]) -> str:
    """
    JSON 序列化函数

    将日志记录转换为 JSON 格式

    使用 orjson（如果可用）提升性能：
    - 比标准库 json 快 2-3 倍
    - 自动处理 datetime、UUID 等类型
    - 更小的内存占用
    """
    subset = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "logger": record["name"],
        "function": record["function"],
        "line": record["line"],
        "message": record["message"],
    }

    # 添加额外字段
    if record.get("extra"):
        subset["extra"] = record["extra"]

    # 添加异常信息
    if record.get("exception"):
        exc_type, exc_value, exc_tb = record["exception"]
        subset["exception"] = {
            "type": exc_type.__name__ if exc_type else "Unknown",
            "message": str(exc_value),
            # 注意：traceback 应该从 record 的其他字段获取
            # 这里简化处理，实际可能需要格式化 traceback
        }
        # 如果有 traceback 信息，添加进去
        if hasattr(exc_tb, 'tb_frame'):
            subset["exception"]["traceback"] = "".join(
                traceback.format_exception(exc_type, exc_value, exc_tb)
            )

    return orjson.dumps(subset, option=orjson.OPT_APPEND_NEWLINE).decode('utf-8')