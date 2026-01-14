# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/12/22 21:37
# Author     ：Maxwell
# Description：
"""

from typing import Optional, List, Dict, Literal
from functools import cached_property
from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseInstanceConfig(BaseSettings):
    enabled: bool = False
    ssl_enabled: bool = False
    type: Literal["mysql", "postgresql", "sqlite"] = "mysql"
    host: Optional[str] = None
    port: Optional[int] = None
    database: str = "infoman"
    user: Optional[str] = None
    password: Optional[str] = None

    # 连接池
    pool_min_size: int = 1
    pool_max_size: int = 20
    pool_recycle: int = 3600

    # 超时
    connect_timeout: int = 10

    # 模型
    models: List[str] = []

    # 数据库特有
    charset: str = "utf8mb4"
    schema_name: str = "public"  # PostgreSQL schema (renamed from schema_content)
    echo: bool = False

    # SSL 配置
    ssl_ca: Optional[str] = None  # SSL CA 证书路径
    ssl_cert: Optional[str] = None  # SSL 客户端证书路径
    ssl_key: Optional[str] = None  # SSL 客户端密钥路径


class DatabaseConfig(BaseSettings):
    USE_PRO_ORM: bool = Field(default=False)
    # ========== MySQL ==========
    MYSQL_ENABLED: bool = Field(default=False)
    MYSQL_HOST: Optional[str] = Field(default=None)
    MYSQL_PORT: int = Field(default=3306)
    MYSQL_DB: str = Field(default="infoman")
    MYSQL_USER: Optional[str] = Field(default=None)
    MYSQL_PASSWORD: Optional[str] = Field(default=None)
    MYSQL_CHARSET: str = Field(default="utf8mb4")
    MYSQL_POOL_MIN_SIZE: int = Field(default=1)
    MYSQL_POOL_MAX_SIZE: int = Field(default=20)
    MYSQL_POOL_RECYCLE: int = Field(default=3600)
    MYSQL_MODELS_PATH: str = Field(default="infoman.models")
    MYSQL_MODELS: str = Field(default="")
    MYSQL_ECHO: bool = Field(default=False)
    MYSQL_SSL_ENABLED: bool = Field(default=False)
    MYSQL_SSL_CA: Optional[str] = Field(default=None)
    MYSQL_SSL_CERT: Optional[str] = Field(default=None)
    MYSQL_SSL_KEY: Optional[str] = Field(default=None)

    # ========== PostgreSQL ==========
    POSTGRES_ENABLED: bool = Field(default=False)
    POSTGRES_HOST: Optional[str] = Field(default=None)
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_DB: str = Field(default="analytics")
    POSTGRES_USER: Optional[str] = Field(default=None)
    POSTGRES_PASSWORD: Optional[str] = Field(default=None)
    POSTGRES_SCHEMA: str = Field(default="public")
    POSTGRES_POOL_MIN_SIZE: int = Field(default=5)
    POSTGRES_POOL_MAX_SIZE: int = Field(default=20)
    POSTGRES_MODELS: str = Field(default="")
    POSTGRES_MODELS_PATH: str = Field(default="infoman.models")
    POSTGRES_ECHO: bool = Field(default=False)
    POSTGRES_SSL_ENABLED: bool = Field(default=False)
    POSTGRES_SSL_CA: Optional[str] = Field(default=None)
    POSTGRES_SSL_CERT: Optional[str] = Field(default=None)
    POSTGRES_SSL_KEY: Optional[str] = Field(default=None)

    # ========== SQLite ==========
    SQLITE_ENABLED: bool = Field(default=False)
    SQLITE_DB: str = Field(default="cache")
    SQLITE_MODELS_PATH: str = Field(default="infoman.models")
    SQLITE_MODELS: str = Field(default="")

    # ========== 通用 ==========
    DB_TIMEZONE: str = Field(default="Asia/Shanghai")
    DB_USE_TZ: bool = Field(default=False)
    DB_MODELS_PATH: str = Field(default="infoman.models")

    # ========== 计算属性 ==========

    @cached_property
    def mysql_config(self) -> Optional[DatabaseInstanceConfig]:
        if not self.MYSQL_ENABLED:
            return None

        models = [m.strip() for m in self.MYSQL_MODELS.split(",") if m.strip()]

        return DatabaseInstanceConfig(
            enabled=True,
            type="mysql",
            host=self.MYSQL_HOST,
            port=self.MYSQL_PORT,
            database=self.MYSQL_DB,
            user=self.MYSQL_USER,
            password=self.MYSQL_PASSWORD,
            pool_min_size=self.MYSQL_POOL_MIN_SIZE,
            pool_max_size=self.MYSQL_POOL_MAX_SIZE,
            pool_recycle=self.MYSQL_POOL_RECYCLE,
            models=[f"{self.MYSQL_MODELS_PATH}.{m}" for m in models],
            charset=self.MYSQL_CHARSET,
            echo=self.MYSQL_ECHO,
            ssl_enabled=self.MYSQL_SSL_ENABLED,
            ssl_ca=self.MYSQL_SSL_CA,
            ssl_cert=self.MYSQL_SSL_CERT,
            ssl_key=self.MYSQL_SSL_KEY,
        )

    @cached_property
    def postgres_config(self) -> Optional[DatabaseInstanceConfig]:
        if not self.POSTGRES_ENABLED:
            return None

        models = [m.strip() for m in self.POSTGRES_MODELS.split(",") if m.strip()]

        return DatabaseInstanceConfig(
            enabled=True,
            type="postgresql",
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            pool_min_size=self.POSTGRES_POOL_MIN_SIZE,
            pool_max_size=self.POSTGRES_POOL_MAX_SIZE,
            models=[f"{self.POSTGRES_MODELS_PATH}.{m}" for m in models],
            schema_name=self.POSTGRES_SCHEMA,
            echo=self.POSTGRES_ECHO,
            ssl_enabled=self.POSTGRES_SSL_ENABLED,
            ssl_ca=self.POSTGRES_SSL_CA,
            ssl_cert=self.POSTGRES_SSL_CERT,
            ssl_key=self.POSTGRES_SSL_KEY,
        )

    @cached_property
    def sqlite_config(self) -> Optional[DatabaseInstanceConfig]:
        if not self.SQLITE_ENABLED:
            return None

        models = [m.strip() for m in self.SQLITE_MODELS.split(",") if m.strip()]

        return DatabaseInstanceConfig(
            enabled=True,
            type="sqlite",
            database=self.SQLITE_DB,
            models=[f"{self.SQLITE_MODELS_PATH}.{m}" for m in models],
        )

    @cached_property
    def enabled_databases(self) -> Dict[str, DatabaseInstanceConfig]:
        databases = {}

        if self.mysql_config:
            databases["mysql"] = self.mysql_config

        if self.postgres_config:
            databases["postgres"] = self.postgres_config

        if self.sqlite_config:
            databases["sqlite"] = self.sqlite_config

        return databases

