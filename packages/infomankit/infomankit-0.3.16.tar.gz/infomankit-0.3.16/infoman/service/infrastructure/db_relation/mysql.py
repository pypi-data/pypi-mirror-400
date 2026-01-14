# database/backends.py
"""
数据库后端实现
"""

from typing import Dict, Any
from infoman.config import DatabaseInstanceConfig


class MySQLBackend:
    """MySQL 后端"""

    @staticmethod
    def get_engine() -> str:
        return "tortoise.backends.mysql"

    @staticmethod
    def get_credentials(config: DatabaseInstanceConfig) -> Dict[str, Any]:
        """生成 MySQL 连接凭证"""
        credentials = {
            "host": config.host,
            "port": config.port,
            "user": config.user,
            "password": config.password,
            "database": config.database,
            "charset": config.charset,
            # 连接池
            "minsize": config.pool_min_size,
            "maxsize": config.pool_max_size,
            "pool_recycle": config.pool_recycle,
            "echo": config.echo,
            # 超时
            "connect_timeout": config.connect_timeout,
            # 其他
            "autocommit": True,
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        }

        # SSL
        if config.ssl_enabled:
            ssl_config = {}
            if config.ssl_ca:
                ssl_config["ca"] = config.ssl_ca
            if config.ssl_cert:
                ssl_config["cert"] = config.ssl_cert
            if config.ssl_key:
                ssl_config["key"] = config.ssl_key

            if ssl_config:
                credentials["ssl"] = ssl_config

        return credentials
