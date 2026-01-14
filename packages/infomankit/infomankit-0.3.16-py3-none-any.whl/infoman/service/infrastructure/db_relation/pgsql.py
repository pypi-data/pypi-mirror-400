# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/12/22 21:10
# Author     ：Maxwell
# Description：
"""
from typing import Dict, Any
from infoman.config import DatabaseInstanceConfig


class PostgreSQLBackend:
    """PostgreSQL 后端"""

    @staticmethod
    def get_engine() -> str:
        return "tortoise.backends.asyncpg"

    @staticmethod
    def get_credentials(config: DatabaseInstanceConfig) -> Dict[str, Any]:
        """生成 PostgreSQL 连接凭证"""
        credentials = {
            "host": config.host,
            "port": config.port,
            "user": config.user,
            "password": config.password,
            "database": config.database,
            # 连接池（注意：asyncpg 参数名不同）
            "min_size": config.pool_min_size,
            "max_size": config.pool_max_size,
            "max_queries": 50000,
            "max_inactive_connection_lifetime": config.pool_recycle,
            # 超时
            "timeout": config.connect_timeout,
            "command_timeout": config.command_timeout,
            # PostgreSQL 特有
            "schema": config.schema_name,
            "server_settings": {
                "application_name": "infoman",
                "jit": "off",
            },
        }

        # SSL
        if config.ssl_enabled:
            import ssl

            ssl_context = ssl.create_default_context()
            if config.ssl_ca:
                ssl_context.load_verify_locations(cafile=config.ssl_ca)
            credentials["ssl"] = ssl_context

        return credentials
