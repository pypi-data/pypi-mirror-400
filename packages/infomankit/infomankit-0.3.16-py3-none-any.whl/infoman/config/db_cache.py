# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/12/22 21:37
# Author     ：Maxwell
# Description：
"""
from typing import Optional, Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class RedisConfig(BaseSettings):
    """Redis/DragonflyDB 缓存配置"""

    # ========== 基础配置 ==========
    REDIS_ENABLED: bool = Field(
        default=False,
        description="是否启用缓存服务"
    )

    REDIS_BACKEND: Literal["redis", "dragonfly", "auto"] = Field(
        default="auto",
        description="缓存后端类型：redis/dragonfly/auto（自动检测）"
    )

    REDIS_HOST: Optional[str] = Field(
        default=None,
        description="缓存服务器主机地址"
    )

    REDIS_PORT: int = Field(
        default=6379,
        description="缓存服务器端口"
    )

    REDIS_DB: int = Field(
        default=0,
        ge=0,
        le=15,
        description="Redis 数据库编号（0-15）"
    )

    REDIS_PASSWORD: Optional[str] = Field(
        default=None,
        description="缓存服务器密码"
    )

    # ========== 连接池配置 ==========
    REDIS_MAX_CONNECTIONS: int = Field(
        default=30,
        ge=1,
        le=1000,
        description="连接池最大连接数"
    )

    REDIS_SOCKET_TIMEOUT: int = Field(
        default=4,
        ge=1,
        description="Socket 超时时间（秒）"
    )

    REDIS_SOCKET_CONNECT_TIMEOUT: int = Field(
        default=2,
        ge=1,
        description="连接超时时间（秒）"
    )

    REDIS_HEALTH_CHECK_INTERVAL: int = Field(
        default=30,
        ge=0,
        description="健康检查间隔（秒），0 表示禁用"
    )

    REDIS_RETRY_ON_TIMEOUT: bool = Field(
        default=True,
        description="超时时是否自动重试"
    )

    # ========== 缓存配置 ==========
    REDIS_CACHE_PREFIX: str = Field(
        default="infoman",
        description="缓存 key 前缀"
    )

    REDIS_CACHE_EXPIRE: int = Field(
        default=3600,
        ge=0,
        description="默认缓存过期时间（秒），0 表示永不过期"
    )

    REDIS_CACHE_VERSION: Optional[str] = Field(
        default=None,
        description="缓存版本号（用于缓存失效），留空则使用应用版本"
    )

    # ========== 编码配置 ==========
    REDIS_ENCODING: str = Field(
        default="utf-8",
        description="编码格式"
    )

    REDIS_DECODE_RESPONSES: bool = Field(
        default=False,
        description="是否自动解码响应（True: 返回 str，False: 返回 bytes）"
    )

    # ========== 验证器 ==========

    @field_validator("REDIS_BACKEND")
    @classmethod
    def validate_backend(cls, v: str) -> str:
        """验证后端类型"""
        allowed = ["redis", "dragonfly", "auto"]
        if v not in allowed:
            raise ValueError(f"REDIS_BACKEND 必须是 {allowed} 之一")
        return v

    @field_validator("REDIS_CACHE_PREFIX")
    @classmethod
    def validate_prefix(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("REDIS_CACHE_PREFIX 不能为空")
        return v.strip()

    @field_validator("REDIS_HOST")
    @classmethod
    def validate_host(cls, v: Optional[str]) -> Optional[str]:
        """验证主机地址"""
        if v:
            v = v.strip()
            if not v:
                return None
        return v

    # ========== 计算属性 ==========

    @property
    def redis_configured(self) -> bool:
        return self.REDIS_ENABLED and bool(self.REDIS_HOST)

    @property
    def is_redis(self) -> bool:
        """是否使用 Redis"""
        return self.REDIS_BACKEND == "redis"

    @property
    def is_dragonfly(self) -> bool:
        """是否使用 DragonflyDB"""
        return self.REDIS_BACKEND == "dragonfly"

    @property
    def is_auto(self) -> bool:
        """是否自动检测"""
        return self.REDIS_BACKEND == "auto"

    @property
    def connection_url(self) -> Optional[str]:
        """
        获取连接 URL

        Returns:
            Redis 连接 URL，例如：redis://:password@localhost:6379/0
        """
        if not self.redis_configured:
            return None

        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def get_cache_key(self, key: str, version: Optional[str] = None) -> str:
        """
        生成完整的缓存 key

        Args:
            key: 原始 key
            version: 版本号，留空则使用配置的版本

        Returns:
            完整的缓存 key，例如：infoman:v1.0.0:user:123
        """
        version = version or self.REDIS_CACHE_VERSION or "default"
        return f"{self.REDIS_CACHE_PREFIX}:v{version}:{key}"

    def to_dict(self) -> dict:
        """
        转换为字典（隐藏敏感信息）

        Returns:
            配置字典
        """
        return {
            "enabled": self.REDIS_ENABLED,
            "backend": self.REDIS_BACKEND,
            "host": self.REDIS_HOST,
            "port": self.REDIS_PORT,
            "db": self.REDIS_DB,
            "password": "***" if self.REDIS_PASSWORD else None,
            "max_connections": self.REDIS_MAX_CONNECTIONS,
            "cache_prefix": self.REDIS_CACHE_PREFIX,
            "cache_expire": self.REDIS_CACHE_EXPIRE,
            "configured": self.redis_configured,
        }


def get_redis_config() -> RedisConfig:
    return RedisConfig()


def print_redis_config():
    config = get_redis_config()

    print("=" * 60)
    print("Redis/DragonflyDB 缓存配置")
    print("=" * 60)

    for key, value in config.to_dict().items():
        print(f"  {key:20s}: {value}")

    print("=" * 60)
    print(f"  连接 URL: {config.connection_url or '未配置'}")
    print("=" * 60)


# ========== 使用示例 ==========

if __name__ == "__main__":
    # 打印配置
    print_redis_config()

    # 测试缓存 key 生成
    config = get_redis_config()

    print("\n缓存 Key 示例：")
    print(f"  user:123 -> {config.get_cache_key('user:123')}")
    print(f"  session:abc -> {config.get_cache_key('session:abc', version='2.0.0')}")
