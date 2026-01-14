# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/12/22 21:38
# Author     ：Maxwell
# Description：
"""
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class VectorDBConfig(BaseSettings):
    # ========== Qdrant ==========
    QDRANT_ENABLED: bool = Field(default=False, description="是否启用 Qdrant")
    QDRANT_HOST: Optional[str] = Field(default=None, description="Qdrant 主机")
    QDRANT_HTTP_PORT: int = Field(default=6333, description="HTTP 端口")
    QDRANT_GRPC_PORT: int = Field(default=6334, description="gRPC 端口")
    QDRANT_API_KEY: Optional[str] = Field(default=None, description="API Key")
    QDRANT_TIMEOUT: int = Field(default=10, description="超时时间（秒）")

    # ========== Milvus ==========
    MILVUS_ENABLED: bool = Field(default=False, description="是否启用 Milvus")
    MILVUS_HOST: Optional[str] = Field(default=None, description="Milvus 主机")
    MILVUS_PORT: int = Field(default=19530, description="Milvus 端口")
    MILVUS_USER: Optional[str] = Field(default=None, description="用户名")
    MILVUS_PASSWORD: Optional[str] = Field(default=None, description="密码")

    @property
    def qdrant_configured(self) -> bool:
        """Qdrant 是否已配置"""
        return self.QDRANT_ENABLED and bool(self.QDRANT_HOST)

    @property
    def milvus_configured(self) -> bool:
        """Milvus 是否已配置"""
        return self.MILVUS_ENABLED and bool(self.MILVUS_HOST)

