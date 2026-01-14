# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/12/22 22:38
# Author     ：Maxwell
# Description：基础设施组件抽象基类
统一管理：
- 数据库（MySQL, PostgreSQL）
- 缓存（Redis, DragonflyDB）
- 消息队列（RabbitMQ, Kafka）
- 搜索引擎（Elasticsearch）
- 对象存储（MinIO, S3）
- 等等...

"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Literal
from enum import Enum
from loguru import logger


class ComponentType(str, Enum):
    """组件类型枚举"""
    DATABASE = "database"  # 数据库
    CACHE = "cache"  # 缓存
    MESSAGE_QUEUE = "message_queue"  # 消息队列
    SEARCH = "search"  # 搜索引擎
    STORAGE = "storage"  # 对象存储
    MONITORING = "monitoring"  # 监控
    TRACING = "tracing"  # 链路追踪
    LOGGING = "logging"  # 日志
    OTHER = "other"  # 其他


class ComponentStatus(str, Enum):
    """组件状态枚举"""
    NOT_CONFIGURED = "not_configured"  # 未配置
    INITIALIZING = "initializing"  # 初始化中
    HEALTHY = "healthy"  # 健康
    UNHEALTHY = "unhealthy"  # 不健康
    DEGRADED = "degraded"  # 降级
    STOPPED = "stopped"  # 已停止


class BaseInfrastructureComponent(ABC):
    """
    基础设施组件抽象基类

    所有基础设施组件（数据库、缓存、MQ 等）都应该继承此类。

    生命周期：
        1. __init__() - 创建实例
        2. startup() - 启动组件
        3. health_check() - 健康检查
        4. shutdown() - 关闭组件
    """

    def __init__(
            self,
            component_type: ComponentType,
            name: str,
            enabled: bool = True,
    ):
        """
        初始化组件

        Args:
            component_type: 组件类型
            name: 组件名称（如 "mysql", "redis"）
            enabled: 是否启用
        """
        self.component_type = component_type
        self.name = name
        self.enabled = enabled
        self._status = ComponentStatus.NOT_CONFIGURED
        self._client: Optional[Any] = None
        self._metadata: Dict[str, Any] = {}

    @property
    def status(self) -> ComponentStatus:
        """获取组件状态"""
        return self._status

    @property
    def client(self) -> Optional[Any]:
        """获取客户端实例"""
        return self._client

    @property
    def is_available(self) -> bool:
        """组件是否可用"""
        return (
                self.enabled and
                self._status in [ComponentStatus.HEALTHY, ComponentStatus.DEGRADED]
        )

    @abstractmethod
    async def startup(self) -> bool:
        """
        启动组件

        职责：
        1. 检查配置
        2. 创建连接/客户端
        3. 测试连接
        4. 初始化资源

        Returns:
            True: 启动成功
            False: 启动失败
        """
        pass

    @abstractmethod
    async def shutdown(self):
        """
        关闭组件

        职责：
        1. 关闭连接
        2. 释放资源
        3. 清理状态
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查

        Returns:
            健康状态字典：
            {
                "status": "healthy" | "unhealthy" | "not_configured",
                "component_type": "database",
                "name": "mysql",
                "details": {...}
            }
        """
        pass

    async def get_info(self) -> Dict[str, Any]:
        """
        获取组件信息

        Returns:
            组件信息字典
        """
        return {
            "component_type": self.component_type.value,
            "name": self.name,
            "enabled": self.enabled,
            "status": self._status.value,
            "available": self.is_available,
            "metadata": self._metadata,
        }

    async def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息（可选实现）

        Returns:
            统计信息字典
        """
        return {}

    def _set_status(self, status: ComponentStatus):
        """设置组件状态"""
        old_status = self._status
        self._status = status

        if old_status != status:
            logger.debug(
                f"[{self.name}] 状态变更: {old_status.value} -> {status.value}"
            )

    def _log_startup(self, success: bool, message: str = ""):
        """记录启动日志"""
        if success:
            logger.success(
                f"✅ [{self.component_type.value}] {self.name} 启动成功"
                + (f": {message}" if message else "")
            )
        else:
            logger.error(
                f"❌ [{self.component_type.value}] {self.name} 启动失败"
                + (f": {message}" if message else "")
            )

    def _log_shutdown(self, success: bool, message: str = ""):
        """记录关闭日志"""
        if success:
            logger.info(
                f"✅ [{self.component_type.value}] {self.name} 已关闭"
                + (f": {message}" if message else "")
            )
        else:
            logger.error(
                f"❌ [{self.component_type.value}] {self.name} 关闭失败"
                + (f": {message}" if message else "")
            )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"type={self.component_type.value}, "
            f"name={self.name}, "
            f"status={self._status.value}"
            f")"
        )
