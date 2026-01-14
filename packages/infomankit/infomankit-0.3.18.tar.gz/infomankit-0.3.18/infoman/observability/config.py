"""
可观测性配置
"""

from typing import Optional, Literal
from pydantic import Field
from pydantic_settings import BaseSettings


class ObservabilityConfig(BaseSettings):
    """可观测性配置"""

    # ========== OpenTelemetry 追踪 ==========
    OTEL_ENABLED: bool = Field(default=True, description="是否启用 OpenTelemetry")
    OTEL_SERVICE_NAME: str = Field(default="infoman-service", description="服务名称")
    OTEL_SERVICE_VERSION: str = Field(default="0.3.15", description="服务版本")
    OTEL_DEPLOYMENT_ENVIRONMENT: str = Field(default="production", description="部署环境")

    # 导出器配置
    OTEL_EXPORTER_TYPE: Literal["otlp", "jaeger", "console"] = Field(
        default="otlp", description="导出器类型"
    )

    # OTLP 导出器
    OTEL_EXPORTER_OTLP_ENDPOINT: str = Field(
        default="http://localhost:4317", description="OTLP gRPC 端点"
    )
    OTEL_EXPORTER_OTLP_HTTP_ENDPOINT: str = Field(
        default="http://localhost:4318", description="OTLP HTTP 端点"
    )
    OTEL_EXPORTER_OTLP_INSECURE: bool = Field(default=True, description="是否使用不安全连接")
    OTEL_EXPORTER_OTLP_HEADERS: Optional[str] = Field(default=None, description="OTLP 请求头")

    # Jaeger 导出器
    OTEL_EXPORTER_JAEGER_AGENT_HOST: str = Field(
        default="localhost", description="Jaeger agent 主机"
    )
    OTEL_EXPORTER_JAEGER_AGENT_PORT: int = Field(
        default=6831, description="Jaeger agent 端口"
    )

    # 采样配置
    OTEL_TRACE_SAMPLER: Literal["always_on", "always_off", "parentbased", "traceidratio"] = Field(
        default="parentbased", description="采样器类型"
    )
    OTEL_TRACE_SAMPLER_RATIO: float = Field(
        default=1.0, description="采样率 (0.0-1.0)", ge=0.0, le=1.0
    )

    # 资源属性
    OTEL_RESOURCE_ATTRIBUTES: Optional[str] = Field(
        default=None, description="额外的资源属性 (key1=value1,key2=value2)"
    )

    # ========== 仪表盘配置 ==========
    OTEL_INSTRUMENT_FASTAPI: bool = Field(default=True, description="自动追踪 FastAPI")
    OTEL_INSTRUMENT_HTTPX: bool = Field(default=True, description="自动追踪 HTTPX")
    OTEL_INSTRUMENT_REDIS: bool = Field(default=True, description="自动追踪 Redis")
    OTEL_INSTRUMENT_SQLALCHEMY: bool = Field(default=True, description="自动追踪 SQLAlchemy")

    # ========== Metrics ==========
    OTEL_METRICS_ENABLED: bool = Field(default=True, description="是否启用 Metrics")
    OTEL_METRICS_EXPORT_INTERVAL: int = Field(default=60, description="Metrics 导出间隔(秒)")

    class Config:
        env_file = ".env"
        case_sensitive = True
