# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
Qdrant 向量数据库后端

功能：
- 异步连接管理
- 健康检查
- 集合管理
- 向量操作
"""

from typing import Optional, Dict, Any, List
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from loguru import logger

from infoman.config import VectorDBConfig
from infoman.service.infrastructure.base import (
    BaseInfrastructureComponent,
    ComponentType,
    ComponentStatus,
)


class QdrantBackend(BaseInfrastructureComponent):
    """Qdrant 向量数据库后端"""

    def __init__(self, config: VectorDBConfig):
        super().__init__(
            component_type=ComponentType.OTHER,  # 向量数据库可以归类为 OTHER
            name="qdrant",
            enabled=config.qdrant_configured,
        )
        self.config = config
        self._client: Optional[AsyncQdrantClient] = None

    async def startup(self) -> bool:
        """启动 Qdrant 连接"""
        if not self.enabled:
            logger.info("⏭️ Qdrant 未启用，跳过初始化")
            self._set_status(ComponentStatus.NOT_CONFIGURED)
            return False

        try:
            self._set_status(ComponentStatus.INITIALIZING)
            logger.info(f"🔌 正在连接 Qdrant [{self.config.QDRANT_HOST}]...")

            # 创建 Qdrant 客户端
            self._client = AsyncQdrantClient(
                host=self.config.QDRANT_HOST,
                port=self.config.QDRANT_HTTP_PORT,
                grpc_port=self.config.QDRANT_GRPC_PORT,
                api_key=self.config.QDRANT_API_KEY,
                timeout=self.config.QDRANT_TIMEOUT,
                prefer_grpc=True,  # 优先使用 gRPC（性能更好）
            )

            # 测试连接
            await self._test_connection()

            self._set_status(ComponentStatus.HEALTHY)
            self._log_startup(
                True,
                f"{self.config.QDRANT_HOST}:{self.config.QDRANT_HTTP_PORT}"
            )

            return True

        except Exception as e:
            self._set_status(ComponentStatus.UNHEALTHY)
            self._log_startup(False, str(e))
            return False

    async def shutdown(self):
        """关闭 Qdrant 连接"""
        if not self._client:
            return

        try:
            logger.info("⏹️ 正在关闭 Qdrant 连接...")

            # Qdrant 客户端会自动清理连接
            # 如果需要显式关闭，可以添加逻辑
            self._client = None

            self._set_status(ComponentStatus.STOPPED)
            self._log_shutdown(True)

        except Exception as e:
            self._log_shutdown(False, str(e))

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        if not self.enabled:
            return {
                "status": "not_configured",
                "component_type": self.component_type.value,
                "name": self.name,
                "details": {"enabled": False}
            }

        if not self._client:
            return {
                "status": "unhealthy",
                "component_type": self.component_type.value,
                "name": self.name,
                "details": {"error": "客户端未初始化"}
            }

        try:
            # 尝试获取集合列表
            collections = await self._client.get_collections()

            return {
                "status": "healthy",
                "component_type": self.component_type.value,
                "name": self.name,
                "details": {
                    "host": self.config.QDRANT_HOST,
                    "http_port": self.config.QDRANT_HTTP_PORT,
                    "grpc_port": self.config.QDRANT_GRPC_PORT,
                    "collections_count": len(collections.collections),
                }
            }

        except Exception as e:
            logger.error(f"Qdrant 健康检查失败: {e}")
            self._set_status(ComponentStatus.UNHEALTHY)

            return {
                "status": "unhealthy",
                "component_type": self.component_type.value,
                "name": self.name,
                "details": {"error": str(e)}
            }

    async def _test_connection(self):
        """测试连接"""
        try:
            # 尝试获取集合列表
            await self._client.get_collections()
            logger.success("✅ Qdrant 连接测试成功")

        except Exception as e:
            logger.error(f"❌ Qdrant 连接测试失败: {e}")
            raise

    # ========== 便捷方法 ==========

    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: Distance = Distance.COSINE,
        **kwargs
    ) -> bool:
        """
        创建集合

        Args:
            collection_name: 集合名称
            vector_size: 向量维度
            distance: 距离度量（COSINE/EUCLID/DOT）
            **kwargs: 其他参数

        Returns:
            是否创建成功
        """
        if not self._client:
            logger.error("Qdrant 客户端未初始化")
            return False

        try:
            # 检查集合是否存在
            collections = await self._client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if collection_name in collection_names:
                logger.warning(f"集合 {collection_name} 已存在")
                return True

            # 创建集合
            await self._client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance,
                ),
                **kwargs
            )

            logger.success(f"✅ 创建集合成功: {collection_name}")
            return True

        except Exception as e:
            logger.error(f"创建集合失败: {e}")
            return False

    async def delete_collection(self, collection_name: str) -> bool:
        """删除集合"""
        if not self._client:
            return False

        try:
            await self._client.delete_collection(collection_name)
            logger.success(f"✅ 删除集合成功: {collection_name}")
            return True

        except Exception as e:
            logger.error(f"删除集合失败: {e}")
            return False

    async def upsert_points(
        self,
        collection_name: str,
        points: List[PointStruct],
    ) -> bool:
        """插入或更新向量点"""
        if not self._client:
            return False

        try:
            await self._client.upsert(
                collection_name=collection_name,
                points=points,
            )
            logger.debug(f"✅ 插入/更新 {len(points)} 个点到 {collection_name}")
            return True

        except Exception as e:
            logger.error(f"插入向量失败: {e}")
            return False

    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        向量搜索

        Args:
            collection_name: 集合名称
            query_vector: 查询向量
            limit: 返回结果数量
            score_threshold: 相似度阈值
            **kwargs: 其他搜索参数

        Returns:
            搜索结果列表
        """
        if not self._client:
            return []

        try:
            results = await self._client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                **kwargs
            )

            return [
                {
                    "id": r.id,
                    "score": r.score,
                    "payload": r.payload,
                }
                for r in results
            ]

        except Exception as e:
            logger.error(f"向量搜索失败: {e}")
            return []

    async def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """获取集合信息"""
        if not self._client:
            return None

        try:
            info = await self._client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
            }

        except Exception as e:
            logger.error(f"获取集合信息失败: {e}")
            return None

    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self._client or not self.is_available:
            return {}

        try:
            collections = await self._client.get_collections()

            stats = {
                "collections_count": len(collections.collections),
                "collections": []
            }

            for collection in collections.collections:
                info = await self.get_collection_info(collection.name)
                if info:
                    stats["collections"].append(info)

            return stats

        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
