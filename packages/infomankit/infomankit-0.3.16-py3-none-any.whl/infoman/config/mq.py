# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/12/22 21:39
# Author     ：Maxwell
# Description：
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class MessageQueueConfig(BaseSettings):
    # ========== NATS ==========
    NATS_ENABLED: bool = Field(default=False, description="是否启用 NATS")
    NATS_SERVERS: List[str] = Field(default=[], description="NATS 服务器列表")
    NATS_NAME: str = Field(default="infoman", description="客户端名称")
    NATS_MAX_RECONNECT_ATTEMPTS: int = Field(default=10, description="最大重连次数")
    NATS_RECONNECT_TIME_WAIT: int = Field(default=2, description="重连等待时间（秒）")

    @property
    def nats_configured(self) -> bool:
        return self.NATS_ENABLED and len(self.NATS_SERVERS) > 0

