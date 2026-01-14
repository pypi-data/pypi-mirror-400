# 性能测试示例

本目录包含了 Infomankit 性能测试模块的完整示例和配置文件。

## 文件说明

### 配置文件

- **`basic-test.yaml`** - 基础性能测试配置
  - 10 并发用户，30秒快速测试
  - 适用于开发阶段快速验证

- **`rest-api-test.yaml`** - REST API 完整测试配置
  - 50 并发用户，60秒测试
  - 覆盖完整的 CRUD 操作
  - 包含认证配置示例

- **`stress-test.yaml`** - 高压力测试配置
  - 200 并发用户，5分钟持续测试
  - 适用于生产环境压测

### 示例脚本

- **`run_test.py`** - 简单的测试运行脚本
  - 展示基本用法
  - 自动生成 HTML 报告

- **`advanced_example.py`** - 高级用法示例
  - 编程方式创建配置
  - 多环境测试
  - 自定义性能标准
  - 条件性测试
  - 结果分析

## 快速开始

### 1. 运行基础测试

```bash
# 使用 Python 脚本
python run_test.py basic-test.yaml

# 使用 Makefile
make perf-test
```

### 2. 运行 REST API 测试

修改 `rest-api-test.yaml` 中的配置：

```yaml
base_url: "http://your-api-server:8000"
auth_token: "your-actual-token"
```

然后运行：

```bash
python run_test.py rest-api-test.yaml
# 或
make perf-test-api
```

### 3. 运行压力测试

⚠️ 注意：压力测试会产生高负载，请确保在测试环境运行

```bash
python run_test.py stress-test.yaml
# 或
make perf-test-stress
```

### 4. 使用 CLI 工具

```bash
# 运行测试
python -m infoman.performance.cli run -c basic-test.yaml

# 生成示例配置
python -m infoman.performance.cli init my-test.yaml

# 查看性能标准
python -m infoman.performance.cli standards
```

## 高级示例

### 运行所有高级示例

```bash
python advanced_example.py
```

### 单独运行某个示例

编辑 `advanced_example.py`，在 `main()` 函数中注释掉其他示例：

```python
async def main():
    # 只运行示例 1
    await example_1_programmatic_config()

    # 其他示例注释掉
    # await example_2_multi_environment()
    # example_3_custom_standards()
```

## 自定义测试

### 创建新的测试配置

1. 复制 `basic-test.yaml` 作为模板
2. 修改配置参数
3. 添加你的测试用例

```yaml
test_cases:
  - name: "你的测试名称"
    url: "/api/your-endpoint"
    method: "GET"
    interface_type: "normal"  # fast/normal/complex/heavy
    params:
      param1: value1
    timeout: 30
```

### 编程方式创建测试

参考 `advanced_example.py` 中的 `example_1_programmatic_config()`

```python
from infoman.performance import TestConfig, APITestCase

config = TestConfig(
    project_name="My Test",
    base_url="http://localhost:8000",
    concurrent_users=20,
    duration=60,
)

config.add_test_case(
    APITestCase(
        name="My API",
        url="/api/test",
        method="GET",
        interface_type="normal",
    )
)
```

## 测试报告

所有测试完成后会生成 HTML 报告：

- `basic-performance-report.html` - 基础测试报告
- `rest-api-performance-report.html` - REST API 测试报告
- `stress-test-report.html` - 压力测试报告

在浏览器中打开查看详细结果：

```bash
open basic-performance-report.html  # macOS
xdg-open basic-performance-report.html  # Linux
start basic-performance-report.html  # Windows
```

## 常见问题

### Q: 如何修改并发数？

A: 在 YAML 配置文件中修改 `concurrent_users`，或使用命令行参数：

```bash
python -m infoman.performance.cli run -c test.yaml -u 100
```

### Q: 如何增加测试时长？

A: 修改配置文件中的 `duration`，或使用命令行参数：

```bash
python -m infoman.performance.cli run -c test.yaml -d 300
```

### Q: 如何添加认证？

A: 在配置文件中添加：

```yaml
auth_type: "bearer"
auth_token: "your-token-here"
```

或使用 Basic Auth：

```yaml
auth_type: "basic"
auth_username: "admin"
auth_password: "password"
```

### Q: 如何禁用某个测试用例？

A: 设置 `enabled: false`：

```yaml
test_cases:
  - name: "临时禁用的测试"
    url: "/api/test"
    enabled: false
```

### Q: 如何查看详细日志？

A: 使用 `-v` 参数：

```bash
python -m infoman.performance.cli run -c test.yaml -v
```

## 最佳实践

1. **从小开始**: 先用低并发（10用户）测试，确认配置正确
2. **逐步增加**: 逐步提高并发数，观察系统表现
3. **设置合理的超时**: 根据接口类型设置适当的 `timeout`
4. **思考时间**: 设置 `think_time` 模拟真实用户行为
5. **监控资源**: 测试时监控服务器 CPU、内存、网络等资源

## 更多文档

查看完整文档：[infoman/performance/README.md](../../infoman/performance/README.md)
