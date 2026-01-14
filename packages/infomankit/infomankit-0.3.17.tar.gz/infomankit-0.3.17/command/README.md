# RWA Service Command Line Tools

命令行工具集，用于快速生成和管理 RWA Service 模块。

## 可用命令

### scaffold - 模块脚手架生成器

快速生成符合项目结构的标准模块代码。

## 安装

工具已集成在项目中，无需额外安装。

## 使用方法

### 基本用法

```bash
# 生成基础模块（包含 models, repository, services, routers）
python -m command.scaffold <module_name>

# 生成完整模块（额外包含 utils 和 tests）
python -m command.scaffold <module_name> --type full
```

### 示例

#### 1. 生成投资者模块

```bash
python -m command.scaffold investor
```

生成的文件结构：
```
app/
├── models/
│   ├── entity/
│   │   └── __init__.py (带示例)
│   └── schemas/
│       └── __init__.py (带示例)
├── repository/
│   └── investor_repository.py (完整CRUD实现)
├── services/
│   └── investor_service.py (业务逻辑层)
└── routers/
    ├── investor_router.py (RESTful API)
    └── _register_investor.txt (注册说明)
```

#### 2. 生成完整的合约模块

```bash
python -m command.scaffold contract --type full
```

额外生成：
```
app/
├── utils/
│   └── contract_utils.py (工具函数)
└── tests/
    ├── test_contract_repository.py (Repository测试)
    └── test_contract_service.py (Service测试)
```

#### 3. 指定目标目录

```bash
python -m command.scaffold token --target /path/to/app
```

## 生成的代码结构

### 1. Entity (models/entity/)

数据库 ORM 模型（基于 SQLAlchemy）

```python
class Investor(BaseModel):
    __tablename__ = "investors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False)
```

### 2. Schema (models/schemas/)

Pydantic 请求/响应模型

```python
class InvestorCreateReq(BaseModel):
    """创建投资者请求"""
    name: str = Field(..., description="Investor name")

class InvestorResp(BaseModel):
    """投资者响应"""
    id: int
    name: str
    created_at: datetime
```

### 3. Repository (repository/)

数据访问层（Repository Pattern）

```python
class InvestorRepository:
    @staticmethod
    async def create(data: dict, session: AsyncSession) -> Investor:
        """创建投资者"""
        pass

    @staticmethod
    async def get_by_id(id: int, session: AsyncSession) -> Optional[Investor]:
        """根据ID获取"""
        pass

    # get_all, update, delete...
```

### 4. Service (services/)

业务逻辑层

```python
class InvestorService:
    @staticmethod
    async def create_investor(
        data: InvestorCreateReq,
        session: AsyncSession,
    ) -> InvestorResp:
        """创建投资者业务逻辑"""
        pass

    # get_investor, list_investors, update_investor, delete_investor...
```

### 5. Router (routers/)

RESTful API 端点

```python
router = APIRouter(prefix="/investors", tags=["Investors"])

@router.post("/")
async def create_investor(data: InvestorCreateReq, ...):
    """创建投资者"""
    pass

@router.get("/{id}")
async def get_investor(id: int, ...):
    """获取投资者"""
    pass

# GET /, PUT /{id}, DELETE /{id}...
```

## 完整工作流程

### 1. 生成模块

```bash
python -m command.scaffold investor
```

### 2. 完善 Entity

编辑 `app/models/entity/investor.py`:

```python
from sqlalchemy import Column, String, Integer, DateTime, Decimal
from infoman.service.models.base import BaseModel

class Investor(BaseModel):
    __tablename__ = "investors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    investment_amount = Column(Decimal(15, 2), default=0)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
```

### 3. 完善 Schema

编辑 `app/models/schemas/investor_schema.py`:

```python
from pydantic import BaseModel, EmailStr, Field
from decimal import Decimal
from datetime import datetime

class InvestorCreateReq(BaseModel):
    """创建投资者请求"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = None
    investment_amount: Decimal = Field(default=0, ge=0)

class InvestorUpdateReq(BaseModel):
    """更新投资者请求"""
    name: str | None = None
    phone: str | None = None

class InvestorResp(BaseModel):
    """投资者响应"""
    id: int
    name: str
    email: str
    phone: str | None
    investment_amount: Decimal
    created_at: datetime
    updated_at: datetime
```

### 4. 注册 Router

根据 `app/routers/_register_investor.txt` 的说明，编辑 `app/routers/__init__.py`:

```python
from fastapi import APIRouter
from .admin_router import router as admin_router
from .investor_router import router as investor_router

api_router = APIRouter()

api_router.include_router(admin_router, prefix="/api")
api_router.include_router(investor_router, prefix="/api")
```

### 5. 运行数据库迁移

如果生成了迁移文件：

```bash
# 查看迁移
alembic current

# 执行迁移
alembic upgrade head
```

或者手动创建表：

```sql
CREATE TABLE investors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    investment_amount DECIMAL(15,2) DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 6. 测试 API

启动服务：

```bash
make dev
# 或
python main.py
```

访问 API 文档：
- http://localhost:8000/docs

测试端点：
- POST /api/investors - 创建投资者
- GET /api/investors/{id} - 获取投资者
- GET /api/investors - 列出投资者
- PUT /api/investors/{id} - 更新投资者
- DELETE /api/investors/{id} - 删除投资者

## 高级功能

### 自定义模板

如果需要自定义生成的代码模板，可以修改 `command/scaffold.py` 中的：

- `BASIC_STRUCTURE` - 基础结构模板
- `FULL_STRUCTURE` - 完整结构模板

### 命令行参数

```bash
python -m command.scaffold --help
```

查看所有可用参数和选项。

## 最佳实践

### 1. 命名规范

- **模块名**: 小写，使用下划线分隔 (e.g., `user_profile`, `token_holder`)
- **类名**: PascalCase (e.g., `UserProfile`, `TokenHolder`)
- **表名**: 复数形式 (e.g., `user_profiles`, `token_holders`)

### 2. 目录结构

遵循项目标准目录结构：
```
app/
├── models/          # 数据模型
│   ├── entity/      # ORM 模型
│   └── schemas/     # Pydantic 模型
├── repository/      # 数据访问
├── services/        # 业务逻辑
├── routers/         # API 端点
├── utils/           # 工具函数
└── tests/           # 测试文件
```

### 3. 代码复用

- Entity 使用 `BaseModel` 基类
- 使用统一的异常处理 (`NotFoundException`, etc.)
- 使用标准响应格式 (`success_response`)
- 统一的数据库会话管理 (`get_db`)

### 4. API 设计

遵循 RESTful 规范：
- POST /resources - 创建
- GET /resources/{id} - 获取单个
- GET /resources - 列表（支持分页）
- PUT /resources/{id} - 更新
- DELETE /resources/{id} - 删除

## 故障排除

### Q: 生成失败，提示目录不存在

**A:** 确保在项目根目录下运行命令，或使用 `--target` 指定正确的 app 目录。

```bash
# 检查当前目录
pwd

# 从项目根目录运行
cd /path/to/rwa_service
python -m command.scaffold investor
```

### Q: 如何删除生成的模块？

**A:** 手动删除相关文件：

```bash
# 删除生成的文件
rm app/models/entity/investor.py
rm app/models/schemas/investor_schema.py
rm app/repository/investor_repository.py
rm app/services/investor_service.py
rm app/routers/investor_router.py
rm app/routers/_register_investor.txt

# 如果是 full 类型
rm app/utils/investor_utils.py
rm -rf app/tests/test_investor_*
```

### Q: 如何修改已生成的代码？

**A:** 直接编辑生成的文件。脚手架只是起点，你可以根据需求自由修改。

### Q: 生成的代码是否可以直接使用？

**A:** 生成的代码是模板，需要根据实际业务需求进行调整：
1. 完善 Entity 的字段定义
2. 完善 Schema 的验证规则
3. 添加业务逻辑到 Service
4. 调整 API 端点和参数

## 示例项目

查看现有模块作为参考：

```bash
# 查看管理员模块
app/
├── models/entity/admin_user.py
├── models/schemas/admin_schema.py
├── repository/admin_repository.py
├── services/admin_service.py
└── routers/admin_router.py

# 查看 NAV 模块
app/
├── models/entity/nav_data.py
├── models/schemas/nav_schema.py
└── repository/nav_repository.py
```

## 反馈与贡献

如有问题或建议，请：
1. 查看项目文档
2. 提交 Issue
3. 提交 Pull Request

## 版本历史

- **v0.1.0** - 初始版本
  - 基础模块生成
  - 完整模块生成（含 utils 和 tests）
  - 数据库迁移文件生成
  - Router 注册说明

---

Happy coding! 🚀
