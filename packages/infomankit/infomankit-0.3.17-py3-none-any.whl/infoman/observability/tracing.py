"""
分布式追踪实现

基于 OpenTelemetry 提供自动和手动追踪能力
"""

import functools
from typing import Optional, Dict, Any, Callable
from contextlib import contextmanager

from loguru import logger

from .config import ObservabilityConfig

# 全局变量
_tracer_provider = None
_tracer = None
_config: Optional[ObservabilityConfig] = None


def setup_tracing(config: Optional[ObservabilityConfig] = None) -> None:
    """
    初始化 OpenTelemetry 追踪

    Args:
        config: 可观测性配置，如果为None则使用默认配置
    """
    global _tracer_provider, _tracer, _config

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as GRPCExporter
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as HTTPExporter
        from opentelemetry.sdk.trace.sampling import (
            AlwaysOn,
            AlwaysOff,
            ParentBasedTraceIdRatio,
            TraceIdRatioBased,
        )
    except ImportError:
        logger.warning("OpenTelemetry not installed, tracing disabled")
        return

    # 加载配置
    _config = config or ObservabilityConfig()

    if not _config.OTEL_ENABLED:
        logger.info("OpenTelemetry tracing is disabled")
        return

    try:
        # 创建资源
        resource_attributes = {
            SERVICE_NAME: _config.OTEL_SERVICE_NAME,
            SERVICE_VERSION: _config.OTEL_SERVICE_VERSION,
            DEPLOYMENT_ENVIRONMENT: _config.OTEL_DEPLOYMENT_ENVIRONMENT,
        }

        # 添加自定义资源属性
        if _config.OTEL_RESOURCE_ATTRIBUTES:
            for attr in _config.OTEL_RESOURCE_ATTRIBUTES.split(","):
                if "=" in attr:
                    key, value = attr.split("=", 1)
                    resource_attributes[key.strip()] = value.strip()

        resource = Resource.create(resource_attributes)

        # 配置采样器
        if _config.OTEL_TRACE_SAMPLER == "always_on":
            sampler = AlwaysOn()
        elif _config.OTEL_TRACE_SAMPLER == "always_off":
            sampler = AlwaysOff()
        elif _config.OTEL_TRACE_SAMPLER == "traceidratio":
            sampler = TraceIdRatioBased(_config.OTEL_TRACE_SAMPLER_RATIO)
        else:  # parentbased
            sampler = ParentBasedTraceIdRatio(_config.OTEL_TRACE_SAMPLER_RATIO)

        # 创建 TracerProvider
        _tracer_provider = TracerProvider(
            resource=resource,
            sampler=sampler,
        )

        # 配置导出器
        if _config.OTEL_EXPORTER_TYPE == "otlp":
            # 使用 gRPC 导出器
            span_exporter = GRPCExporter(
                endpoint=_config.OTEL_EXPORTER_OTLP_ENDPOINT,
                insecure=_config.OTEL_EXPORTER_OTLP_INSECURE,
            )
        elif _config.OTEL_EXPORTER_TYPE == "jaeger":
            from opentelemetry.exporter.jaeger.thrift import JaegerExporter

            span_exporter = JaegerExporter(
                agent_host_name=_config.OTEL_EXPORTER_JAEGER_AGENT_HOST,
                agent_port=_config.OTEL_EXPORTER_JAEGER_AGENT_PORT,
            )
        else:  # console
            from opentelemetry.sdk.trace.export import ConsoleSpanExporter

            span_exporter = ConsoleSpanExporter()

        # 添加 SpanProcessor
        _tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))

        # 设置全局 TracerProvider
        trace.set_tracer_provider(_tracer_provider)

        # 获取 tracer
        _tracer = trace.get_tracer(__name__)

        logger.success(
            f"OpenTelemetry tracing initialized: "
            f"service={_config.OTEL_SERVICE_NAME}, "
            f"exporter={_config.OTEL_EXPORTER_TYPE}"
        )

        # 自动仪表盘
        _auto_instrument()

    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry tracing: {e}")


def _auto_instrument() -> None:
    """自动仪表盘常用库"""
    if not _config:
        return

    try:
        # FastAPI
        if _config.OTEL_INSTRUMENT_FASTAPI:
            try:
                from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

                FastAPIInstrumentor().instrument()
                logger.debug("FastAPI instrumentation enabled")
            except ImportError:
                pass

        # HTTPX
        if _config.OTEL_INSTRUMENT_HTTPX:
            try:
                from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

                HTTPXClientInstrumentor().instrument()
                logger.debug("HTTPX instrumentation enabled")
            except ImportError:
                pass

        # Redis
        if _config.OTEL_INSTRUMENT_REDIS:
            try:
                from opentelemetry.instrumentation.redis import RedisInstrumentor

                RedisInstrumentor().instrument()
                logger.debug("Redis instrumentation enabled")
            except ImportError:
                pass

        # SQLAlchemy
        if _config.OTEL_INSTRUMENT_SQLALCHEMY:
            try:
                from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

                SQLAlchemyInstrumentor().instrument()
                logger.debug("SQLAlchemy instrumentation enabled")
            except ImportError:
                pass

    except Exception as e:
        logger.warning(f"Auto instrumentation failed: {e}")


def get_tracer():
    """获取全局 tracer"""
    if _tracer is None:
        setup_tracing()
    return _tracer


@contextmanager
def trace_span(name: str, attributes: Optional[Dict[str, Any]] = None):
    """
    创建一个追踪 span 的上下文管理器

    Usage:
        with trace_span("my_operation", {"key": "value"}):
            # your code here
            pass
    """
    tracer = get_tracer()
    if tracer is None:
        yield None
        return

    with tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
        yield span


def trace_function(
    name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
):
    """
    装饰器：追踪同步函数

    Args:
        name: span 名称，默认使用函数名
        attributes: span 属性

    Usage:
        @trace_function(name="my_func", attributes={"key": "value"})
        def my_func():
            pass
    """

    def decorator(func: Callable) -> Callable:
        span_name = name or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with trace_span(span_name, attributes):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def trace_async_function(
    name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
):
    """
    装饰器：追踪异步函数

    Args:
        name: span 名称，默认使用函数名
        attributes: span 属性

    Usage:
        @trace_async_function(name="my_async_func")
        async def my_async_func():
            pass
    """

    def decorator(func: Callable) -> Callable:
        span_name = name or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            with trace_span(span_name, attributes):
                return await func(*args, **kwargs)

        return wrapper

    return decorator


def add_span_event(name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
    """
    在当前 span 中添加事件

    Args:
        name: 事件名称
        attributes: 事件属性
    """
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        if span.is_recording():
            span.add_event(name, attributes or {})
    except Exception:
        pass


def set_span_attribute(key: str, value: Any) -> None:
    """
    设置当前 span 的属性

    Args:
        key: 属性键
        value: 属性值
    """
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute(key, str(value))
    except Exception:
        pass


def record_exception(exception: Exception) -> None:
    """
    记录异常到当前 span

    Args:
        exception: 异常对象
    """
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        if span.is_recording():
            span.record_exception(exception)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(exception)))
    except Exception:
        pass
