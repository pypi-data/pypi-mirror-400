#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
数据库模型基类 - 支持多 ORM 后端

设计原则：
1. 用户代码只依赖抽象基类
2. 运行时根据配置选择后端
3. 100% 向前兼容现有 Tortoise 代码

Version: 0.3.0
Author: Maxwell
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Any
from datetime import datetime

# ==================== 抽象接口层 ====================


class BaseTimestampMixin(ABC):
    """时间戳混入抽象类 - ORM 无关"""
    id: int
    created_at: datetime
    updated_at: datetime


T = TypeVar('T', bound=BaseTimestampMixin)


class BaseRepository(ABC, Generic[T]):
    """
    仓储模式抽象类 - 隔离 ORM 实现细节

    使用示例：
        >>> repo = create_repository(User)
        >>> user = await repo.get(1)
        >>> users = await repo.filter(name="Alice")
    """

    @abstractmethod
    async def get(self, id: int) -> Optional[T]:
        """根据 ID 获取单条记录"""
        pass

    @abstractmethod
    async def filter(self, **kwargs) -> List[T]:
        """根据条件筛选"""
        pass

    @abstractmethod
    async def create(self, **kwargs) -> T:
        """创建记录"""
        pass

    @abstractmethod
    async def update(self, id: int, **kwargs) -> T:
        """更新记录"""
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """删除记录"""
        pass

    @abstractmethod
    async def all(self) -> List[T]:
        """获取所有记录"""
        pass

    @abstractmethod
    async def count(self, **kwargs) -> int:
        """计数"""
        pass


# ==================== Tortoise ORM 实现（向前兼容）====================

try:
    from tortoise import fields
    from tortoise.models import Model as TortoiseModel

    class TimestampMixin(TortoiseModel, BaseTimestampMixin):
        """
        Tortoise ORM 时间戳混入 - 保持现有 API 不变

        使用示例（向前兼容）：
            >>> class User(TimestampMixin):
            ...     name = fields.CharField(max_length=100)
            >>> user = await User.create(name="Alice")
        """

        class Meta:
            abstract = True

        id = fields.IntField(pk=True, null=False)
        created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
        updated_at = fields.DatetimeField(auto_now=True, description="更新时间")


    class MySQLModel(TortoiseModel):
        """MySQL 模型基类（Tortoise）"""
        class Meta:
            abstract = True
            app = 'mysql_models'


    class PostgreSQLModel(TortoiseModel):
        """PostgreSQL 模型基类（Tortoise）"""
        class Meta:
            abstract = True
            app = 'postgres_models'


    class SQLiteModel(TortoiseModel):
        """SQLite 模型基类（Tortoise）"""
        class Meta:
            abstract = True
            app = 'sqlite_models'


    class TortoiseRepository(BaseRepository[T]):
        """
        Tortoise ORM 仓储实现

        使用示例：
            >>> repo = TortoiseRepository(User)
            >>> user = await repo.create(name="Alice")
        """

        def __init__(self, model_class):
            self.model = model_class

        async def get(self, id: int) -> Optional[T]:
            try:
                return await self.model.get(id=id)
            except Exception:
                return None

        async def filter(self, **kwargs) -> List[T]:
            return await self.model.filter(**kwargs).all()

        async def create(self, **kwargs) -> T:
            return await self.model.create(**kwargs)

        async def update(self, id: int, **kwargs) -> T:
            instance = await self.model.get(id=id)
            await instance.update_from_dict(kwargs).save()
            return instance

        async def delete(self, id: int) -> bool:
            instance = await self.model.get(id=id)
            await instance.delete()
            return True

        async def all(self) -> List[T]:
            return await self.model.all()

        async def count(self, **kwargs) -> int:
            return await self.model.filter(**kwargs).count()

    _TORTOISE_AVAILABLE = True

except ImportError:
    # Tortoise 未安装，使用占位符
    _TORTOISE_AVAILABLE = False

    class TimestampMixin(BaseTimestampMixin):  # type: ignore
        """占位符：需要安装 tortoise-orm"""
        pass

    class MySQLModel:  # type: ignore
        """占位符：需要安装 tortoise-orm"""
        pass

    class PostgreSQLModel:  # type: ignore
        """占位符：需要安装 tortoise-orm"""
        pass

    class SQLiteModel:  # type: ignore
        """占位符：需要安装 tortoise-orm"""
        pass

    class TortoiseRepository(BaseRepository[T]):  # type: ignore
        """占位符：需要安装 tortoise-orm"""
        def __init__(self, model_class):
            raise ImportError("需要安装 tortoise-orm: pip install infomankit[database]")

        async def get(self, id: int) -> Optional[T]:
            raise NotImplementedError
        async def filter(self, **kwargs) -> List[T]:
            raise NotImplementedError
        async def create(self, **kwargs) -> T:
            raise NotImplementedError
        async def update(self, id: int, **kwargs) -> T:
            raise NotImplementedError
        async def delete(self, id: int) -> bool:
            raise NotImplementedError
        async def all(self) -> List[T]:
            raise NotImplementedError
        async def count(self, **kwargs) -> int:
            raise NotImplementedError


# ==================== SQLAlchemy 实现（新增）====================

try:
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
    from sqlalchemy import Integer, DateTime, func, select, delete as sql_delete
    from sqlalchemy.ext.asyncio import AsyncSession

    class AlchemyBase(DeclarativeBase):
        """
        SQLAlchemy 基类

        使用示例：
            >>> class User(AlchemyBase, AlchemyTimestampMixin):
            ...     __tablename__ = "users"
            ...     name: Mapped[str] = mapped_column(String(100))
        """
        pass


    class AlchemyTimestampMixin(BaseTimestampMixin):
        """
        SQLAlchemy 时间戳混入

        提供自动管理的 id, created_at, updated_at 字段
        """
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        created_at: Mapped[datetime] = mapped_column(
            DateTime,
            server_default=func.now(),
            comment="创建时间"
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime,
            server_default=func.now(),
            onupdate=func.now(),
            comment="更新时间"
        )


    class SQLAlchemyRepository(BaseRepository[T]):
        """
        SQLAlchemy 仓储实现

        使用示例：
            >>> session_maker = get_session_maker()
            >>> repo = SQLAlchemyRepository(User, session_maker)
            >>> user = await repo.create(name="Alice")
        """

        def __init__(self, model_class, session_factory):
            self.model = model_class
            self.session_factory = session_factory

        async def get(self, id: int) -> Optional[T]:
            async with self.session_factory() as session:
                stmt = select(self.model).where(self.model.id == id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()

        async def filter(self, **kwargs) -> List[T]:
            async with self.session_factory() as session:
                stmt = select(self.model).filter_by(**kwargs)
                result = await session.execute(stmt)
                return list(result.scalars().all())

        async def create(self, **kwargs) -> T:
            async with self.session_factory() as session:
                instance = self.model(**kwargs)
                session.add(instance)
                await session.commit()
                await session.refresh(instance)
                return instance

        async def update(self, id: int, **kwargs) -> T:
            async with self.session_factory() as session:
                stmt = select(self.model).where(self.model.id == id)
                result = await session.execute(stmt)
                instance = result.scalar_one()

                for key, value in kwargs.items():
                    setattr(instance, key, value)

                await session.commit()
                await session.refresh(instance)
                return instance

        async def delete(self, id: int) -> bool:
            async with self.session_factory() as session:
                stmt = sql_delete(self.model).where(self.model.id == id)
                await session.execute(stmt)
                await session.commit()
                return True

        async def all(self) -> List[T]:
            async with self.session_factory() as session:
                stmt = select(self.model)
                result = await session.execute(stmt)
                return list(result.scalars().all())

        async def count(self, **kwargs) -> int:
            async with self.session_factory() as session:
                from sqlalchemy import func as sql_func
                stmt = select(sql_func.count()).select_from(self.model).filter_by(**kwargs)
                result = await session.execute(stmt)
                return result.scalar()

    _SQLALCHEMY_AVAILABLE = True

except ImportError:
    # SQLAlchemy 未安装
    _SQLALCHEMY_AVAILABLE = False

    class AlchemyBase:  # type: ignore
        """占位符：需要安装 sqlalchemy"""
        pass

    class AlchemyTimestampMixin(BaseTimestampMixin):  # type: ignore
        """占位符：需要安装 sqlalchemy"""
        pass

    class SQLAlchemyRepository(BaseRepository[T]):  # type: ignore
        """占位符：需要安装 sqlalchemy"""
        def __init__(self, model_class, session_factory):
            raise ImportError("需要安装 sqlalchemy: pip install infomankit[database-alchemy]")

        async def get(self, id: int) -> Optional[T]:
            raise NotImplementedError
        async def filter(self, **kwargs) -> List[T]:
            raise NotImplementedError
        async def create(self, **kwargs) -> T:
            raise NotImplementedError
        async def update(self, id: int, **kwargs) -> T:
            raise NotImplementedError
        async def delete(self, id: int) -> bool:
            raise NotImplementedError
        async def all(self) -> List[T]:
            raise NotImplementedError
        async def count(self, **kwargs) -> int:
            raise NotImplementedError


# ==================== 工厂函数（自动选择后端）====================

def create_repository(model_class, backend: str = "auto", session_factory=None) -> BaseRepository:
    """
    创建仓储实例 - 自动选择后端

    Args:
        model_class: 模型类
        backend: 'tortoise', 'sqlalchemy', 'auto'（默认）
        session_factory: SQLAlchemy session factory（仅 SQLAlchemy 后端需要）

    Returns:
        BaseRepository 实例

    Raises:
        ValueError: 不支持的后端或无法自动检测
        ImportError: 所需的 ORM 库未安装

    Example:
        >>> # 自动检测
        >>> user_repo = create_repository(User)
        >>> users = await user_repo.all()

        >>> # 指定后端
        >>> user_repo = create_repository(User, backend="tortoise")
        >>> user = await user_repo.create(name="Alice")
    """
    if backend == "auto":
        # 自动检测模型类型
        if hasattr(model_class, '_meta') and hasattr(model_class._meta, 'table'):
            backend = "tortoise"
        elif hasattr(model_class, '__table__'):
            backend = "sqlalchemy"
        else:
            raise ValueError(
                f"无法自动检测模型类型: {model_class}. "
                f"请显式指定 backend='tortoise' 或 'sqlalchemy'"
            )

    if backend == "tortoise":
        if not _TORTOISE_AVAILABLE:
            raise ImportError(
                "Tortoise ORM 未安装。请运行: pip install infomankit[database]"
            )
        return TortoiseRepository(model_class)

    elif backend == "sqlalchemy":
        if not _SQLALCHEMY_AVAILABLE:
            raise ImportError(
                "SQLAlchemy 未安装。请运行: pip install infomankit[database-alchemy]"
            )

        if session_factory is None:
            # 尝试从全局管理器获取
            try:
                from infoman.service.infrastructure.db_relation.manager import hybrid_db_manager
                session_factory = hybrid_db_manager.get_sqlalchemy_session_maker()
            except Exception:
                raise ValueError(
                    "SQLAlchemy 后端需要提供 session_factory 参数，"
                    "或确保 HybridDatabaseManager 已初始化"
                )

        return SQLAlchemyRepository(model_class, session_factory)

    else:
        raise ValueError(f"不支持的后端: {backend}. 仅支持 'tortoise', 'sqlalchemy', 'auto'")


# ==================== 向前兼容导出 ====================

__all__ = [
    # 抽象基类
    'BaseTimestampMixin',
    'BaseRepository',

    # Tortoise（向前兼容）
    'TimestampMixin',
    'MySQLModel',
    'PostgreSQLModel',
    'SQLiteModel',
    'TortoiseRepository',

    # SQLAlchemy（新增）
    'AlchemyBase',
    'AlchemyTimestampMixin',
    'SQLAlchemyRepository',

    # 工厂函数
    'create_repository',

    # 可用性标志
    '_TORTOISE_AVAILABLE',
    '_SQLALCHEMY_AVAILABLE',
]
