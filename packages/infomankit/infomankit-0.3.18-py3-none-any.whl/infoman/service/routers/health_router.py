# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
健康检查路由

提供多层次的健康检查端点，支持 Kubernetes 探针
- /api/health - 基础健康检查
- /api/health/liveness - 存活探针
- /api/health/readiness - 就绪探针
- /api/health/startup - 启动探针
- /api/health/detailed - 详细健康状态
"""

import time
from typing import Dict, Any, List
from fastapi import Request, APIRouter, status
from loguru import logger

from infoman.service.core.response import success, failed

health_router = APIRouter(prefix="")

# 应用启动时间
_startup_time = time.time()


@health_router.get(
    summary="基础健康检查",
    path="",
    description="返回应用的基本健康状态",
)
async def api_health(req: Request):
    """基础健康检查 - 仅检查应用是否运行"""
    uptime = time.time() - _startup_time
    return success(data={
        "status": "healthy",
        "uptime_seconds": round(uptime, 2),
    })


@health_router.get(
    "/liveness",
    summary="存活探针",
    description="Kubernetes liveness probe - 检查应用是否存活",
    status_code=status.HTTP_200_OK,
)
async def liveness_check(req: Request):
    """
    存活探针 (Liveness Probe)

    用于判断应用是否还活着，如果失败，Kubernetes 会重启 Pod
    这个检查应该非常轻量，只检查应用进程是否响应
    """
    return {"status": "alive"}


@health_router.get(
    "/readiness",
    summary="就绪探针",
    description="Kubernetes readiness probe - 检查应用是否就绪接受流量",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Application is ready"},
        503: {"description": "Application is not ready"},
    },
)
async def readiness_check(req: Request):
    """
    就绪探针 (Readiness Probe)

    用于判断应用是否准备好接受流量
    如果失败，Kubernetes 会将 Pod 从 Service 负载均衡中移除

    检查项：
    - 数据库连接
    - Redis 连接
    - 其他关键依赖
    """
    checks: Dict[str, Any] = {}
    all_ready = True

    # 检查数据库
    try:
        if hasattr(req.app.state, "db_manager"):
            db_health = await req.app.state.db_manager.health_check()
            checks["database"] = db_health
            if db_health.get("status") != "healthy":
                all_ready = False
        else:
            checks["database"] = {"status": "not_configured"}
    except Exception as e:
        logger.error(f"Database readiness check failed: {e}")
        checks["database"] = {"status": "unhealthy", "error": str(e)}
        all_ready = False

    # 检查 Redis
    try:
        if hasattr(req.app.state, "redis_manager"):
            redis_health = await req.app.state.redis_manager.health_check()
            checks["redis"] = redis_health
            if redis_health.get("status") != "healthy":
                all_ready = False
        else:
            checks["redis"] = {"status": "not_configured"}
    except Exception as e:
        logger.error(f"Redis readiness check failed: {e}")
        checks["redis"] = {"status": "unhealthy", "error": str(e)}
        all_ready = False

    # 检查向量数据库
    try:
        if hasattr(req.app.state, "vector_manager"):
            vector_health = await req.app.state.vector_manager.health_check()
            checks["vector_db"] = vector_health
            if vector_health.get("status") != "healthy":
                all_ready = False
        else:
            checks["vector_db"] = {"status": "not_configured"}
    except Exception as e:
        logger.error(f"Vector DB readiness check failed: {e}")
        checks["vector_db"] = {"status": "unhealthy", "error": str(e)}
        all_ready = False

    # 检查消息队列
    try:
        if hasattr(req.app.state, "nats_manager"):
            nats_health = await req.app.state.nats_manager.health_check()
            checks["message_queue"] = nats_health
            if nats_health.get("status") != "healthy":
                all_ready = False
        else:
            checks["message_queue"] = {"status": "not_configured"}
    except Exception as e:
        logger.error(f"NATS readiness check failed: {e}")
        checks["message_queue"] = {"status": "unhealthy", "error": str(e)}
        all_ready = False

    if all_ready:
        return {
            "status": "ready",
            "checks": checks,
        }
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "checks": checks,
            },
        )


@health_router.get(
    "/startup",
    summary="启动探针",
    description="Kubernetes startup probe - 检查应用是否已完成启动",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Application has started"},
        503: {"description": "Application is still starting"},
    },
)
async def startup_check(req: Request):
    """
    启动探针 (Startup Probe)

    用于检查应用是否已经完成启动
    适用于启动缓慢的应用，避免 liveness probe 过早杀死容器

    启动完成标准：
    - 应用运行超过最小启动时间
    - 所有关键服务已初始化
    """
    uptime = time.time() - _startup_time
    min_startup_time = 5  # 最小启动时间（秒）

    if uptime < min_startup_time:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "starting",
                "uptime_seconds": round(uptime, 2),
                "message": f"Application is still starting (min: {min_startup_time}s)",
            },
        )

    # 检查关键服务是否已初始化
    checks = {}

    if hasattr(req.app.state, "db_manager"):
        checks["database"] = "initialized"
    if hasattr(req.app.state, "redis_manager"):
        checks["redis"] = "initialized"
    if hasattr(req.app.state, "vector_manager"):
        checks["vector_db"] = "initialized"
    if hasattr(req.app.state, "nats_manager"):
        checks["message_queue"] = "initialized"

    return {
        "status": "started",
        "uptime_seconds": round(uptime, 2),
        "initialized_services": checks,
    }


@health_router.get(
    "/detailed",
    summary="详细健康状态",
    description="返回所有组件的详细健康状态",
)
async def detailed_health(req: Request):
    """
    详细健康检查

    返回应用和所有依赖服务的详细健康状态
    包括版本信息、连接状态、性能指标等
    """
    from infoman.config.settings import settings
    import psutil

    uptime = time.time() - _startup_time

    health_data: Dict[str, Any] = {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime_seconds": round(uptime, 2),
        "application": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENV,
        },
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
        },
        "dependencies": {},
    }

    # 收集所有依赖的健康状态
    dependencies_health: List[Dict[str, Any]] = []

    # 数据库
    if hasattr(req.app.state, "db_manager"):
        try:
            db_health = await req.app.state.db_manager.health_check()
            dependencies_health.append(db_health)
            health_data["dependencies"]["database"] = db_health
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            health_data["dependencies"]["database"] = {
                "status": "error",
                "error": str(e),
            }

    # Redis
    if hasattr(req.app.state, "redis_manager"):
        try:
            redis_health = await req.app.state.redis_manager.health_check()
            dependencies_health.append(redis_health)
            health_data["dependencies"]["redis"] = redis_health
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            health_data["dependencies"]["redis"] = {
                "status": "error",
                "error": str(e),
            }

    # 向量数据库
    if hasattr(req.app.state, "vector_manager"):
        try:
            vector_health = await req.app.state.vector_manager.health_check()
            dependencies_health.append(vector_health)
            health_data["dependencies"]["vector_db"] = vector_health
        except Exception as e:
            logger.error(f"Vector DB health check failed: {e}")
            health_data["dependencies"]["vector_db"] = {
                "status": "error",
                "error": str(e),
            }

    # 消息队列
    if hasattr(req.app.state, "nats_manager"):
        try:
            nats_health = await req.app.state.nats_manager.health_check()
            dependencies_health.append(nats_health)
            health_data["dependencies"]["message_queue"] = nats_health
        except Exception as e:
            logger.error(f"NATS health check failed: {e}")
            health_data["dependencies"]["message_queue"] = {
                "status": "error",
                "error": str(e),
            }

    # 判断整体健康状态
    unhealthy_count = sum(
        1 for dep in dependencies_health
        if dep.get("status") not in ["healthy", "not_configured"]
    )

    if unhealthy_count > 0:
        health_data["status"] = "degraded"
        health_data["unhealthy_dependencies"] = unhealthy_count

    return success(data=health_data)


# 导入 JSONResponse
from fastapi.responses import JSONResponse
