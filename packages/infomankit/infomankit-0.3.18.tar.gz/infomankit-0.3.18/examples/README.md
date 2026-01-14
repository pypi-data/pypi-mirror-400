# Infomankit 使用示例

> 基于 infomankit 快速构建应用的示例集合

---

## 📦 示例列表

### 1. 简单扩展 (`simple_extend.py`)

**最简单的用法：导入 application，添加路由，启动！**

```python
from infoman.service.app import application
from fastapi import APIRouter

router = APIRouter()

@router.get("/hello")
def hello():
    return {"message": "Hello!"}

application.include_router(router, prefix="/api")
```

**启动方式：**

```bash
# 方式 1: Python 直接运行
python examples/simple_extend.py

# 方式 2: 使用 infoman-serve
infoman-serve --app examples.simple_extend:application --reload

# 方式 3: 使用 Granian
granian --interface asgi examples.simple_extend:application
```

**访问：**
- API 文档: http://localhost:8000/doc
- 你的接口: http://localhost:8000/api/hello

---

### 2. 完整项目 (`complete_project/`)

**标准的项目结构，适合生产环境**

```
complete_project/
├── main.py          # 入口文件
├── routers/         # 业务路由
│   ├── users.py     # 用户管理
│   └── products.py  # 产品管理
└── .env             # 配置文件
```

**启动：**

```bash
cd examples/complete_project
infoman-serve --app main:application --reload
```

**访问：**
- 用户列表: http://localhost:8000/api/users/
- 产品列表: http://localhost:8000/api/products/
- API 文档: http://localhost:8000/doc

---

## 🚀 核心用法

### 导入并扩展 application

```python
# ========== 步骤 1: 导入 ==========
from infoman.service.app import application

# ========== 步骤 2: 添加路由 ==========
from fastapi import APIRouter

router = APIRouter()

@router.get("/my-endpoint")
def my_endpoint():
    return {"data": "my data"}

# 注册路由
application.include_router(router, prefix="/api", tags=["我的业务"])

# ========== 步骤 3: 启动 ==========
# infoman-serve --app your_module:application
```

### application 已经包含的功能

✅ **日志系统** - 开箱即用的 loguru 日志
✅ **中间件** - CORS、GZip、RequestID、Logging
✅ **异常处理** - 统一的错误响应
✅ **生命周期管理** - 数据库、Redis 等自动初始化和关闭
✅ **监控指标** - Prometheus metrics (`/metrics`)
✅ **内置路由** - 健康检查 (`/health`)、监控 (`/monitor`)
✅ **Granian 支持** - 高性能生产部署

---

## 📝 开发流程

### 1. 创建项目

```bash
mkdir myproject
cd myproject
```

### 2. 安装依赖

```bash
pip install "infomankit[web]"
```

### 3. 创建应用 (`main.py`)

```python
from infoman.service.app import application
from fastapi import APIRouter

router = APIRouter()

@router.get("/hello")
def hello():
    return {"message": "Hello World!"}

application.include_router(router, prefix="/api")
```

### 4. 配置环境 (`.env`)

```bash
ENV=dev
APP_NAME=MyApp
APP_PORT=8000
LOG_LEVEL=INFO
```

### 5. 启动开发服务器

```bash
# 热重载开发
infoman-serve --app main:application --reload

# 或
python main.py
```

### 6. 访问应用

- API 文档: http://localhost:8000/doc
- 你的接口: http://localhost:8000/api/hello
- 健康检查: http://localhost:8000/health
- 监控指标: http://localhost:8000/metrics

---

## 🎯 高级用法

### 1. 使用数据库

```python
from infoman.service.app import application
from fastapi import Request, APIRouter

router = APIRouter()

@router.get("/db-test")
async def db_test(request: Request):
    # 访问数据库管理器
    db_manager = request.app.state.db_manager

    if db_manager.is_available:
        # 执行数据库操作
        # ...
        return {"status": "database connected"}
    else:
        return {"status": "database not configured"}

application.include_router(router)
```

### 2. 使用 Redis 缓存

```python
from infoman.service.app import application
from infoman.service.utils.cache import redis_cache
from fastapi import Request, APIRouter

router = APIRouter()

@router.get("/cached-data")
@redis_cache(prefix="mydata", ttl=300)
async def get_cached_data(request: Request, key: str):
    # 自动缓存到 Redis（5 分钟）
    return {"key": key, "value": "expensive computation result"}

application.include_router(router)
```

### 3. 添加自定义中间件

```python
from infoman.service.app import application
from starlette.middleware.base import BaseHTTPMiddleware

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # 请求前处理
        response = await call_next(request)
        # 响应后处理
        return response

# 添加中间件
application.add_middleware(CustomMiddleware)
```

### 4. 覆盖配置

```python
from infoman.service.app import application
from infoman.config import settings

# 动态修改配置
application.title = "My Custom Title"
application.version = "2.0.0"
```

---

## 🔧 启动方式对比

| 方式 | 命令 | 适用场景 |
|------|------|---------|
| **Python 直接运行** | `python main.py` | 开发调试 |
| **infoman-serve** | `infoman-serve --app main:application` | 推荐方式 |
| **Granian** | `granian --interface asgi main:application` | 生产环境 |
| **Uvicorn** | `uvicorn main:application --reload` | 开发环境 |

---

## 📚 更多文档

- [Granian 部署指南](../doc/granian_usage.md)
- [日志系统文档](../doc/future_2_log.md)
- [项目架构说明](../doc/CLAUDE.md)

---

## 💡 最佳实践

1. **开发环境** - 使用 `--reload` 热重载
2. **生产环境** - 使用 Granian + 多进程
3. **日志管理** - 配置 JSON 格式 + Loki 收集
4. **配置管理** - 使用 `.env` 文件 + 环境变量
5. **路由组织** - 按业务模块拆分 router
6. **依赖注入** - 使用 FastAPI Depends

---

## ❓ 常见问题

### Q1: 如何禁用内置路由？

```python
# 不导入内置路由即可，自己重新创建 application
from fastapi import FastAPI
from infoman.logger import setup_logger

setup_logger()
app = FastAPI()

# 添加自己的路由
# ...
```

### Q2: 如何添加认证？

```python
from infoman.service.core.auth import get_current_user
from fastapi import Depends

@router.get("/protected")
def protected_route(user = Depends(get_current_user)):
    return {"user": user}
```

### Q3: 如何连接数据库？

在 `.env` 中配置：

```bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DB=mydb
```

应用会自动连接数据库。

---

## 🚀 快速开始

```bash
# 1. 安装
pip install "infomankit[web]"

# 2. 复制示例
cp examples/simple_extend.py my_app.py

# 3. 修改路由
# 编辑 my_app.py，添加你的业务逻辑

# 4. 启动
infoman-serve --app my_app:application --reload

# 5. 访问
open http://localhost:8000/doc
```

**就是这么简单！** 🎉
