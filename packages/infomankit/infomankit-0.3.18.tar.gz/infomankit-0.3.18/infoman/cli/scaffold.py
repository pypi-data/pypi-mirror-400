"""
Project scaffolding generator

Generates standard project structure based on infoman/service architecture.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any


class ProjectScaffold:
    """Project structure generator based on infoman/service standard"""

    @staticmethod
    def _get_templates_dir() -> Path:
        """Get the templates directory path"""
        return Path(__file__).parent / "templates"

    @staticmethod
    def _load_template(template_path: str) -> str:
        """
        Load a template file from the templates directory

        Args:
            template_path: Relative path to template file (e.g., "app/app.py.template")

        Returns:
            Template content as string
        """
        templates_dir = ProjectScaffold._get_templates_dir()
        full_path = templates_dir / template_path

        if not full_path.exists():
            raise FileNotFoundError(f"Template file not found: {full_path}")

        return full_path.read_text(encoding="utf-8")

    @staticmethod
    def _build_structure_from_templates() -> Dict[str, Any]:
        """
        Build STRUCTURE dictionary by loading from template files

        Returns:
            Dictionary representing the app/ directory structure
        """
        return {
            "__init__.py": ProjectScaffold._load_template("app/__init__.py.template"),
            "app.py": ProjectScaffold._load_template("app/app.py.template"),
            "models": {
                "__init__.py": '"""\nData models\n"""\n',
                "base.py": ProjectScaffold._load_template("app/models_base.py.template"),
                "entity": {
                    "__init__.py": ProjectScaffold._load_template("app/models_entity_init.py.template"),
                },
                "schemas": {
                    "__init__.py": ProjectScaffold._load_template("app/models_schemas_init.py.template"),
                },
            },
            "routers": {
                "__init__.py": ProjectScaffold._load_template("app/routers_init.py.template"),
            },
            "services": {
                "__init__.py": ProjectScaffold._load_template("app/services_init.py.template"),
            },
            "repository": {
                "__init__.py": ProjectScaffold._load_template("app/repository_init.py.template"),
            },
            "utils": {
                "__init__.py": ProjectScaffold._load_template("app/utils_init.py.template"),
            },
            "static": {
                "css": {
                    "style.css": ProjectScaffold._load_template("app/static_style.css.template"),
                },
                "js": {
                    "main.js": ProjectScaffold._load_template("app/static_main.js.template"),
                },
                "images": {},
                "index.html": ProjectScaffold._load_template("app/static_index.html.template"),
            },
            "template": {},
        }

    @staticmethod
    def _build_config_structure_from_templates() -> Dict[str, str]:
        """
        Build CONFIG_STRUCTURE dictionary by loading from template files

        Returns:
            Dictionary representing the config/ directory structure
        """
        return {
            ".env.dev": ProjectScaffold._load_template("config/.env.dev.template"),
            ".env.prod": ProjectScaffold._load_template("config/.env.prod.template"),
            "README.md": ProjectScaffold._load_template("config/README.md.template"),
        }

    # 标准项目目录结构（基于用户需求的 app 结构）
    # STRUCTURE is built dynamically from template files
    STRUCTURE = None  # Will be initialized in __init__

    # Add config directory structure
    CONFIG_STRUCTURE = None  # Will be initialized in __init__

    # Old CONFIG_STRUCTURE (kept for reference, will be removed)
    _OLD_CONFIG_STRUCTURE = {
        ".env.dev": """# Application Settings
APP_NAME={project_name}
APP_ENV=dev
APP_PORT=8000
APP_DEBUG=true

LOG_DIR=logs
LOG_LEVEL=DEBUG
LOG_FORMAT=simple

USE_TEMPLATES=1
USE_PRO_ORM=1
TEMPLATE_DIR=./app/template
#USE_STATIC=1

# Database Configuration (infomankit format)
MYSQL_ENABLED=true
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DB=XXX
MYSQL_USER=XXX
MYSQL_PASSWORD=XXX
MYSQL_CHARSET=utf8mb4
MYSQL_POOL_MAX_SIZE=10
MYSQL_POOL_RECYCLE=3600
MYSQL_ECHO=false
MYSQL_MODELS_PATH=app.models
MYSQL_MODELS=entity


# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Redis Configuration (Optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
""",
        ".env.prod": """# Application Settings
APP_NAME={project_name}
APP_ENV=prod
APP_PORT=8000
APP_DEBUG=false

LOG_DIR=logs
LOG_LEVEL=INFO
LOG_FORMAT=json

USE_TEMPLATES=1
USE_PRO_ORM=1
TEMPLATE_DIR=./app/template
#USE_STATIC=1

# Database Configuration (infomankit format)
MYSQL_ENABLED=true
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DB=XXX
MYSQL_USER=XXX
MYSQL_PASSWORD=XXX
MYSQL_CHARSET=utf8mb4
MYSQL_POOL_MAX_SIZE=20
MYSQL_POOL_RECYCLE=3600
MYSQL_ECHO=false
MYSQL_MODELS_PATH=app.models
MYSQL_MODELS=entity


# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration (comma-separated origins)
CORS_ORIGINS=https://your-domain.com

# Redis Configuration (Optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
""",
        "README.md": """# Configuration Files

Environment-specific configuration files for {project_name}.

## Available Configurations

- `.env.dev` - Development environment configuration
- `.env.prod` - Production environment configuration

## Usage

Copy the appropriate config file to your project root as `.env`:

```bash
# For development
cp config/.env.dev .env

# For production
cp config/.env.prod .env
```

Then edit `.env` with your actual values.

## Configuration Variables

- **APP_NAME**: Application name
- **APP_ENV**: Environment (dev/prod)
- **APP_PORT**: Server port
- **APP_DEBUG**: Debug mode (true/false)
- **LOG_LEVEL**: Logging level (DEBUG/INFO/WARNING/ERROR)
- **MYSQL_***: MySQL database configuration
- **JWT_***: JWT authentication settings
- **CORS_ORIGINS**: Allowed CORS origins
- **REDIS_***: Redis configuration (optional)
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

        # Initialize structures from templates
        if ProjectScaffold.STRUCTURE is None:
            ProjectScaffold.STRUCTURE = ProjectScaffold._build_structure_from_templates()
        if ProjectScaffold.CONFIG_STRUCTURE is None:
            ProjectScaffold.CONFIG_STRUCTURE = ProjectScaffold._build_config_structure_from_templates()

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
        # .env
        env_template = self._load_template("project/.env.example.template")
        (self.target_dir / ".env").write_text(
            env_template.format(project_name=self.project_name),
            encoding="utf-8"
        )

        # pyproject.toml
        pyproject_template = self._load_template("project/pyproject.toml.template")
        (self.target_dir / "pyproject.toml").write_text(
            pyproject_template.format(project_name=self.project_name),
            encoding="utf-8"
        )

        # README.md
        readme_template = self._load_template("project/README.md.template")
        (self.target_dir / "README.md").write_text(
            readme_template.format(project_name=self.project_name),
            encoding="utf-8"
        )

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
        main_py_template = self._load_template("project/main.py.template")
        (self.target_dir / "main.py").write_text(
            main_py_template.format(project_name=self.project_name),
            encoding="utf-8"
        )

        # .gitignore
        gitignore_template = self._load_template("project/.gitignore.template")
        (self.target_dir / ".gitignore").write_text(
            gitignore_template.format(project_name=self.project_name),
            encoding="utf-8"
        )

    def create_makefile(self) -> None:
        """创建 Makefile"""
        makefile_template = self._load_template("project/Makefile.template")
        (self.target_dir / "Makefile").write_text(
            makefile_template.format(project_name=self.project_name),
            encoding="utf-8"
        )

    def create_service_script(self) -> None:
        """创建 service.sh 服务管理脚本"""
        service_sh_template = self._load_template("project/service.sh.template")
        service_path = self.target_dir / "service.sh"
        service_path.write_text(
            service_sh_template.format(project_name=self.project_name),
            encoding="utf-8"
        )
        # Make executable
        import os
        os.chmod(service_path, 0o755)

    def generate_docker_files(self) -> None:
        """生成 Docker 相关文件到 /docker 目录"""
        docker_dir = self.target_dir / "docker"
        docker_dir.mkdir(parents=True, exist_ok=True)

        # Dockerfile
        dockerfile_template = self._load_template("docker/Dockerfile.template")
        (docker_dir / "Dockerfile").write_text(
            dockerfile_template.format(project_name=self.project_name),
            encoding="utf-8"
        )

        # docker-compose.yml
        docker_compose_template = self._load_template("docker/docker-compose.yml.template")
        (docker_dir / "docker-compose.yml").write_text(
            docker_compose_template.format(project_name=self.project_name),
            encoding="utf-8"
        )

        # .dockerignore
        dockerignore_template = self._load_template("docker/.dockerignore.template")
        (docker_dir / ".dockerignore").write_text(
            dockerignore_template.format(project_name=self.project_name),
            encoding="utf-8"
        )

        # MySQL configuration
        mysql_conf_dir = docker_dir / "mysql" / "conf.d"
        mysql_conf_dir.mkdir(parents=True, exist_ok=True)

        mysql_config_template = self._load_template("docker/mysql_custom.cnf.template")
        (mysql_conf_dir / "custom.cnf").write_text(
            mysql_config_template.format(project_name=self.project_name),
            encoding="utf-8"
        )

        # MySQL init script
        mysql_init_dir = docker_dir / "mysql" / "init"
        mysql_init_dir.mkdir(parents=True, exist_ok=True)

        mysql_init_template = self._load_template("docker/mysql_init.sql.template")
        (mysql_init_dir / "01-init.sql").write_text(
            mysql_init_template.format(project_name=self.project_name),
            encoding="utf-8"
        )

        # README
        readme_template = self._load_template("docker/README.md.template")
        (docker_dir / "README.md").write_text(
            readme_template.format(project_name=self.project_name),
            encoding="utf-8"
        )

        print(f"✓ Docker files generated in '{self.project_name}/docker/' directory")
        print(f"\n📦 Generated Docker files:")
        print(f"  • docker/Dockerfile")
        print(f"  • docker/docker-compose.yml")
        print(f"  • docker/.dockerignore")
        print(f"  • docker/mysql/conf.d/custom.cnf")
        print(f"  • docker/mysql/init/01-init.sql")
        print(f"  • docker/README.md")
        print(f"\n🚀 Quick start:")
        print(f"  cd {self.project_name}/docker")
        print(f"  docker-compose up -d")

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

        # 创建 config 目录结构
        config_dir = self.target_dir / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        self.create_structure(self.CONFIG_STRUCTURE, config_dir)

        # 创建配置文件
        self.create_config_files()

        # 创建 Makefile
        self.create_makefile()

        # 创建 service.sh
        self.create_service_script()

        print(f"✓ Project '{self.project_name}' created successfully!")
        print(f"\nGenerated structure:")
        print(f"  📁 Application code (app/)")
        print(f"  📁 Configuration (config/)")
        print(f"  📄 Environment (.env)")
        print(f"  🔧 Development tools (Makefile)")
        print(f"  🚀 Service management (service.sh)")
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
