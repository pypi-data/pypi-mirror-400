"""
性能测试标准定义

定义不同级别的性能标准，用于评估接口性能
"""

from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass


class StandardLevel(str, Enum):
    """标准级别"""
    EXCELLENT = "excellent"    # 优秀
    GOOD = "good"             # 良好
    ACCEPTABLE = "acceptable" # 可接受
    POOR = "poor"            # 较差
    CRITICAL = "critical"    # 严重


@dataclass
class PerformanceThreshold:
    """性能阈值"""
    excellent: float  # 优秀阈值
    good: float      # 良好阈值
    acceptable: float # 可接受阈值
    poor: float      # 较差阈值
    # 超过 poor 即为 critical


class PerformanceStandards:
    """
    性能测试标准

    定义了不同类型接口的性能标准
    """

    # 标准定义 (单位: 毫秒)
    STANDARDS = {
        # 快速接口 (如健康检查、静态资源)
        "fast": PerformanceThreshold(
            excellent=10,    # < 10ms
            good=30,        # < 30ms
            acceptable=50,  # < 50ms
            poor=100,       # < 100ms
        ),

        # 一般接口 (如简单查询、列表)
        "normal": PerformanceThreshold(
            excellent=50,    # < 50ms
            good=100,       # < 100ms
            acceptable=200, # < 200ms
            poor=500,       # < 500ms
        ),

        # 复杂接口 (如复杂查询、聚合)
        "complex": PerformanceThreshold(
            excellent=100,   # < 100ms
            good=200,       # < 200ms
            acceptable=500, # < 500ms
            poor=1000,      # < 1s
        ),

        # 重型接口 (如文件处理、批量操作)
        "heavy": PerformanceThreshold(
            excellent=200,   # < 200ms
            good=500,       # < 500ms
            acceptable=1000, # < 1s
            poor=3000,      # < 3s
        ),
    }

    # 吞吐量标准 (requests/second)
    THROUGHPUT_STANDARDS = {
        "fast": {
            "excellent": 1000,
            "good": 500,
            "acceptable": 200,
            "poor": 100,
        },
        "normal": {
            "excellent": 500,
            "good": 200,
            "acceptable": 100,
            "poor": 50,
        },
        "complex": {
            "excellent": 200,
            "good": 100,
            "acceptable": 50,
            "poor": 20,
        },
        "heavy": {
            "excellent": 100,
            "good": 50,
            "acceptable": 20,
            "poor": 10,
        },
    }

    # 并发用户标准
    CONCURRENCY_STANDARDS = {
        "low": 10,      # 低并发
        "medium": 50,   # 中并发
        "high": 100,    # 高并发
        "extreme": 500, # 极限并发
    }

    # 成功率标准
    SUCCESS_RATE_STANDARDS = {
        "excellent": 99.9,   # 99.9%
        "good": 99.0,       # 99%
        "acceptable": 95.0, # 95%
        "poor": 90.0,       # 90%
    }

    @classmethod
    def evaluate_response_time(
        cls,
        response_time: float,
        interface_type: str = "normal"
    ) -> StandardLevel:
        """
        评估响应时间

        Args:
            response_time: 响应时间 (毫秒)
            interface_type: 接口类型 (fast/normal/complex/heavy)

        Returns:
            标准级别
        """
        threshold = cls.STANDARDS.get(interface_type, cls.STANDARDS["normal"])

        if response_time <= threshold.excellent:
            return StandardLevel.EXCELLENT
        elif response_time <= threshold.good:
            return StandardLevel.GOOD
        elif response_time <= threshold.acceptable:
            return StandardLevel.ACCEPTABLE
        elif response_time <= threshold.poor:
            return StandardLevel.POOR
        else:
            return StandardLevel.CRITICAL

    @classmethod
    def evaluate_throughput(
        cls,
        throughput: float,
        interface_type: str = "normal"
    ) -> StandardLevel:
        """评估吞吐量"""
        standards = cls.THROUGHPUT_STANDARDS.get(
            interface_type,
            cls.THROUGHPUT_STANDARDS["normal"]
        )

        if throughput >= standards["excellent"]:
            return StandardLevel.EXCELLENT
        elif throughput >= standards["good"]:
            return StandardLevel.GOOD
        elif throughput >= standards["acceptable"]:
            return StandardLevel.ACCEPTABLE
        elif throughput >= standards["poor"]:
            return StandardLevel.POOR
        else:
            return StandardLevel.CRITICAL

    @classmethod
    def evaluate_success_rate(cls, success_rate: float) -> StandardLevel:
        """评估成功率"""
        if success_rate >= cls.SUCCESS_RATE_STANDARDS["excellent"]:
            return StandardLevel.EXCELLENT
        elif success_rate >= cls.SUCCESS_RATE_STANDARDS["good"]:
            return StandardLevel.GOOD
        elif success_rate >= cls.SUCCESS_RATE_STANDARDS["acceptable"]:
            return StandardLevel.ACCEPTABLE
        elif success_rate >= cls.SUCCESS_RATE_STANDARDS["poor"]:
            return StandardLevel.POOR
        else:
            return StandardLevel.CRITICAL

    @classmethod
    def get_threshold(cls, interface_type: str = "normal") -> PerformanceThreshold:
        """获取性能阈值"""
        return cls.STANDARDS.get(interface_type, cls.STANDARDS["normal"])

    @classmethod
    def get_level_color(cls, level: StandardLevel) -> str:
        """获取级别对应的颜色"""
        colors = {
            StandardLevel.EXCELLENT: "#10b981",  # 绿色
            StandardLevel.GOOD: "#3b82f6",      # 蓝色
            StandardLevel.ACCEPTABLE: "#f59e0b", # 橙色
            StandardLevel.POOR: "#ef4444",      # 红色
            StandardLevel.CRITICAL: "#991b1b",  # 深红色
        }
        return colors.get(level, "#6b7280")

    @classmethod
    def get_level_label(cls, level: StandardLevel) -> str:
        """获取级别标签 (中文)"""
        labels = {
            StandardLevel.EXCELLENT: "优秀",
            StandardLevel.GOOD: "良好",
            StandardLevel.ACCEPTABLE: "可接受",
            StandardLevel.POOR: "较差",
            StandardLevel.CRITICAL: "严重",
        }
        return labels.get(level, "未知")

    @classmethod
    def get_recommendation(cls, level: StandardLevel) -> str:
        """获取优化建议"""
        recommendations = {
            StandardLevel.EXCELLENT: "性能优异，继续保持",
            StandardLevel.GOOD: "性能良好，可考虑进一步优化",
            StandardLevel.ACCEPTABLE: "性能可接受，建议优化以提升用户体验",
            StandardLevel.POOR: "性能较差，建议优先优化此接口",
            StandardLevel.CRITICAL: "性能严重不足，需要立即优化",
        }
        return recommendations.get(level, "")
