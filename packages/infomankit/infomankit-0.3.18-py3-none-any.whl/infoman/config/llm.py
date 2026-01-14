# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/12/23 08:32
# Author     ：Maxwell
# Description：
"""
from pydantic import Field
from pydantic_settings import BaseSettings


class LLMConfig(BaseSettings):
    LLM_PROXY: str = Field(default="litellm_proxy", description="LLM 代理")
    LLM_TIMEOUT: int = Field(default=60, ge=5, description="LLM 请求超时")
    LLM_MAX_RETRIES: int = Field(default=3, ge=0, le=10, description="最大重试次数")