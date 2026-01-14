# aiomqtt 高级封装 - 基于纯 async/await 架构

import asyncio
import json
import ssl
from typing import Callable, Optional
from loguru import logger
import aiomqtt

from .config import MQTTConfig
from .exceptions import MessageError
from .protocol import parse_message


class MQTTClient:
    """基于 aiomqtt 的 MQTT 客户端

    设计决策：
    - aiomqtt 基于 paho-mqtt 封装，成熟稳定
    - 不自动重连，需要手动实现重连循环（官方推荐模式）
    - 使用 `async for message in client.messages` 异步迭代器
    """

    def __init__(self, config: MQTTConfig):
        """初始化 MQTT 客户端

        Args:
            config: MQTT 配置对象

        注意:
            初始化后不会立即连接，需要调用 connect() 或使用 async with
        """
        self.config = config
        self._client: Optional[aiomqtt.Client] = None
        self._subscriptions: set[str] = set()  # 订阅列表（用于重连恢复）
        self._message_handlers: dict[str, Callable] = {}  # topic → handler 映射
        self._running = False
        self._connected = False  # 修复 P0-2：真实连接状态标志
        self._reconnect_task: Optional[asyncio.Task] = None
        self._message_task: Optional[asyncio.Task] = None

    async def connect(self):
        """连接到 MQTT Broker

        启动后台重连任务，自动处理连接断开和重连

        """
        if self._running:
            logger.warning("客户端已在运行中")
            return

        self._running = True

        self._reconnect_task = asyncio.create_task(
            self._reconnect_loop(), name="mqtt_reconnect"
        )

    async def disconnect(self):
        """断开连接并清理资源"""
        self._running = False
        self._connected = False  # 修复 P0-2：标记为未连接

        # 取消后台任务
        if self._reconnect_task:
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass

        # 取消消息处理任务
        if self._message_task:
            self._message_task.cancel()
            try:
                await self._message_task
            except asyncio.CancelledError:
                pass
        if self._client:
            self._client = None

        logger.info("MQTT 客户端已断开")

    async def __aenter__(self):
        """上下文管理器入口

        示例:
            async with MQTTClient(config) as client:
                # 使用客户端
                pass  # 自动断开连接
        """
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """上下文管理器退出"""
        await self.disconnect()

    async def _reconnect_loop(self):
        """重连循环（aiomqtt 核心模式）

        无限循环尝试连接 MQTT Broker，连接断开后自动重连

        重连策略：
        - 初始间隔：config.reconnect.interval（默认 5 秒）
        - 指数退避：每次失败后间隔乘以 backoff_multiplier
        - 最大间隔：config.reconnect.max_interval（默认 60 秒）
        - 最大次数：config.reconnect.max_attempts（0 = 无限）


        异常处理：
        - aiomqtt.MqttError：连接/协议错误，触发重连
        - asyncio.CancelledError：任务被取消，退出循环
        """
        attempt = 0
        interval = self.config.reconnect.interval

        while self._running:
            try:
                # 创建 TLS 上下文
                tls_context = (
                    self._create_tls_context() if self.config.tls.enabled else None
                )

                # region 调用代码溯源(aiomqtt.Client)
                # aiomqtt.Client 是异步上下文管理器
                # 文档：https://aiomqtt.bo3hm.com/reconnection.html
                # 进入上下文时自动连接
                # endregion
                async with aiomqtt.Client(
                    hostname=self.config.broker_host,
                    port=self.config.broker_port,
                    username=self.config.auth.username,
                    password=self.config.auth.password,
                    identifier=self.config.client_id
                    or None,  # 空字符串 → None = 自动生成
                    clean_session=self.config.clean_session,
                    keepalive=self.config.keepalive,
                    tls_context=tls_context,
                    max_queued_outgoing_messages=self.config.max_queued_messages
                    or None,
                ) as client:
                    self._client = client
                    self._connected = True  # 修复 P0-2：标记为已连接
                    logger.success(
                        f"MQTT 连接成功 - {self.config.broker_host}:{self.config.broker_port}"
                    )

                    # 重置重连计数
                    attempt = 0
                    interval = self.config.reconnect.interval

                    # 恢复订阅
                    await self._restore_subscriptions()

                    # 启动消息处理任务
                    self._message_task = asyncio.create_task(
                        self._message_loop(), name="mqtt_messages"
                    )

                    # 等待消息循环结束（连接断开）
                    await self._message_task

            except aiomqtt.MqttError as e:
                logger.error(f"MQTT 连接失败: {e}")
                self._client = None
                self._connected = False  # 修复 P0-2：标记为未连接

                # 检查重连次数限制
                if self.config.reconnect.max_attempts > 0:
                    if attempt >= self.config.reconnect.max_attempts:
                        logger.error("达到最大重连次数，停止重连")
                        break

                # 计算指数退避延迟
                attempt += 1
                interval = min(
                    interval * self.config.reconnect.backoff_multiplier,
                    self.config.reconnect.max_interval,
                )

                logger.info(f"{interval:.1f}s 后重连（第 {attempt} 次）...")
                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                logger.info("重连任务已取消")
                break

            except Exception as e:
                logger.exception(f"重连循环异常: {e}")
                await asyncio.sleep(interval)

    async def _message_loop(self):
        """消息处理循环（aiomqtt 核心模式）

        使用 async for 迭代消息，替代 gmqtt 的 on_message 回调

        关键特性：
        - 非阻塞：异步迭代器自动 yield 控制权
        - 顺序处理：每条消息按顺序处理
        - 并发处理：每条消息在独立 Task 中处理（不阻塞迭代器）

        异常处理：
        - asyncio.CancelledError：任务被取消，退出循环
        - aiomqtt.MqttError：连接断开/协议错误，重新抛出触发外层重连
        - 其他异常：记录日志，不退出循环
        """
        if not self._client:
            return

        try:
            # region 调用代码溯源(aiomqtt.Client.messages)
            # aiomqtt.Client.messages 是一个异步迭代器
            # 内部调用：
            #   paho.mqtt.client.Client._handle_on_message()
            #   → 将消息放入队列
            #   → aiomqtt 从队列中取出消息
            # GitHub：https://github.com/sbtinstruments/aiomqtt/blob/main/aiomqtt/client.py#L400
            # endregion
            async for message in self._client.messages:
                # 异步处理消息（不阻塞迭代器）
                asyncio.create_task(
                    self._handle_message(message), name=f"handle_{message.topic}"
                )
        except asyncio.CancelledError:
            logger.info("消息处理任务已取消")
            raise
        except aiomqtt.MqttError as e:
            logger.warning(f"消息循环 MQTT 错误: {e}")
            raise  # 关键：重新抛出，让外层重连逻辑处理
        except Exception as e:
            logger.exception(f"消息循环异常: {e}")

    async def _handle_message(self, message: aiomqtt.Message):
        """处理单条消息
        Args:
            message: aiomqtt.Message 对象

        消息处理流程：
        1. 检查 payload 大小
        2. 解码 UTF-8
        3. 解析 JSON
        4. 使用 protocol.parse_message() 验证和解析
        5. 路由到对应处理器
        """

        try:
            # 检查 payload 大小（防御 DoS）
            if len(message.payload) > self.config.max_payload_size:
                logger.warning(
                    f"Payload 过大，已忽略 - "
                    f"topic: {message.topic}, size: {len(message.payload)}"
                )
                return

            try:
                text = message.payload.decode("utf-8")
                data = json.loads(text)
            except UnicodeDecodeError as e:
                logger.error(
                    f"UTF-8 解码失败 - topic: {message.topic}, error: {e!r}, "
                    f"preview: {message.payload[:100]}"
                )
                return
            except json.JSONDecodeError as e:
                logger.error(
                    f"JSON 解析失败 - topic: {message.topic}, error: {e!r}, "
                    f"preview: {text[:100]}"
                )
                return

            # 解析消息类型（使用 dataclass 替代 Box）
            msg = parse_message(data)

            # 路由到对应处理器
            topic_str = str(message.topic)
            handler = self._message_handlers.get(topic_str)

            if handler:
                # 调用处理器
                if asyncio.iscoroutinefunction(handler):
                    await handler(topic_str, msg)
                else:
                    handler(topic_str, msg)
            else:
                # 修复 P0-3：RPC 请求无处理器时，立即返回错误响应（防止调用方超时）
                from .protocol import RPCRequest, RPCResponse
                if isinstance(msg, RPCRequest):
                    logger.warning(
                        f"收到 RPC 请求但无处理器 - topic: {topic_str}, method: {msg.method}"
                    )
                    # 立即发送错误响应
                    error_response = RPCResponse(
                        request_id=msg.request_id,
                        error=f"No RPC handler registered for topic: {topic_str}"
                    )
                    await self.publish(msg.reply_to, json.dumps(error_response.to_dict()), qos=1)
                else:
                    logger.debug(f"收到消息（无处理器）- topic: {topic_str}")

        except MessageError as e:
            logger.error(f"消息解析失败: {e}")
        except Exception as e:
            logger.exception(f"消息处理失败: {e}")

    def subscribe(self, topic: str, handler: Optional[Callable] = None):
        """订阅主题

        修复点：
        - ✅ P0-1: 未连接时不崩溃，队列化订阅

        Args:
            topic: MQTT 主题（支持通配符 +/#）
            handler: 消息处理器
                签名：async def handler(topic: str, message: RPCRequest | RPCResponse)
                或：def handler(topic: str, message: RPCRequest | RPCResponse)

        设计决策：
        - 记录订阅到 _subscriptions set（用于重连恢复）
        - 如果已连接，立即订阅
        - 如果未连接，等待连接后自动订阅

        示例:
            # 同步处理器
            def my_handler(topic, message):
                print(f"收到消息: {topic} - {message}")

            client.subscribe("test/topic", my_handler)

            # 异步处理器
            async def my_async_handler(topic, message):
                await process_message(message)

            client.subscribe("test/topic", my_async_handler)
        """
        # 记录订阅（用于重连恢复）
        self._subscriptions.add(topic)

        # 注册处理器
        if handler:
            self._message_handlers[topic] = handler

        # 如果已连接，立即订阅
        if self._client:
            asyncio.create_task(self._do_subscribe(topic))
        else:
            logger.info(f"订阅已队列化（等待连接）- topic: {topic}")

    async def _do_subscribe(self, topic: str):
        """执行订阅（内部方法）

        Args:
            topic: MQTT 主题
        """
        if not self._client:
            return

        try:
            await self._client.subscribe(topic)
            logger.success(f"订阅成功 - topic: {topic}")
        except aiomqtt.MqttError as e:
            logger.error(f"订阅失败 - topic: {topic}, error: {e}")

    async def _restore_subscriptions(self):
        """恢复所有订阅（重连后调用）

        注意：
        - aiomqtt 不会记录订阅列表（源码中没有 _subscriptions 存储）
        - 连接成功回调（_on_connect）不会恢复订阅
        - clean_session=False 只是服务器保持会话，客户端仍需手动重新订阅
        - 本方法在每次重连成功后调用，手动恢复 _subscriptions 中的订阅
        """
        if not self._subscriptions:
            return

        logger.info(f"恢复 {len(self._subscriptions)} 个订阅...")

        for topic in self._subscriptions:
            await self._do_subscribe(topic)

        logger.success("订阅恢复完成")

    async def publish(self, topic: str, payload: str, qos: int = 0):
        """发布消息

        修复点：
        - ✅ P1-2: 未连接时记录警告

        Args:
            topic: 目标主题
            payload: 消息载荷（字符串）
            qos: QoS 等级（0/1/2）

        异常:
            aiomqtt.MqttError: 发布失败
        """
        if not self._client:
            logger.warning(f"发布失败：客户端未连接 - topic: {topic}")
            return

        try:
            await self._client.publish(topic, payload, qos=qos)
            logger.debug(f"消息已发布 - topic: {topic}, qos: {qos}")
        except aiomqtt.MqttError as e:
            logger.error(f"发布失败 - topic: {topic}, error: {e}")

    def _create_tls_context(self) -> ssl.SSLContext:
        """创建 TLS 上下文

        Returns:
            ssl.SSLContext 对象

        配置项：
        - ca_certs: CA 证书路径
        - certfile: 客户端证书路径
        - keyfile: 客户端私钥路径
        - verify_mode: 验证模式（CERT_REQUIRED/CERT_OPTIONAL/CERT_NONE）
        - check_hostname: 是否验证主机名
        """
        context = ssl.create_default_context()

        # 加载 CA 证书
        if self.config.tls.ca_certs:
            context.load_verify_locations(cafile=str(self.config.tls.ca_certs))

        # 加载客户端证书（双向认证）
        if self.config.tls.certfile:
            context.load_cert_chain(
                certfile=str(self.config.tls.certfile),
                keyfile=str(self.config.tls.keyfile)
                if self.config.tls.keyfile
                else None,
            )

        # 验证模式
        if self.config.tls.verify_mode == "CERT_REQUIRED":
            context.check_hostname = self.config.tls.check_hostname
            context.verify_mode = ssl.CERT_REQUIRED
        elif self.config.tls.verify_mode == "CERT_OPTIONAL":
            context.verify_mode = ssl.CERT_OPTIONAL
        elif self.config.tls.verify_mode == "CERT_NONE":
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        return context

    @property
    def is_connected(self) -> bool:
        """检查连接状态

        修复 P0-2：使用独立标志位而非对象存在性

        Returns:
            True = 已连接，False = 未连接

        注意:
            连接成功后 _connected 设为 True
            连接断开或失败时 _connected 设为 False
        """
        return self._connected
