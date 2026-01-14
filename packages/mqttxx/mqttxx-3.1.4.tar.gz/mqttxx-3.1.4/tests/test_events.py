# 事件系统测试

import pytest
import asyncio
from mqttxx import EventChannelManager, EventMessage


pytestmark = [pytest.mark.integration, pytest.mark.p0]


class TestEventPubSub:
    """Event Channel 发布-订阅测试"""

    @pytest.mark.asyncio
    async def test_basic_event_pubsub(self, event_channel_manager, two_mqtt_clients, test_topic_namespace):
        """测试基础事件发布-订阅"""
        events = event_channel_manager
        publisher, subscriber = two_mqtt_clients
        subscriber_events = EventChannelManager(subscriber)

        queue = asyncio.Queue()

        # 订阅
        topic = f"{test_topic_namespace}/event/basic"
        async def handler(t, m):
            await queue.put(m)
        subscriber_events.subscribe(topic, handler)
        await asyncio.sleep(0.3)

        # 发布
        await events.publish(topic, {"data": "test event"})

        # 验证
        msg = await asyncio.wait_for(queue.get(), timeout=5.0)
        assert msg["data"] == "test event"

    @pytest.mark.asyncio
    async def test_structured_event_message(self, event_channel_manager, two_mqtt_clients, test_topic_namespace):
        """测试结构化 EventMessage"""
        events = event_channel_manager
        publisher, subscriber = two_mqtt_clients
        subscriber_events = EventChannelManager(subscriber)

        queue = asyncio.Queue()

        topic = f"{test_topic_namespace}/event/structured"
        async def handler(t, m):
            await queue.put(m)
        subscriber_events.subscribe(topic, handler)
        await asyncio.sleep(0.3)

        # 发布结构化事件
        event = EventMessage(
            event_type="temperature.changed",
            data={"value": 25.5, "unit": "C"},
            source="sensor_001"
        )
        await events.publish(topic, event)

        # 验证
        msg = await asyncio.wait_for(queue.get(), timeout=5.0)
        assert msg["type"] == "event"
        assert msg["event_type"] == "temperature.changed"
        assert msg["data"]["value"] == 25.5
        assert msg["source"] == "sensor_001"
        assert "timestamp" in msg

    @pytest.mark.asyncio
    async def test_raw_dict_event(self, event_channel_manager, two_mqtt_clients, test_topic_namespace):
        """测试原始字典事件（零开销）"""
        events = event_channel_manager
        publisher, subscriber = two_mqtt_clients
        subscriber_events = EventChannelManager(subscriber)

        queue = asyncio.Queue()

        topic = f"{test_topic_namespace}/event/raw"
        async def handler(t, m):
            await queue.put(m)
        subscriber_events.subscribe(topic, handler)
        await asyncio.sleep(0.3)

        # 发布原始字典
        await events.publish(topic, {"temp": 26.0, "humidity": 60})

        # 验证
        msg = await asyncio.wait_for(queue.get(), timeout=5.0)
        assert msg["temp"] == 26.0
        assert msg["humidity"] == 60

    @pytest.mark.asyncio
    async def test_auto_wrapped_value(self, event_channel_manager, two_mqtt_clients, test_topic_namespace):
        """测试简单值自动包装"""
        events = event_channel_manager
        publisher, subscriber = two_mqtt_clients
        subscriber_events = EventChannelManager(subscriber)

        queue = asyncio.Queue()

        topic = f"{test_topic_namespace}/event/wrapped"
        async def handler(t, m):
            await queue.put(m)
        subscriber_events.subscribe(topic, handler)
        await asyncio.sleep(0.3)

        # 发布简单值
        await events.publish(topic, "Fire alarm!")

        # 验证自动包装
        msg = await asyncio.wait_for(queue.get(), timeout=5.0)
        assert msg["data"] == "Fire alarm!"


class TestEventWildcards:
    """Event Channel 通配符订阅测试"""

    @pytest.mark.asyncio
    async def test_single_level_wildcard(self, event_channel_manager, two_mqtt_clients, test_topic_namespace):
        """测试事件单级通配符（+）"""
        publisher, subscriber = two_mqtt_clients
        subscriber_events = EventChannelManager(subscriber)
        queue = asyncio.Queue()

        # 订阅 sensors/+/temperature
        pattern = f"{test_topic_namespace}/sensors/+/temperature"
        async def handler(t, m):
            await queue.put((t, m))
        subscriber_events.subscribe(pattern, handler)
        await asyncio.sleep(0.3)

        # 发布到多个匹配的 topic
        topics = [
            f"{test_topic_namespace}/sensors/room1/temperature",
            f"{test_topic_namespace}/sensors/room2/temperature",
        ]

        for topic in topics:
            await event_channel_manager.publish(topic, {"value": 25.0})

        # 验证收到所有消息
        received = []
        for _ in range(len(topics)):
            t, m = await asyncio.wait_for(queue.get(), timeout=2.0)
            received.append(t)

        assert set(received) == set(topics)

    @pytest.mark.asyncio
    async def test_multi_level_wildcard(self, event_channel_manager, two_mqtt_clients, test_topic_namespace):
        """测试事件多级通配符（#）"""
        publisher, subscriber = two_mqtt_clients
        subscriber_events = EventChannelManager(subscriber)
        queue = asyncio.Queue()

        # 订阅 sensors/#
        pattern = f"{test_topic_namespace}/sensors/#"
        async def handler(t, m):
            await queue.put((t, m))
        subscriber_events.subscribe(pattern, handler)
        await asyncio.sleep(0.3)

        # 发布到各级 topic
        topics = [
            f"{test_topic_namespace}/sensors/temp",
            f"{test_topic_namespace}/sensors/room1/temp",
            f"{test_topic_namespace}/sensors/room1/floor2/temp",
        ]

        for topic in topics:
            await event_channel_manager.publish(topic, {"data": "test"})

        # 验证
        received = []
        for _ in range(len(topics)):
            t, m = await asyncio.wait_for(queue.get(), timeout=2.0)
            received.append(t)

        assert set(received) == set(topics)


class TestEventQoS:
    """Event Channel QoS 测试"""

    @pytest.mark.asyncio
    async def test_event_qos0(self, event_channel_manager, two_mqtt_clients, test_topic_namespace):
        """测试事件 QoS 0"""
        publisher, subscriber = two_mqtt_clients
        subscriber_events = EventChannelManager(subscriber)
        queue = asyncio.Queue()

        topic = f"{test_topic_namespace}/event/qos0"
        async def handler(t, m):
            await queue.put(m)
        subscriber_events.subscribe(topic, handler)
        await asyncio.sleep(0.3)

        await event_channel_manager.publish(topic, {"qos": 0}, qos=0)

        msg = await asyncio.wait_for(queue.get(), timeout=5.0)
        assert msg["qos"] == 0

    @pytest.mark.asyncio
    async def test_event_qos1(self, event_channel_manager, two_mqtt_clients, test_topic_namespace):
        """测试事件 QoS 1"""
        publisher, subscriber = two_mqtt_clients
        subscriber_events = EventChannelManager(subscriber)
        queue = asyncio.Queue()

        topic = f"{test_topic_namespace}/event/qos1"
        async def handler(t, m):
            await queue.put(m)
        subscriber_events.subscribe(topic, handler)
        await asyncio.sleep(0.3)

        await event_channel_manager.publish(topic, {"qos": 1}, qos=1)

        msg = await asyncio.wait_for(queue.get(), timeout=5.0)
        assert msg["qos"] == 1


class TestMultipleSubscribers:
    """多订阅者测试"""

    @pytest.mark.asyncio
    async def test_multiple_handlers_same_pattern(self, event_channel_manager, mqtt_client, test_topic_namespace):
        """测试同一 pattern 的多个处理器"""
        events = event_channel_manager
        queue1 = asyncio.Queue()
        queue2 = asyncio.Queue()

        topic = f"{test_topic_namespace}/event/multi"

        # 订阅同一 pattern 多次
        async def handler1(t, m):
            await queue1.put("handler1")
        async def handler2(t, m):
            await queue2.put("handler2")

        events.subscribe(topic, handler1)
        events.subscribe(topic, handler2)
        await asyncio.sleep(0.3)

        # 发布
        await events.publish(topic, {"test": "data"})

        # 验证两个 handler 都被调用
        msg1 = await asyncio.wait_for(queue1.get(), timeout=5.0)
        msg2 = await asyncio.wait_for(queue2.get(), timeout=5.0)

        assert msg1 == "handler1"
        assert msg2 == "handler2"
