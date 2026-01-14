# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2024/2/2 10:10
# Author     ：Maxwell
# Description：
"""
from fastapi import APIRouter
from infoman.service.routers.monitor_router import monitor_router
from infoman.service.routers.health_router import health_router
from infoman.config.settings import settings

api_router = APIRouter(prefix=settings.APP_BASE_URI)
api_router.include_router(
    prefix="/api/monitor", router=monitor_router, tags=["服务状态"]
)
api_router.include_router(prefix="/api/health", router=health_router, tags=["服务状态"])
