# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/12/23 17:59
# Author     ：Maxwell
# Description：
"""
import sys
import socket
from typing import Optional, cast
from loguru import logger
from infoman.config.log import get_log_config, LogConfig
from .formatters import get_console_format, get_file_format, serialize_json
from .handlers import LokiHandler
from .filters import (
    ModuleFilter,
    KeywordFilter,
    LevelFilter,
    RateLimitFilter,
    SanitizeFilter,
)
from .context import get_all_context
from .metrics import get_metrics


class LoggerManager:

    def __init__(self, config: Optional[LogConfig] = None):
        """
        初始化日志管理器

        Args:
            config: 日志配置（None 则自动加载）
        """
        self.config = config or get_log_config()
        self.is_initialized = False
        self._handler_ids = []

        # 获取主机名和应用名
        self.hostname = socket.gethostname()
        self.app_name = getattr(self.config, 'APP_NAME', 'infoman')

    def initialize(self):
        """初始化日志系统"""
        if self.is_initialized:
            logger.warning("日志系统已初始化，跳过重复初始化")
            return

        logger.remove()

        # 配置日志处理器
        self._setup_console_handler()
        self._setup_file_handlers()
        self._setup_loki_handler()

        # 配置全局过滤器
        self._setup_filters()

        # 配置上下文注入
        self._setup_context_injection()

        # 配置指标统计
        if self.config.LOG_ENABLE_METRICS:
            self._setup_metrics()

        self.is_initialized = True

        logger.info(
            f"日志系统初始化完成 [ENV={self.config.ENV}, "
            f"LEVEL={self.config.LOG_LEVEL}, "
            f"FORMAT={self.config.LOG_FORMAT}]"
        )

    def _setup_console_handler(self):
        if not self.config.LOG_ENABLE_CONSOLE:
            return

        console_format = get_console_format(self.config.LOG_FORMAT)
        handler_config = {
            "sink": sys.stderr,
            "level": self.config.LOG_LEVEL_CONSOLE or self.config.LOG_LEVEL,
            "format": console_format,
            "colorize": self.config.LOG_ENABLE_CONSOLE_COLOR,
            "backtrace": self.config.LOG_ENABLE_BACKTRACE,
            "diagnose": self.config.LOG_ENABLE_DIAGNOSE,
        }
        handler_id = logger.add(**handler_config)
        self._handler_ids.append(handler_id)

        logger.debug("控制台处理器已配置")

    def _setup_file_handlers(self):
        if not self.config.LOG_ENABLE_FILE:
            return

        file_format = get_file_format(self.config.LOG_FORMAT)

        # 通用文件配置
        common_config = {
            "format": file_format,
            "rotation": self.config.LOG_ROTATION,
            "retention": self.config.LOG_RETENTION,
            "compression": self.config.LOG_COMPRESSION,
            "encoding": self.config.LOG_FILE_ENCODING,
            "backtrace": self.config.LOG_ENABLE_BACKTRACE,
            "diagnose": self.config.LOG_ENABLE_DIAGNOSE,
            "enqueue": self.config.LOG_ENABLE_ASYNC,
        }

        # JSON 格式特殊处理
        if self.config.LOG_FORMAT == "json":
            common_config["serialize"] = True

        # ========== all.log（所有日志） ==========
        if self.config.LOG_ENABLE_ALL_FILE:
            handler_id = logger.add(
                sink=self.config.LOG_DIR / "all.log",
                level=cast(str, self.config.LOG_LEVEL_FILE or self.config.LOG_LEVEL),
                **common_config
            )
            self._handler_ids.append(handler_id)
            logger.debug("all.log 处理器已配置")

        # ========== 按级别分割日志 ==========
        if self.config.LOG_ENABLE_SPLIT_BY_LEVEL:
            # info.log（INFO 及以上）
            handler_id = logger.add(
                sink=self.config.LOG_DIR / "info.log",
                level="INFO",
                filter=lambda record: record["level"].name == "INFO",
                **common_config
            )
            self._handler_ids.append(handler_id)

            # warning.log（WARNING 及以上）
            handler_id = logger.add(
                sink=self.config.LOG_DIR / "warning.log",
                level="WARNING",
                filter=lambda record: record["level"].name == "WARNING",
                **common_config
            )
            self._handler_ids.append(handler_id)

            # error.log（ERROR 及以上）
            handler_id = logger.add(
                sink=self.config.LOG_DIR / "error.log",
                level="ERROR",
                filter=lambda record: record["level"].name in ("ERROR", "CRITICAL"),
                **common_config
            )
            self._handler_ids.append(handler_id)

            logger.debug("分级日志文件处理器已配置")

        # ========== debug.log（开发环境） ==========
        if self.config.LOG_ENABLE_DEBUG_FILE:
            handler_id = logger.add(
                sink=self.config.LOG_DIR / "debug.log",
                level="DEBUG",
                **common_config
            )
            self._handler_ids.append(handler_id)
            logger.debug("debug.log 处理器已配置")

    def _setup_loki_handler(self):
        """配置 Loki 处理器"""
        if not self.config.LOG_ENABLE_LOKI:
            return

        try:
            loki_handler = LokiHandler(
                url=self.config.LOG_LOKI_URL,
                labels=self.config.get_loki_labels(),
                batch_size=self.config.LOG_LOKI_BATCH_SIZE,
                flush_interval=self.config.LOG_LOKI_FLUSH_INTERVAL,
                timeout=self.config.LOG_LOKI_TIMEOUT,
                retry_times=self.config.LOG_LOKI_RETRY_TIMES,
                retry_backoff=self.config.LOG_LOKI_RETRY_BACKOFF,
                enable_fallback=self.config.LOG_LOKI_ENABLE_FALLBACK,
                fallback_file=self.config.LOG_DIR / self.config.LOG_LOKI_FALLBACK_FILE,
            )
            handler_id = logger.add(
                sink=loki_handler,
                level=cast(str, self.config.LOG_LEVEL_LOKI or self.config.LOG_LEVEL),
                format="{message}",  # Loki 处理器自己格式化
                enqueue=True,  # 异步推送
            )
            self._handler_ids.append(handler_id)

            logger.info(f"Loki 处理器已配置 [URL={self.config.LOG_LOKI_URL}]")

        except ImportError:
            logger.error("无法导入 LokiHandler，请检查 httpx 是否安装")
        except Exception as e:
            logger.error(f"配置 Loki 处理器失败: {e}")

    def _setup_filters(self):
        """配置全局过滤器"""
        # 模块过滤
        if self.config.LOG_FILTER_MODULES:
            module_filter = ModuleFilter(self.config.LOG_FILTER_MODULES)
            logger.add(
                lambda msg: None,  # 空处理器
                filter=module_filter,
            )
            logger.debug(f"模块过滤器已配置: {self.config.LOG_FILTER_MODULES}")

        # 关键词过滤
        if self.config.LOG_FILTER_KEYWORDS:
            keyword_filter = KeywordFilter(self.config.LOG_FILTER_KEYWORDS)
            logger.add(
                lambda msg: None,
                filter=keyword_filter,
            )
            logger.debug(f"关键词过滤器已配置: {self.config.LOG_FILTER_KEYWORDS}")

        # 速率限制
        if self.config.LOG_ENABLE_RATE_LIMIT:
            rate_limit_filter = RateLimitFilter(
                self.config.LOG_RATE_LIMIT_MESSAGES
            )
            logger.add(
                lambda msg: None,
                filter=rate_limit_filter,
            )
            logger.debug(
                f"速率限制过滤器已配置: "
                f"{self.config.LOG_RATE_LIMIT_MESSAGES} msg/s"
            )

        # 敏感信息脱敏
        if self.config.LOG_ENABLE_SANITIZE:
            sanitize_filter = SanitizeFilter(
                self.config.LOG_SANITIZE_FIELDS,
                self.config.LOG_SANITIZE_PATTERN,
            )
            logger.add(
                lambda msg: None,
                filter=sanitize_filter,
            )
            logger.debug(
                f"脱敏过滤器已配置: {len(self.config.LOG_SANITIZE_FIELDS)} 个字段"
            )

    def _setup_context_injection(self):
        """配置上下文注入"""
        if not self.config.LOG_ENABLE_CONTEXT:
            return

        # 配置上下文处理器
        def context_patcher(record):
            """注入上下文信息"""
            context = get_all_context()

            # 注入到 extra 字段
            record["extra"].update(context)

            # 注入环境信息
            record["extra"]["hostname"] = self.hostname
            record["extra"]["app_name"] = self.app_name
            record["extra"]["env"] = self.config.ENV

        logger.configure(patcher=context_patcher)
        logger.debug("上下文注入已配置")

    def _setup_metrics(self):
        """配置指标统计"""
        metrics = get_metrics()

        def metrics_sink(message):
            """指标统计处理器"""
            record = message.record
            level = record["level"].name
            metrics.record(level)

            # 检查错误阈值
            if metrics.check_error_threshold(
                    self.config.LOG_ERROR_THRESHOLD,
                    self.config.LOG_ERROR_WINDOW
            ):
                logger.warning(
                    f"错误日志超过阈值: "
                    f"{self.config.LOG_ERROR_THRESHOLD} 条/"
                    f"{self.config.LOG_ERROR_WINDOW} 秒"
                )

        handler_id = logger.add(
            sink=metrics_sink,
            level="DEBUG",
            format="{message}",
        )
        self._handler_ids.append(handler_id)

        logger.debug("指标统计已配置")

    def shutdown(self):
        """关闭日志系统"""
        if not self.is_initialized:
            return

        logger.info("正在关闭日志系统...")

        # 移除所有处理器
        for handler_id in self._handler_ids:
            try:
                logger.remove(handler_id)
            except ValueError:
                pass

        self._handler_ids.clear()
        self.is_initialized = False

        logger.info("日志系统已关闭")

    def reload(self):
        """重新加载日志配置"""
        logger.info("正在重新加载日志配置...")

        self.shutdown()

        from infoman.config.log import reload_log_config
        self.config = reload_log_config()

        self.initialize()

        logger.info("日志配置已重新加载")


# =================================================================
# 全局实例
# =================================================================

_logger_manager: Optional[LoggerManager] = None


def setup_logger(config: Optional[LogConfig] = None) -> LoggerManager:
    global _logger_manager

    if _logger_manager is None:
        _logger_manager = LoggerManager(config)
        _logger_manager.initialize()

    return _logger_manager


def get_logger_manager() -> Optional[LoggerManager]:
    """获取日志管理器实例"""
    return _logger_manager


def shutdown_logger():
    """关闭日志系统"""
    global _logger_manager

    if _logger_manager is not None:
        _logger_manager.shutdown()
        _logger_manager = None
