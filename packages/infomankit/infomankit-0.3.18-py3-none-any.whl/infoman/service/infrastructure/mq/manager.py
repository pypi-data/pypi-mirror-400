# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
消息队列管理器

支持：
- NATS
- 其他消息队列（待实现）
"""

from typing import Optional, Dict, Any
from fastapi import FastAPI
from loguru import logger

from infoman.config import settings
from infoman.service.infrastructure.mq.nats.nats_client import NATSClient


class NATSManager:
    """NATS 消息队列管理器"""

    def __init__(self):
        self.nats_client: Optional[NATSClient] = None
        self.initialized = False

    @property
    def is_available(self) -> bool:
        """是否可用"""
        return self.nats_client is not None and self.nats_client.connected

    @property
    def client(self):
        """获取 NATS 客户端"""
        return self.nats_client

    async def startup(self, app: Optional[FastAPI] = None) -> bool:
        """
        启动 NATS 连接

        Args:
            app: FastAPI 应用实例（可选）

        Returns:
            是否成功启动
        """
        if self.initialized:
            logger.warning("⚠️ NATSManager 已初始化，跳过重复初始化")
            return True

        if not settings.NATS_SERVERS:
            logger.info("⏭️ NATS 未配置，跳过初始化")
            return False

        logger.info("🚀 初始化 NATS...")

        try:
            self.nats_client = NATSClient(
                servers=settings.NATS_SERVERS,
                name=settings.APP_NAME
            )

            # 连接到 NATS
            await self.nats_client.connect()

            # 挂载到 app.state（如果提供了 app）
            if app:
                app.state.nats_client = self.nats_client
                logger.debug("✅ NATS 客户端已挂载到 app.state")

            self.initialized = True
            logger.success(f"✅ NATS 连接成功: {settings.NATS_SERVERS}")
            return True

        except Exception as e:
            logger.error(f"❌ NATS 连接失败: {e}")
            return False

    async def shutdown(self):
        """关闭 NATS 连接"""
        if not self.initialized:
            return

        logger.info("⏹️ 关闭 NATS 连接...")

        try:
            if self.nats_client:
                await self.nats_client.close()
                logger.success("✅ NATS 连接已关闭")

        except Exception as e:
            logger.error(f"❌ NATS 关闭失败: {e}")

        finally:
            self.initialized = False

    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查

        Returns:
            {
                "status": "healthy" | "unhealthy" | "not_configured",
                "name": "nats",
                "details": {...}
            }
        """
        if not settings.NATS_SERVER:
            return {
                "status": "not_configured",
                "name": "nats",
                "details": {"enabled": False}
            }

        if not self.initialized or not self.nats_client:
            return {
                "status": "unhealthy",
                "name": "nats",
                "details": {"error": "未初始化"}
            }

        try:
            # 检查连接状态
            is_connected = self.nats_client.connected

            if is_connected:
                return {
                    "status": "healthy",
                    "name": "nats",
                    "details": {
                        "connected": True,
                        "servers": self.nats_client.servers
                    }
                }
            else:
                return {
                    "status": "unhealthy",
                    "name": "nats",
                    "details": {
                        "connected": False,
                        "error": "连接已断开"
                    }
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "name": "nats",
                "details": {"error": str(e)}
            }

    async def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            {
                "connected": bool,
                "servers": list,
            }
        """
        if not self.is_available:
            return {}

        return {
            "connected": self.nats_client.connected,
            "servers": self.nats_client.servers,
        }
