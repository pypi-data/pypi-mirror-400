# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
向量数据库管理器

支持：
- Qdrant
- Milvus (待实现)
- 统一的管理接口
"""

from typing import Optional, Dict, Any
from fastapi import FastAPI
from loguru import logger

from infoman.config import settings
from infoman.service.infrastructure.db_vector.qdrant import QdrantBackend


class VectorDBManager:
    """向量数据库管理器"""

    def __init__(self):
        self.qdrant: Optional[QdrantBackend] = None
        self.initialized = False

    @property
    def is_available(self) -> bool:
        """是否有可用的向量数据库"""
        return (
            (self.qdrant and self.qdrant.is_available) or
            False  # 其他数据库
        )

    @property
    def client(self):
        """
        获取默认客户端

        优先级：Qdrant > Milvus
        """
        if self.qdrant and self.qdrant.is_available:
            return self.qdrant.client

        return None

    async def startup(self, app: Optional[FastAPI] = None) -> bool:
        if self.initialized:
            logger.warning("⚠️ VectorDBManager 已初始化，跳过重复初始化")
            return True

        success_count = 0

        # ========== 启动 Qdrant ==========
        if settings.qdrant_configured:
            self.qdrant = QdrantBackend(settings)

            if await self.qdrant.startup():
                success_count += 1

                if app:
                    app.state.qdrant_client = self.qdrant.client
                    logger.debug("✅ Qdrant 客户端已挂载到 app.state")

            # ========== 初始化完成 ==========
            if success_count > 0:
                self.initialized = True
                logger.success(f"✅ 向量数据库初始化完成（{success_count} 个）")
                return True
        return False

    async def shutdown(self):
        if not self.initialized:
            return

        logger.info("⏹️ 关闭向量数据库连接...")

        if self.qdrant:
            await self.qdrant.shutdown()

        self.initialized = False
        logger.success("✅ 所有向量数据库已关闭")

    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查

        Returns:
            {
                "qdrant": {"status": "healthy", ...},
                "milvus": {"status": "not_configured", ...},
            }
        """
        health = {}

        # Qdrant
        if self.qdrant:
            health["qdrant"] = await self.qdrant.health_check()
        else:
            health["qdrant"] = {
                "status": "not_configured",
                "name": "qdrant",
                "details": {"enabled": False}
            }

        # Milvus
        # if self.milvus:
        #     health["milvus"] = await self.milvus.health_check()

        return health

    async def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            {
                "qdrant": {...},
                "milvus": {...},
            }
        """
        stats = {}

        if self.qdrant and self.qdrant.is_available:
            stats["qdrant"] = await self.qdrant.get_stats()

        # if self.milvus and self.milvus.is_available:
        #     stats["milvus"] = await self.milvus.get_stats()

        return stats

    # ========== 便捷方法 ==========

    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        backend: str = "qdrant",
        **kwargs
    ) -> bool:
        """
        创建集合

        Args:
            collection_name: 集合名称
            vector_size: 向量维度
            backend: 使用的后端（qdrant/milvus）
            **kwargs: 其他参数

        Returns:
            是否创建成功
        """
        if backend == "qdrant" and self.qdrant:
            return await self.qdrant.create_collection(
                collection_name, vector_size, **kwargs
            )

        logger.error(f"后端 {backend} 不可用")
        return False

    async def search(
        self,
        collection_name: str,
        query_vector: list,
        limit: int = 10,
        backend: str = "qdrant",
        **kwargs
    ):
        """
        向量搜索

        Args:
            collection_name: 集合名称
            query_vector: 查询向量
            limit: 返回结果数量
            backend: 使用的后端
            **kwargs: 其他参数

        Returns:
            搜索结果
        """
        if backend == "qdrant" and self.qdrant:
            return await self.qdrant.search(
                collection_name, query_vector, limit, **kwargs
            )

        logger.error(f"后端 {backend} 不可用")
        return []
