# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/12/23 08:37
# Author     ：Maxwell
# Description：
"""
from pydantic import Field
from pydantic_settings import BaseSettings


class JWTConfig(BaseSettings):
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_SECRET_KEY: str = Field(default="your-secret-key-for-jwt")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, ge=0, le=24*30*60)
