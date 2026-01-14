# Infoman CLI - 项目脚手架工具

快速生成基于 infomankit 标准架构的项目结构。

## 安装

```bash
pip install infomankit
```

## 使用方法

### 1. 交互式创建项目

```bash
infomancli init
# 会提示输入项目名称
```

### 2. 直接指定项目名称

```bash
infomancli init my-awesome-project
```

### 3. 指定目标目录

```bash
# 在指定目录下创建项目
infomancli init my-project --dir /path/to/workspace

# 在临时目录测试
infomancli init test-project --dir /tmp
```

### 4. 查看帮助

```bash
infomancli --help
infomancli --version
```

## 生成的项目结构

生成的项目遵循 `infoman/service` 的标准架构:

```
my-project/
├── .env.example          # 环境变量模板
├── .gitignore            # Git 忽略文件
├── README.md             # 项目说明文档
├── main.py               # 主应用入口
├── pyproject.toml        # 项目配置文件
│
├── core/                 # 核心业务逻辑
│   ├── __init__.py
│   ├── auth.py           # 认证授权
│   └── response.py       # 标准响应模型
│
├── routers/              # API 路由
│   └── __init__.py       # API 路由注册
│
├── models/               # 数据模型
│   ├── __init__.py
│   ├── entity/           # 数据库实体 (ORM 模型)
│   ├── dto/              # 数据传输对象 (API 模型)
│   └── schemas/          # Pydantic 验证模式
│
├── repository/           # 数据访问层
│   └── __init__.py
│
├── services/             # 业务逻辑服务
│   └── __init__.py
│
├── exception/            # 自定义异常
│   └── __init__.py
│
├── middleware/           # 自定义中间件
│   └── __init__.py
│
├── infrastructure/       # 基础设施
│   ├── __init__.py
│   ├── database/         # 数据库连接
│   └── cache/            # 缓存管理
│
└── utils/                # 工具函数
    ├── __init__.py
    ├── cache/            # 缓存工具
    └── parse/            # 解析工具
```

## 项目初始化步骤

创建项目后，按照以下步骤进行初始化:

```bash
# 1. 进入项目目录
cd my-project

# 2. 安装依赖
pip install -e .

# 3. 复制环境变量文件
cp .env.example .env

# 4. 编辑 .env 配置你的环境变量
vim .env

# 5. 运行开发服务器
infoman-serve run main:app --reload

# 6. 访问 API 文档
open http://localhost:8000/docs
```

## 架构说明

生成的项目遵循 infomankit 的标准架构,各目录职责如下:

### core/
核心业务逻辑和应用生命周期管理
- `auth.py` - 认证和授权逻辑
- `response.py` - 标准 API 响应模型

### routers/
API 端点和路由定义
- 所有的 API 路由在此定义
- 使用 FastAPI 的 `APIRouter`

### models/
数据模型定义
- `entity/` - 数据库 ORM 模型 (支持 Tortoise ORM 或 SQLAlchemy)
- `dto/` - API 请求/响应的数据传输对象
- `schemas/` - Pydantic 数据验证模式

### repository/
数据访问层 (Repository 模式)
- 封装数据库操作
- 提供数据访问接口

### services/
业务逻辑服务层
- 处理复杂的业务逻辑
- 协调多个 repository

### exception/
自定义异常
- 继承自 infomankit 的异常基类
- 统一的异常处理

### middleware/
自定义中间件
- 可以使用 infomankit 内置的中间件
- 或实现自定义中间件

### infrastructure/
基础设施组件
- `database/` - 数据库连接和管理
- `cache/` - 缓存管理

### utils/
通用工具函数
- `cache/` - 缓存装饰器和工具
- `parse/` - 数据解析工具

## 生成的核心文件说明

### main.py
包含 FastAPI 应用的入口点:
- 使用 `infoman.service.app.create_app` 创建应用
- 注册路由
- 提供基础的健康检查端点

### pyproject.toml
项目配置文件:
- 项目元数据
- 依赖声明 (默认包含 `infomankit[web]`)
- 开发依赖和工具配置

### .env.example
环境变量模板:
- 应用基础配置 (名称、端口、日志)
- 数据库配置 (MySQL, PostgreSQL)
- 缓存配置 (Redis)
- 向量数据库配置 (Qdrant)
- 消息队列配置 (NATS)
- LLM 配置

### README.md
项目说明文档:
- 项目介绍和快速开始
- 项目结构说明
- API 开发流程
- 使用示例

## 开发流程

### 1. 创建数据模型

在 `models/entity/` 创建 ORM 模型:
```python
from infoman.service.models.base import BaseModel
from sqlalchemy import Column, String, Integer

class User(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
```

### 2. 定义 DTO

在 `models/dto/` 创建 API 模型:
```python
from pydantic import BaseModel, EmailStr

class UserCreateDTO(BaseModel):
    name: str
    email: EmailStr

class UserResponseDTO(BaseModel):
    id: int
    name: str
    email: str
```

### 3. 实现 Repository

在 `repository/` 创建数据访问层:
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.entity import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
```

### 4. 创建 Service

在 `services/` 实现业务逻辑:
```python
from repository.user_repository import UserRepository
from models.dto import UserCreateDTO, UserResponseDTO

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self, data: UserCreateDTO) -> UserResponseDTO:
        # 业务逻辑
        user = await self.repo.create(data)
        return UserResponseDTO.from_orm(user)
```

### 5. 添加 API 端点

在 `routers/` 创建路由:
```python
from fastapi import APIRouter, Depends
from models.dto import UserCreateDTO, UserResponseDTO

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponseDTO)
async def create_user(data: UserCreateDTO):
    # 处理逻辑
    pass
```

在 `routers/__init__.py` 注册路由:
```python
from .user_router import router as user_router
api_router.include_router(user_router)
```

## 扩展项目

根据需求安装额外的依赖:

```bash
# 添加数据库支持 (SQLAlchemy)
pip install "infomankit[database-alchemy]"

# 添加缓存支持
pip install "infomankit[cache]"

# 添加 LLM 支持
pip install "infomankit[llm]"

# 添加向量数据库支持
pip install "infomankit[vector]"

# 添加消息队列支持
pip install "infomankit[messaging]"

# 完整功能
pip install "infomankit[full]"
```

在 `pyproject.toml` 中更新依赖:
```toml
dependencies = [
    "infomankit[web,database-alchemy,cache]>=0.3.0",
]
```

## 最佳实践

### 目录使用指南

- **core/** - 核心业务逻辑,与技术实现无关
- **routers/** - API 端点定义,保持精简
- **models/entity/** - 数据库表结构
- **models/dto/** - API 输入/输出模型
- **repository/** - 数据库操作封装
- **services/** - 复杂业务逻辑编排
- **exception/** - 自定义异常和错误处理
- **middleware/** - 请求/响应拦截处理
- **infrastructure/** - 外部服务连接管理
- **utils/** - 可复用的工具函数

### 架构原则

1. **分层架构**: Router -> Service -> Repository -> Database
2. **依赖注入**: 使用 FastAPI 的依赖注入系统
3. **单一职责**: 每个模块只负责一件事
4. **异常处理**: 使用 infomankit 提供的异常类
5. **日志记录**: 使用 infomankit 的日志系统
6. **配置管理**: 使用环境变量和 Pydantic Settings

## 常见问题

### Q: 项目已存在怎么办?
A: CLI 会检查目录是否存在,如果存在会报错。请选择不同的项目名称或删除现有目录。

### Q: 如何选择 ORM?
A: 默认支持 SQLAlchemy 2.0。在 `.env` 中设置 `ORM_BACKEND=sqlalchemy` 或 `ORM_BACKEND=tortoise`。

### Q: 如何自定义项目结构?
A: 生成项目后,可以根据需要添加或删除目录。生成的结构是推荐的最佳实践。

### Q: 可以在现有项目中使用吗?
A: 建议用于新项目。如果要在现有项目中使用,可以生成到临时目录,然后手动复制需要的部分。

### Q: 与 infoman/service 有什么关系?
A: 生成的项目结构完全遵循 `infoman/service` 的标准架构,可以无缝使用 infomankit 的所有功能。

## 与 infomankit 的集成

生成的项目自动集成了以下 infomankit 功能:

- ✅ FastAPI 应用工厂 (`create_app`)
- ✅ 异步数据库支持 (Tortoise ORM / SQLAlchemy)
- ✅ Redis 缓存
- ✅ 日志系统
- ✅ 异常处理
- ✅ 中间件系统
- ✅ 配置管理
- ✅ 健康检查端点

## 反馈与贡献

- Issue: https://github.com/infoman-lib/infoman-pykit/issues
- PR: https://github.com/infoman-lib/infoman-pykit/pulls

## 许可证

MIT License
