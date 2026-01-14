# Event Channel 层 - 高吞吐、低耦合的事件广播通道

import asyncio
import time
from typing import Callable, Any, Optional, Type
from dataclasses import dataclass
from loguru import logger

from .client import MQTTClient
from .protocol import Codec, JSONCodec


@dataclass
class EventMessage:
    """事件消息（可选的结构化格式）

    这是一个**可选**的辅助工具类，用户可以选择：
    1. 使用 EventMessage 发布（带时间戳、事件类型）
    2. 直接发布原始字典（零开销）

    订阅者会根据消息是否包含 "type": "event" 自动区分

    Attributes:
        type: 消息类型标识（固定为 "event"）
        event_type: 事件类型（如 "sensor.temperature", "user.login"）
        data: 事件数据（任意 JSON 可序列化对象）
        timestamp: Unix 时间戳（秒，自动填充）
        source: 事件源（可选，发布者标识）

    示例:
        # 创建事件消息
        msg = EventMessage(
            event_type="temperature.changed",
            data={"value": 25.5, "unit": "C"},
            source="sensor_001"
        )

        # 序列化
        data = msg.to_dict()
        # {
        #     "type": "event",
        #     "event_type": "temperature.changed",
        #     "data": {"value": 25.5, "unit": "C"},
        #     "timestamp": 1673456789.123,
        #     "source": "sensor_001"
        # }
    """

    # 固定字段（用于区分事件消息和 RPC 消息）
    type: str = "event"

    # 事件核心字段
    event_type: str = ""  # 事件类型
    data: Any = None  # 事件数据

    # 元数据（自动填充）
    timestamp: float = 0.0  # Unix 时间戳（秒）
    source: str = ""  # 事件源

    def __post_init__(self):
        """自动填充时间戳"""
        if self.timestamp == 0.0:
            self.timestamp = time.time()

    def to_dict(self) -> dict:
        """序列化为字典

        Returns:
            包含所有字段的字典
        """
        return {
            "type": self.type,
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EventMessage":
        """从字典反序列化

        Args:
            data: 包含事件字段的字典

        Returns:
            EventMessage 实例
        """
        return cls(
            event_type=data.get("event_type", ""),
            data=data.get("data"),
            timestamp=data.get("timestamp", 0.0),
            source=data.get("source", ""),
        )

    def encode(self, codec: Type[Codec] = JSONCodec) -> bytes:
        """编码为 bytes

        Args:
            codec: 编解码器（默认 JSONCodec）

        Returns:
            编码后的 bytes
        """
        return codec.encode(self)

    @classmethod
    def decode(cls, data: bytes, codec: Type[Codec] = JSONCodec) -> "EventMessage":
        """从 bytes 解码

        Args:
            data: 原始 bytes 数据
            codec: 编解码器（默认 JSONCodec）

        Returns:
            EventMessage 对象
        """
        obj = codec.decode(data)
        return cls.from_dict(obj)


# 事件处理器类型定义
# 参数：(topic: str, message: dict)
EventHandler = Callable[[str, dict], Any]


class EventChannelManager:
    """Event Channel 管理器 - 极薄的发布订阅层

    核心特性：
    1. 发布：零包装，直接转发到 MQTT（可选 EventMessage 格式化）
    2. 订阅：支持通配符，自动区分结构化/原始消息
    3. 过滤：基于 topic 模式匹配（MQTT 原生支持）
    4. 无返回值：明确告诉使用者"这不是 RPC"

    与 RPC 的共存：
    - RPC 消息：type = "rpc_request" | "rpc_response"
    - Event 消息：type = "event" | 原始字典（无 type 字段）
    - 通过 type 字段自动分流（在 MQTTClient._handle_message 中）

    使用示例:
        # 创建管理器
        events = EventChannelManager(client)

        # 订阅事件（支持通配符）
        @events.subscribe("sensors/+/temperature")
        async def on_temperature(topic, message):
            print(f"温度更新: {topic} -> {message}")

        # 发布结构化事件
        await events.publish(
            "sensors/room1/temperature",
            EventMessage(
                event_type="temperature.changed",
                data={"value": 25.5, "unit": "C"}
            )
        )

        # 发布原始事件（零开销）
        await events.publish(
            "sensors/room1/humidity",
            {"value": 60.2, "unit": "%"}
        )
    """

    def __init__(self, client: MQTTClient):
        """初始化 Event Channel 管理器

        Args:
            client: MQTTClient 实例（必须已连接或准备连接）
        """
        self._client = client
        self._patterns: dict[str, list[EventHandler]] = {}  # pattern → handlers
        self._dispatchers: dict[str, Callable] = {}  # 保存 dispatcher 引用（修复 P0-B）

        logger.info("EventChannelManager 已初始化")

    def subscribe(self, pattern: str, handler: Optional[EventHandler] = None):
        """订阅事件主题（支持通配符）

        核心设计：
        1. 支持 MQTT 通配符（+ 和 #）
        2. 一个 pattern 可以有多个处理器（广播模式）
        3. 自动在 MQTTClient 层注册订阅

        Args:
            pattern: MQTT 主题模式（支持通配符）
                - "+": 单级通配符（sensors/+/temperature）
                - "#": 多级通配符（sensors/#）
            handler: 事件处理器（可选，也可以用作装饰器）

        返回：
            装饰器函数（如果 handler 为 None）

        使用示例:
            # 方式 1: 装饰器
            @events.subscribe("sensors/+/temperature")
            async def on_temp(topic, message):
                pass

            # 方式 2: 直接注册
            events.subscribe("sensors/+/temperature", on_temp)
        """

        def decorator(func: EventHandler):
            # 添加到处理器列表
            if pattern not in self._patterns:
                self._patterns[pattern] = []

                # 第一次订阅这个 pattern，创建专属 dispatcher（修复 P0-B：避免闭包泄漏）
                async def dispatcher(topic: str, payload: bytes):
                    """专属 dispatcher（bytes → dict → handler）"""
                    try:
                        # 解码（使用 JSONCodec）
                        data = JSONCodec.decode(payload)

                        # 分发到所有 handlers（使用 get 避免 KeyError）
                        for h in self._patterns.get(pattern, []):
                            try:
                                if asyncio.iscoroutinefunction(h):
                                    await h(topic, data)
                                else:
                                    h(topic, data)
                            except Exception as e:
                                logger.exception(
                                    f"Event handler 异常 - pattern: {pattern}, error: {e}"
                                )
                    except Exception as e:
                        logger.error(f"事件消息解码失败 - topic: {topic}, error: {e}")

                # 保存 dispatcher 引用（修复 P0-B）
                self._dispatchers[pattern] = dispatcher

                # 注册到 MQTTClient 层
                self._client.subscribe(pattern, dispatcher)

            self._patterns[pattern].append(func)
            logger.debug(
                f"事件订阅成功 - pattern: {pattern}, handlers: {len(self._patterns[pattern])}"
            )
            return func

        if handler is None:
            return decorator
        else:
            return decorator(handler)

    def unsubscribe(self, pattern: str, handler: Optional[EventHandler] = None):
        """取消订阅（修复 P0-B：真正清理底层订阅）

        Args:
            pattern: MQTT 主题模式
            handler: 要移除的处理器（None = 移除所有）

        改进：
            现在会真正调用 MQTTClient.unsubscribe 来清理底层 MQTT 订阅
            避免内存泄漏
        """
        if pattern not in self._patterns:
            return

        if handler is None:
            # 移除所有处理器
            del self._patterns[pattern]

            # 清理 dispatcher（修复 P0-B）
            dispatcher = self._dispatchers.pop(pattern, None)
            if dispatcher:
                self._client.unsubscribe(pattern, dispatcher)

            logger.info(f"已取消订阅 - pattern: {pattern}")
        else:
            # 移除指定处理器
            if handler in self._patterns[pattern]:
                self._patterns[pattern].remove(handler)

                # 如果没有处理器了，清理 dispatcher（修复 P0-B）
                if not self._patterns[pattern]:
                    del self._patterns[pattern]

                    dispatcher = self._dispatchers.pop(pattern, None)
                    if dispatcher:
                        self._client.unsubscribe(pattern, dispatcher)

                    logger.info(f"已取消订阅（最后一个 handler）- pattern: {pattern}")
                else:
                    logger.debug(
                        f"已移除处理器 - pattern: {pattern}, 剩余 {len(self._patterns[pattern])} 个"
                    )

    async def publish(
        self,
        topic: str,
        message: EventMessage | dict | Any,
        qos: int = 0,
    ):
        """发布事件（极薄包装）

        设计原则：
        - 不创建 Future（无返回值）
        - 不等待确认（fire-and-forget）
        - 直接调用 client.publish()

        Args:
            topic: 目标主题
            message: 事件消息
                - EventMessage: 自动序列化为 JSON
                - dict: 直接序列化为 JSON
                - 其他类型: 包装为 {"data": message}
            qos: QoS 等级（0 = 最多一次，1 = 至少一次，2 = 恰好一次）

        使用示例:
            # 结构化事件
            await events.publish(
                "sensors/room1/temperature",
                EventMessage(event_type="temp.changed", data={"value": 25.5})
            )

            # 原始字典
            await events.publish(
                "sensors/room1/humidity",
                {"value": 60.2, "unit": "%"}
            )

            # 简单值（自动包装）
            await events.publish(
                "alerts/fire",
                "Fire detected in room 3!"
            )
        """
        # 编码消息
        if isinstance(message, EventMessage):
            payload = message.encode(JSONCodec)
        elif isinstance(message, dict):
            payload = JSONCodec.encode(message)
        else:
            # 其他类型自动包装
            payload = JSONCodec.encode({"data": message})

        # 直接发布（零开销）
        await self._client.raw.publish(topic, payload, qos=qos)
