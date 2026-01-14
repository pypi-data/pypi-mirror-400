# !/usr/bin/env python
# -*-coding:utf-8 -*-

from infoman.config.settings import settings
from infoman.logger import setup_logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from infoman.service.middleware.logging import LoggingMiddleware
from infoman.service.middleware.request_id import RequestIDMiddleware
from infoman.service.routers import api_router
from infoman.config.settings import settings as config
from infoman.service.core.response import ProRJSONResponse
from infoman.service.core.monitor import instrumentator
from infoman.service.core.lifespan import lifespan
from infoman.service.exception.handler import register_exception_handlers

# ============ 日志配置 ============
setup_logger()

# ============ 可观测性配置 ============
try:
    from infoman.observability import setup_tracing
    from infoman.observability.config import ObservabilityConfig

    otel_config = ObservabilityConfig()
    if otel_config.OTEL_ENABLED:
        setup_tracing(otel_config)
except ImportError:
    pass  # OpenTelemetry 未安装，跳过

# ============ 创建 FastAPI 应用实例 ============
application = FastAPI(
    title=config.APP_NAME,
    docs_url=config.DOCS_URL,
    redoc_url=config.APP_REDOC_URL,
    description=config.APP_DESCRIPTION,
    default_response_class=ProRJSONResponse,
    lifespan=lifespan
)

# ============ 异常处理器 ============
register_exception_handlers(application)

# ============ 中间件（添加顺序和执行顺序相反-洋葱模型） ============
application.add_middleware(GZipMiddleware, minimum_size=1000)
application.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOW_ORIGINS,
    allow_credentials=config.ALLOW_CREDENTIALS,
    allow_methods=config.ALLOW_METHODS,
    allow_headers=config.ALLOW_HEADERS,
    max_age=config.MAX_AGE,
)
application.add_middleware(RequestIDMiddleware)
application.add_middleware(LoggingMiddleware)

# ============ 内置路由（可选，用户可以选择不使用） ============
if config.USE_DEFAULT_ROUTER:
    application.include_router(api_router)

if config.USE_TEMPLATES:
    from fastapi.templating import Jinja2Templates
    application.state.templates = Jinja2Templates(directory=config.TEMPLATE_DIR)

if config.USE_STATIC:
    from fastapi.staticfiles import StaticFiles
    application.mount(
        path=config.STATIC_URL,
        app=StaticFiles(directory=config.STATIC_DIR),
        name=config.STATIC_NAME
    )

# ============ Prometheus 监控 ============
if config.USE_PROMETHEUS_ROUTER:
    instrumentator.instrument(application).expose(application, endpoint="/metrics")


