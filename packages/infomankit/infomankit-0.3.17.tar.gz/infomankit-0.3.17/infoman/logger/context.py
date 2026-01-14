# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/12/23 17:58
# Author     ：Maxwell
# Description：
"""
import contextvars
from typing import Dict, Any, Optional
from uuid import uuid4

# =================================================================
# 上下文变量
# =================================================================

# 请求 ID
request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'request_id', default=None
)

# 用户 ID
user_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'user_id', default=None
)

# 追踪 ID（分布式追踪）
trace_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'trace_id', default=None
)

# Span ID（分布式追踪）
span_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'span_id', default=None
)

# 自定义上下文
custom_context_var: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar(
    'custom_context', default={}
)


# =================================================================
# 上下文管理函数
# =================================================================

def set_request_id(request_id: Optional[str] = None) -> str:
    """
    设置请求 ID

    Args:
        request_id: 请求 ID（None 则自动生成）

    Returns:
        请求 ID
    """
    if request_id is None:
        request_id = str(uuid4())

    request_id_var.set(request_id)
    return request_id


def get_request_id() -> Optional[str]:
    """获取请求 ID"""
    return request_id_var.get()


def set_user_id(user_id: str):
    """设置用户 ID"""
    user_id_var.set(user_id)


def get_user_id() -> Optional[str]:
    """获取用户 ID"""
    return user_id_var.get()


def set_trace_id(trace_id: str):
    """设置追踪 ID"""
    trace_id_var.set(trace_id)


def get_trace_id() -> Optional[str]:
    """获取追踪 ID"""
    return trace_id_var.get()


def set_span_id(span_id: str):
    """设置 Span ID"""
    span_id_var.set(span_id)


def get_span_id() -> Optional[str]:
    """获取 Span ID"""
    return span_id_var.get()


def set_context(key: str, value: Any):
    """
    设置自定义上下文

    Args:
        key: 键
        value: 值
    """
    context = custom_context_var.get().copy()
    context[key] = value
    custom_context_var.set(context)


def get_context(key: str) -> Optional[Any]:
    """获取自定义上下文"""
    return custom_context_var.get().get(key)


def get_all_context() -> Dict[str, Any]:
    """获取所有上下文"""
    context = {
        "request_id": get_request_id(),
        "user_id": get_user_id(),
        "trace_id": get_trace_id(),
        "span_id": get_span_id(),
    }

    # 合并自定义上下文
    context.update(custom_context_var.get())

    # 移除 None 值
    return {k: v for k, v in context.items() if v is not None}


def clear_context():
    """清除所有上下文"""
    request_id_var.set(None)
    user_id_var.set(None)
    trace_id_var.set(None)
    span_id_var.set(None)
    custom_context_var.set({})


# =================================================================
# 上下文装饰器
# =================================================================

from functools import wraps


def with_request_id(func):
    """
    自动设置请求 ID 的装饰器

    用法:
        @with_request_id
        def my_function():
            logger.info("处理请求")  # 自动包含 request_id
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        set_request_id()
        try:
            return func(*args, **kwargs)
        finally:
            clear_context()

    return wrapper


def with_user_context(user_id: str):
    """
    自动设置用户上下文的装饰器

    用法:
        @with_user_context("user_123")
        def my_function():
            logger.info("用户操作")  # 自动包含 user_id
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            set_user_id(user_id)
            try:
                return func(*args, **kwargs)
            finally:
                clear_context()

        return wrapper

    return decorator
