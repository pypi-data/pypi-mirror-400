"""
数据库关系层 - 统一导出

Version: 0.3.0

向前兼容说明：
- 默认导出保持不变（使用原有的 Tortoise 单一后端管理器）
- 新的混合管理器通过 hybrid_db_manager 导出
"""

# ==================== 向前兼容（默认使用 Tortoise）====================

from infoman.service.infrastructure.db_relation.manager import (
    DatabaseManager,
    db_manager,
    register_databases as register_databases_tortoise,
    check_databases_health as check_databases_health_tortoise,
    close_databases as close_databases_tortoise,
    get_connection_names as get_connection_names_tortoise,
)


# ==================== 默认导出（向前兼容）====================

# 为了100%向前兼容，默认导出仍然是 Tortoise 单一后端
__all__ = [
    # Tortoise 管理器（默认，向前兼容）
    "DatabaseManager",
    "db_manager",
    "register_databases",
    "check_databases_health",
    "close_databases",
    "get_connection_names",

]

# 默认导出指向 Tortoise 版本（向前兼容）
register_databases = register_databases_tortoise
check_databases_health = check_databases_health_tortoise
close_databases = close_databases_tortoise
get_connection_names = get_connection_names_tortoise
