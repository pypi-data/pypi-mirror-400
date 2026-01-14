# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/12/23 17:27
# Author     ：Maxwell
# Description：
"""

from loguru import logger
from .core import setup_logger, get_logger_manager, shutdown_logger
from .context import (
    set_request_id,
    get_request_id,
    set_user_id,
    get_user_id,
    set_trace_id,
    get_trace_id,
    set_span_id,
    get_span_id,
    set_context,
    get_context,
    get_all_context,
    clear_context,
    with_request_id,
    with_user_context,
)
from .metrics import get_metrics

__all__ = [
    # 日志对象
    "logger",

    # 核心功能
    "setup_logger",
    "get_logger_manager",
    "shutdown_logger",

    # 上下文管理
    "set_request_id",
    "get_request_id",
    "set_user_id",
    "get_user_id",
    "set_trace_id",
    "get_trace_id",
    "set_span_id",
    "get_span_id",
    "set_context",
    "get_context",
    "get_all_context",
    "clear_context",
    "with_request_id",
    "with_user_context",

    # 指标统计
    "get_metrics",
]
