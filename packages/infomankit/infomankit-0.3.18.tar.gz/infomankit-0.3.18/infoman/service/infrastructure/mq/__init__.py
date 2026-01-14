# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
消息队列基础设施

支持:
- NATS: 高性能消息队列
"""

from .manager import NATSManager

__all__ = [
    "NATSManager",
]
