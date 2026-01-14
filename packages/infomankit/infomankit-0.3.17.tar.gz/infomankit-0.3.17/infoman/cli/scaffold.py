"""
Project scaffolding generator

Generates standard project structure based on infoman/service architecture.
"""

import os
from pathlib import Path
from typing import Optional


class ProjectScaffold:
    """Project structure generator based on infoman/service standard"""

    # 标准项目目录结构（基于用户需求的 app 结构）
    STRUCTURE = {
        "__init__.py": '"""\n{project_name} Application Package\n"""\n',
        "app.py": '''"""
FastAPI Application Factory

Creates and configures the FastAPI application instance.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.core.config import settings
from app.core.database import engine, Base
from app.routers import api_router


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="API service built with infomankit",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Mount static files
    static_path = Path(__file__).parent / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

    # Include routers
    app.include_router(api_router, prefix="/api")

    @app.on_event("startup")
    async def startup():
        """Initialize on startup"""
        # Create database tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @app.on_event("shutdown")
    async def shutdown():
        """Cleanup on shutdown"""
        await engine.dispose()

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {{"message": "Welcome to {project_name}"}}

    @app.get("/health")
    async def health():
        """Health check endpoint"""
        return {{"status": "healthy", "service": "{project_name}"}}

    return app


# Create app instance
app = create_app()
''',
        "core": {
            "__init__.py": '"""\nCore application components\n"""\n',
            "config.py": '''"""
Application Configuration

Manages application settings from environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # App
    APP_NAME: str = "{project_name}"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    # Security
    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
''',
            "database.py": '''"""
Database Configuration

Async database connection and session management.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

from app.core.config import settings


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for ORM models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
''',
            "auth.py": '''"""
Authentication and Authorization

JWT token handling and password utilities.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token

    Args:
        data: Token payload data
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({{"exp": expire}})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify and decode JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={{"WWW-Authenticate": "Bearer"}},
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Get current authenticated user from token

    Args:
        token: JWT token from request

    Returns:
        User information from token
    """
    payload = verify_token(token)
    return payload
''',
        },
        "models": {
            "__init__.py": '"""\nData models\n"""\n',
            "base.py": '''"""
Base Model

Base class for all ORM models with common fields.
"""

from sqlalchemy import Column, Integer, DateTime, func
from app.core.database import Base


class BaseModel(Base):
    """Base model with common fields"""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
''',
            "entity": {
                "__init__.py": '"""\nDatabase ORM Models\n"""\n',
            },
            "schemas": {
                "__init__.py": '"""\nPydantic Schemas for API\n"""\n',
            },
        },
        "routers": {
            "__init__.py": '''"""
API Routers

Central router registration.
"""

from fastapi import APIRouter

# Create main API router
api_router = APIRouter()

# Import and register sub-routers here
# Example:
# from app.routers import user_router
# api_router.include_router(user_router.router, prefix="/users", tags=["Users"])
''',
        },
        "services": {
            "__init__.py": '"""\nBusiness Logic Services\n"""\n',
        },
        "repository": {
            "__init__.py": '"""\nData Access Layer (Repository Pattern)\n"""\n',
        },
        "exception": {
            "__init__.py": '"""\nCustom Exceptions\n"""\n',
            "error.py": '''"""
Custom Error Classes

Application-specific exception classes.
"""

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base exception for API errors"""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(BaseAPIException):
    """Resource not found exception"""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class BadRequestException(BaseAPIException):
    """Bad request exception"""

    def __init__(self, detail: str = "Bad request"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class UnauthorizedException(BaseAPIException):
    """Unauthorized exception"""

    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(BaseAPIException):
    """Forbidden exception"""

    def __init__(self, detail: str = "Forbidden"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)
''',
        },
        "utils": {
            "__init__.py": '"""\nUtility Functions\n"""\n',
        },
        "static": {
            "README.md": "# Static Files\\n\\nPlace your static files (CSS, JS, images) here.\\n",
            "css": {
                "main.css": "/* Main stylesheet */\\n",
            },
            "js": {
                "main.js": "// Main JavaScript file\\n",
            },
            "images": {
                ".gitkeep": "",
            },
            "index.html": "<!DOCTYPE html>\\n<html>\\n<head>\\n    <title>{project_name}</title>\\n</head>\\n<body>\\n    <h1>Welcome to {project_name}</h1>\\n</body>\\n</html>\\n",
        },
        "template": {
            ".gitkeep": "",
        },
    }

    # Add docker directory structure
    DOCKER_STRUCTURE = {
        "mysql": {
            "conf.d": {
                "custom.cnf": """[mysqld]
# Character set
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci

# Connection settings
max_connections=200
wait_timeout=28800
interactive_timeout=28800

# InnoDB settings
innodb_buffer_pool_size=256M
innodb_log_file_size=64M
innodb_flush_log_at_trx_commit=2
innodb_flush_method=O_DIRECT

# Query cache
query_cache_type=1
query_cache_size=16M

# Logging
general_log=0
slow_query_log=1
slow_query_log_file=/var/log/mysql/slow.log
long_query_time=2

[mysql]
default-character-set=utf8mb4

[client]
default-character-set=utf8mb4
""",
            },
            "init": {
                "01-init.sql": """-- Initialize database for {project_name}
-- This script runs when MySQL container starts for the first time

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS {project_name}
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Use the database
USE {project_name};

-- Create sample table (modify as needed)
-- CREATE TABLE IF NOT EXISTS sample (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     name VARCHAR(100) NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add your initialization SQL here
""",
            },
        },
    }

    # Add config directory structure
    CONFIG_STRUCTURE = {
        "README.md": """# Configuration Files

Place your configuration files here.

## Environment-specific configs
- `dev.yaml` - Development environment
- `prod.yaml` - Production environment
- `test.yaml` - Testing environment

## Example structure
```yaml
# config/dev.yaml
database:
  host: localhost
  port: 3306
  name: {project_name}_dev

redis:
  host: localhost
  port: 6379
```
""",
    }

    def __init__(self, project_name: str, target_dir: Optional[Path] = None):
        """
        初始化项目脚手架

        Args:
            project_name: 项目名称
            target_dir: 目标目录，默认为当前目录下的项目名称目录
        """
        self.project_name = project_name
        self.target_dir = target_dir or Path.cwd() / project_name

    def create_structure(self, structure: dict, parent_path: Path) -> None:
        """
        递归创建目录结构

        Args:
            structure: 目录结构字典
            parent_path: 父目录路径
        """
        for name, content in structure.items():
            current_path = parent_path / name

            if isinstance(content, dict):
                # 创建目录
                current_path.mkdir(parents=True, exist_ok=True)
                # 递归创建子结构
                self.create_structure(content, current_path)
            else:
                # 创建文件
                current_path.parent.mkdir(parents=True, exist_ok=True)
                # Format content with project name
                formatted_content = content.format(project_name=self.project_name)
                with open(current_path, "w", encoding="utf-8") as f:
                    f.write(formatted_content)

    def create_config_files(self) -> None:
        """创建配置文件"""
        # .env.example
        env_example = """# Application Settings
ENV=dev
APP_NAME={project_name}
APP_HOST=0.0.0.0
APP_PORT=8000
APP_BASE_URI=
LOG_LEVEL=INFO
LOG_FORMAT=json

# Database (optional)
# ORM backend: tortoise or sqlalchemy
# ORM_BACKEND=sqlalchemy

# MySQL
# MYSQL_ENABLED=false
# MYSQL_HOST=localhost
# MYSQL_PORT=3306
# MYSQL_USER=root
# MYSQL_PASSWORD=
# MYSQL_DATABASE={project_name}

# PostgreSQL (optional)
# PGSQL_ENABLED=false
# PGSQL_HOST=localhost
# PGSQL_PORT=5432
# PGSQL_USER=postgres
# PGSQL_PASSWORD=
# PGSQL_DATABASE={project_name}

# Redis (optional)
# REDIS_ENABLED=false
# REDIS_HOST=localhost
# REDIS_PORT=6379
# REDIS_DB=0
# REDIS_PASSWORD=

# Vector Database (optional)
# QDRANT_ENABLED=false
# QDRANT_HOST=localhost
# QDRANT_PORT=6333

# Message Queue (optional)
# NATS_ENABLED=false
# NATS_URL=nats://localhost:4222

# LLM (optional)
# LLM_PROVIDER=openai
# LLM_API_KEY=
# LLM_MODEL=gpt-4
# LLM_BASE_URL=
""".format(project_name=self.project_name)

        (self.target_dir / ".env.example").write_text(env_example, encoding="utf-8")

        # pyproject.toml
        pyproject = """[project]
name = "{project_name}"
version = "0.1.0"
description = "A project built with infomankit"
requires-python = ">=3.11"

dependencies = [
    "infomankit[web]>=0.3.0",
]

[project.optional-dependencies]
# Add database support
database = [
    "infomankit[database-alchemy]",
]

# Add full features
full = [
    "infomankit[full]",
]

dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.14.10",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
target-version = "py311"
line-length = 88
select = ["E", "W", "F", "I", "B"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
""".format(project_name=self.project_name)

        (self.target_dir / "pyproject.toml").write_text(pyproject, encoding="utf-8")

        # README.md
        readme = """# {project_name}

A project built with [infomankit](https://github.com/infoman-lib/infoman-pykit).

## Quick Start

```bash
# Method 1: Local Development
make init-env              # Create .env file
make install               # Install dependencies
make dev                   # Run development server

# Method 2: Docker
make docker-build          # Build Docker image
make docker-up             # Start services
```

Visit http://localhost:8000/docs for API documentation.

## Available Commands

Run `make help` to see all available commands:

- `make dev` - Run development server with auto-reload
- `make test` - Run tests
- `make lint` - Check code quality
- `make format` - Format code
- `make docker-up` - Start Docker services
- `make docker-down` - Stop Docker services

## Project Structure

```
{project_name}/
├── core/                # Core business logic
├── routers/             # API endpoints
├── models/              # Data models
│   ├── entity/          # Database ORM models
│   ├── dto/             # Request/response models
│   └── schemas/         # Validation schemas
├── repository/          # Data access layer
├── services/            # Business logic
├── infrastructure/      # Database, cache connections
├── exception/           # Custom exceptions
├── middleware/          # Custom middleware
├── utils/               # Utility functions
├── doc/                 # Documentation
├── main.py              # Application entry
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose setup
└── Makefile             # Development commands
```

## Documentation

- [doc/1-API-GUIDE.md](doc/1-API-GUIDE.md) - API 开发指南
- [doc/2-DEPLOYMENT.md](doc/2-DEPLOYMENT.md) - 部署指南

## Features

This project includes:

- FastAPI application with auto-generated API docs
- Async/await support throughout
- Optional database integration (SQLAlchemy/Tortoise ORM)
- Redis caching support
- Docker and Docker Compose setup
- Development tools (linting, formatting, testing)
- Clean architecture with separation of concerns
- Built-in logging and monitoring
- Production-ready configuration

## Learn More

- [Infomankit GitHub](https://github.com/infoman-lib/infoman-pykit)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- Read the guides in `doc/` directory for detailed information
""".format(project_name=self.project_name)

        (self.target_dir / "README.md").write_text(readme, encoding="utf-8")

        # Create doc directory structure
        doc_dir = self.target_dir / "doc"
        doc_dir.mkdir(exist_ok=True)

        # Create API documentation template
        api_doc = """# API 开发指南

## 快速开始

本文档介绍如何使用 {project_name} 开发 API。

## 数据流程

1. **定义数据模型** (`models/entity/`) - 数据库 ORM 模型
2. **创建 DTO** (`models/dto/`) - API 请求/响应模型
3. **实现 Repository** (`repository/`) - 数据访问层
4. **编写 Service** (`services/`) - 业务逻辑
5. **添加 Router** (`routers/`) - API 端点

## 示例：用户管理 API

### 1. 定义 Entity (models/entity/user.py)

```python
from infoman.service.models.base import BaseModel
from sqlalchemy import Column, String, Integer

class User(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
```

### 2. 创建 DTO (models/dto/user.py)

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

### 3. 实现 Repository (repository/user_repository.py)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from models.entity.user import User
from models.dto.user import UserCreateDTO

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: UserCreateDTO) -> User:
        user = User(**data.model_dump())
        self.session.add(user)
        await self.session.commit()
        return user
```

### 4. 创建 Service (services/user_service.py)

```python
from repository.user_repository import UserRepository
from models.dto.user import UserCreateDTO, UserResponseDTO

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self, data: UserCreateDTO) -> UserResponseDTO:
        user = await self.repo.create(data)
        return UserResponseDTO(
            id=user.id,
            name=user.name,
            email=user.email
        )
```

### 5. 添加 Router (routers/user_router.py)

```python
from fastapi import APIRouter, Depends
from models.dto.user import UserCreateDTO, UserResponseDTO
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponseDTO)
async def create_user(
    data: UserCreateDTO,
    service: UserService = Depends()
):
    return await service.create_user(data)
```

### 6. 注册 Router (routers/__init__.py)

```python
from .user_router import router as user_router

api_router.include_router(user_router)
```

## 更多信息

查看 infomankit 文档：https://github.com/infoman-lib/infoman-pykit
""".format(project_name=self.project_name)

        (doc_dir / "1-API-GUIDE.md").write_text(api_doc, encoding="utf-8")

        # Create deployment guide
        deploy_doc = """# 部署指南

## Docker 部署（推荐）

### 1. 构建镜像

```bash
make docker-build
```

### 2. 启动服务

```bash
make docker-up
```

### 3. 查看日志

```bash
make docker-logs
```

### 4. 停止服务

```bash
make docker-down
```

## 本地部署

### 1. 安装依赖

```bash
make install
```

### 2. 配置环境

```bash
make init-env
# 编辑 .env 文件
```

### 3. 运行服务

```bash
# 开发模式
make dev

# 生产模式
make run
```

## 生产环境建议

- 使用环境变量管理配置
- 配置反向代理（Nginx/Caddy）
- 启用 HTTPS
- 设置日志轮转
- 配置健康检查
- 使用进程管理器（systemd/supervisor）

## 监控

访问以下端点检查服务状态：

- `/health` - 健康检查
- `/api/docs` - API 文档
- `/metrics` - Prometheus 指标（如已启用）
"""

        (doc_dir / "2-DEPLOYMENT.md").write_text(deploy_doc, encoding="utf-8")

        # main.py
        main_py = '''"""
{project_name} - Main Application Entry Point

Built with infomankit framework.
"""

from app.app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
'''.format(project_name=self.project_name)

        (self.target_dir / "main.py").write_text(main_py, encoding="utf-8")

        # .gitignore
        gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.env.local
.env.*.local

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# OS
.DS_Store
Thumbs.db
"""

        (self.target_dir / ".gitignore").write_text(gitignore, encoding="utf-8")

    def create_docker_files(self) -> None:
        """创建 Docker 相关文件"""
        # Dockerfile
        dockerfile = '''# Multi-stage build for optimal image size
# Stage 1: Builder
FROM python:3.11-slim as builder

ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1 \\
    PIP_NO_CACHE_DIR=1 \\
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy requirements
COPY pyproject.toml ./
COPY *.py ./

# Install dependencies
RUN pip install --no-cache-dir -e .

# Stage 2: Runtime
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1 \\
    PATH="/app/.venv/bin:$PATH" \\
    ENV=production \\
    APP_HOST=0.0.0.0 \\
    APP_PORT=8000

# Create non-root user
RUN groupadd -r appuser && \\
    useradd -r -g appuser -u 1000 -m -s /bin/bash appuser

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application
COPY --chown=appuser:appuser . .

# Create directories
RUN mkdir -p /app/logs /app/data && \\
    chown -R appuser:appuser /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${{APP_PORT}}/health')" || exit 1

USER appuser

EXPOSE 8000

CMD ["infoman-serve", "run", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

        (self.target_dir / "Dockerfile").write_text(dockerfile, encoding="utf-8")

        # docker-compose.yml
        docker_compose = '''version: '3.8'

services:
  # Application
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: {project_name}-app
    restart: unless-stopped
    ports:
      - "${{APP_PORT:-8000}}:8000"
    environment:
      - ENV=${{ENV:-development}}
      - APP_HOST=0.0.0.0
      - APP_PORT=8000
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: {project_name}-redis
    restart: unless-stopped
    ports:
      - "${{REDIS_PORT:-6379}}:6379"
    volumes:
      - redis_data:/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    command: redis-server --appendonly yes

volumes:
  redis_data:
    driver: local

networks:
  app-network:
    driver: bridge
'''.format(project_name=self.project_name)

        (self.target_dir / "docker-compose.yml").write_text(docker_compose, encoding="utf-8")

        # .dockerignore
        dockerignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
env/

# Build
build/
dist/
*.egg-info/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# Environment
.env
.env.local

# Git
.git/
.gitignore

# Documentation
docs/
*.md

# Other
.DS_Store
"""

        (self.target_dir / ".dockerignore").write_text(dockerignore, encoding="utf-8")

    def create_makefile(self) -> None:
        """创建 Makefile"""
        makefile = '''.PHONY: help install dev test lint format clean docker-build docker-up docker-down

.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip
PYTEST := pytest
DOCKER_COMPOSE := docker compose

help: ## Show this help message
	@echo '════════════════════════════════════════════════════════'
	@echo '         {project_name} - Development Commands         '
	@echo '════════════════════════════════════════════════════════'
	@echo ''
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "  \\033[36m%-20s\\033[0m %s\\n", $$1, $$2}}'
	@echo ''

# ==================== Installation ====================

install: ## Install dependencies
	$(PIP) install -e .

install-dev: ## Install with dev dependencies
	$(PIP) install -e ".[dev]"

upgrade: ## Upgrade dependencies
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -e .

# ==================== Development ====================

dev: ## Run development server
	infoman-serve run main:app --host 0.0.0.0 --port 8000 --reload

run: ## Run production server
	infoman-serve run main:app --host 0.0.0.0 --port 8000

# ==================== Testing ====================

test: ## Run tests
	$(PYTEST) tests/ -v

test-cov: ## Run tests with coverage
	$(PYTEST) tests/ -v --cov --cov-report=term-missing

# ==================== Code Quality ====================

lint: ## Run linting
	ruff check .

lint-fix: ## Fix linting issues
	ruff check . --fix

format: ## Format code
	ruff format .

format-check: ## Check formatting
	ruff format . --check

# ==================== Docker ====================

docker-build: ## Build Docker image
	docker build -t {project_name}:latest .

docker-up: ## Start services
	$(DOCKER_COMPOSE) up -d

docker-down: ## Stop services
	$(DOCKER_COMPOSE) down

docker-logs: ## Show logs
	$(DOCKER_COMPOSE) logs -f

docker-clean: ## Clean Docker resources
	$(DOCKER_COMPOSE) down -v --remove-orphans

# ==================== Utilities ====================

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache/ .ruff_cache/
	rm -rf htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {{}} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete

init-env: ## Initialize .env from example
	cp .env.example .env
	@echo "✅ .env file created"
	@echo "⚠️  Update .env with your configuration"
'''.format(project_name=self.project_name)

        (self.target_dir / "Makefile").write_text(makefile, encoding="utf-8")

    def create_manage_script(self) -> None:
        """创建 manage.sh 管理脚本"""
        manage_sh = '''#!/bin/bash
# {project_name} Management Script
# Provides convenient commands for managing the application

set -e

PROJECT_NAME="{project_name}"
DOCKER_COMPOSE="docker compose"

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

# Helper functions
log_info() {{
    echo -e "${{BLUE}}[INFO]${{NC}} $1"
}}

log_success() {{
    echo -e "${{GREEN}}[SUCCESS]${{NC}} $1"
}}

log_warning() {{
    echo -e "${{YELLOW}}[WARNING]${{NC}} $1"
}}

log_error() {{
    echo -e "${{RED}}[ERROR]${{NC}} $1"
}}

# Command functions
cmd_help() {{
    cat << EOF
════════════════════════════════════════════════════════
  $PROJECT_NAME - Management Commands
════════════════════════════════════════════════════════

Usage: ./manage.sh <command> [options]

Available Commands:

  Development:
    dev               Run development server (with reload)
    run               Run production server
    shell             Open Python interactive shell

  Docker:
    docker-build      Build Docker image
    docker-up         Start Docker services
    docker-down       Stop Docker services
    docker-logs       Show Docker logs
    docker-shell      Open shell in running container
    docker-restart    Restart Docker services

  Database:
    db-migrate        Run database migrations
    db-upgrade        Upgrade database to latest
    db-downgrade      Downgrade database one version
    db-init           Initialize database

  Testing & Quality:
    test              Run tests
    test-cov          Run tests with coverage
    lint              Check code quality
    format            Format code

  Utilities:
    clean             Clean build artifacts
    install           Install dependencies
    init-env          Initialize .env from example

Examples:
  ./manage.sh dev
  ./manage.sh docker-up
  ./manage.sh test

════════════════════════════════════════════════════════
EOF
}}

cmd_dev() {{
    log_info "Starting development server..."
    python -m uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload
}}

cmd_run() {{
    log_info "Starting production server..."
    python -m uvicorn app.app:app --host 0.0.0.0 --port 8000
}}

cmd_shell() {{
    log_info "Opening Python shell..."
    python -i -c "from app.app import app; from app.core.database import engine, AsyncSessionLocal"
}}

cmd_docker_build() {{
    log_info "Building Docker image..."
    docker build -t $PROJECT_NAME:latest .
    log_success "Docker image built successfully"
}}

cmd_docker_up() {{
    log_info "Starting Docker services..."
    $DOCKER_COMPOSE up -d
    log_success "Docker services started"
    log_info "Application: http://localhost:8000"
    log_info "API Docs: http://localhost:8000/docs"
}}

cmd_docker_down() {{
    log_info "Stopping Docker services..."
    $DOCKER_COMPOSE down
    log_success "Docker services stopped"
}}

cmd_docker_logs() {{
    $DOCKER_COMPOSE logs -f
}}

cmd_docker_shell() {{
    log_info "Opening shell in container..."
    docker exec -it ${{PROJECT_NAME}}-app /bin/bash
}}

cmd_docker_restart() {{
    log_info "Restarting Docker services..."
    $DOCKER_COMPOSE restart
    log_success "Docker services restarted"
}}

cmd_test() {{
    log_info "Running tests..."
    pytest tests/ -v
}}

cmd_test_cov() {{
    log_info "Running tests with coverage..."
    pytest tests/ -v --cov --cov-report=term-missing --cov-report=html
}}

cmd_lint() {{
    log_info "Checking code quality..."
    ruff check .
}}

cmd_format() {{
    log_info "Formatting code..."
    ruff format .
    log_success "Code formatted"
}}

cmd_clean() {{
    log_info "Cleaning build artifacts..."
    rm -rf build/ dist/ *.egg-info
    rm -rf .pytest_cache/ .ruff_cache/
    rm -rf htmlcov/ .coverage
    find . -type d -name __pycache__ -exec rm -rf {{}} + 2>/dev/null || true
    find . -type f -name '*.pyc' -delete
    log_success "Cleaned successfully"
}}

cmd_install() {{
    log_info "Installing dependencies..."
    pip install -e .
    log_success "Dependencies installed"
}}

cmd_init_env() {{
    if [ -f .env ]; then
        log_warning ".env file already exists"
        read -p "Overwrite? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Keeping existing .env file"
            exit 0
        fi
    fi
    cp .env.example .env
    log_success ".env file created"
    log_warning "Please update .env with your configuration"
}}

cmd_db_init() {{
    log_info "Initializing database..."
    python -c "from app.core.database import engine, Base; import asyncio; asyncio.run(engine.run_sync(Base.metadata.create_all))"
    log_success "Database initialized"
}}

# Main command dispatcher
case "$1" in
    help|--help|-h|"")
        cmd_help
        ;;
    dev)
        cmd_dev
        ;;
    run)
        cmd_run
        ;;
    shell)
        cmd_shell
        ;;
    docker-build)
        cmd_docker_build
        ;;
    docker-up)
        cmd_docker_up
        ;;
    docker-down)
        cmd_docker_down
        ;;
    docker-logs)
        cmd_docker_logs
        ;;
    docker-shell)
        cmd_docker_shell
        ;;
    docker-restart)
        cmd_docker_restart
        ;;
    test)
        cmd_test
        ;;
    test-cov)
        cmd_test_cov
        ;;
    lint)
        cmd_lint
        ;;
    format)
        cmd_format
        ;;
    clean)
        cmd_clean
        ;;
    install)
        cmd_install
        ;;
    init-env)
        cmd_init_env
        ;;
    db-init)
        cmd_db_init
        ;;
    *)
        log_error "Unknown command: $1"
        echo ""
        cmd_help
        exit 1
        ;;
esac
'''.format(project_name=self.project_name)

        manage_path = self.target_dir / "manage.sh"
        manage_path.write_text(manage_sh, encoding="utf-8")
        # Make executable
        import os
        os.chmod(manage_path, 0o755)

    def generate(self) -> None:
        """生成完整的项目结构"""
        if self.target_dir.exists():
            raise FileExistsError(f"Directory '{self.target_dir}' already exists")

        # 创建项目根目录
        self.target_dir.mkdir(parents=True, exist_ok=True)

        # 创建 app 目录结构
        app_dir = self.target_dir / "app"
        app_dir.mkdir(parents=True, exist_ok=True)
        self.create_structure(self.STRUCTURE, app_dir)

        # 创建 docker 目录结构
        docker_dir = self.target_dir / "docker"
        docker_dir.mkdir(parents=True, exist_ok=True)
        self.create_structure(self.DOCKER_STRUCTURE, docker_dir)

        # 创建 config 目录结构
        config_dir = self.target_dir / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        self.create_structure(self.CONFIG_STRUCTURE, config_dir)

        # 创建配置文件
        self.create_config_files()

        # 创建 Docker 文件
        self.create_docker_files()

        # 创建 Makefile
        self.create_makefile()

        # 创建 manage.sh
        self.create_manage_script()

        print(f"✓ Project '{self.project_name}' created successfully!")
        print(f"\nGenerated structure:")
        print(f"  📁 Application code (core/, routers/, models/, services/)")
        print(f"  📁 Documentation (doc/)")
        print(f"  📄 Configuration (.env.example, pyproject.toml)")
        print(f"  🐳 Docker setup (Dockerfile, docker-compose.yml)")
        print(f"  🔧 Development tools (Makefile)")
        print(f"\nNext steps:")
        print(f"  cd {self.project_name}")
        print(f"  make help                  # See all commands")
        print(f"\n  Quick start (local):")
        print(f"  make init-env && make install && make dev")
        print(f"\n  Quick start (Docker):")
        print(f"  make docker-build && make docker-up")
        print(f"\n📚 Documentation:")
        print(f"  README.md               - Project overview")
        print(f"  doc/1-API-GUIDE.md      - API development guide")
        print(f"  doc/2-DEPLOYMENT.md     - Deployment instructions")
        print(f"\n🌐 After starting: http://localhost:8000/docs")
