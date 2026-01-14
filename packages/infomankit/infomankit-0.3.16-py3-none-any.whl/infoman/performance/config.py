"""
性能测试配置

定义测试配置和测试用例
"""

from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field
import yaml
from pathlib import Path


class APITestCase(BaseModel):
    """单个 API 测试用例"""

    name: str = Field(..., description="测试用例名称")
    url: str = Field(..., description="API URL (相对路径或绝对路径)")
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = Field(
        default="GET",
        description="HTTP 方法"
    )
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="请求头"
    )
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="URL 参数 (GET)"
    )
    json: Optional[Dict[str, Any]] = Field(
        default=None,
        description="JSON 请求体 (POST/PUT/PATCH)"
    )
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="表单数据"
    )
    interface_type: Literal["fast", "normal", "complex", "heavy"] = Field(
        default="normal",
        description="接口类型 (用于性能标准评估)"
    )
    timeout: int = Field(
        default=30,
        description="请求超时时间 (秒)"
    )
    description: str = Field(
        default="",
        description="测试描述"
    )
    enabled: bool = Field(
        default=True,
        description="是否启用此测试"
    )


class TestConfig(BaseModel):
    """性能测试配置"""

    # 基础配置
    project_name: str = Field(default="Infomankit", description="项目名称")
    base_url: str = Field(default="http://localhost:8000", description="基础 URL")

    # 并发配置
    concurrent_users: int = Field(default=10, description="并发用户数")
    duration: int = Field(default=60, description="测试持续时间 (秒)")
    spawn_rate: int = Field(default=1, description="每秒启动用户数")

    # 全局请求头
    global_headers: Dict[str, str] = Field(
        default_factory=lambda: {
            "User-Agent": "Infomankit-Performance-Test/1.0",
            "Accept": "application/json",
        },
        description="全局请求头"
    )

    # 认证配置
    auth_type: Optional[Literal["basic", "bearer", "custom"]] = Field(
        default=None,
        description="认证类型"
    )
    auth_token: Optional[str] = Field(default=None, description="Bearer Token")
    auth_username: Optional[str] = Field(default=None, description="Basic Auth 用户名")
    auth_password: Optional[str] = Field(default=None, description="Basic Auth 密码")

    # 测试用例
    test_cases: List[APITestCase] = Field(
        default_factory=list,
        description="API 测试用例列表"
    )

    # 报告配置
    report_title: str = Field(default="性能测试报告", description="报告标题")
    report_output: str = Field(
        default="performance-report.html",
        description="报告输出路径"
    )

    # 高级配置
    think_time_min: int = Field(default=1, description="最小思考时间 (秒)")
    think_time_max: int = Field(default=3, description="最大思考时间 (秒)")

    stop_on_error: bool = Field(
        default=False,
        description="遇到错误时停止测试"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "project_name": "Infomankit API",
                "base_url": "http://localhost:8000",
                "concurrent_users": 50,
                "duration": 120,
                "auth_type": "bearer",
                "auth_token": "your-token-here",
                "test_cases": [
                    {
                        "name": "健康检查",
                        "url": "/api/health",
                        "method": "GET",
                        "interface_type": "fast",
                    },
                    {
                        "name": "用户列表",
                        "url": "/api/v1/users",
                        "method": "GET",
                        "interface_type": "normal",
                        "params": {"page": 1, "page_size": 20},
                    },
                ]
            }
        }

    @classmethod
    def from_yaml(cls, filepath: str) -> "TestConfig":
        """从 YAML 文件加载配置"""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {filepath}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls(**data)

    def to_yaml(self, filepath: str):
        """保存配置到 YAML 文件"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(
                self.model_dump(exclude_none=True),
                f,
                allow_unicode=True,
                sort_keys=False,
            )

    def add_test_case(self, test_case: APITestCase):
        """添加测试用例"""
        self.test_cases.append(test_case)

    def get_enabled_test_cases(self) -> List[APITestCase]:
        """获取启用的测试用例"""
        return [tc for tc in self.test_cases if tc.enabled]
