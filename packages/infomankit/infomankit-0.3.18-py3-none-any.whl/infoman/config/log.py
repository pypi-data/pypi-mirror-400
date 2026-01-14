"""
日志系统配置模块
支持：本地文件 + Loki 远程推送 + 动态配置
"""
from typing import Literal, Optional, Dict, Any
from pathlib import Path
from pydantic import Field, field_validator, model_validator, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogConfig(BaseSettings):
    """
    日志系统配置

    设计原则：
    1. 默认值适合开发环境
    2. 生产环境通过环境变量覆盖
    3. 自动根据 ENV 调整配置
    4. 所有配置都有合理的约束
    """
    # ========== 环境 ==========
    ENV: Literal["dev", "test", "prod"] = Field(default="dev")

    # =================================================================
    # 日志级别配置
    # =================================================================

    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="全局日志级别"
    )

    LOG_LEVEL_CONSOLE: Optional[Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]] = Field(
        default=None,
        description="控制台日志级别（None 则使用 LOG_LEVEL）"
    )

    LOG_LEVEL_FILE: Optional[Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]] = Field(
        default=None,
        description="文件日志级别（None 则使用 LOG_LEVEL）"
    )

    LOG_LEVEL_LOKI: Optional[Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]] = Field(
        default=None,
        description="Loki 日志级别（None 则使用 LOG_LEVEL）"
    )

    # =================================================================
    # 日志输出控制
    # =================================================================

    LOG_ENABLE_CONSOLE: bool = Field(
        default=True,
        description="启用控制台输出"
    )

    LOG_ENABLE_FILE: bool = Field(
        default=True,
        description="启用文件输出"
    )

    LOG_ENABLE_LOKI: bool = Field(
        default=False,
        description="启用 Loki 远程推送"
    )

    # =================================================================
    # 文件存储配置
    # =================================================================

    LOG_DIR: Path = Field(
        default=Path("./logs"),
        description="日志根目录"
    )

    LOG_RETENTION: str = Field(
        default="7 days",
        description="日志保留时间（格式: '7 days', '2 weeks', '1 month', '90 days'）"
    )

    LOG_ROTATION: str = Field(
        default="200 MB",
        description="日志轮转大小（格式: '100 MB', '500 MB', '1 GB'）"
    )

    LOG_COMPRESSION: Literal["zip", "gz", "bz2", "xz", None] = Field(
        default="zip",
        description="日志压缩格式（None 表示不压缩）"
    )

    LOG_FILE_ENCODING: str = Field(
        default="utf-8",
        description="日志文件编码"
    )

    # =================================================================
    # 日志格式配置
    # =================================================================

    LOG_FORMAT: Literal["simple", "detailed", "debug", "json", "pro"] = Field(
        default="detailed",
        description="日志格式预设"
    )

    LOG_ENABLE_CONSOLE_COLOR: bool = Field(
        default=True,
        description="启用控制台颜色输出"
    )

    LOG_RECORD_CALLER: bool = Field(
        default=True,
        description="记录调用者信息（文件名、函数名、行号）"
    )

    LOG_RECORD_PROCESS: bool = Field(
        default=False,
        description="记录进程信息（进程 ID、线程 ID）"
    )

    LOG_ENABLE_BACKTRACE: bool = Field(
        default=True,
        description="启用异常回溯（显示完整调用栈）"
    )

    LOG_ENABLE_DIAGNOSE: bool = Field(
        default=True,
        description="启用诊断模式（显示变量值）"
    )

    # =================================================================
    # 上下文配置
    # =================================================================

    LOG_ENABLE_CONTEXT: bool = Field(
        default=True,
        description="启用上下文管理（request_id, user_id 等）"
    )

    LOG_CONTEXT_FIELDS: list[str] = Field(
        default=["request_id", "user_id", "trace_id", "span_id"],
        description="默认上下文字段"
    )

    # =================================================================
    # 性能配置
    # =================================================================

    LOG_ENABLE_ASYNC: bool = Field(
        default=True,
        description="启用异步日志写入（提升性能）"
    )

    LOG_QUEUE_SIZE: int = Field(
        default=1000,
        ge=100,
        le=100000,
        description="异步队列大小（100-100000）"
    )

    # =================================================================
    # Loki 推送配置
    # =================================================================

    LOG_LOKI_URL: str = Field(
        default="http://loki:3100",
        description="Loki 服务地址"
    )

    LOG_LOKI_BATCH_SIZE: int = Field(
        default=100,
        ge=10,
        le=1000,
        description="批量推送大小（10-1000）"
    )

    LOG_LOKI_FLUSH_INTERVAL: float = Field(
        default=5.0,
        ge=1.0,
        le=60.0,
        description="刷新间隔（1-60 秒）"
    )

    LOG_LOKI_TIMEOUT: float = Field(
        default=10.0,
        ge=1.0,
        le=30.0,
        description="推送超时（1-30 秒）"
    )

    LOG_LOKI_RETRY_TIMES: int = Field(
        default=3,
        ge=0,
        le=10,
        description="重试次数（0-10）"
    )

    LOG_LOKI_RETRY_BACKOFF: float = Field(
        default=2.0,
        ge=1.0,
        le=10.0,
        description="重试退避系数（1.0-10.0）"
    )

    LOG_LOKI_LABELS: Dict[str, str] = Field(
        default_factory=dict,
        description="自定义 Loki Labels（会与默认 labels 合并）"
    )

    LOG_LOKI_ENABLE_FALLBACK: bool = Field(
        default=True,
        description="启用降级策略（Loki 失败时写备份文件）"
    )

    LOG_LOKI_FALLBACK_FILE: str = Field(
        default="loki_backup.log",
        description="Loki 备份文件名"
    )

    # =================================================================
    # 日志过滤配置
    # =================================================================

    LOG_FILTER_MODULES: list[str] = Field(
        default_factory=lambda: ["uvicorn.access", "uvicorn.error"],
        description="需要过滤的模块列表"
    )

    LOG_FILTER_KEYWORDS: list[str] = Field(
        default_factory=lambda: ["health_check", "heartbeat"],
        description="需要过滤的关键词列表"
    )

    LOG_ENABLE_RATE_LIMIT: bool = Field(
        default=False,
        description="启用日志速率限制（防止日志风暴）"
    )

    LOG_RATE_LIMIT_MESSAGES: int = Field(
        default=100,
        ge=10,
        le=10000,
        description="速率限制：每秒最多日志数（10-10000）"
    )

    # =================================================================
    # 敏感信息脱敏配置
    # =================================================================

    LOG_ENABLE_SANITIZE: bool = Field(
        default=True,
        description="启用敏感信息脱敏"
    )

    LOG_SANITIZE_FIELDS: list[str] = Field(
        default_factory=lambda: [
            "password", "token", "secret", "api_key", "credit_card",
            "ssn", "phone", "email", "access_token", "refresh_token"
        ],
        description="需要脱敏的字段名"
    )

    LOG_SANITIZE_PATTERN: str = Field(
        default="***REDACTED***",
        description="脱敏替换文本"
    )

    # =================================================================
    # 分级日志文件配置
    # =================================================================

    LOG_ENABLE_SPLIT_BY_LEVEL: bool = Field(
        default=True,
        description="按级别分割日志文件（info.log, error.log 等）"
    )

    LOG_ENABLE_DEBUG_FILE: bool = Field(
        default=False,
        description="启用 debug.log（仅开发环境推荐）"
    )

    LOG_ENABLE_ALL_FILE: bool = Field(
        default=True,
        description="启用 all.log（包含所有级别）"
    )

    # =================================================================
    # 监控和告警配置
    # =================================================================

    LOG_ENABLE_METRICS: bool = Field(
        default=False,
        description="启用日志指标统计（日志数量、错误率等）"
    )

    LOG_ERROR_THRESHOLD: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="错误日志阈值（超过后触发告警）"
    )

    LOG_ERROR_WINDOW: int = Field(
        default=60,
        ge=10,
        le=3600,
        description="错误统计窗口（秒）"
    )

    # =================================================================
    # 验证器
    # =================================================================

    @field_validator("LOG_DIR", mode="before")
    @classmethod
    def create_log_dir(cls, v) -> Path:
        """自动创建日志目录"""
        log_dir = Path(v)
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir

    @field_validator("LOG_LOKI_URL")
    @classmethod
    def validate_loki_url(cls, v: str) -> str:
        """验证并标准化 Loki URL"""
        if not v:
            return v

        # 补充协议
        if not v.startswith(("http://", "https://")):
            v = f"http://{v}"

        # 移除尾部斜杠
        v = v.rstrip("/")

        # 验证端口
        if ":" not in v.split("//")[1]:
            v = f"{v}:3100"  # 默认端口

        return v

    @field_validator("LOG_RETENTION")
    @classmethod
    def validate_retention(cls, v: str) -> str:
        """验证保留时间格式"""
        import re
        pattern = r'^\d+\s+(day|days|week|weeks|month|months)s?$'
        if not re.match(pattern, v, re.IGNORECASE):
            raise ValueError(
                f"LOG_RETENTION 格式错误: {v}，"
                f"正确格式: '7 days', '2 weeks', '1 month'"
            )
        return v

    @field_validator("LOG_ROTATION")
    @classmethod
    def validate_rotation(cls, v: str) -> str:
        """验证轮转大小格式"""
        import re
        pattern = r'^\d+\s+(MB|GB|KB)$'
        if not re.match(pattern, v, re.IGNORECASE):
            raise ValueError(
                f"LOG_ROTATION 格式错误: {v}，"
                f"正确格式: '100 MB', '1 GB'"
            )
        return v

    def model_post_init(self, __context):
        """初始化后处理（根据环境调整配置）"""

        # ========== 开发环境 ==========
        if self.ENV == "dev":
            self.LOG_LEVEL = "DEBUG"
            self.LOG_FORMAT = "simple"
            self.LOG_ENABLE_CONSOLE_COLOR = True
            self.LOG_ENABLE_BACKTRACE = True
            self.LOG_ENABLE_DIAGNOSE = True
            self.LOG_ENABLE_DEBUG_FILE = True
            self.LOG_RETENTION = "3 days"
            self.LOG_ENABLE_LOKI = False

        # ========== 测试环境 ==========
        elif self.ENV == "test":
            self.LOG_LEVEL = "INFO"
            self.LOG_FORMAT = "detailed"
            self.LOG_RETENTION = "7 days"

            if not self.LOG_ENABLE_LOKI:
                import warnings
                warnings.warn(
                    "测试环境建议启用 Loki: LOG_ENABLE_LOKI=true",
                    UserWarning
                )

        # ========== 预发布环境 ==========
        elif self.ENV == "staging":
            self.LOG_LEVEL = "INFO"
            self.LOG_FORMAT = "pro"
            self.LOG_ENABLE_CONSOLE_COLOR = False
            self.LOG_RETENTION = "14 days"

            if not self.LOG_ENABLE_LOKI:
                raise ValueError("预发布环境必须启用 Loki: LOG_ENABLE_LOKI=true")

        # ========== 生产环境 ==========
        elif self.ENV == "prod":
            if self.LOG_LEVEL == "DEBUG":
                self.LOG_LEVEL = "INFO"

            self.LOG_FORMAT = "json"
            self.LOG_ENABLE_CONSOLE_COLOR = False
            self.LOG_ENABLE_DIAGNOSE = False
            self.LOG_ENABLE_DEBUG_FILE = False

            if self.LOG_RETENTION == "7 days":
                self.LOG_RETENTION = "30 days"

            if self.LOG_ROTATION == "200 MB":
                self.LOG_ROTATION = "500 MB"

            # if not self.LOG_ENABLE_LOKI:
            #     raise ValueError("生产环境必须启用 Loki: LOG_ENABLE_LOKI=true")

            self.LOG_ENABLE_METRICS = True
            self.LOG_ENABLE_SANITIZE = True

        # 设置分级日志级别
        if self.LOG_LEVEL_CONSOLE is None:
            self.LOG_LEVEL_CONSOLE = self.LOG_LEVEL

        if self.LOG_LEVEL_FILE is None:
            self.LOG_LEVEL_FILE = self.LOG_LEVEL

        if self.LOG_LEVEL_LOKI is None:
            self.LOG_LEVEL_LOKI = "INFO" if self.LOG_LEVEL == "DEBUG" else self.LOG_LEVEL

        # 验证依赖
        if self.LOG_ENABLE_LOKI:
            try:
                import httpx
            except ImportError:
                raise ValueError(
                    "启用 Loki 需要安装 httpx: pip install httpx"
                )

        if self.LOG_ENABLE_ASYNC and self.LOG_QUEUE_SIZE < 100:
            import warnings
            warnings.warn(
                f"异步队列大小过小 ({self.LOG_QUEUE_SIZE})，建议至少 1000",
                UserWarning
            )

    @model_validator(mode='after')
    def validate_dependencies(self) -> 'LogConfig':
        """验证依赖关系"""

        # Loki 启用时，检查 httpx
        if self.LOG_ENABLE_LOKI:
            try:
                import httpx
            except ImportError:
                raise ValueError(
                    "启用 Loki 需要安装 httpx: pip install httpx"
                )

        # 异步日志启用时，队列大小必须合理
        if self.LOG_ENABLE_ASYNC and self.LOG_QUEUE_SIZE < 100:
            import warnings
            warnings.warn(
                f"异步队列大小过小 ({self.LOG_QUEUE_SIZE})，建议至少 1000",
                UserWarning
            )

        return self

    # =================================================================
    # 辅助方法
    # =================================================================

    def get_loki_labels(self) -> Dict[str, str]:
        """获取完整的 Loki Labels"""
        import socket

        default_labels = {
            "app": self.APP_NAME,
            "env": self.ENV,
            "hostname": socket.gethostname(),
        }

        # 合并自定义 labels
        return {**default_labels, **self.LOG_LOKI_LABELS}

    def get_log_file_path(self, log_type: str) -> Path:
        """获取日志文件路径"""
        return self.LOG_DIR / f"{log_type}.log"

    def is_production(self) -> bool:
        """是否生产环境"""
        return self.ENV == "prod"

    def is_development(self) -> bool:
        """是否开发环境"""
        return self.ENV == "dev"

    def should_log_to_console(self) -> bool:
        """是否输出到控制台"""
        # 生产环境默认不输出控制台（除非明确启用）
        return self.LOG_ENABLE_CONSOLE

    # =================================================================
    # Pydantic 配置
    # =================================================================

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=True,
        extra="ignore",
        validate_assignment=True,  # 赋值时验证
        frozen=False,  # 允许修改（用于动态调整）
    )


# =================================================================
# 导出单例
# =================================================================

_log_config_instance: Optional[LogConfig] = None


def get_log_config() -> LogConfig:
    """获取日志配置单例"""
    global _log_config_instance
    if _log_config_instance is None:
        _log_config_instance = LogConfig()
    return _log_config_instance


def reload_log_config() -> LogConfig:
    """重新加载日志配置"""
    global _log_config_instance
    _log_config_instance = LogConfig()
    return _log_config_instance


# =================================================================
# 配置验证工具
# =================================================================

def validate_log_config() -> tuple[bool, list[str]]:
    """
    验证日志配置

    Returns:
        (is_valid, errors)
    """
    errors = []

    try:
        config = get_log_config()

        # 检查日志目录权限
        test_file = config.LOG_DIR / ".write_test"
        try:
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            errors.append(f"日志目录不可写: {config.LOG_DIR} - {e}")

        # 检查 Loki 连接
        if config.LOG_ENABLE_LOKI:
            try:
                import httpx
                response = httpx.get(
                    f"{config.LOG_LOKI_URL}/ready",
                    timeout=5.0
                )
                if response.status_code != 200:
                    errors.append(f"Loki 服务不可用: {config.LOG_LOKI_URL}")
            except Exception as e:
                errors.append(f"无法连接 Loki: {e}")

        return len(errors) == 0, errors

    except Exception as e:
        return False, [f"配置加载失败: {e}"]


# =================================================================
# 使用示例
# =================================================================

if __name__ == "__main__":
    # 测试配置加载
    config = get_log_config()

    print("=" * 60)
    print("日志配置信息")
    print("=" * 60)
    print(f"应用名称: {config.APP_NAME}")
    print(f"运行环境: {config.ENV}")
    print(f"日志级别: {config.LOG_LEVEL}")
    print(f"日志目录: {config.LOG_DIR}")
    print(f"日志格式: {config.LOG_FORMAT}")
    print(f"控制台输出: {config.LOG_ENABLE_CONSOLE}")
    print(f"文件输出: {config.LOG_ENABLE_FILE}")
    print(f"Loki 推送: {config.LOG_ENABLE_LOKI}")

    if config.LOG_ENABLE_LOKI:
        print(f"\nLoki 配置:")
        print(f"  URL: {config.LOG_LOKI_URL}")
        print(f"  批量大小: {config.LOG_LOKI_BATCH_SIZE}")
        print(f"  刷新间隔: {config.LOG_LOKI_FLUSH_INTERVAL}s")
        print(f"  Labels: {config.get_loki_labels()}")

    print(f"\n性能配置:")
    print(f"  异步日志: {config.LOG_ENABLE_ASYNC}")
    print(f"  队列大小: {config.LOG_QUEUE_SIZE}")

    print("\n" + "=" * 60)

    # 验证配置
    is_valid, errors = validate_log_config()
    if is_valid:
        print("✅ 配置验证通过")
    else:
        print("❌ 配置验证失败:")
        for error in errors:
            print(f"  - {error}")
