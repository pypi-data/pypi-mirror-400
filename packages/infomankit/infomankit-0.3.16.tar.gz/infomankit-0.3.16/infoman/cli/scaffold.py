"""
Project scaffolding generator

Generates standard project structure based on infoman/service architecture.
"""

import os
from pathlib import Path
from typing import Optional


class ProjectScaffold:
    """Project structure generator based on infoman/service standard"""

    # 标准项目目录结构（基于 infoman/service）
    STRUCTURE = {
        "core": {
            "__init__.py": '"""\nCore business logic and application lifecycle\n"""\n',
            "auth.py": '"""\nAuthentication and authorization logic\n"""\n\nfrom infoman.service.core.auth import *\n',
            "response.py": '"""\nStandard API response models\n"""\n\nfrom infoman.service.core.response import *\n',
        },
        "routers": {
            "__init__.py": '"""\nAPI routers and endpoints\n"""\n\nfrom fastapi import APIRouter\n\napi_router = APIRouter()\n\n# Register your routers here\n# from .your_router import your_router\n# api_router.include_router(your_router, prefix="/your-prefix", tags=["Your Tag"])\n',
        },
        "models": {
            "__init__.py": '"""\nData models\n"""\n',
            "entity": {
                "__init__.py": '"""\nDatabase entities (ORM models)\n\nExample:\n    from infoman.service.models.base import BaseModel\n    from sqlalchemy import Column, String, Integer\n\n    class User(BaseModel):\n        __tablename__ = "users"\n\n        id = Column(Integer, primary_key=True)\n        name = Column(String(100), nullable=False)\n        email = Column(String(100), unique=True)\n"""\n',
            },
            "dto": {
                "__init__.py": '"""\nData Transfer Objects (API request/response models)\n\nExample:\n    from pydantic import BaseModel, EmailStr\n\n    class UserCreateDTO(BaseModel):\n        name: str\n        email: EmailStr\n\n    class UserResponseDTO(BaseModel):\n        id: int\n        name: str\n        email: str\n"""\n',
            },
            "schemas": {
                "__init__.py": '"""\nPydantic schemas for data validation\n"""\n',
            },
        },
        "repository": {
            "__init__.py": '"""\nData access layer (Repository pattern)\n\nExample:\n    from sqlalchemy.ext.asyncio import AsyncSession\n    from sqlalchemy import select\n    from models.entity import User\n\n    class UserRepository:\n        def __init__(self, session: AsyncSession):\n            self.session = session\n\n        async def get_by_id(self, user_id: int) -> User | None:\n            result = await self.session.execute(\n                select(User).where(User.id == user_id)\n            )\n            return result.scalar_one_or_none()\n"""\n',
        },
        "exception": {
            "__init__.py": '"""\nCustom exceptions\n"""\n\nfrom infoman.service.exception import (\n    BaseAPIException,\n    BadRequestException,\n    UnauthorizedException,\n    ForbiddenException,\n    NotFoundException,\n    InternalServerException,\n)\n\n__all__ = [\n    "BaseAPIException",\n    "BadRequestException",\n    "UnauthorizedException",\n    "ForbiddenException",\n    "NotFoundException",\n    "InternalServerException",\n]\n',
        },
        "middleware": {
            "__init__.py": '"""\nCustom middleware\n"""\n\n# You can import infoman\'s built-in middleware:\n# from infoman.service.middleware import LoggingMiddleware, RequestIDMiddleware\n',
        },
        "utils": {
            "__init__.py": '"""\nUtility functions\n"""\n',
            "cache": {
                "__init__.py": '"""\nCache utilities\n"""\n\nfrom infoman.service.utils.cache import *\n',
            },
            "parse": {
                "__init__.py": '"""\nParsing utilities\n"""\n\nfrom infoman.service.utils.parse import *\n',
            },
        },
        "infrastructure": {
            "__init__.py": '"""\nInfrastructure components (database, cache, mq, etc.)\n"""\n',
            "database": {
                "__init__.py": '"""\nDatabase connection and management\n\nExample:\n    from infoman.service.infrastructure.db_relation import get_db_manager\n\n    db_manager = get_db_manager()\n    await db_manager.init()\n"""\n',
            },
            "cache": {
                "__init__.py": '"""\nCache management\n\nExample:\n    from infoman.service.infrastructure.db_cache import get_cache_manager\n\n    cache_manager = get_cache_manager()\n    await cache_manager.init()\n"""\n',
            },
        },
        "services": {
            "__init__.py": '"""\nBusiness logic services\n\nExample:\n    class UserService:\n        def __init__(self, user_repo: UserRepository):\n            self.user_repo = user_repo\n\n        async def create_user(self, user_data: UserCreateDTO) -> UserResponseDTO:\n            # Business logic here\n            pass\n"""\n',
        },
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
                with open(current_path, "w", encoding="utf-8") as f:
                    f.write(content)

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

from fastapi import FastAPI
from infoman.service.app import create_app
from infoman.logger import get_logger

# Import routers
from routers import api_router

logger = get_logger(__name__)

# Create FastAPI application using infomankit
app = create_app(
    title="{project_name}",
    description="API service built with infomankit",
    version="0.1.0",
)

# Register routers
app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint - Health check"""
    return {{
        "status": "ok",
        "service": "{project_name}",
        "version": "0.1.0",
    }}


@app.get("/health")
async def health():
    """Detailed health check"""
    return {{
        "status": "healthy",
        "service": "{project_name}",
        "checks": {{
            "api": "ok",
        }}
    }}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
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

    def generate(self) -> None:
        """生成完整的项目结构"""
        if self.target_dir.exists():
            raise FileExistsError(f"Directory '{self.target_dir}' already exists")

        # 创建项目根目录
        self.target_dir.mkdir(parents=True, exist_ok=True)

        # 创建标准目录结构
        self.create_structure(self.STRUCTURE, self.target_dir)

        # 创建配置文件
        self.create_config_files()

        # 创建 Docker 文件
        self.create_docker_files()

        # 创建 Makefile
        self.create_makefile()

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
