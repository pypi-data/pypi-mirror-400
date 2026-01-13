# -*- coding: utf-8 -*-
# @Author	: brotherbaby
# @Date		: 2025/8/22 10:18
# @Last Modified by:   brotherbaby
# @Last Modified time: 2025/8/22 10:18
# Thanks for your comments!

import asyncio
import json
import logging
import traceback
import uuid
from typing import Any, Callable, Dict, Optional, Union, Awaitable

from aio_pika import connect_robust, Message, ExchangeType
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection

from .defs import RabbitMQConnectionConfig

logger = logging.getLogger(__name__)


class AsyncRabbitMQClient:
    """异步 RabbitMQ 客户端封装"""

    def __init__(self, config: RabbitMQConnectionConfig):
        self.config = config
        self._connection: Optional[AbstractRobustConnection] = None
        self._channel = None
        self._exchanges = {}
        self._queues = {}
        self._consuming_tasks = []
        self._rpc_futures = {}  # 用于存储 RPC 回调的 futures
        self._connected = False
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """初始化 RabbitMQ 连接、交换机和队列"""
        await self.connect()
        await self.setup_infrastructure()

    async def connect(self) -> None:
        """建立 RabbitMQ 连接"""
        if self._connected:
            return

        async with self._lock:
            if self._connected:
                return

            try:
                # 创建连接
                self._connection = await connect_robust(
                    host=self.config.host,
                    port=self.config.port,
                    login=self.config.username,
                    password=self.config.password,
                    virtualhost=self.config.virtual_host,
                    heartbeat=self.config.heartbeat,
                    timeout=self.config.timeout
                )

                # 创建通道
                self._channel = await self._connection.channel()

                # 设置 QoS，prefetch_count同时消费的消息数量
                await self._channel.set_qos(prefetch_count=20)

                self._connected = True
                logger.info("RabbitMQ connection established successfully")

            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise

    async def setup_infrastructure(self) -> None:
        """设置交换机和队列基础设施"""
        # 声明交换机
        for exchange_config in self.config.exchanges:
            await self.declare_exchange(
                exchange_config.name,
                ExchangeType[exchange_config.type.value.upper()],
                exchange_config.durable
            )

        # 声明队列
        for queue_config in self.config.queues:
            await self.declare_queue(
                queue_config.name,
                queue_config.durable,
                queue_config.exclusive,
                queue_config.auto_delete,
                queue_config.arguments
            )

        # 声明绑定
        for binding_config in self.config.bindings:
            await self.bind_queue(
                binding_config.queue,
                binding_config.exchange,
                binding_config.routing_key
            )

    async def close(self) -> None:
        """关闭 RabbitMQ 连接"""
        async with self._lock:
            if not self._connected:
                return

            try:
                # 取消所有消费者
                for task in self._consuming_tasks:
                    if not task.done():
                        task.cancel()

                # 等待所有消费者任务完成
                if self._consuming_tasks:
                    await asyncio.gather(*self._consuming_tasks, return_exceptions=True)

                # 关闭通道和连接
                if self._channel and not self._channel.is_closed:
                    await self._channel.close()

                if self._connection and not self._connection.is_closed:
                    await self._connection.close()

            except Exception:
                logger.error(f"Error during close: {traceback.format_exc()}")
            finally:
                self._connected = False
                self._consuming_tasks.clear()
                self._exchanges.clear()
                self._queues.clear()
                self._rpc_futures.clear()
                logger.info("RabbitMQ connection closed")

    async def ensure_connection(self) -> None:
        """确保连接可用，如果不可用则重新连接"""
        try:
            if (not self._connected or
                    self._connection is None or
                    self._connection.is_closed or
                    self._channel is None or
                    self._channel.is_closed):
                logger.warning("Connection is not healthy, reconnecting...")
                await self.close()
                await self.connect()
                await self.setup_infrastructure()  # 重新设置基础设施
        except Exception as e:
            logger.error(f"Error ensuring connection: {e}")
            # 尝试重新建立连接
            await asyncio.sleep(1)  # 等待一段时间后重试
            await self.ensure_connection()

    async def declare_exchange(
            self,
            exchange_name: str,
            exchange_type: ExchangeType = ExchangeType.DIRECT,
            durable: bool = True
    ) -> None:
        """声明交换机"""
        await self.ensure_connection()

        if exchange_name not in self._exchanges:
            if not exchange_type:
                exchange_type = ExchangeType.DIRECT
            exchange = await self._channel.declare_exchange(
                exchange_name,
                exchange_type,
                durable=durable
            )
            self._exchanges[exchange_name] = exchange
            logger.info(f"Exchange declared: {exchange_name}")

    async def declare_queue(
            self,
            queue_name: str,
            durable: bool = True,
            exclusive: bool = False,
            auto_delete: bool = False,
            arguments: Optional[Dict] = None
    ) -> None:
        """声明队列"""
        await self.ensure_connection()

        if queue_name not in self._queues:
            queue = await self._channel.declare_queue(
                queue_name,
                durable=durable,
                exclusive=exclusive,
                auto_delete=auto_delete,
                arguments=arguments
            )
            self._queues[queue_name] = queue
            logger.info(f"Queue declared: {queue_name}")

    async def bind_queue(
            self,
            queue_name: str,
            exchange_name: str,
            routing_key: str = ""
    ) -> None:
        """绑定队列到交换机"""
        await self.ensure_connection()

        if queue_name not in self._queues:
            await self.declare_queue(queue_name)

        if exchange_name not in self._exchanges:
            await self.declare_exchange(exchange_name)

        queue = self._queues[queue_name]
        exchange = self._exchanges[exchange_name]

        await queue.bind(exchange, routing_key)
        logger.info(f"Queue {queue_name} bound to exchange {exchange_name} with routing key {routing_key}")

    async def publish(
            self,
            exchange_name: str,
            routing_key: str,
            message: Union[Dict, str, bytes],
            exchange_type: ExchangeType = None,
            persistent: bool = True,
            headers: Optional[Dict] = None,
            properties: Optional[Dict] = None
    ) -> None:
        """
        发布消息到交换机

        :param exchange_name: 交换机名称
        :param routing_key: 路由键
        :param message: 消息内容，可以是字典、字符串或字节
        :param exchange_type:
        :param persistent: 是否持久化消息
        :param headers: 消息头
        :param properties:
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await self.ensure_connection()

                if exchange_name == "":  # 默认交换机
                    exchange = self._channel.default_exchange
                else:
                    if exchange_name not in self._exchanges:
                        await self.declare_exchange(exchange_name, exchange_type)
                    exchange = self._exchanges[exchange_name]

                # 序列化消息
                if isinstance(message, dict):
                    message_body = json.dumps(message).encode()
                    content_type = "application/json"
                elif isinstance(message, str):
                    message_body = message.encode()
                    content_type = "text/plain"
                else:
                    message_body = message
                    content_type = "application/octet-stream"

                # 处理properties
                properties = properties or {}
                correlation_id = properties.get('correlation_id')
                reply_to = properties.get('reply_to')
                message_id = properties.get('message_id')
                content_encoding = properties.get('content_encoding')
                priority = properties.get('priority')
                expiration = properties.get('expiration')
                timestamp = properties.get('timestamp')
                type_ = properties.get('type')
                user_id = properties.get('user_id')
                app_id = properties.get('app_id')

                # 创建消息
                delivery_mode = 2 if persistent else 1
                message_obj = Message(
                    message_body,
                    delivery_mode=delivery_mode,
                    headers=headers or {},
                    content_type=content_type,
                    content_encoding=content_encoding,
                    priority=priority,
                    correlation_id=correlation_id,
                    reply_to=reply_to,
                    expiration=expiration,
                    message_id=message_id,
                    timestamp=timestamp,
                    type=type_,
                    user_id=user_id,
                    app_id=app_id
                )

                # 发布消息
                await exchange.publish(message_obj, routing_key)
                logger.info(f"Message published to {exchange_name} with routing key {routing_key}")

                break
            except Exception as e:
                logger.error(f"Publish attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1)

    async def consume(
            self,
            queue_name: str,
            callback: Callable[[Dict, Any], Awaitable[None]],
            auto_ack: bool = False,
            prefetch_count: int = 20
    ) -> None:
        """
        消费队列消息

        :param queue_name: 队列名称
        :param callback: 消息处理回调函数
        :param auto_ack: 是否自动确认消息
        :param prefetch_count: 预取消息数量
        """
        await self.ensure_connection()

        if queue_name not in self._queues:
            await self.declare_queue(queue_name)

        queue = self._queues[queue_name]

        # 设置 QoS
        await self._channel.set_qos(prefetch_count=prefetch_count)

        # 定义消息处理函数
        async def process_message(message: AbstractIncomingMessage) -> None:
            try:
                # 解析消息
                if message.content_type == "application/json":
                    body = json.loads(message.body.decode())
                elif message.content_type == "text/plain":
                    body = message.body.decode()
                else:
                    body = message.body

                # 检查是否是 RPC 请求
                is_rpc = message.reply_to and message.correlation_id

                # 处理消息
                result = await callback(body, message)

                # 如果是 RPC 请求，发送响应
                if is_rpc and result is not None:
                    await self.publish(
                        exchange_name="",  # 默认交换机
                        routing_key=message.reply_to,
                        message=result,
                        exchange_type=ExchangeType.DIRECT,
                        properties={"correlation_id": message.correlation_id}
                    )

                # 确认消息
                if not auto_ack:
                    await message.ack()

            except Exception as e:
                logger.error(f"Error processing message: {e}")

                # 拒绝消息并重新入队
                if not auto_ack:
                    await message.nack(requeue=True)

        # 开始消费
        consumer_tag = f"consumer-{queue_name}-{uuid.uuid4().hex[:8]}"
        task = asyncio.create_task(
            queue.consume(process_message, no_ack=auto_ack, consumer_tag=consumer_tag)
        )

        self._consuming_tasks.append(task)
        logger.info(f"Started consuming queue: {queue_name}")

    async def rpc_call(
            self,
            exchange_name: str,
            routing_key: str,
            message: Union[Dict, str, bytes],
            exchange_type: ExchangeType = ExchangeType.TOPIC,
            timeout: int = 30
    ) -> Any:
        """
        RPC 调用 - 发送请求并等待响应

        :param exchange_name: 交换机名称
        :param routing_key: 路由键
        :param message: 请求消息
        :param timeout: 超时时间（秒）
        :return: 响应消息
        """
        await self.ensure_connection()

        # 创建临时回调队列
        callback_queue = await self._channel.declare_queue(
            exclusive=True, auto_delete=True
        )
        callback_queue_name = callback_queue.name

        # 生成唯一关联ID
        correlation_id = str(uuid.uuid4())

        # 创建 Future 对象用于等待响应
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        self._rpc_futures[correlation_id] = future

        consumer_tag = None
        try:
            # 启动消费者监听回调队列
            async def on_response(message: AbstractIncomingMessage) -> None:
                if message.correlation_id == correlation_id:
                    try:
                        # 解析响应
                        if message.content_type == "application/json":
                            body = json.loads(message.body.decode())
                        elif message.content_type == "text/plain":
                            body = message.body.decode()
                        else:
                            body = message.body

                        # 设置 Future 结果
                        if correlation_id in self._rpc_futures:
                            self._rpc_futures[correlation_id].set_result(body)
                            await message.ack()
                    except Exception as e:
                        logger.error(f"Error processing RPC response: {traceback.format_exc()}")
                        if correlation_id in self._rpc_futures:
                            self._rpc_futures[correlation_id].set_exception(e)

            consumer_tag = f"rpc-consumer-{correlation_id}"
            await callback_queue.consume(on_response, no_ack=True, consumer_tag=consumer_tag)

            # 发送 RPC 请求
            await self.publish(
                exchange_name=exchange_name,
                routing_key=routing_key,
                message=message,
                exchange_type=exchange_type,
                properties={
                    "reply_to": callback_queue_name,
                    "correlation_id": correlation_id
                }
            )

            # 等待响应或超时
            try:
                result = await asyncio.wait_for(future, timeout=timeout)
                return result
            except asyncio.TimeoutError:
                logger.error(f"RPC call timed out after {timeout} seconds")
                raise TimeoutError(f"RPC call timed out after {timeout} seconds")

        finally:
            # 清理
            if correlation_id in self._rpc_futures:
                del self._rpc_futures[correlation_id]
            # 先取消消费者，再删除队列
            try:
                if consumer_tag and callback_queue:
                    # 取消消费者
                    await callback_queue.cancel(consumer_tag)
                    # 等待一小段时间确保消费者完全取消
                    await asyncio.sleep(0.1)
            except Exception as e:
                logger.warning(f"Error cancelling RPC consumer: {e}")

            # 安全删除队列，增加重试机制
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await callback_queue.delete()
                    logger.debug(f"Successfully deleted RPC callback queue: {callback_queue_name}")
                    break
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} to delete queue failed: {e}")
                    if attempt == max_retries - 1:
                        logger.error(
                            f"Failed to delete RPC callback queue after {max_retries} attempts: {callback_queue_name}")
                    else:
                        await asyncio.sleep(0.5 * (attempt + 1))

    async def query_mq(
            self,
            exchange_name: str,
            rk: str,
            message: Union[Dict, str, bytes],
            exchange_type: ExchangeType = ExchangeType.TOPIC,
            timeout: int = 30
    ) -> Any:
        """
        调用远程服务方法（RPC 调用的简化封装）

        :param exchange_name: 交换机名称
        :param rk: 路由键
        :param message: 消息内容
        :param timeout: 超时时间（秒）
        :return: 远程方法执行结果
        """
        return await self.rpc_call(exchange_name, rk, message, exchange_type, timeout)
