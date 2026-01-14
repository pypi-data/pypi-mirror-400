# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/12/22 21:11
# Author     ：Maxwell
# Description：
"""
from typing import Dict, Any
from infoman.config import DatabaseConfig


class SQLiteBackend:
    """SQLite 后端"""

    @staticmethod
    def get_engine() -> str:
        return "tortoise.backends.sqlite"

    @staticmethod
    def get_credentials(config: DatabaseConfig) -> Dict[str, Any]:
        """生成 SQLite 连接凭证"""
        return {
            "file_path": f"{config.database}.db",
        }
