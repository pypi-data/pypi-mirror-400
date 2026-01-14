# Infomankit 测试套件

## 📋 概览

这是 Infomankit 项目的测试套件，包含单元测试、集成测试和端到端测试。

**当前覆盖率目标**: 85%+

## 🏗️ 测试结构

```
tests/
├── unit/                    # 单元测试（不需要外部依赖）
│   ├── test_encryption.py   # 加密模块测试
│   ├── test_decorators.py   # 装饰器测试
│   ├── test_hash.py         # 哈希工具测试
│   └── test_response.py     # 响应格式测试
│
├── integration/             # 集成测试（需要外部服务）
│   └── test_redis_cache.py  # Redis 集成测试
│
├── e2e/                     # 端到端测试
│   └── test_api_health.py   # API 健康检查测试
│
├── fixtures/                # 测试数据
├── helpers/                 # 测试辅助工具
└── conftest.py              # Pytest 配置和 fixtures
```

## 🚀 快速开始

### 安装依赖

```bash
# 安装测试依赖
pip install -e ".[dev]"

# 或使用 uv
uv pip install -e ".[dev]"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit

# 运行特定文件
pytest tests/unit/test_encryption.py

# 运行特定测试
pytest tests/unit/test_encryption.py::TestAESCipher::test_encrypt_decrypt_roundtrip

# 带覆盖率报告
pytest --cov=infoman --cov-report=html

# 详细输出
pytest -vv

# 快速测试（跳过集成测试）
pytest -m "not integration"
```

## 📊 测试标记

我们使用 pytest 标记来组织测试：

- `@pytest.mark.unit` - 单元测试（默认）
- `@pytest.mark.integration` - 集成测试（需要外部服务）
- `@pytest.mark.e2e` - 端到端测试
- `@pytest.mark.slow` - 慢速测试

### 按标记运行

```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 跳过慢速测试
pytest -m "not slow"

# 运行单元测试和 E2E 测试
pytest -m "unit or e2e"
```

## 🐳 运行集成测试

集成测试需要外部服务（Redis、MySQL、NATS 等）。

### 使用 Docker Compose

```bash
# 启动所有服务
docker compose up -d

# 运行集成测试
pytest -m integration

# 停止服务
docker compose down
```

### 手动启动服务

```bash
# Redis
docker run -d -p 6379:6379 redis:7-alpine

# MySQL
docker run -d -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=test \
  -e MYSQL_DATABASE=infoman \
  mysql:8.0

# NATS
docker run -d -p 4222:4222 -p 8222:8222 nats:latest -js -m 8222
```

## 📈 查看覆盖率

### 终端输出

```bash
pytest --cov=infoman --cov-report=term-missing
```

### HTML 报告

```bash
pytest --cov=infoman --cov-report=html

# 打开报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### XML 报告（CI 用）

```bash
pytest --cov=infoman --cov-report=xml
```

## 🔍 调试测试

### 进入 pdb 调试器

```bash
# 失败时进入 pdb
pytest --pdb

# 开始时就进入 pdb
pytest --trace
```

### 显示打印输出

```bash
pytest -s
```

### 只运行失败的测试

```bash
pytest --lf  # last failed
pytest --ff  # failed first
```

### 详细的失败信息

```bash
pytest -vv --tb=long
```

## ✍️ 编写测试

### 测试命名规范

```python
# 文件: test_<模块名>.py
# 类: Test<功能名>
# 函数: test_<具体测试内容>

class TestAESCipher:
    def test_encrypt_decrypt_roundtrip(self):
        """测试加解密往返"""
        pass

    def test_invalid_key_length(self):
        """测试无效密钥长度"""
        pass
```

### AAA 模式

```python
def test_example():
    # Arrange - 准备测试数据
    cipher = AESCipher(key=test_key)
    plaintext = "test"

    # Act - 执行操作
    encrypted = cipher.encrypt(plaintext)

    # Assert - 验证结果
    assert encrypted != plaintext
```

### 使用 Fixtures

```python
def test_with_fixture(aes_key):
    """使用预定义的 fixture"""
    cipher = AESCipher(key=aes_key)
    # ...
```

### 异步测试

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected
```

### 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
])
def test_upper(input, expected):
    assert input.upper() == expected
```

### Mock 外部依赖

```python
from unittest.mock import patch, AsyncMock

@patch("infoman.llm.llm.acompletion")
async def test_llm(mock_completion):
    mock_completion.return_value = mock_response
    result = await LLM.ask("test")
    assert result.success
```

## 🎯 覆盖率目标

### 按模块

| 模块 | 目标 | 当前 | 状态 |
|-----|------|------|------|
| `utils/encryption/` | 95% | - | 🔄 进行中 |
| `utils/decorators/` | 90% | - | 🔄 进行中 |
| `utils/hash/` | 90% | - | 🔄 进行中 |
| `service/core/` | 85% | - | ⏳ 待开始 |
| `llm/` | 80% | - | ⏳ 待开始 |

**总体目标**: 85%+

## 📝 CI/CD 集成

### GitHub Actions

测试在以下情况自动运行：

- Push 到 main 分支
- Pull Request
- 每日定时任务

### 本地预提交检查

```bash
# 安装 pre-commit hooks
pre-commit install

# 手动运行
pre-commit run --all-files
```

## 🐛 常见问题

### Q: 测试运行很慢

A: 使用 `-m "not integration"` 跳过集成测试，或使用 `-n auto` 并行运行。

### Q: Redis 连接失败

A: 确保 Redis 在 localhost:6379 运行，或使用 docker compose。

### Q: Import 错误

A: 确保已安装项目：`pip install -e ".[dev]"`

### Q: 覆盖率不准确

A: 清理缓存：`pytest --cache-clear --cov=infoman`

## 📚 相关文档

- [完整测试指南](/doc/optimization_test.md)
- [Pytest 文档](https://docs.pytest.org/)
- [Coverage.py 文档](https://coverage.readthedocs.io/)

## 🤝 贡献

添加新测试时：

1. 遵循现有的命名和组织规范
2. 确保测试是独立的（不依赖执行顺序）
3. 添加清晰的 docstring
4. 测试通过后再提交
5. 保持或提高覆盖率

## 📧 支持

遇到问题？

- 查看 `/doc/optimization_test.md` 详细指南
- 提交 Issue
- 联系维护者
