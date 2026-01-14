"""
SQLAlchemy 专业版数据库管理器

Version: 1.0.0
Author: Maxwell
"""

from typing import Dict, Optional, Any
from fastapi import FastAPI
from loguru import logger

from infoman.config import settings, DatabaseConfig

# ==================== SQLAlchemy 导入 ====================

try:
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from sqlalchemy import text
    from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool

    _SQLALCHEMY_AVAILABLE = True
except ImportError:
    _SQLALCHEMY_AVAILABLE = False
    raise ImportError(
        "SQLAlchemy 未安装，请运行: pip install sqlalchemy[asyncio] asyncmy asyncpg aiosqlite"
    )


# ==================== SQLAlchemy 后端实现 ====================

class SQLAlchemyMySQLBackend:
    """SQLAlchemy MySQL 后端"""

    @staticmethod
    def get_url(config: DatabaseConfig) -> str:
        """生成 MySQL 连接 URL"""
        return (
            f"mysql+asyncmy://{config.user}:{config.password}@"
            f"{config.host}:{config.port}/{config.database}"
            f"?charset={config.charset}"
        )


class SQLAlchemyPostgreSQLBackend:
    """SQLAlchemy PostgreSQL 后端"""

    @staticmethod
    def get_url(config: DatabaseConfig) -> str:
        """生成 PostgreSQL 连接 URL"""
        return (
            f"postgresql+asyncpg://{config.user}:{config.password}@"
            f"{config.host}:{config.port}/{config.database}"
        )


class SQLAlchemySQLiteBackend:
    """SQLAlchemy SQLite 后端"""

    @staticmethod
    def get_url(config: DatabaseConfig) -> str:
        """生成 SQLite 连接 URL"""
        return f"sqlite+aiosqlite:///{config.database}"


SQLALCHEMY_BACKENDS = {
    "mysql": SQLAlchemyMySQLBackend,
    "postgresql": SQLAlchemyPostgreSQLBackend,
    "sqlite": SQLAlchemySQLiteBackend,
}


# ==================== 专业版数据库管理器 ====================

class ProDatabaseManager:
    """
    专业版数据库管理器 - 仅支持 SQLAlchemy

    功能：
    - 支持多个数据库同时连接
    - 支持 MySQL、PostgreSQL、SQLite
    - 统一的健康检查
    - 优雅关闭
    - 连接池管理

    使用示例：
        >>> manager = ProDatabaseManager()
        >>> await manager.startup(app)
        >>>
        >>> # 获取 session maker
        >>> session_maker = manager.get_session_maker("default")
        >>> async with session_maker() as session:
        >>>     result = await session.execute(text("SELECT 1"))
        >>>
        >>> # 获取 engine
        >>> engine = manager.get_engine("default")
    """

    def __init__(self):
        # SQLAlchemy 引擎和会话
        self.engines: Dict[str, Any] = {}
        self.session_makers: Dict[str, Any] = {}
        self.configs: Dict[str, DatabaseConfig] = {}
        self.initialized = False

    @property
    def is_available(self) -> bool:
        """是否有可用的数据库连接"""
        return self.initialized and len(self.engines) > 0

    def get_session_maker(self, name: str = "default"):
        if not self.initialized:
            raise RuntimeError("DatabaseManager 未初始化")

        session_maker = self.session_makers.get(name)
        if not session_maker:
            raise RuntimeError(f"连接 '{name}' 不存在")

        return session_maker

    def get_engine(self, name: str = "default"):
        """
        获取 SQLAlchemy Engine

        Args:
            name: 连接名称

        Returns:
            AsyncEngine 实例

        Raises:
            RuntimeError: 未初始化或连接不存在
        """
        if not self.initialized:
            raise RuntimeError("DatabaseManager 未初始化")

        engine = self.engines.get(name)
        if not engine:
            raise RuntimeError(f"连接 '{name}' 不存在")

        return engine

    def _get_pool_class(self, db_config: DatabaseConfig):
        """根据配置获取连接池类"""
        # SQLite 使用 NullPool（单线程）
        if db_config.type == "sqlite":
            return NullPool
        # 其他数据库使用 AsyncAdaptedQueuePool（异步引擎专用）
        return AsyncAdaptedQueuePool

    async def _init_connection(
        self,
        conn_name: str,
        db_config: DatabaseConfig
    ):
        """初始化单个数据库连接"""
        backend_class = SQLALCHEMY_BACKENDS.get(db_config.type)

        if not backend_class:
            logger.error(f"❌ 不支持的数据库类型: {db_config.type}")
            return

        url = backend_class.get_url(db_config)

        logger.info(
            f"   - [{conn_name}] {db_config.type.upper()}: "
            f"{db_config.user}@{db_config.host}:{db_config.port}/{db_config.database}"
        )

        # 获取连接池类
        pool_class = self._get_pool_class(db_config)

        # 创建引擎
        engine_kwargs = {
            "url": url,
            "echo": db_config.echo,
            "pool_pre_ping": True,  # 健康检查
            "poolclass": pool_class,
        }

        # 非 NullPool 才设置连接池参数
        if pool_class != NullPool:
            engine_kwargs.update({
                "pool_size": db_config.pool_max_size,
                "max_overflow": db_config.pool_max_size,
                "pool_recycle": db_config.pool_recycle,
            })

        engine = create_async_engine(**engine_kwargs)

        # 创建 session maker
        session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        self.engines[conn_name] = engine
        self.session_makers[conn_name] = session_maker
        self.configs[conn_name] = db_config

    async def startup(self, app: Optional[FastAPI] = None) -> bool:
        if self.initialized:
            logger.warning("⚠️  DatabaseManager 已初始化，跳过重复初始化")
            return True

        enabled_dbs = settings.enabled_databases

        if not enabled_dbs:
            logger.info("⏭️  数据库未配置，跳过初始化")
            return False

        try:
            logger.info("🚀 初始化 SQLAlchemy 数据库管理器...")

            # 初始化所有连接
            for conn_name, db_config in enabled_dbs.items():
                await self._init_connection(conn_name, db_config)

            if not self.engines:
                logger.warning("⚠️  没有成功初始化任何数据库连接")
                return False

            # 挂载到 app.state
            if app:
                app.state.db_engines = self.engines
                app.state.db_sessions = self.session_makers
                logger.debug("✅ 数据库引擎已挂载到 app.state")

            self.initialized = True
            logger.success(
                f"✅ SQLAlchemy 连接成功（{len(self.engines)} 个）\n"
                f"   连接名: {list(self.engines.keys())}"
            )

            return True

        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            raise

    async def register(self, app: FastAPI) -> bool:
        """注册到 FastAPI 应用"""
        return await self.startup(app)

    async def health_check(self, conn_name: Optional[str] = None) -> Dict:
        if not self.is_available:
            return {
                "status": "not_configured",
                "name": "database",
                "details": {"enabled": False}
            }

        results = {}

        # 检查所有连接或指定连接
        for name in self.engines.keys():
            if conn_name is None or conn_name == name:
                results[name] = await self._check_connection(name)

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

    async def _check_connection(self, conn_name: str) -> Dict:
        """检查单个连接"""
        try:
            engine = self.engines.get(conn_name)
            session_maker = self.session_makers.get(conn_name)
            db_config = self.configs.get(conn_name)

            if not engine or not session_maker or not db_config:
                return {
                    "status": "not_found",
                    "error": f"连接 '{conn_name}' 不存在",
                }

            # 执行健康检查查询
            async with session_maker() as session:
                result = await session.execute(text("SELECT 1"))
                result.scalar()

            # 获取连接池状态
            pool = engine.pool
            pool_status = {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
            } if hasattr(pool, 'size') else {"type": "NullPool"}

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
        """关闭所有数据库连接"""
        if not self.initialized:
            return

        try:
            logger.info("⏹️  关闭数据库连接...")

            for conn_name, engine in self.engines.items():
                logger.info(f"   - 关闭引擎: {conn_name}")
                await engine.dispose()

            self.engines.clear()
            self.session_makers.clear()
            self.configs.clear()
            self.initialized = False

            logger.success("✅ 所有数据库连接已关闭")

        except Exception as e:
            logger.error(f"❌ 关闭数据库连接失败: {e}")

    async def close(self):
        """关闭所有数据库连接（兼容旧接口）"""
        await self.shutdown()


# ==================== 全局单例 ====================

db_manager = ProDatabaseManager()


# ==================== 便捷函数 ====================

async def register_databases(app: FastAPI) -> bool:
    """注册数据库到 FastAPI 应用"""
    return await db_manager.register(app)


async def check_databases_health(conn_name: Optional[str] = None) -> Dict:
    """检查数据库健康状态"""
    return await db_manager.health_check(conn_name)


async def close_databases():
    """关闭所有数据库连接"""
    await db_manager.close()


def get_connection_names() -> list[str]:
    """获取所有连接名称"""
    return list(db_manager.engines.keys())


# ==================== 依赖注入辅助函数 ====================

async def get_db_session(conn_name: str = "myql"):
    """
    FastAPI 依赖注入：获取数据库会话

    使用示例：
        >>> @app.get("/users")
        >>> async def get_users(session: AsyncSession = Depends(get_db_session)):
        >>>     result = await session.execute(text("SELECT * FROM users"))
        >>>     return result.fetchall()

    Raises:
        RuntimeError: 数据库未初始化或连接不存在
    """
    # 检查数据库管理器是否已初始化
    if not db_manager.initialized:
        raise RuntimeError(
            "数据库管理器未初始化。请确保：\n"
            "1. 在 FastAPI 应用中使用了 lifespan\n"
            "2. 或在应用启动时调用了 await db_manager.startup(app)\n"
            "3. settings.enabled_databases 已正确配置"
        )

    # 检查连接是否存在
    if conn_name not in db_manager.session_makers:
        available = list(db_manager.session_makers.keys())
        raise RuntimeError(
            f"数据库连接 '{conn_name}' 不存在。\n"
            f"可用的连接: {available}"
        )

    session_maker = db_manager.session_makers[conn_name]
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
