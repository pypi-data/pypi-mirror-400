# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/12/22 21:40
# Author     ：Maxwell
# Description：
"""

from typing import Literal
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class BaseConfig(BaseSettings):
    # ========== 环境 ==========
    ENV: Literal["dev", "test", "prod"] = Field(default="dev")

    # ========== 应用 ==========
    APP_NAME: str = Field(default="InfoMan")
    APP_BASE_URI: str = Field(default="/infoman")
    APP_VERSION: str = Field(default="1.0.0")
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: int = Field(default=8000)
    APP_DESCRIPTION: str = Field(default="Information System")

    DEFAULT_LANGUAGE_IS_EN: bool = Field(default=True)

    # ========== 服务器配置 ==========
    APP_WORKERS: int = Field(default=2, description="工作进程数（Granian/Gunicorn）")
    APP_THREADS: int = Field(default=1, description="每个 worker 的线程数（Granian）")

    # ========== API 文档 ==========
    DOCS_URL: str = Field(default="/doc")
    APP_REDOC_URL: str = Field(default="/redoc")

    # ========== CORS ==========
    ALLOW_ORIGINS: list[str] = Field(default=["*"])
    ALLOW_CREDENTIALS: bool = Field(default=False)
    ALLOW_METHODS: list[str] = Field(default=["GET", "POST"])
    ALLOW_HEADERS: list[str] = Field(default=["Content-Type", "Authorization", "X-Request-ID"])
    MAX_AGE: int = Field(default=600)

    # ========== Router配置 ==========
    USE_DEFAULT_ROUTER: bool = Field(default=False)
    USE_PROMETHEUS_ROUTER: bool = Field(default=False)
    USE_STATIC: bool = Field(default=False)
    STATIC_NAME: str = Field(default="static")
    STATIC_DIR: str = Field(default="./app/static")
    STATIC_URL: str = Field(default="/static")
    USE_TEMPLATES: bool = Field(default=False)
    TEMPLATE_DIR: str = Field(default="./app/template")

    @property
    def is_dev(self) -> bool:
        return self.ENV == "dev"

    @property
    def is_test(self) -> bool:
        return self.ENV == "test"

    @property
    def is_prod(self) -> bool:
        return self.ENV == "pro"



