"""
HTML 报告生成器

生成精美的性能测试报告
"""

from typing import Dict
from datetime import datetime
from pathlib import Path
from jinja2 import Template

from .runner import AggregatedResult
from .config import TestConfig
from .standards import PerformanceStandards, StandardLevel


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ config.report_title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB',
                'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            background: white;
            border-radius: 16px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }

        .header h1 {
            font-size: 36px;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .header .meta {
            color: #666;
            font-size: 14px;
        }

        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .summary-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            transition: transform 0.2s;
        }

        .summary-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        }

        .summary-card .label {
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
        }

        .summary-card .value {
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }

        .summary-card .unit {
            font-size: 14px;
            color: #999;
            margin-left: 4px;
        }

        .summary-card.excellent .value { color: #10b981; }
        .summary-card.good .value { color: #3b82f6; }
        .summary-card.warning .value { color: #f59e0b; }
        .summary-card.danger .value { color: #ef4444; }

        .results {
            background: white;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }

        .results h2 {
            font-size: 24px;
            margin-bottom: 30px;
            color: #333;
        }

        .test-case {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            margin-bottom: 30px;
            overflow: hidden;
        }

        .test-case-header {
            background: #f9fafb;
            padding: 20px;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .test-case-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
        }

        .test-case-url {
            font-size: 12px;
            color: #666;
            font-family: 'Monaco', 'Courier New', monospace;
            margin-top: 4px;
        }

        .level-badge {
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .level-excellent { background: #d1fae5; color: #065f46; }
        .level-good { background: #dbeafe; color: #1e40af; }
        .level-acceptable { background: #fef3c7; color: #92400e; }
        .level-poor { background: #fee2e2; color: #991b1b; }
        .level-critical { background: #991b1b; color: white; }

        .test-case-body {
            padding: 20px;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .metric {
            text-align: center;
            padding: 16px;
            background: #f9fafb;
            border-radius: 8px;
        }

        .metric-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 8px;
        }

        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }

        .metric-unit {
            font-size: 12px;
            color: #999;
        }

        .percentiles {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            padding: 20px;
            background: #f0f9ff;
            border-radius: 8px;
        }

        .percentile {
            text-align: center;
        }

        .percentile-label {
            font-size: 12px;
            color: #0369a1;
            margin-bottom: 4px;
        }

        .percentile-value {
            font-size: 20px;
            font-weight: bold;
            color: #0c4a6e;
        }

        .errors {
            margin-top: 20px;
            padding: 16px;
            background: #fef2f2;
            border-radius: 8px;
            border-left: 4px solid #ef4444;
        }

        .errors h4 {
            color: #991b1b;
            margin-bottom: 12px;
            font-size: 14px;
        }

        .error-list {
            list-style: none;
        }

        .error-list li {
            padding: 8px 0;
            color: #7f1d1d;
            font-size: 13px;
            border-bottom: 1px solid #fecaca;
        }

        .error-list li:last-child {
            border-bottom: none;
        }

        .recommendation {
            margin-top: 16px;
            padding: 12px 16px;
            background: #f0fdf4;
            border-radius: 8px;
            border-left: 4px solid #10b981;
            font-size: 14px;
            color: #065f46;
        }

        .recommendation.warning {
            background: #fffbeb;
            border-left-color: #f59e0b;
            color: #92400e;
        }

        .recommendation.danger {
            background: #fef2f2;
            border-left-color: #ef4444;
            color: #991b1b;
        }

        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: white;
            font-size: 14px;
        }

        .footer a {
            color: white;
            text-decoration: none;
            border-bottom: 1px solid rgba(255,255,255,0.5);
        }

        @media print {
            body {
                background: white;
                padding: 0;
            }

            .summary-card,
            .test-case {
                break-inside: avoid;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>{{ config.report_title }}</h1>
            <div class="meta">
                <span>📅 {{ report_time }}</span>
                <span style="margin-left: 20px;">🎯 项目: {{ config.project_name }}</span>
                <span style="margin-left: 20px;">🔗 {{ config.base_url }}</span>
            </div>
        </div>

        <!-- Summary Cards -->
        <div class="summary">
            <div class="summary-card">
                <div class="label">总请求数</div>
                <div class="value">{{ summary.total_requests }}</div>
            </div>
            <div class="summary-card {{ 'excellent' if summary.success_rate >= 99 else 'good' if summary.success_rate >= 95 else 'warning' if summary.success_rate >= 90 else 'danger' }}">
                <div class="label">成功率</div>
                <div class="value">{{ "%.2f"|format(summary.success_rate) }}<span class="unit">%</span></div>
            </div>
            <div class="summary-card {{ 'excellent' if summary.avg_response_time < 100 else 'good' if summary.avg_response_time < 200 else 'warning' if summary.avg_response_time < 500 else 'danger' }}">
                <div class="label">平均响应时间</div>
                <div class="value">{{ "%.0f"|format(summary.avg_response_time) }}<span class="unit">ms</span></div>
            </div>
            <div class="summary-card">
                <div class="label">吞吐量</div>
                <div class="value">{{ "%.1f"|format(summary.throughput) }}<span class="unit">req/s</span></div>
            </div>
            <div class="summary-card">
                <div class="label">并发用户</div>
                <div class="value">{{ config.concurrent_users }}</div>
            </div>
            <div class="summary-card">
                <div class="label">测试时长</div>
                <div class="value">{{ config.duration }}<span class="unit">秒</span></div>
            </div>
        </div>

        <!-- Detailed Results -->
        <div class="results">
            <h2>📊 详细测试结果</h2>

            {% for name, result in results.items() %}
            <div class="test-case">
                <div class="test-case-header">
                    <div>
                        <div class="test-case-title">
                            {{ result.method }} {{ result.test_case_name }}
                        </div>
                        <div class="test-case-url">{{ result.url }}</div>
                    </div>
                    <span class="level-badge level-{{ result.overall_level }}">
                        {{ get_level_label(result.overall_level) }}
                    </span>
                </div>

                <div class="test-case-body">
                    <!-- 核心指标 -->
                    <div class="metrics-grid">
                        <div class="metric">
                            <div class="metric-label">总请求数</div>
                            <div class="metric-value">{{ result.total_requests }}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">成功 / 失败</div>
                            <div class="metric-value">
                                <span style="color: #10b981;">{{ result.successful_requests }}</span>
                                /
                                <span style="color: #ef4444;">{{ result.failed_requests }}</span>
                            </div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">成功率</div>
                            <div class="metric-value">{{ "%.2f"|format(result.success_rate) }}<span class="metric-unit">%</span></div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">吞吐量</div>
                            <div class="metric-value">{{ "%.1f"|format(result.throughput) }}<span class="metric-unit">req/s</span></div>
                        </div>
                    </div>

                    <!-- 响应时间百分位 -->
                    <div class="percentiles">
                        <div class="percentile">
                            <div class="percentile-label">最小</div>
                            <div class="percentile-value">{{ "%.0f"|format(result.min_response_time) }}ms</div>
                        </div>
                        <div class="percentile">
                            <div class="percentile-label">P50</div>
                            <div class="percentile-value">{{ "%.0f"|format(result.p50_response_time) }}ms</div>
                        </div>
                        <div class="percentile">
                            <div class="percentile-label">平均</div>
                            <div class="percentile-value">{{ "%.0f"|format(result.avg_response_time) }}ms</div>
                        </div>
                        <div class="percentile">
                            <div class="percentile-label">P95</div>
                            <div class="percentile-value">{{ "%.0f"|format(result.p95_response_time) }}ms</div>
                        </div>
                        <div class="percentile">
                            <div class="percentile-label">P99</div>
                            <div class="percentile-value">{{ "%.0f"|format(result.p99_response_time) }}ms</div>
                        </div>
                        <div class="percentile">
                            <div class="percentile-label">最大</div>
                            <div class="percentile-value">{{ "%.0f"|format(result.max_response_time) }}ms</div>
                        </div>
                    </div>

                    <!-- 错误信息 -->
                    {% if result.error_messages %}
                    <div class="errors">
                        <h4>⚠️ 错误信息 ({{ result.error_messages|length }})</h4>
                        <ul class="error-list">
                            {% for error in result.error_messages[:5] %}
                            <li>{{ error }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                    {% endif %}

                    <!-- 优化建议 -->
                    <div class="recommendation {{ 'warning' if result.overall_level in ['acceptable', 'poor'] else 'danger' if result.overall_level == 'critical' else '' }}">
                        💡 {{ get_recommendation(result.overall_level) }}
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>Generated by <a href="https://github.com/infoman-lib/infoman-pykit" target="_blank">Infomankit Performance Test Tool</a></p>
            <p style="margin-top: 8px; font-size: 12px;">v0.3.15 | © 2026 Infoman Contributors</p>
        </div>
    </div>
</body>
</html>
"""


class HTMLReporter:
    """HTML 报告生成器"""

    def __init__(self, config: TestConfig):
        self.config = config

    def generate(
        self,
        results: Dict[str, AggregatedResult],
        output_path: str = None
    ) -> str:
        """
        生成 HTML 报告

        Args:
            results: 聚合结果
            output_path: 输出路径 (默认使用配置中的路径)

        Returns:
            输出文件路径
        """
        if output_path is None:
            output_path = self.config.report_output

        # 计算汇总数据
        summary = self._calculate_summary(results)

        # 渲染模板
        template = Template(HTML_TEMPLATE)
        html_content = template.render(
            config=self.config,
            results=results,
            summary=summary,
            report_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            get_level_label=PerformanceStandards.get_level_label,
            get_recommendation=PerformanceStandards.get_recommendation,
        )

        # 保存文件
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html_content, encoding="utf-8")

        return str(output_file.absolute())

    def _calculate_summary(
        self,
        results: Dict[str, AggregatedResult]
    ) -> Dict:
        """计算汇总数据"""
        if not results:
            return {
                "total_requests": 0,
                "success_rate": 0,
                "avg_response_time": 0,
                "throughput": 0,
            }

        total_requests = sum(r.total_requests for r in results.values())
        successful_requests = sum(r.successful_requests for r in results.values())
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0

        # 加权平均响应时间
        total_rt = sum(r.avg_response_time * r.total_requests for r in results.values())
        avg_response_time = total_rt / total_requests if total_requests > 0 else 0

        # 总吞吐量
        throughput = sum(r.throughput for r in results.values())

        return {
            "total_requests": total_requests,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "throughput": throughput,
        }
