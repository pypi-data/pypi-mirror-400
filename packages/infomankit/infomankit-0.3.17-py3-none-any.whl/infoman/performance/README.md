# 性能测试模块

Infomankit 性能测试模块提供标准化的 API 性能测试工具，支持定制化配置和精美的 HTML 报告生成。

## 特性

- 📊 **标准化性能评估**: 内置 4 种接口类型的性能标准（fast/normal/complex/heavy）
- 🎯 **定制化测试配置**: 支持 YAML 配置文件，灵活定义测试用例
- ⚡ **高并发测试**: 基于 asyncio 和 httpx 的异步并发测试
- 📈 **详细统计分析**: P50/P95/P99 响应时间、吞吐量、成功率等指标
- 🎨 **精美 HTML 报告**: 响应式设计、色彩分级、打印友好
- 🔐 **认证支持**: Bearer Token、Basic Auth 等多种认证方式

## 快速开始

### 1. 创建配置文件

创建 `performance-test.yaml`:

```yaml
project_name: "My API"
base_url: "http://localhost:8000"

# 并发配置
concurrent_users: 50
duration: 60  # 秒
spawn_rate: 5  # 每秒启动用户数

# 认证（可选）
auth_type: "bearer"
auth_token: "your-token-here"

# 测试用例
test_cases:
  - name: "健康检查"
    url: "/api/health"
    method: "GET"
    interface_type: "fast"
    description: "健康检查接口"

  - name: "用户列表"
    url: "/api/v1/users"
    method: "GET"
    interface_type: "normal"
    params:
      page: 1
      page_size: 20

  - name: "创建用户"
    url: "/api/v1/users"
    method: "POST"
    interface_type: "normal"
    json:
      username: "testuser"
      email: "test@example.com"

  - name: "复杂查询"
    url: "/api/v1/analytics"
    method: "GET"
    interface_type: "complex"
    params:
      start_date: "2024-01-01"
      end_date: "2024-12-31"
      group_by: "month"
```

### 2. 运行测试

使用 Python 代码运行测试:

```python
import asyncio
from infoman.performance import TestConfig, PerformanceTestRunner, HTMLReporter

async def main():
    # 加载配置
    config = TestConfig.from_yaml("performance-test.yaml")

    # 运行测试
    runner = PerformanceTestRunner(config)
    results = await runner.run()

    # 生成 HTML 报告
    reporter = HTMLReporter(config)
    report_path = reporter.generate(results)
    print(f"报告已生成: {report_path}")

if __name__ == "__main__":
    asyncio.run(main())
```

或使用命令行工具:

```bash
infoman perf-test -c performance-test.yaml
```

### 3. 查看报告

在浏览器中打开生成的 `performance-report.html` 查看详细结果。

## 性能标准

模块内置了 4 种接口类型的性能标准：

### 快速接口 (fast)
适用于：健康检查、静态资源、简单查询

- 优秀: < 10ms
- 良好: < 30ms
- 可接受: < 50ms
- 较差: < 100ms
- 严重: ≥ 100ms

### 一般接口 (normal)
适用于：列表查询、单条数据获取、简单 CRUD

- 优秀: < 50ms
- 良好: < 100ms
- 可接受: < 200ms
- 较差: < 500ms
- 严重: ≥ 500ms

### 复杂接口 (complex)
适用于：复杂查询、多表关联、数据聚合

- 优秀: < 100ms
- 良好: < 200ms
- 可接受: < 500ms
- 较差: < 1s
- 严重: ≥ 1s

### 重型接口 (heavy)
适用于：文件处理、批量操作、报表生成

- 优秀: < 200ms
- 良好: < 500ms
- 可接受: < 1s
- 较差: < 3s
- 严重: ≥ 3s

## 配置详解

### 基础配置

```yaml
project_name: "项目名称"
base_url: "http://localhost:8000"
```

### 并发配置

```yaml
concurrent_users: 50    # 并发用户数
duration: 60           # 测试持续时间（秒）
spawn_rate: 5          # 每秒启动用户数
think_time_min: 1      # 最小思考时间（秒）
think_time_max: 3      # 最大思考时间（秒）
```

### 认证配置

#### Bearer Token

```yaml
auth_type: "bearer"
auth_token: "your-jwt-token"
```

#### Basic Auth

```yaml
auth_type: "basic"
auth_username: "admin"
auth_password: "password"
```

### 全局请求头

```yaml
global_headers:
  User-Agent: "My-Test/1.0"
  Accept: "application/json"
  X-Custom-Header: "value"
```

### 测试用例配置

#### GET 请求

```yaml
test_cases:
  - name: "获取用户列表"
    url: "/api/v1/users"
    method: "GET"
    interface_type: "normal"
    params:
      page: 1
      page_size: 20
    timeout: 30
```

#### POST 请求

```yaml
test_cases:
  - name: "创建订单"
    url: "/api/v1/orders"
    method: "POST"
    interface_type: "normal"
    json:
      product_id: 123
      quantity: 2
    headers:
      Content-Type: "application/json"
```

#### 表单提交

```yaml
test_cases:
  - name: "上传文件"
    url: "/api/v1/upload"
    method: "POST"
    interface_type: "heavy"
    data:
      filename: "test.txt"
```

#### 禁用测试用例

```yaml
test_cases:
  - name: "临时禁用的测试"
    url: "/api/test"
    method: "GET"
    enabled: false  # 不会执行此测试
```

### 报告配置

```yaml
report_title: "API 性能测试报告"
report_output: "./reports/performance-report.html"
```

## 编程 API

### 配置管理

```python
from infoman.performance import TestConfig, APITestCase

# 从 YAML 加载
config = TestConfig.from_yaml("test.yaml")

# 保存为 YAML
config.to_yaml("output.yaml")

# 动态添加测试用例
config.add_test_case(
    APITestCase(
        name="新测试",
        url="/api/test",
        method="GET",
        interface_type="fast"
    )
)

# 获取启用的测试用例
enabled_cases = config.get_enabled_test_cases()
```

### 运行测试

```python
from infoman.performance import PerformanceTestRunner

runner = PerformanceTestRunner(config)
results = await runner.run()

# 访问结果
for name, result in results.items():
    print(f"测试: {name}")
    print(f"  总请求: {result.total_requests}")
    print(f"  成功率: {result.success_rate:.2f}%")
    print(f"  平均响应时间: {result.avg_response_time:.2f}ms")
    print(f"  P95: {result.p95_response_time:.2f}ms")
    print(f"  吞吐量: {result.throughput:.2f} req/s")
    print(f"  综合评级: {result.overall_level}")
```

### 生成报告

```python
from infoman.performance import HTMLReporter

reporter = HTMLReporter(config)
report_path = reporter.generate(
    results=results,
    output_path="custom-report.html"
)
```

### 性能评估

```python
from infoman.performance import PerformanceStandards, StandardLevel

# 评估响应时间
level = PerformanceStandards.evaluate_response_time(
    response_time=120,  # 毫秒
    interface_type="normal"
)
print(level)  # StandardLevel.GOOD

# 评估吞吐量
level = PerformanceStandards.evaluate_throughput(
    throughput=300,  # req/s
    interface_type="normal"
)

# 评估成功率
level = PerformanceStandards.evaluate_success_rate(99.5)

# 获取标签和建议
label = PerformanceStandards.get_level_label(level)
recommendation = PerformanceStandards.get_recommendation(level)
```

## 高级用法

### 自定义性能标准

```python
from infoman.performance.standards import PerformanceStandards, PerformanceThreshold

# 添加自定义接口类型
PerformanceStandards.STANDARDS["custom"] = PerformanceThreshold(
    excellent=80,
    good=150,
    acceptable=300,
    poor=800
)

# 使用自定义类型
level = PerformanceStandards.evaluate_response_time(
    response_time=200,
    interface_type="custom"
)
```

### 多环境测试

```python
environments = {
    "dev": "http://dev.example.com",
    "staging": "http://staging.example.com",
    "prod": "http://prod.example.com"
}

for env_name, base_url in environments.items():
    config = TestConfig.from_yaml("test.yaml")
    config.base_url = base_url
    config.report_output = f"report-{env_name}.html"

    runner = PerformanceTestRunner(config)
    results = await runner.run()

    reporter = HTMLReporter(config)
    reporter.generate(results)
```

### 集成到 CI/CD

```yaml
# .github/workflows/performance.yml
name: Performance Test

on:
  schedule:
    - cron: '0 0 * * *'  # 每天运行

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Performance Test
        run: |
          pip install infomankit
          infoman perf-test -c performance-test.yaml

      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: performance-report
          path: performance-report.html
```

## 最佳实践

### 1. 合理设置并发数

根据服务器资源调整并发用户数：

- 开发环境: 10-20
- 测试环境: 50-100
- 生产环境压测: 100-500

### 2. 设置思考时间

模拟真实用户行为，避免过度压测：

```yaml
think_time_min: 2
think_time_max: 5
```

### 3. 分类测试用例

按接口类型正确分类，获得准确的性能评估：

```yaml
test_cases:
  - name: "健康检查"
    interface_type: "fast"  # 简单接口

  - name: "用户列表"
    interface_type: "normal"  # 一般接口

  - name: "数据分析"
    interface_type: "complex"  # 复杂接口

  - name: "导出报表"
    interface_type: "heavy"  # 重型接口
```

### 4. 逐步增加负载

使用 `spawn_rate` 控制用户启动速率，避免瞬间冲击：

```yaml
concurrent_users: 100
spawn_rate: 10  # 10秒内逐步启动所有用户
```

### 5. 监控服务器资源

在测试期间监控：
- CPU 使用率
- 内存使用率
- 网络带宽
- 数据库连接数

## 故障排查

### 连接失败

```
错误: 连接失败
```

**解决方案**:
- 检查 `base_url` 是否正确
- 确认服务是否运行
- 检查网络连接和防火墙

### 超时错误

```
错误: 请求超时
```

**解决方案**:
- 增加 `timeout` 配置
- 检查接口性能
- 降低并发数

### 认证失败

```
错误: HTTP 401: Unauthorized
```

**解决方案**:
- 检查 `auth_token` 是否有效
- 确认认证方式配置正确
- 检查 token 是否过期

## 示例场景

### 场景 1: REST API 性能测试

```yaml
project_name: "REST API Performance Test"
base_url: "https://api.example.com"
concurrent_users: 100
duration: 300  # 5分钟

test_cases:
  - name: "列表查询"
    url: "/api/v1/items"
    method: "GET"
    interface_type: "normal"

  - name: "详情查询"
    url: "/api/v1/items/1"
    method: "GET"
    interface_type: "fast"

  - name: "创建记录"
    url: "/api/v1/items"
    method: "POST"
    interface_type: "normal"
    json:
      name: "Test Item"
```

### 场景 2: 微服务压力测试

```yaml
project_name: "Microservices Stress Test"
base_url: "http://gateway.local"
concurrent_users: 500
duration: 600  # 10分钟
spawn_rate: 50

test_cases:
  - name: "用户服务 - 登录"
    url: "/user-service/api/login"
    method: "POST"
    interface_type: "normal"

  - name: "订单服务 - 创建订单"
    url: "/order-service/api/orders"
    method: "POST"
    interface_type: "complex"

  - name: "支付服务 - 支付"
    url: "/payment-service/api/pay"
    method: "POST"
    interface_type: "heavy"
```

### 场景 3: 搜索性能测试

```yaml
project_name: "Search Performance Test"
base_url: "https://search.example.com"
concurrent_users: 200
duration: 120

test_cases:
  - name: "简单搜索"
    url: "/api/search"
    method: "GET"
    interface_type: "normal"
    params:
      q: "test"

  - name: "高级搜索"
    url: "/api/search/advanced"
    method: "POST"
    interface_type: "complex"
    json:
      query: "test"
      filters:
        category: "tech"
        date_range: "2024"
```

## 相关链接

- [性能标准定义](./standards.py)
- [配置模型](./config.py)
- [测试运行器](./runner.py)
- [报告生成器](./reporter.py)

## 许可证

MIT License - 详见项目根目录 LICENSE 文件
