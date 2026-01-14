# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
Redis 缓存管理器
"""
from typing import Optional, Dict, Any
from fastapi import FastAPI
import redis.asyncio as redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from loguru import logger
from infoman.config import settings


class RedisManager:
    """Redis 管理器"""

    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.initialized = False

    @property
    def is_available(self) -> bool:
        """是否可用"""
        return self.client is not None and self.initialized

    async def startup(self, app: Optional[FastAPI] = None) -> bool:
        """
        启动 Redis 连接

        Args:
            app: FastAPI 应用实例（可选）

        Returns:
            是否成功启动
        """
        if self.initialized:
            logger.warning("⚠️ RedisManager 已初始化，跳过重复初始化")
            return True

        if not settings.redis_configured:
            return False

        logger.info("🚀 初始化 Redis...")

        try:
            # 创建连接池
            pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                encoding="utf-8",
                decode_responses=False,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
                health_check_interval=settings.REDIS_HEALTH_CHECK_INTERVAL,
            )

            # 创建客户端
            self.client = redis.Redis(connection_pool=pool)

            # 测试连接
            await self.client.ping()

            # 挂载到 app.state（如果提供了 app）
            if app:
                app.state.redis_client = self.client
                logger.debug("✅ Redis 客户端已挂载到 app.state")

            # 初始化缓存
            FastAPICache.init(
                RedisBackend(self.client),
                prefix=f"{settings.REDIS_CACHE_PREFIX}:v{settings.APP_VERSION}:",
            )

            self.initialized = True
            logger.success(f"✅ Redis 连接成功: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            return True

        except Exception as e:
            logger.error(f"❌ Redis 连接失败: {e}")
            self.client = None
            return False

    async def shutdown(self):
        """关闭 Redis 连接"""
        if not self.initialized:
            return

        logger.info("⏹️ 关闭 Redis 连接...")

        try:
            if self.client:
                await self.client.close()
                await self.client.connection_pool.disconnect()
                logger.success("✅ Redis 连接已关闭")
        except Exception as e:
            logger.error(f"❌ Redis 关闭失败: {e}")
        finally:
            self.initialized = False

    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查

        Returns:
            {
                "status": "healthy" | "unhealthy" | "not_configured",
                "name": "redis",
                "details": {...}
            }
        """
        if not settings.redis_configured:
            return {
                "status": "not_configured",
                "name": "redis",
                "details": {"enabled": False}
            }

        if not self.initialized or not self.client:
            return {
                "status": "unhealthy",
                "name": "redis",
                "details": {"error": "未初始化"}
            }

        try:
            await self.client.ping()

            # 获取 Redis 信息
            info = await self.client.info()

            return {
                "status": "healthy",
                "name": "redis",
                "details": {
                    "host": settings.REDIS_HOST,
                    "port": settings.REDIS_PORT,
                    "db": settings.REDIS_DB,
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory_human": info.get("used_memory_human", "N/A"),
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "name": "redis",
                "details": {"error": str(e)}
            }

    async def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            {
                "host": str,
                "port": int,
                "db": int,
                "info": {...}
            }
        """
        if not self.is_available:
            return {}

        try:
            info = await self.client.info()

            return {
                "host": settings.REDIS_HOST,
                "port": settings.REDIS_PORT,
                "db": settings.REDIS_DB,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "N/A"),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
            }
        except Exception as e:
            logger.error(f"获取 Redis 统计信息失败: {e}")
            return {}
