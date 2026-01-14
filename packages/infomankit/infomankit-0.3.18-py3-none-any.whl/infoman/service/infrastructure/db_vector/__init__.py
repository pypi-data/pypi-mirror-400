# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
向量数据库基础设施

支持:
- Qdrant: 高性能向量搜索引擎
- Milvus: 待实现

Usage:
    # 方式 1: 通过 lifespan 自动初始化
    from infoman.service.app import application
    # VectorDBManager 会在应用启动时自动初始化

    # 方式 2: 手动使用
    from infoman.service.infrastructure.db_vector import VectorDBManager

    manager = VectorDBManager()
    await manager.startup()

    # 使用 Qdrant
    client = manager.qdrant.client
    await client.create_collection(...)

    # 便捷方法
    await manager.create_collection("my_collection", vector_size=768)
    results = await manager.search("my_collection", query_vector=[...])

    # 关闭
    await manager.shutdown()
"""

from .manager import VectorDBManager
from .qdrant import QdrantBackend

__all__ = [
    "VectorDBManager",
    "QdrantBackend",
]
