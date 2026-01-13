# -*- coding: utf-8 -*-
# @Author	: brotherbaby
# @Date		: 2025/8/22 15:16
# @Last Modified by:   brotherbaby
# @Last Modified time: 2025/8/22 15:16
# Thanks for your comments!

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ExchangeTypeStr(Enum):
    """交换机类型枚举"""
    DIRECT = "direct"
    FANOUT = "fanout"
    TOPIC = "topic"
    HEADERS = "headers"


@dataclass
class QueueConfig:
    """队列配置"""
    name: str
    durable: bool = True
    exclusive: bool = False
    auto_delete: bool = False
    arguments: Optional[Dict] = None


@dataclass
class ExchangeConfig:
    """交换机配置"""
    name: str
    type: ExchangeTypeStr = ExchangeTypeStr.DIRECT
    durable: bool = True


@dataclass
class BindingConfig:
    """绑定配置"""
    queue: str
    exchange: str
    routing_key: str = ""


@dataclass
class RabbitMQConnectionConfig:
    """RabbitMQ 连接配置数据类"""
    host: str = "localhost"
    port: int = 5672
    username: str = "guest"
    password: str = "guest"
    virtual_host: str = "/"
    heartbeat: int = 600
    timeout: int = 10
    exchanges: List[ExchangeConfig] = field(default_factory=list)
    queues: List[QueueConfig] = field(default_factory=list)
    bindings: List[BindingConfig] = field(default_factory=list)
