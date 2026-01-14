#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""
应用启动入口（库模式）

作为基础库使用时，支持：
1. 直接启动内置应用：python -m infoman.service.launch
2. 启动用户应用：python -m infoman.service.launch --app your_module:app
3. 作为库函数调用：from infoman.service.launch import serve

支持多种 ASGI 服务器：
- granian (推荐生产环境，Rust 实现，性能最佳)
- uvicorn (开发环境友好，热重载)
- gunicorn (传统部署)
"""

import os
from typing import Optional, Dict, Any
from loguru import logger


def serve(
    app_target: str = "infoman.service.app:application",
    server: str = "granian",
    host: Optional[str] = None,
    port: Optional[int] = None,
    workers: Optional[int] = None,
    threads: Optional[int] = None,
    reload: Optional[bool] = None,
    log_level: Optional[str] = None,
    **kwargs
):
    """
    启动 ASGI 应用服务器（库函数）

    Args:
        app_target: 应用目标 (格式: "module.path:app_instance")
        server: 服务器类型 (granian/uvicorn/gunicorn)
        host: 监听地址
        port: 监听端口
        workers: 工作进程数
        threads: 线程数（仅 Granian）
        reload: 是否启用热重载
        log_level: 日志级别
        **kwargs: 其他服务器特定参数

    Examples:
        >>> # 启动默认应用
        >>> from infoman.service.launch import serve
        >>> serve()

        >>> # 启动自定义应用
        >>> serve(app_target="myapp.main:app", port=8080)

        >>> # 生产环境配置
        >>> serve(
        ...     app_target="myapp.main:app",
        ...     server="granian",
        ...     workers=4,
        ...     reload=False,
        ...     log_level="info"
        ... )
    """
    # 导入配置（优先使用参数，其次使用配置文件）
    try:
        from infoman.config import settings
    except ImportError:
        settings = None

    # 参数优先级：函数参数 > 配置文件 > 默认值
    # 注意：在 macOS 上使用 Granian 时，0.0.0.0 可能导致 "Can't assign requested address" 错误
    import platform

    # 确定主机地址
    if host:
        # 用户明确指定，直接使用
        resolved_host = host
    elif settings and settings.APP_HOST != "0.0.0.0":
        # 配置文件中有非默认值，使用配置
        resolved_host = settings.APP_HOST
    else:
        # 使用平台相关的默认值
        if server == "granian" and platform.system() == "Darwin":
            # macOS + Granian: 使用 127.0.0.1
            resolved_host = "127.0.0.1"
        else:
            # 其他情况：使用 0.0.0.0
            resolved_host = "0.0.0.0"

    config = {
        "host": resolved_host,
        "port": port or (settings.APP_PORT if settings else 8000),
        "workers": workers or (settings.APP_WORKERS if settings and hasattr(settings, "APP_WORKERS") else 2),
        "reload": reload if reload is not None else (settings.is_dev if settings else False),
        "log_level": log_level or (settings.LOG_LEVEL.lower() if settings and hasattr(settings, "LOG_LEVEL") else "info"),
        "app_name": settings.APP_NAME if settings else "Application",
        "env": settings.ENV if settings else "unknown",
        "docs_url": settings.DOCS_URL if settings and hasattr(settings, "DOCS_URL") else "/docs",
    }

    # 合并 kwargs
    config.update(kwargs)

    # 根据服务器类型启动
    if server == "granian":
        _run_granian(app_target, config)
    elif server == "uvicorn":
        _run_uvicorn(app_target, config)
    elif server == "gunicorn":
        _run_gunicorn(app_target, config)
    else:
        raise ValueError(f"不支持的服务器类型: {server}")


def _run_granian(app_target: str, config: Dict[str, Any]):
    """使用 Granian 启动（内部函数）"""
    try:
        from granian import Granian
        from granian.constants import Interfaces, Loops
    except ImportError:
        raise ImportError(
            "Granian 未安装。请运行: pip install granian\n"
            "或安装完整 web 依赖: pip install infomankit[web]"
        )

    print(f"🚀 使用 Granian 启动 [{config['app_name']}]")
    print(f"   应用: {app_target}")
    print(f"   环境: {config['env']}")
    print(f"   地址: http://{config['host']}:{config['port']}")
    print(f"   文档: http://{config['host']}:{config['port']}{config['docs_url']}")
    print(f"   进程: {config['workers']} workers")
    # 创建 Granian 实例（仅使用核心兼容参数）
    # Granian 2.6.0+ 的核心参数
    app = Granian(
        target=app_target,
        address=config["host"],
        port=int(config["port"]),
        interface=Interfaces.ASGI,
        workers=config["workers"],
        loop=Loops.auto,
        log_level=config["log_level"],
        reload=config["reload"],
    )
    app.serve()


def _run_uvicorn(app_target: str, config: Dict[str, Any]):
    """使用 Uvicorn 启动（内部函数）"""
    try:
        import uvicorn
    except ImportError:
        raise ImportError(
            "Uvicorn 未安装。请运行: pip install uvicorn\n"
            "或安装完整 web 依赖: pip install infomankit[web]"
        )

    print(f"🚀 使用 Uvicorn 启动 [{config['app_name']}]")
    print(f"   应用: {app_target}")
    print(f"   环境: {config['env']}")
    print(f"   地址: http://{config['host']}:{config['port']}")
    uvicorn.run(
        app_target,
        host=config["host"],
        port=int(config["port"]),
        reload=config["reload"],
        log_level=config["log_level"],
        access_log=config.get("access_log", config["reload"]),
        workers=config["workers"] if not config["reload"] else 1,  # reload 模式只能单进程
    )


def _run_gunicorn(app_target: str, config: Dict[str, Any]):
    """使用 Gunicorn 启动（内部函数）"""
    try:
        import gunicorn
    except ImportError:
        raise ImportError(
            "Gunicorn 未安装。请运行: pip install gunicorn\n"
            "注意: Gunicorn 仅支持 Linux/macOS"
        )

    print(f"🚀 使用 Gunicorn 启动 [{config['app_name']}]")
    print(f"   应用: {app_target}")
    print(f"   环境: {config['env']}")
    print(f"   地址: http://{config['host']}:{config['port']}")

    # Gunicorn 配置
    bind_address = f"{config['host']}:{config['port']}"
    worker_class = "uvicorn.workers.UvicornWorker"
    workers = config["workers"]
    os.system(
        f'gunicorn {app_target} '
        f'-b {bind_address} '
        f'-w {workers} '
        f'-k {worker_class} '
        f'--log-level {config["log_level"]} '
        f'--access-logfile - '
        f'--error-logfile -'
    )


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Infoman Service Launcher - 启动 ASGI 应用服务器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 启动内置应用
  python -m infoman.service.launch

  # 启动自定义应用
  python -m infoman.service.launch --app myapp.main:app

  # 生产环境配置
  python -m infoman.service.launch --server granian --workers 4 --port 8080

  # 开发环境热重载
  python -m infoman.service.launch --server uvicorn --reload
        """
    )

    parser.add_argument(
        "--app",
        default="infoman.service.app:application",
        help="应用目标 (格式: module.path:app_instance, 默认: infoman.service.app:application)",
    )
    parser.add_argument(
        "--server",
        choices=["granian", "uvicorn", "gunicorn"],
        default="granian",
        help="选择 ASGI 服务器 (默认: granian)",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="监听地址 (默认: 从配置文件读取或 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="监听端口 (默认: 从配置文件读取或 8000)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="工作进程数 (默认: 从配置文件读取或 2)",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=None,
        help="线程数 (仅 Granian, 默认: 1)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="启用热重载 (开发环境)",
    )
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error", "critical"],
        default=None,
        help="日志级别 (默认: info)",
    )

    args = parser.parse_args()

    # 调用 serve 函数
    serve(
        app_target=args.app,
        server=args.server,
        host=args.host,
        port=args.port,
        workers=args.workers,
        threads=args.threads,
        reload=args.reload,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main()
