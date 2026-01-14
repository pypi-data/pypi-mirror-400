# aiomqtt 高级封装 - 基于纯 async/await 架构

import asyncio
import os
import ssl
from typing import Callable, Optional, TYPE_CHECKING, Any
from loguru import logger
import aiomqtt
from paho.mqtt.matcher import MQTTMatcher

from .config import MQTTConfig

if TYPE_CHECKING:
    from .client import MQTTClient


class MQTTClient:
    """基于 aiomqtt 的 MQTT 客户端

    设计决策：
    - aiomqtt 基于 paho-mqtt 封装，成熟稳定
    - 不自动重连，需要手动实现重连循环（官方推荐模式）
    - 使用 `async for message in client.messages` 异步迭代器


    并发安全:
        - ✅ 单 loop 内并发调用 subscribe/unsubscribe：安全

    示例:
        # ✅ 正确：单 loop
        async def main():
            client = MQTTClient(config)
            await client.connect()
            client.subscribe("topic", handler1)  # 安全
            client.subscribe("topic", handler2)  # 安全

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

        # Raw 订阅（使用 MQTTMatcher 进行通配符匹配）
        # _raw_matcher 是核心匹配引擎（用于 iter_match）
        # _raw_handlers 是辅助追踪结构（因 MQTTMatcher 不支持 getitem/contains）
        self._raw_matcher = MQTTMatcher()
        self._raw_handlers: dict[str, list[Callable]] = {}

        self._running = False
        self._connected = False  # 真实连接状态标志
        self._reconnect_task: Optional[asyncio.Task] = None
        self._message_task: Optional[asyncio.Task] = None
        self._tls_context: Optional[ssl.SSLContext] = None  # TLS 上下文（复用）

        # 消息处理队列和 Workers（
        self._message_queue: asyncio.Queue = asyncio.Queue(
            maxsize=config.message_queue_maxsize
        )
        self._workers: list[asyncio.Task] = []
        # Worker 数量：默认 CPU核数×2（IO-bound 最优）
        self._num_workers = config.num_workers or (os.cpu_count() or 1) * 2

    async def connect(self):
        """连接到 MQTT Broker

        启动后台重连任务，自动处理连接断开和重连

        """
        if self._running:
            logger.warning("客户端已在运行中")
            return

        self._running = True

        # 创建 TLS 上下文（只创建一次，可复用）
        if self.config.tls.enabled:
            self._tls_context = self._create_tls_context()

        # 创建 aiomqtt.Client（只创建一次，在重连循环中复用）
        self._client = aiomqtt.Client(
            hostname=self.config.broker_host,
            port=self.config.broker_port,
            username=self.config.auth.username,
            password=self.config.auth.password,
            identifier=self.config.client_id or None,
            clean_session=self.config.clean_session,
            keepalive=self.config.keepalive,
            tls_context=self._tls_context,
            max_queued_outgoing_messages=self.config.max_queued_messages or None,
        )

        # 启动消息处理 workers
        for i in range(self._num_workers):
            worker = asyncio.create_task(self._worker(i), name=f"mqtt_worker_{i}")
            self._workers.append(worker)

        self._reconnect_task = asyncio.create_task(
            self._reconnect_loop(), name="mqtt_reconnect"
        )

        # 等待首次连接建立（最多 60 秒）
        for _ in range(600):  # 60 秒超时，每次检查 0.1 秒
            if self._connected:
                break
            await asyncio.sleep(0.1)
        else:
            self._running = False  # 清理状态
            raise TimeoutError(
                f"MQTT 连接超时（60秒）：{self.config.broker_host}:{self.config.broker_port}"
            )

    async def disconnect(self):
        """断开连接并清理资源"""
        self._running = False
        self._connected = False  # ：标记为未连接

        # 等待 workers 处理完队列
        if self._workers:
            # 等待所有 workers 完成（最多 5 秒）
            _, pending = await asyncio.wait(self._workers, timeout=5.0)
            # 取消未完成的 workers
            for w in pending:
                w.cancel()
            self._workers.clear()

        # 取消后台任务
        if self._reconnect_task:
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass

        # 取消消息处理任务（修复 P0-D）
        # 这会导致 _reconnect_loop 中的 async with 块退出，aiomqtt 自动清理连接
        if self._message_task:
            self._message_task.cancel()
            try:
                await self._message_task
            except asyncio.CancelledError:
                pass

        # 清理 Client 和 TLS 上下文
        self._client = None
        self._tls_context = None

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

        关键改进：
        - Client 在 connect() 中创建（只创建一次）
        - 循环内只使用 async with self._client: 来连接
        - 符合 aiomqtt 官方推荐模式
        """
        attempt = 0
        interval = self.config.reconnect.interval

        while self._running:
            try:
                # 使用已创建的 Client（在 connect() 中创建）
                # async with 会连接，退出时会自动断开
                async with self._client:
                    self._connected = True  # 修复 P0-2：标记为已连接

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
        """消息接收循环

        使用 async for 迭代消息，将消息放入队列由 workers 处理

        关键改进：
        - 接收和处理分离：避免高吞吐下任务爆炸
        - 有界队列：maxsize 可配置（默认 100k），作为保险丝
        - 队列满时阻塞：形成自然背压，CPU/延迟会变明显（扩容信号）

        异常处理：
        - asyncio.CancelledError：任务被取消，退出循环
        - aiomqtt.MqttError：连接断开/协议错误，重新抛出触发外层重连
        - 其他异常：记录日志，不退出循环
        """
        if not self._client:
            return

        try:
            async for message in self._client.messages:
                # 将消息放入队列（阻塞等待，形成自然背压）
                await self._message_queue.put(message)
        except asyncio.CancelledError:
            logger.info("消息处理任务已取消")
            raise
        except aiomqtt.MqttError as e:
            logger.warning(f"消息循环 MQTT 错误: {e}")
            raise  # 关键：重新抛出，让外层重连逻辑处理
        except Exception as e:
            logger.exception(f"消息循环异常: {e}")

    async def _worker(self, worker_id: int):
        """消息处理 Worker

        从队列中取消息并处理，支持并发控制

        Args:
            worker_id: Worker ID（用于日志）

        设计要点：
        - 并发上限可控（默认 16 个 worker）
        - 异常隔离（worker 崩溃不影响其他 worker）
        - 优雅退出（_running=False 时退出）
        """
        while self._running:
            try:
                # 从队列取消息（带超时，避免无法退出） asyncio.Queue 是原子安全的
                message = await asyncio.wait_for(self._message_queue.get(), timeout=1.0)
                # 处理消息
                await self._handle_message(message)
            except asyncio.TimeoutError:
                # 队列为空，继续等待
                continue
            except asyncio.CancelledError:
                logger.debug(f"Worker {worker_id} 被取消")
                break
            except Exception as e:
                logger.exception(f"Worker {worker_id} 异常: {e}")
                # 继续运行，不退出

    def subscribe(self, pattern: str, handler: Callable[[str, bytes], Any]):
        """订阅原始消息 (bytes)

        Args:
            pattern: MQTT topic pattern (支持通配符 +/#)
            handler: 回调函数
                - 签名: async def handler(topic: str, payload: bytes)
                - topic: 实际收到消息的 topic
                - payload: 原始 bytes 数据 (未解码)

        并发行为:
            - 同一 pattern 的多个 handlers 按注册顺序**顺序调用**（非并发）
            - 如需并发处理，请在 handler 内部使用 asyncio.create_task()

        注意:
            - 订阅在重连时自动恢复
        """
        if pattern not in self._raw_handlers:
            self._raw_handlers[pattern] = []
            self._raw_matcher[pattern] = self._raw_handlers[pattern]

            # 立即向 MQTT broker 订阅
            if self._client:
                # 使用 asyncio.create_task 避免阻塞
                asyncio.create_task(self._client.subscribe(pattern))

        self._raw_handlers[pattern].append(handler)
        self._subscriptions.add(pattern)

        logger.debug(f"订阅已注册 - pattern: {pattern}")

    @property
    def raw(self) -> aiomqtt.Client:
        """暴露底层 aiomqtt.Client，用于高级用法

        使用场景：
            await client.raw.publish(topic, payload, qos=1, retain=False)

        Raises:
            RuntimeError: 客户端未连接
        """
        if not self._client:
            raise RuntimeError("Client not connected")
        return self._client

    def unsubscribe(self, pattern: str, handler: Optional[Callable] = None):
        """取消订阅

        Args:
            pattern: MQTT topic pattern
            handler: 要移除的 handler（None = 移除所有）

        注意:
            - 只移除内存中的 handler，不发送 MQTT UNSUBSCRIBE
            - 如需完全取消订阅，下次重连时会自动生效
        """
        if pattern not in self._raw_handlers:
            logger.debug(f"取消订阅失败：pattern 不存在 - {pattern}")
            return

        if handler is None:
            del self._raw_handlers[pattern]
            del self._raw_matcher[pattern]
            self._subscriptions.discard(pattern)
            logger.debug(f"取消订阅（全部）- pattern: {pattern}")
        else:
            handlers = self._raw_handlers[pattern]
            if handler in handlers:
                handlers.remove(handler)

                if not handlers:
                    del self._raw_handlers[pattern]
                    del self._raw_matcher[pattern]
                    self._subscriptions.discard(pattern)
                    logger.debug(
                        f"取消订阅（全部，最后一个 handler）- pattern: {pattern}"
                    )
                else:
                    logger.debug(
                        f"取消订阅（部分）- pattern: {pattern}, 剩余 {len(handlers)} 个 handler"
                    )
            else:
                logger.debug(f"取消订阅失败：handler 不存在 - pattern: {pattern}")

    async def _handle_message(self, message: aiomqtt.Message):
        """处理单条消息（传输层，只处理 bytes）

        核心改变：
        1. 不再解析 JSON/协议
        2. 将 payload (bytes) 分发给 raw handlers
        3. 不再区分 RPC/Event（让上层处理）

        Args:
            message: aiomqtt.Message 对象
        """
        topic_str = str(message.topic)
        payload = message.payload  # bytes 类型

        # 检查 payload 大小（防御 DoS）
        if len(payload) > self.config.max_payload_size:
            logger.warning(
                f"Payload 过大，已忽略 - topic: {topic_str}, size: {len(payload)}"
            )
            return

        # === 唯一职责：将 bytes 分发给所有匹配的 handlers ===
        # MQTTMatcher.iter_match 返回值列表，不是 (pattern, handlers) 元组
        for handlers in self._raw_matcher.iter_match(topic_str):
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(topic_str, payload)  # 传递 bytes！
                    else:
                        handler(topic_str, payload)
                except Exception as e:
                    logger.exception(f"Handler 异常 - topic: {topic_str}, error: {e}")

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

        # 创建快照，避免遍历时被修改（修复 P0-C）
        topics = list(self._subscriptions)
        logger.info(f"恢复 {len(topics)} 个订阅...")

        for topic in topics:
            try:
                await self._client.subscribe(topic)
            except aiomqtt.MqttError as e:
                logger.error(f"恢复订阅失败 - topic: {topic}, error: {e}")

        logger.success("订阅恢复完成")

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
