# infomankit

> 现代化 Python/AI 服务脚手架与工具箱。封装了配置加载、日志、FastAPI 服务、LLM 调用、缓存、消息队列、加解密等常用能力，帮助你快速把 idea 变成可部署的生产级服务。

## 特性亮点
- **统一配置体系**：`.env` + `config.py` 支持多环境加载，覆盖应用、数据库、缓存、LLM、MQ、向量库等关键参数。
- **FastAPI 微服务基线**：开箱即可运行的 `infoman.service.app`，内置 CORS、GZip、链路日志、中英文错误码、请求 ID、健康/监控接口。
- **灵活的 ORM 选择**：支持 `Tortoise ORM`（简单易用）和 `SQLAlchemy 2.0`（强大性能），可单独或同时使用。
- **异步基础设施**：MySQL/PostgreSQL、Redis 缓存、Litellm、NATS、Qdrant/Milvus 的集成入口，易于按需扩展。
- **AI/LLM 辅助**：`infoman.llm.LLM` 提供问答、对话、流式输出、翻译、总结、代码审查等常用封装。
- **性能测试工具**：内置标准化性能测试模块，支持定制化接口测试、精美 HTML 报告生成、多种接口类型评估标准。
- **实用工具集**：日志系统、缓存/重试/计时装饰器、AES/RSA、异步 HTTP、文本结构化提取、Feishu Bot 等常用基建。
- **细粒度模块化**：可单独安装 `web`、`database`、`database-alchemy`、`llm`、`vector`、`messaging` 等 extra，仅引入所需依赖。

## 目录速览
```
infoman/
├── config/            # 环境变量加载与全局配置
├── llm/               # Litellm 包装，提供 Chat/Stream/API
├── performance/       # 性能测试模块（新增）
│   ├── config.py      # 测试配置管理
│   ├── runner.py      # 测试运行器
│   ├── reporter.py    # HTML 报告生成
│   ├── standards.py   # 性能标准定义
│   └── cli.py         # 命令行工具
├── service/
│   ├── app.py         # FastAPI Application 入口
│   ├── routers/       # 健康检查与监控 API
│   ├── core/          # 事件、响应、认证
│   ├── infrastructure/  # 数据库，消息队列
│   ├── exception/     # 错误码、异常处理
│   ├── middleware/    # Logging、RequestID、RateLimit、中间件基类
│   ├── models/        # Tortoise 模型基类 & Embedding 配置
│   └── utils/         # redis 缓存装饰器、解析/转换
└── utils/
    ├── log/           # Loguru 配置与上下文
    ├── decorators/    # cache、retry、timing 等装饰器
    ├── encryption/    # AES/RSA/ECC
    ├── http/          # aiohttp 客户端、请求信息提取
    ├── notification/  # 飞书机器人通知
    └── text/          # JSON 结构提取等
```

## 快速开始

### 一键创建项目

```bash
# 安装 infomankit
pip install -U infomankit

# 创建新项目（自动生成标准目录结构）
infomancli init my-awesome-project

# 进入项目
cd my-awesome-project

# 安装依赖并运行
pip install -e .
cp .env.example .env
infoman-serve run main:app --reload
```

访问 http://localhost:8000 查看运行效果！

### 手动安装

```bash
# Python >= 3.11
pip install -U infomankit

# 基础 Web 服务
pip install -U "infomankit[web]"

# 完整功能（使用 Tortoise ORM，100% 向前兼容）
pip install -U "infomankit[full]"

# 完整功能增强版（同时支持 Tortoise + SQLAlchemy）
pip install -U "infomankit[full-enhanced]"
```

常用 extra 组合：

| Extra          | 说明                             |
|----------------|--------------------------------|
| `web`          | FastAPI/Granian/orjson         |
| `database`     | Tortoise ORM（默认）             |
| `database-pro` | SQLAlchemy 2.0（高性能）          |
| `cache`        | Redis + fastapi-cache2        |
| `llm`          | Litellm                        |
| `vector`       | Qdrant                         |
| `messaging`    | NATS                           |
| `full`         | 完整功能（使用 Tortoise）            |
| `full-pro`     | 完整功能增强版（Tortoise + SQLAlchemy） |

本地开发推荐：

```bash
git clone https://github.com/yourusername/infoman-pykit.git
cd infomankit
pip install -e ".[dev,full]"   # 安装所有依赖和 lint/test 工具
```

## 快速上手

### 1. 配置环境变量
创建 `.env.dev`，并设置 `ENV=dev` (默认 dev)。可根据 `infoman/config/config.py` 填写常用变量：

```bash
APP_NAME=Infoman Service
APP_HOST=0.0.0.0
APP_PORT=8808
MYSQL_HOST=127.0.0.1
MYSQL_DB=infoman
MYSQL_USER=root
MYSQL_PASSWORD=secret
REDIS_HOST=127.0.0.1
QDRANT_HOST=127.0.0.1
LLM_PROXY=litellm_proxy
JWT_SECRET_KEY=change-me
```

运行时会依次加载 `.env` 与 `.env.{ENV}`，缺省值可在 `config.py` 中找到。

### 2. 启动 FastAPI 服务
```bash
export ENV=dev
uvicorn infoman.service.app:application --host ${APP_HOST:-0.0.0.0} --port ${APP_PORT:-8808} --reload
# or
python -m infoman.service.launch --mode gunicorn
```

应用启动后默认提供：
- `/api/health`：健康检查，返回 `{code:200}`。
- `/api/monitor`：进程 & 系统指标、环境信息。
- 启动事件中会自动注册 MySQL、Redis 缓存、NATS、Qdrant 等（根据配置是否填写）。

### 3. 调用 LLM
```python
import asyncio
from infoman.llm import LLM

async def main():
    resp = await LLM.ask(
        model="gpt-4o-mini",
        prompt="请用一句话介绍 infoman-pykit。",
        system_prompt="You are a concise assistant."
    )
    if resp.success:
        print(resp.content, resp.total_tokens)

asyncio.run(main())
```

- `LLM.ask/chat/stream` 会自动补全 `LLM_PROXY` 前缀并返回 token 统计。
- `LLM.quick_*` 返回字符串，`LLM.translate/summarize/code_review` 内置常用 system prompt。

### 4. 使用 Redis 缓存装饰器
```python
from pydantic import BaseModel
from infoman.service.utils.cache import redis_cache

class ConfigSchema(BaseModel):
    key: str
    value: str

class ConfigService:
    @redis_cache(prefix="config", ttl=600)
    async def get_config(self, request, key: str) -> ConfigSchema:
        # request.app.state.redis_client 将被装饰器自动读取
        ...
```

返回值可以是 `BaseModel`、`list[BaseModel]` 或普通 `dict`，装饰器会自动序列化/反序列化。

### 5. 消息队列与事件路由

```python
from infoman.service.infrastructure.mq.nats import event_router


@event_router.on("topic.user.created", queue="worker")
async def handle_user_created(msg, nats_cli):
    payload = msg.data.decode()
    ...

# 启动时在 startup 事件中执行：
# await event_router.register(app.state.nats_client)
```

`NATSClient` 支持 `publish/request/subscribe/close`，并在 `events.startup` 中自动连接（配置 `NATS_SERVER` 后生效）。

## 日志与中间件
- `infoman.utils.log.logger` 基于 Loguru，自动创建多种文件（all/info/error/debug）并支持 JSON 日志、请求上下文（RequestID）。
- `LoggingMiddleware`：记录请求耗时、客户端信息；`RequestIDMiddleware` 为每次请求注入 `X-Request-ID`。
- `RateLimitMiddleware`：IP/用户/路径多策略限流，内存或 Redis 持久化。
- `BaseMiddleware` 为自定义中间件提供 session / 处理耗时写入示例。

## 统一错误与响应
- `infoman.service.exception.error` 定义系统、请求、数据库、业务、安全、外部服务等错误码枚举，可中英文提示。
- `AppException` + `handler.py` 将数据库、Pydantic、HTTP 异常统一转换为 `{code, message, details}`。
- `infoman.service.core.response.success/failed` 提供标准响应结构。

## 更多工具箱
- **装饰器**：`retry`(支持 async/sync 指数退避)、`cache`(内存缓存)、`timing`(执行耗时)。
- **加密**：AES(自动填充/随机 IV)、RSA(4096/自定义序列化)。
- **HTTP Client**：`HttpAsyncClient` 支持表单/JSON/文件上传，返回 `HttpResult`。
- **文本处理**：`utils.text.extractor.extract_json_from_string` 可从非结构化文本中提取 JSON。
- **通知**：`notification.feishu.RobotManager` 发送飞书机器人消息。
- **Embedding 配置**：`service.models.type.embed` 统一管理不同向量模型的维度/长度、集合命名。

## 配置清单速查

| 分类         | 重点变量 |
|--------------|----------|
| 应用         | `APP_NAME`, `APP_HOST`, `APP_PORT`, `APP_BASE_URI`, `APP_DEBUG` |
| 安全         | `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`, `OAUTH2_REDIRECT_URL` |
| 数据库       | `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DB`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_TABLE_MODELS` |
| 缓存 / Redis | `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_PASSWORD` |
| 向量数据库   | `QDRANT_HOST`/`API_KEY`/`HTTP_PORT`/`GRPC_PORT`、`MILVUS_HOST` 等（Milvus 需实现 `AsyncMilvusClient`） |
| MQ           | `NATS_SERVER`（逗号分隔多实例）, `NATS_NAME` |
| LLM          | `LLM_PROXY`（litellm 代理地址） |
| 日志         | `LOG_LEVEL`, `LOG_FORMAT`, `LOG_DIR`, `LOG_RETENTION`, `LOG_ENABLE_*` |

## 开发 & 测试
```bash
# Lint / 格式化
ruff check infoman
black infoman
isort infoman

# 类型检查
mypy infoman

# 测试
pytest
```

## 🔀 ORM 选择指南

从 v0.3.0 开始，infomankit 支持两种 ORM：

### Tortoise ORM（默认）
**适合**：简单 CRUD、快速开发、学习成本低
```python
from infoman.service.models.base import TimestampMixin
from tortoise import fields

class User(TimestampMixin):
    name = fields.CharField(max_length=100)

# 直接使用
user = await User.create(name="Alice")
```

### SQLAlchemy 2.0（高性能）
**适合**：复杂查询、高性能需求、工业级项目
```python
from infoman.service.models.base import AlchemyBase, AlchemyTimestampMixin
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

class User(AlchemyBase, AlchemyTimestampMixin):
    __tablename__ = "users"
    name: Mapped[str] = mapped_column(String(100))

# 使用仓储模式
from infoman.service.models.base import create_repository
user_repo = create_repository(User)
user = await user_repo.create(name="Alice")
```

**详细迁移指南**: 👉 [doc/MIGRATION_TO_SQLALCHEMY.md](./doc/MIGRATION_TO_SQLALCHEMY.md)

---

## 📊 性能测试模块

infomankit 内置了标准化的性能测试工具，支持定制化接口测试和精美的 HTML 报告生成。

### 核心特性

- **标准化评估**：内置 4 种接口类型（fast/normal/complex/heavy）的性能标准
- **定制化配置**：支持 YAML 配置文件，灵活定义测试用例
- **高并发测试**：基于 asyncio 的异步并发执行
- **详细统计**：P50/P95/P99 响应时间、吞吐量、成功率等指标
- **精美报告**：自动生成响应式 HTML 报告，色彩分级展示
- **认证支持**：Bearer Token、Basic Auth 等多种认证方式

### 快速开始

#### 1. 创建配置文件

```yaml
# performance-test.yaml
project_name: "My API"
base_url: "http://localhost:8000"

# 并发配置
concurrent_users: 50
duration: 60  # 秒

# 测试用例
test_cases:
  - name: "健康检查"
    url: "/api/health"
    method: "GET"
    interface_type: "fast"

  - name: "用户列表"
    url: "/api/v1/users"
    method: "GET"
    interface_type: "normal"
    params:
      page: 1
      page_size: 20
```

#### 2. 运行测试

```bash
# 使用 Python 代码
python -c "
import asyncio
from infoman.performance import TestConfig, PerformanceTestRunner, HTMLReporter

async def test():
    config = TestConfig.from_yaml('performance-test.yaml')
    runner = PerformanceTestRunner(config)
    results = await runner.run()

    reporter = HTMLReporter(config)
    reporter.generate(results)

asyncio.run(test())
"

# 或使用 Makefile
make perf-test
make perf-test-api
make perf-test-stress
```

#### 3. 查看报告

测试完成后会生成精美的 HTML 报告，包含：
- 汇总指标（总请求数、成功率、平均响应时间、吞吐量）
- 每个接口的详细统计
- 响应时间百分位（P50/P95/P99）
- 性能评级和优化建议
- 错误信息汇总

### 性能标准

模块内置 4 种接口类型的标准：

| 接口类型 | 优秀 | 良好 | 可接受 | 较差 |
|---------|------|------|--------|------|
| **快速接口** (fast) | <10ms | <30ms | <50ms | <100ms |
| **一般接口** (normal) | <50ms | <100ms | <200ms | <500ms |
| **复杂接口** (complex) | <100ms | <200ms | <500ms | <1s |
| **重型接口** (heavy) | <200ms | <500ms | <1s | <3s |

### 更多文档

- 完整文档：[infoman/performance/README.md](./infoman/performance/README.md)
- 配置示例：[examples/performance/](./examples/performance/)
- 高级用法：[examples/performance/advanced_example.py](./examples/performance/advanced_example.py)

---

## 🛠️ CLI 脚手架工具

infomankit 提供了 `infomancli` 命令行工具,帮助你快速生成标准化的项目结构。

### 基本用法

```bash
# 交互式创建项目
infomancli init

# 直接指定项目名
infomancli init my-project

# 在指定目录创建
infomancli init my-project --dir /path/to/workspace
```

### 生成的项目结构

生成的项目遵循 `infoman/service` 的标准架构:

```
my-project/
├── .env.example          # 环境变量模板
├── .gitignore
├── README.md
├── main.py               # FastAPI 应用入口
├── pyproject.toml
│
├── core/                 # 核心业务逻辑
│   ├── auth.py          # 认证授权
│   └── response.py      # 标准响应模型
├── routers/              # API 路由
├── models/               # 数据模型
│   ├── entity/          # 数据库实体 (ORM)
│   ├── dto/             # 数据传输对象
│   └── schemas/         # Pydantic 验证模式
├── repository/           # 数据访问层
├── services/             # 业务逻辑服务
├── exception/            # 自定义异常
├── middleware/           # 自定义中间件
├── infrastructure/       # 基础设施
│   ├── database/        # 数据库连接
│   └── cache/           # 缓存管理
└── utils/                # 工具函数
    ├── cache/
    └── parse/
```

### 快速体验

```bash
# 1. 创建项目
infomancli init demo-api

# 2. 进入并安装
cd demo-api
pip install -e .

# 3. 启动服务
cp .env.example .env
infoman-serve run main:app --reload

# 4. 访问 API 文档
open http://localhost:8000/docs
```

生成的项目包含:
- ✅ 完整的项目结构
- ✅ FastAPI 应用框架
- ✅ 环境变量配置
- ✅ 健康检查端点
- ✅ Git 配置
- ✅ 开发文档

## License
MIT License © Infoman Contributors
