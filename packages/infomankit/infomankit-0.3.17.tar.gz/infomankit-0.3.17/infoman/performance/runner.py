"""
性能测试运行器

执行性能测试并收集结果
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import httpx
from loguru import logger

from .config import TestConfig, APITestCase
from .standards import PerformanceStandards, StandardLevel


@dataclass
class TestResult:
    """单次测试结果"""
    test_case_name: str
    url: str
    method: str
    status_code: int
    response_time: float  # 毫秒
    success: bool
    error_message: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class AggregatedResult:
    """聚合测试结果"""
    test_case_name: str
    url: str
    method: str
    interface_type: str

    # 请求统计
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    success_rate: float = 0.0

    # 响应时间统计 (毫秒)
    min_response_time: float = 0.0
    max_response_time: float = 0.0
    avg_response_time: float = 0.0
    median_response_time: float = 0.0
    p50_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0

    # 吞吐量 (requests/second)
    throughput: float = 0.0

    # 性能评级
    response_time_level: StandardLevel = StandardLevel.ACCEPTABLE
    throughput_level: StandardLevel = StandardLevel.ACCEPTABLE
    success_rate_level: StandardLevel = StandardLevel.ACCEPTABLE
    overall_level: StandardLevel = StandardLevel.ACCEPTABLE

    # 错误信息
    error_messages: List[str] = field(default_factory=list)


class PerformanceTestRunner:
    """性能测试运行器"""

    def __init__(self, config: TestConfig):
        self.config = config
        self.results: Dict[str, List[TestResult]] = {}
        self.start_time: float = 0
        self.end_time: float = 0

    async def run(self) -> Dict[str, AggregatedResult]:
        """
        运行性能测试

        Returns:
            聚合结果字典 {test_case_name: AggregatedResult}
        """
        logger.info(f"🚀 开始性能测试: {self.config.project_name}")
        logger.info(f"   并发用户: {self.config.concurrent_users}")
        logger.info(f"   持续时间: {self.config.duration}秒")
        logger.info(f"   测试用例: {len(self.config.get_enabled_test_cases())}个")

        self.start_time = time.time()

        # 创建并发任务
        tasks = []
        for i in range(self.config.concurrent_users):
            task = asyncio.create_task(self._user_task(i))
            tasks.append(task)
            # 控制启动速率
            await asyncio.sleep(1 / self.config.spawn_rate)

        # 等待所有任务完成
        await asyncio.gather(*tasks, return_exceptions=True)

        self.end_time = time.time()

        logger.success(f"✅ 性能测试完成，耗时: {self.end_time - self.start_time:.2f}秒")

        # 聚合结果
        aggregated = self._aggregate_results()

        return aggregated

    async def _user_task(self, user_id: int):
        """单个用户的测试任务"""
        test_cases = self.config.get_enabled_test_cases()
        if not test_cases:
            logger.warning("没有启用的测试用例")
            return

        end_time = self.start_time + self.config.duration

        async with httpx.AsyncClient(timeout=30.0) as client:
            while time.time() < end_time:
                # 依次执行所有测试用例
                for test_case in test_cases:
                    if time.time() >= end_time:
                        break

                    result = await self._execute_test_case(client, test_case)

                    # 保存结果
                    if test_case.name not in self.results:
                        self.results[test_case.name] = []
                    self.results[test_case.name].append(result)

                    # 思考时间
                    think_time = (
                        self.config.think_time_min +
                        (self.config.think_time_max - self.config.think_time_min) * 0.5
                    )
                    await asyncio.sleep(think_time)

    async def _execute_test_case(
        self,
        client: httpx.AsyncClient,
        test_case: APITestCase
    ) -> TestResult:
        """执行单个测试用例"""
        url = self._build_url(test_case.url)

        # 构建请求头
        headers = {**self.config.global_headers, **test_case.headers}

        # 添加认证
        if self.config.auth_type == "bearer" and self.config.auth_token:
            headers["Authorization"] = f"Bearer {self.config.auth_token}"

        start_time = time.time()
        success = False
        status_code = 0
        error_message = ""

        try:
            response = await client.request(
                method=test_case.method,
                url=url,
                headers=headers,
                params=test_case.params,
                json=test_case.json,
                data=test_case.data,
                timeout=test_case.timeout,
            )

            status_code = response.status_code
            success = 200 <= status_code < 300

            if not success:
                error_message = f"HTTP {status_code}: {response.text[:200]}"

        except httpx.TimeoutException:
            error_message = "请求超时"
        except httpx.ConnectError:
            error_message = "连接失败"
        except Exception as e:
            error_message = str(e)

        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # 转换为毫秒

        return TestResult(
            test_case_name=test_case.name,
            url=url,
            method=test_case.method,
            status_code=status_code,
            response_time=response_time,
            success=success,
            error_message=error_message,
        )

    def _build_url(self, path: str) -> str:
        """构建完整 URL"""
        if path.startswith("http://") or path.startswith("https://"):
            return path

        base_url = self.config.base_url.rstrip("/")
        path = path.lstrip("/")
        return f"{base_url}/{path}"

    def _aggregate_results(self) -> Dict[str, AggregatedResult]:
        """聚合测试结果"""
        aggregated = {}
        test_duration = self.end_time - self.start_time

        for test_case_name, results in self.results.items():
            if not results:
                continue

            # 找到对应的测试用例配置
            test_case = next(
                (tc for tc in self.config.test_cases if tc.name == test_case_name),
                None
            )
            interface_type = test_case.interface_type if test_case else "normal"

            # 基本统计
            total = len(results)
            successful = sum(1 for r in results if r.success)
            failed = total - successful
            success_rate = (successful / total * 100) if total > 0 else 0

            # 响应时间统计
            response_times = [r.response_time for r in results]
            response_times.sort()

            min_rt = min(response_times) if response_times else 0
            max_rt = max(response_times) if response_times else 0
            avg_rt = statistics.mean(response_times) if response_times else 0
            median_rt = statistics.median(response_times) if response_times else 0

            # 百分位
            p50 = self._percentile(response_times, 0.50)
            p95 = self._percentile(response_times, 0.95)
            p99 = self._percentile(response_times, 0.99)

            # 吞吐量
            throughput = total / test_duration if test_duration > 0 else 0

            # 性能评级
            rt_level = PerformanceStandards.evaluate_response_time(
                avg_rt, interface_type
            )
            tp_level = PerformanceStandards.evaluate_throughput(
                throughput, interface_type
            )
            sr_level = PerformanceStandards.evaluate_success_rate(success_rate)

            # 综合评级 (取最差的)
            overall_level = max(
                [rt_level, tp_level, sr_level],
                key=lambda x: list(StandardLevel).index(x)
            )

            # 错误信息
            error_messages = [
                r.error_message
                for r in results
                if not r.success and r.error_message
            ]
            unique_errors = list(set(error_messages))[:10]  # 最多10条

            aggregated[test_case_name] = AggregatedResult(
                test_case_name=test_case_name,
                url=results[0].url,
                method=results[0].method,
                interface_type=interface_type,
                total_requests=total,
                successful_requests=successful,
                failed_requests=failed,
                success_rate=success_rate,
                min_response_time=min_rt,
                max_response_time=max_rt,
                avg_response_time=avg_rt,
                median_response_time=median_rt,
                p50_response_time=p50,
                p95_response_time=p95,
                p99_response_time=p99,
                throughput=throughput,
                response_time_level=rt_level,
                throughput_level=tp_level,
                success_rate_level=sr_level,
                overall_level=overall_level,
                error_messages=unique_errors,
            )

        return aggregated

    @staticmethod
    def _percentile(data: List[float], percentile: float) -> float:
        """计算百分位数"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]
