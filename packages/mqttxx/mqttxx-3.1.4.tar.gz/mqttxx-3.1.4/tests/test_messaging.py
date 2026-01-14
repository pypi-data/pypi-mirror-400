# 消息传输测试

import pytest
import asyncio
from mqttxx import MQTTClient, MQTTConfig


pytestmark = [pytest.mark.integration, pytest.mark.p0]


class TestPubSub:
    """发布-订阅基础测试"""

    @pytest.mark.asyncio
    async def test_basic_pubsub(self, two_mqtt_clients, test_topic_namespace, message_handler, wait_for_message):
        """测试基础发布-订阅"""
        publisher, subscriber = two_mqtt_clients
        topic = f"{test_topic_namespace}/basic"

        # 订阅
        subscriber.subscribe(topic, message_handler())

        await asyncio.sleep(0.3)  # 等待订阅生效

        # 发布
        payload = b"Hello MQTT"
        await publisher.publish(topic, payload)

        # 验证
        msg = await wait_for_message()
        assert msg["topic"] == topic
        assert msg["payload"] == payload

    @pytest.mark.asyncio
    async def test_multiple_messages(self, two_mqtt_clients, test_topic_namespace):
        """测试连续发布多条消息"""
        publisher, subscriber = two_mqtt_clients
        topic = f"{test_topic_namespace}/multiple"
        queue = asyncio.Queue()

        async def handler(t, p):
            await queue.put((t, p))

        subscriber.subscribe(topic, handler)
        await asyncio.sleep(0.3)

        # 发布多条消息
        messages = [f"Message {i}".encode() for i in range(5)]
        for msg in messages:
            await publisher.publish(topic, msg)
            await asyncio.sleep(0.1)

        # 验证所有消息都收到
        received = []
        for _ in range(len(messages)):
            t, p = await asyncio.wait_for(queue.get(), timeout=5.0)
            received.append(p)

        assert received == messages

    @pytest.mark.asyncio
    async def test_multiple_subscribers(self, mqtt_broker_config, test_topic_namespace):
        """测试多个订阅者（广播）"""
        # 创建 3 个订阅者
        subscribers = []
        queues = []

        for i in range(3):
            config = MQTTConfig(
                broker_host=mqtt_broker_config["host"],
                broker_port=mqtt_broker_config["port"],
                client_id=f"test_subscriber_{i}_{int(asyncio.get_event_loop().time())}",
            )
            client = MQTTClient(config)
            await client.connect()
            subscribers.append(client)

            q = asyncio.Queue()
            queues.append(q)

            # 创建闭包来捕获队列
            def make_handler(q):
                async def handler(t, p):
                    await q.put(p)
                return handler

            client.subscribe(f"{test_topic_namespace}/broadcast", make_handler(q))

        await asyncio.sleep(0.5)

        # 创建发布者
        publisher_config = MQTTConfig(
            broker_host=mqtt_broker_config["host"],
            broker_port=mqtt_broker_config["port"],
            client_id=f"test_publisher_{int(asyncio.get_event_loop().time())}",
        )
        async with MQTTClient(publisher_config) as publisher:
            await asyncio.sleep(0.5)  # 等待发布者连接
            payload = b"Broadcast message"
            await publisher.publish(f"{test_topic_namespace}/broadcast", payload)

        await asyncio.sleep(1.0)  # 增加等待时间，确保消息送达

        # 验证所有订阅者都收到
        for q in queues:
            msg = await asyncio.wait_for(q.get(), timeout=3.0)
            assert msg == payload

        # 清理
        for sub in subscribers:
            await sub.disconnect()


class TestQoS:
    """QoS 等级测试"""

    @pytest.mark.asyncio
    async def test_qos0(self, two_mqtt_clients, test_topic_namespace, message_handler, wait_for_message):
        """测试 QoS 0（最多一次）"""
        publisher, subscriber = two_mqtt_clients
        topic = f"{test_topic_namespace}/qos0"

        subscriber.subscribe(topic, message_handler())
        await asyncio.sleep(0.3)

        await publisher.publish(topic, b"QoS 0 message", qos=0)

        msg = await wait_for_message()
        assert msg["payload"] == b"QoS 0 message"

    @pytest.mark.asyncio
    async def test_qos1(self, two_mqtt_clients, test_topic_namespace, message_handler, wait_for_message):
        """测试 QoS 1（至少一次）"""
        publisher, subscriber = two_mqtt_clients
        topic = f"{test_topic_namespace}/qos1"

        subscriber.subscribe(topic, message_handler())
        await asyncio.sleep(0.3)

        await publisher.publish(topic, b"QoS 1 message", qos=1)

        msg = await wait_for_message()
        assert msg["payload"] == b"QoS 1 message"

    @pytest.mark.asyncio
    async def test_qos2(self, two_mqtt_clients, test_topic_namespace, message_handler, wait_for_message):
        """测试 QoS 2（恰好一次）"""
        publisher, subscriber = two_mqtt_clients
        topic = f"{test_topic_namespace}/qos2"

        subscriber.subscribe(topic, message_handler())
        await asyncio.sleep(0.3)

        await publisher.publish(topic, b"QoS 2 message", qos=2)

        msg = await wait_for_message()
        assert msg["payload"] == b"QoS 2 message"


class TestWildcards:
    """通配符订阅测试"""

    @pytest.mark.asyncio
    async def test_single_level_wildcard(self, two_mqtt_clients, test_topic_namespace):
        """测试单级通配符 (+）"""
        publisher, subscriber = two_mqtt_clients
        queue = asyncio.Queue()

        # 订阅 sensors/+/temperature
        pattern = f"{test_topic_namespace}/sensors/+/temperature"
        async def handler(t, p):
            await queue.put((t, p))
        subscriber.subscribe(pattern, handler)
        await asyncio.sleep(0.3)

        # 发布到匹配的 topic
        topics = [
            f"{test_topic_namespace}/sensors/room1/temperature",
            f"{test_topic_namespace}/sensors/room2/temperature",
        ]

        for topic in topics:
            await publisher.publish(topic, b"temp data")

        # 验证收到所有消息
        received = []
        for _ in range(len(topics)):
            t, p = await asyncio.wait_for(queue.get(), timeout=2.0)
            received.append(t)

        assert set(received) == set(topics)

    @pytest.mark.asyncio
    async def test_multi_level_wildcard(self, two_mqtt_clients, test_topic_namespace):
        """测试多级通配符 (#）"""
        publisher, subscriber = two_mqtt_clients
        queue = asyncio.Queue()

        # 订阅 sensors/#
        pattern = f"{test_topic_namespace}/sensors/#"
        async def handler(t, p):
            await queue.put((t, p))
        subscriber.subscribe(pattern, handler)
        await asyncio.sleep(0.3)

        # 发布到各级 topic
        topics = [
            f"{test_topic_namespace}/sensors/temperature",
            f"{test_topic_namespace}/sensors/room1/temperature",
            f"{test_topic_namespace}/sensors/room1/floor2/temperature",
        ]

        for topic in topics:
            await publisher.publish(topic, b"sensor data")

        # 验证收到所有消息
        received = []
        for _ in range(len(topics)):
            t, p = await asyncio.wait_for(queue.get(), timeout=2.0)
            received.append(t)

        assert set(received) == set(topics)

    @pytest.mark.asyncio
    async def test_wildcard_no_match(self, two_mqtt_clients, test_topic_namespace):
        """测试通配符不匹配的情况"""
        publisher, subscriber = two_mqtt_clients
        queue = asyncio.Queue()

        # 订阅 sensors/+/temperature
        pattern = f"{test_topic_namespace}/sensors/+/temperature"
        async def handler(t, p):
            await queue.put((t, p))
        subscriber.subscribe(pattern, handler)
        await asyncio.sleep(0.3)

        # 发布到不匹配的 topic
        await publisher.publish(
            f"{test_topic_namespace}/sensors/room1/humidity",
            b"should not match"
        )

        # 验证没有收到消息
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(queue.get(), timeout=1.0)


class TestPayload:
    """消息载荷测试"""

    @pytest.mark.asyncio
    async def test_large_payload(self, two_mqtt_clients, test_topic_namespace):
        """测试大消息载荷（256KB）"""
        publisher, subscriber = two_mqtt_clients
        queue = asyncio.Queue()

        topic = f"{test_topic_namespace}/large"
        async def handler(t, p):
            await queue.put(p)
        subscriber.subscribe(topic, handler)
        await asyncio.sleep(0.3)

        # 创建 256KB 载荷（减小以避免超时）
        large_payload = b"x" * (256 * 1024)
        await publisher.publish(topic, large_payload)

        # 验证
        received = await asyncio.wait_for(queue.get(), timeout=15.0)
        assert len(received) == len(large_payload)

    @pytest.mark.asyncio
    async def test_binary_payload(self, two_mqtt_clients, test_topic_namespace):
        """测试二进制载荷"""
        publisher, subscriber = two_mqtt_clients
        queue = asyncio.Queue()

        topic = f"{test_topic_namespace}/binary"
        async def handler(t, p):
            await queue.put(p)
        subscriber.subscribe(topic, handler)
        await asyncio.sleep(0.3)

        # 二进制数据
        binary_data = bytes(range(256))
        await publisher.publish(topic, binary_data)

        received = await asyncio.wait_for(queue.get(), timeout=5.0)
        assert received == binary_data

    @pytest.mark.asyncio
    async def test_utf8_payload(self, two_mqtt_clients, test_topic_namespace):
        """测试 UTF-8 文本载荷"""
        publisher, subscriber = two_mqtt_clients
        queue = asyncio.Queue()

        topic = f"{test_topic_namespace}/utf8"
        async def handler(t, p):
            await queue.put(p)
        subscriber.subscribe(topic, handler)
        await asyncio.sleep(0.3)

        # 多语言文本
        utf8_text = "你好世界 Hello World 🌍".encode('utf-8')
        await publisher.publish(topic, utf8_text)

        received = await asyncio.wait_for(queue.get(), timeout=5.0)
        assert received == utf8_text
