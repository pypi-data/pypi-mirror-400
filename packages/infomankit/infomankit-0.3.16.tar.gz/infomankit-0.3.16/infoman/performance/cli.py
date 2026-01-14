#!/usr/bin/env python3
"""
性能测试命令行工具

提供简单的 CLI 接口用于运行性能测试
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from loguru import logger

from .config import TestConfig
from .runner import PerformanceTestRunner
from .reporter import HTMLReporter


@click.group()
@click.version_option()
def cli():
    """Infomankit 性能测试工具"""
    pass


@cli.command()
@click.option(
    "-c",
    "--config",
    "config_file",
    required=True,
    type=click.Path(exists=True),
    help="配置文件路径 (YAML)",
)
@click.option(
    "-o",
    "--output",
    "output_file",
    type=click.Path(),
    help="报告输出路径 (覆盖配置文件中的设置)",
)
@click.option(
    "-u",
    "--users",
    "concurrent_users",
    type=int,
    help="并发用户数 (覆盖配置文件中的设置)",
)
@click.option(
    "-d",
    "--duration",
    type=int,
    help="测试持续时间(秒) (覆盖配置文件中的设置)",
)
@click.option(
    "-v", "--verbose", is_flag=True, help="显示详细日志"
)
def run(
    config_file: str,
    output_file: Optional[str],
    concurrent_users: Optional[int],
    duration: Optional[int],
    verbose: bool,
):
    """运行性能测试"""

    # 配置日志级别
    if not verbose:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    try:
        # 加载配置
        logger.info(f"加载配置: {config_file}")
        config = TestConfig.from_yaml(config_file)

        # 覆盖命令行参数
        if concurrent_users:
            config.concurrent_users = concurrent_users
            logger.info(f"覆盖并发用户数: {concurrent_users}")

        if duration:
            config.duration = duration
            logger.info(f"覆盖测试时长: {duration}秒")

        if output_file:
            config.report_output = output_file
            logger.info(f"覆盖报告输出: {output_file}")

        # 显示测试信息
        logger.info("=" * 60)
        logger.info(f"项目: {config.project_name}")
        logger.info(f"目标: {config.base_url}")
        logger.info(f"并发用户: {config.concurrent_users}")
        logger.info(f"持续时间: {config.duration}秒")
        logger.info(f"测试用例: {len(config.get_enabled_test_cases())}个")
        logger.info("=" * 60)

        # 运行测试
        asyncio.run(_run_test(config))

    except FileNotFoundError as e:
        logger.error(f"配置文件不存在: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"测试失败: {e}")
        if verbose:
            raise
        sys.exit(1)


async def _run_test(config: TestConfig):
    """执行测试"""
    # 运行测试
    runner = PerformanceTestRunner(config)
    results = await runner.run()

    # 显示简要结果
    logger.info("\n" + "=" * 60)
    logger.info("测试结果汇总")
    logger.info("=" * 60)

    for name, result in results.items():
        logger.info(f"\n📊 {name}")
        logger.info(f"  总请求: {result.total_requests}")
        logger.info(f"  成功率: {result.success_rate:.2f}%")
        logger.info(f"  平均响应: {result.avg_response_time:.2f}ms")
        logger.info(f"  P95: {result.p95_response_time:.2f}ms")
        logger.info(f"  吞吐量: {result.throughput:.2f} req/s")
        logger.info(f"  评级: {result.overall_level}")

    # 生成报告
    logger.info("\n" + "=" * 60)
    logger.info("生成报告...")
    reporter = HTMLReporter(config)
    report_path = reporter.generate(results)
    logger.success(f"✅ 报告已生成: {report_path}")
    logger.info("=" * 60)


@cli.command()
@click.argument("output", type=click.Path())
def init(output: str):
    """生成示例配置文件"""
    config = TestConfig(
        project_name="My API",
        base_url="http://localhost:8000",
        concurrent_users=10,
        duration=60,
    )

    # 添加示例测试用例
    from .config import APITestCase

    config.add_test_case(
        APITestCase(
            name="健康检查",
            url="/api/health",
            method="GET",
            interface_type="fast",
            description="API 健康检查",
        )
    )

    config.add_test_case(
        APITestCase(
            name="用户列表",
            url="/api/v1/users",
            method="GET",
            interface_type="normal",
            params={"page": 1, "page_size": 20},
            description="用户列表查询",
        )
    )

    # 保存配置
    config.to_yaml(output)
    logger.success(f"✅ 配置文件已生成: {output}")
    logger.info("请编辑配置文件后运行测试:")
    logger.info(f"  infoman perf run -c {output}")


@cli.command()
def standards():
    """显示性能标准"""
    from .standards import PerformanceStandards

    logger.info("=" * 60)
    logger.info("性能标准")
    logger.info("=" * 60)

    for interface_type, threshold in PerformanceStandards.STANDARDS.items():
        logger.info(f"\n{interface_type.upper()} 接口:")
        logger.info(f"  优秀 (Excellent): < {threshold.excellent}ms")
        logger.info(f"  良好 (Good):      < {threshold.good}ms")
        logger.info(f"  可接受 (Acceptable): < {threshold.acceptable}ms")
        logger.info(f"  较差 (Poor):     < {threshold.poor}ms")
        logger.info(f"  严重 (Critical): >= {threshold.poor}ms")

    logger.info("\n" + "=" * 60)
    logger.info("成功率标准")
    logger.info("=" * 60)
    for level, rate in PerformanceStandards.SUCCESS_RATE_STANDARDS.items():
        logger.info(f"  {level:12}: >= {rate}%")


def main():
    """主函数"""
    cli()


if __name__ == "__main__":
    main()
