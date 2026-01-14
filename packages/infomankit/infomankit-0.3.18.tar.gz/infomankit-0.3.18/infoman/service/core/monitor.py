from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_client import Counter, Histogram, Gauge

# ===== 1. HTTP 指标（自动收集）=====
instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/health", "/metrics", "/doc", "/redoc", "/openapi.json"],
)

instrumentator.add(metrics.default())
instrumentator.add(metrics.request_size())
instrumentator.add(metrics.response_size())

# ===== 2. 业务指标（手动收集）=====

# 用户操作
user_operations = Counter(
    "user_operations_total", "Total user operations", ["operation_type", "status"]
)

# 数据库查询
db_query_duration = Histogram(
    "db_query_duration_seconds",
    "Database query duration",
    ["query_type"],
    buckets=[0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0],
)

# 缓存
cache_hits = Counter("cache_hits_total", "Cache hits", ["cache_type"])
cache_misses = Counter("cache_misses_total", "Cache misses", ["cache_type"])

# 连接数
active_db_connections = Gauge("active_db_connections", "Active database connections")
active_redis_connections = Gauge("active_redis_connections", "Active Redis connections")

# 队列
task_queue_length = Gauge("task_queue_length", "Task queue length")

# 在线用户
online_users = Gauge("online_users", "Online users count")

# ===== 3. 导出所有指标（方便使用）=====
__all__ = [
    "instrumentator",
    "user_operations",
    "db_query_duration",
    "cache_hits",
    "cache_misses",
    "active_db_connections",
    "active_redis_connections",
    "task_queue_length",
    "online_users",
]
