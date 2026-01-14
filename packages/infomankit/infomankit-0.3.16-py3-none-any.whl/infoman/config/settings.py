# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/12/22 21:38
# Author     ：Maxwell
# Description：
"""
import os
from dotenv import load_dotenv
from functools import lru_cache
from pathlib import Path
from .base import BaseConfig
from .db_relation import DatabaseConfig
from .db_cache import RedisConfig
from .db_vector import VectorDBConfig
from .mq import MessageQueueConfig
from .jwt import JWTConfig
from .llm import LLMConfig
from .log import LogConfig
from pydantic_settings import SettingsConfigDict


ENV_FILE_MAP = {
    'dev': 'config/.env.dev',
    'test': 'config/.env.test',
    'prod': 'config/.env.prod',
}


load_dotenv()
ENV = os.getenv('ENV', 'dev')

if ENV not in ENV_FILE_MAP:
    raise ValueError(f"无效的环境变量 ENV={ENV}，有效值: {list(ENV_FILE_MAP.keys())}")

ENV_FILE = ENV_FILE_MAP[ENV]
if not Path(ENV_FILE).exists():
    raise FileNotFoundError(f"配置文件不存在: {ENV_FILE}")


class Settings(
    BaseConfig,
    DatabaseConfig,
    RedisConfig,
    VectorDBConfig,
    MessageQueueConfig,
    JWTConfig,
    LLMConfig,
    LogConfig
):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
