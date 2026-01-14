# service/core/lifespan.py
"""
应用生命周期管理（精简版）

职责：
- 协调各个服务的启动和关闭
- 不包含具体的连接逻辑
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger

from infoman.config import settings

if settings.USE_PRO_ORM:
    from infoman.service.infrastructure.db_relation.manager_pro import db_manager
    _DB_MANAGER_TYPE = "pro"
else:
    from infoman.service.infrastructure.db_relation.manager import db_manager
    _DB_MANAGER_TYPE = "basic"

from infoman.service.infrastructure.db_cache.manager import RedisManager
from infoman.service.infrastructure.db_vector.manager import VectorDBManager
from infoman.service.infrastructure.mq import NATSManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""

    # ========== 启动 ==========
    logger.info(f"🚀 应用启动中 [{settings.APP_NAME} v{settings.APP_VERSION}]")
    logger.info(f"   环境: {settings.ENV}")
    logger.info(f"   数据库管理器: {_DB_MANAGER_TYPE}")

    # 初始化管理器
    redis_manager = RedisManager()
    vector_manager = VectorDBManager()
    nats_manager = NATSManager()

    # 保存到 app.state
    app.state.db_manager = db_manager
    app.state.redis_manager = redis_manager
    app.state.vector_manager = vector_manager
    app.state.nats_manager = nats_manager

    try:
        # 1. 数据库
        await db_manager.startup(app)

        # 2. Redis
        await redis_manager.startup(app)

        # 3. 向量数据库
        await vector_manager.startup(app)

        # 4. 消息队列
        await nats_manager.startup(app)

        logger.success("✅ 所有服务启动完成")

    except Exception as e:
        logger.error(f"❌ 服务启动失败: {e}")
        raise

    # ========== 运行 ==========
    yield

    # ========== 关闭 ==========
    logger.info("⏹️ 应用关闭中...")

    try:
        # 按相反顺序关闭
        await nats_manager.shutdown()
        await vector_manager.shutdown()
        await redis_manager.shutdown()
        await db_manager.shutdown()

        logger.success("✅ 所有服务已关闭")

    except Exception as e:
        logger.error(f"❌ 服务关闭失败: {e}")
