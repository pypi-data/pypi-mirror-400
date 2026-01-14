"""
可观测性模块

提供分布式追踪、指标收集和日志关联功能
基于 OpenTelemetry 标准
"""

from .tracing import (
    setup_tracing,
    get_tracer,
    trace_function,
    trace_async_function,
)
from .config import ObservabilityConfig

__all__ = [
    "setup_tracing",
    "get_tracer",
    "trace_function",
    "trace_async_function",
    "ObservabilityConfig",
]
