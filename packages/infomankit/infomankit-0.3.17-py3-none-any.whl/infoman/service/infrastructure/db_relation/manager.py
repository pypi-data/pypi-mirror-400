# database/manager.py
"""
多数据库管理器

功能：
- 支持多个数据库同时连接
- 每个数据库独立配置
- 统一的健康检查
- 优雅关闭
"""

from typing import Dict, Optional, List, Any
from fastapi import FastAPI
from tortoise import Tortoise
from loguru import logger

from infoman.config import settings, DatabaseConfig
from infoman.service.infrastructure.db_relation.mysql import MySQLBackend
from infoman.service.infrastructure.db_relation.sqllite import SQLiteBackend
from infoman.service.infrastructure.db_relation.pgsql import PostgreSQLBackend


BACKENDS = {
    "mysql": MySQLBackend,
    "postgresql": PostgreSQLBackend,
    "sqlite": SQLiteBackend,
}


class DatabaseManager:
    """数据库管理器"""

    def __init__(self):
        self.connections: Dict[str, DatabaseConfig] = {}
        self.initialized = False

    @property
    def is_available(self) -> bool:
        """是否有可用的数据库连接"""
        return self.initialized and len(self.connections) > 0

    @property
    def client(self):
        """
        获取默认客户端（Tortoise connections）

        Returns:
            Tortoise connections 对象
        """
        if not self.initialized:
            return None

        from tortoise import connections
        return connections

    def gen_tortoise_config(self) -> Optional[dict]:
        enabled_dbs = settings.enabled_databases

        if not enabled_dbs:
            logger.warning("⚠️ 没有启用任何数据库")
            return None

        # ========== 连接配置 ==========
        connections = {}

        for conn_name, db_config in enabled_dbs.items():
            backend_class = BACKENDS.get(db_config.type)

            if not backend_class:
                logger.error(f"❌ 不支持的数据库类型: {db_config.type}")
                continue

            connections[conn_name] = {
                "engine": backend_class.get_engine(),
                "credentials": backend_class.get_credentials(db_config),
            }

            self.connections[conn_name] = db_config

        # ========== 应用配置（模型分组）==========
        apps = {}

        for conn_name, db_config in enabled_dbs.items():
            if db_config.models:
                app_name = f"{conn_name}_models"
                apps[app_name] = {
                    "models": db_config.models,
                    "default_connection": conn_name,
                }

        if not apps and connections:
            return None

        config = {
            "connections": connections,
            "apps": apps,
            "use_tz": settings.DB_USE_TZ,
            "timezone": settings.DB_TIMEZONE,
        }
        return config

    async def startup(self, app: Optional[FastAPI] = None) -> bool:
        if self.initialized:
            logger.warning("⚠️ DatabaseManager 已初始化，跳过重复初始化")
            return True

        config = self.gen_tortoise_config()

        if not config:
            logger.info("⏭️ 数据库未配置，跳过初始化")
            return False

        try:
            logger.info("🚀 初始化数据库...")
            for conn_name, db_config in self.connections.items():
                logger.info(
                    f"   - [{conn_name}] {db_config.type.upper()}: "
                    f"{db_config.user}@{db_config.host}:{db_config.port}/{db_config.database}"
                )

            await Tortoise.init(config=config)

            if app:
                app.state.db_client = self.client
                logger.debug("✅ 数据库客户端已挂载到 app.state")
                self.initialized = True

                logger.success(
                    f"✅ 数据库连接成功（{len(self.connections)} 个）\n"
                    f"   连接名: {list(self.connections.keys())}"
                )
            else:
                logger.info(f"无app实例，数据库跳过初始化")

            return True
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            return False

    async def register(self, app: FastAPI) -> bool:
        return await self.startup(app)

    async def health_check(self, conn_name: Optional[str] = None) -> Dict:
        if not settings.enabled_databases:
            return {
                "status": "not_configured",
                "name": "database",
                "details": {"enabled": False}
            }

        if not self.initialized:
            return {
                "status": "unhealthy",
                "name": "database",
                "details": {"error": "未初始化"}
            }

        # 检查单个连接
        if conn_name:
            result = await self._check_single_connection(conn_name)
            return {
                "status": result.get("status", "unhealthy"),
                "name": f"database_{conn_name}",
                "details": result
            }

        # 检查所有连接
        results = {}
        for name in self.connections.keys():
            results[name] = await self._check_single_connection(name)

        # 汇总状态
        all_healthy = all(r.get("status") == "healthy" for r in results.values())

        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "name": "database",
            "details": {
                "connections": results,
                "count": len(results)
            }
        }

    async def check_health(self, conn_name: Optional[str] = None) -> Dict:
        return await self.health_check(conn_name)

    async def _check_single_connection(self, conn_name: str) -> Dict:
        try:
            from tortoise import connections

            conn = connections.get(conn_name)
            db_config = self.connections.get(conn_name)

            if not conn or not db_config:
                return {
                    "status": "not_found",
                    "error": f"连接 '{conn_name}' 不存在",
                }

            # 执行健康检查查询
            await conn.execute_query("SELECT 1")

            # 获取连接池状态
            pool_status = {
                "size": conn._pool.size() if hasattr(conn, "_pool") else "N/A",
                "free": conn._pool.freesize() if hasattr(conn, "_pool") else "N/A",
            }

            return {
                "status": "healthy",
                "type": db_config.type,
                "database": db_config.database,
                "pool": pool_status,
            }

        except Exception as e:
            logger.error(f"❌ 连接 '{conn_name}' 健康检查失败: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    async def shutdown(self):
        if not self.initialized:
            return

        try:
            logger.info("⏹️ 关闭数据库连接...")

            for conn_name in self.connections.keys():
                logger.info(f"   - 关闭连接: {conn_name}")

            await Tortoise.close_connections()

            self.initialized = False

            logger.success("✅ 所有数据库连接已关闭")

        except Exception as e:
            logger.error(f"❌ 关闭数据库连接失败: {e}")

    async def close(self):
        """关闭所有数据库连接（兼容旧接口）"""
        await self.shutdown()

    async def get_stats(self) -> Dict[str, Any]:
        if not self.is_available:
            return {}

        stats = {
            "connections_count": len(self.connections),
            "connections": {}
        }

        # 获取每个连接的详细信息
        for conn_name, db_config in self.connections.items():
            conn_stat = await self._check_single_connection(conn_name)
            stats["connections"][conn_name] = {
                "type": db_config.type,
                "database": db_config.database,
                "host": db_config.host,
                "port": db_config.port,
                "status": conn_stat.get("status"),
                "pool": conn_stat.get("pool", {})
            }

        return stats

    def get_connection_names(self) -> List[str]:
        """获取所有连接名称"""
        return list(self.connections.keys())

    def has_connection(self, conn_name: str) -> bool:
        """检查连接是否存在"""
        return conn_name in self.connections


# 全局单例
db_manager = DatabaseManager()


# =================================================================
# 便捷函数
# =================================================================


async def register_databases(app: FastAPI) -> bool:
    return await db_manager.register(app)


async def check_databases_health(conn_name: Optional[str] = None) -> Dict:
    return await db_manager.check_health(conn_name)


async def close_databases():
    await db_manager.close()


def get_connection_names() -> List[str]:
    return db_manager.get_connection_names()
