# MQTTClient 基础功能测试

import asyncio
import pytest
from loguru import logger
from mqttxx import MQTTClient


@pytest.mark.integration
async def test_connect_disconnect(mqtt_config):
    """测试连接和断开"""
    logger.info("[测试] 连接和断开")

    client = MQTTClient(mqtt_config)
    assert not client.is_connected, "初始状态应该是未连接"

    # 连接
    await client.connect()
    await asyncio.sleep(1)  # 等待连接建立

    assert client.is_connected, "连接后状态应该是已连接"
    logger.success(f"[成功] 客户端已连接: {mqtt_config.client_id}")

    # 断开
    await client.disconnect()
    await asyncio.sleep(0.5)

    assert not client.is_connected, "断开后状态应该是未连接"
    logger.success("[成功] 客户端已断开")


@pytest.mark.integration
async def test_subscribe_publish_single(mqtt_config):
    """测试订阅和发布单个 topic"""
    print("\n[测试] 订阅和发布单个 topic")

    async with MQTTClient(mqtt_config) as client:
        # 等待连接
        await asyncio.sleep(1)

        # 创建事件等待消息
        received = asyncio.Event()
        received_data = {}

        # 订阅
        test_topic = f"test/single/{mqtt_config.client_id}"

        async def handler(topic: str, payload: bytes):
            received_data["topic"] = topic
            received_data["payload"] = payload
            received.set()
            print(f"[收到] topic: {topic}, payload: {payload}")

        client.subscribe(test_topic, handler)
        await asyncio.sleep(0.5)
        print(f"[订阅] topic: {test_topic}")

        # 发布消息
        test_message = b"Hello MQTTX"
        await client.raw.publish(test_topic, test_message)
        print(f"[发布] topic: {test_topic}, message: {test_message}")

        # 等待接收
        await asyncio.wait_for(received.wait(), timeout=5.0)

        assert received.is_set(), "应该收到消息"
        assert received_data["topic"] == test_topic, "topic 应该匹配"
        assert received_data["payload"] == test_message, "payload 应该匹配"
        print("[成功] 订阅和发布测试通过")


@pytest.mark.integration
async def test_subscribe_multiple_handlers(mqtt_config):
    """测试同一 topic 多个 handler"""
    print("\n[测试] 同一 topic 多个 handler")

    async with MQTTClient(mqtt_config) as client:
        await asyncio.sleep(1)

        test_topic = f"test/multi/{mqtt_config.client_id}"
        received_count = {"count": 0}

        # 创建多个 handler
        async def handler1(topic: str, payload: bytes):
            received_count["count"] += 1
            print("[Handler1] 收到消息")

        async def handler2(topic: str, payload: bytes):
            received_count["count"] += 1
            print("[Handler2] 收到消息")

        async def handler3(topic: str, payload: bytes):
            received_count["count"] += 1
            print("[Handler3] 收到消息")

        # 注册多个 handler
        client.subscribe(test_topic, handler1)
        client.subscribe(test_topic, handler2)
        client.subscribe(test_topic, handler3)
        await asyncio.sleep(0.5)

        print(f"[订阅] topic: {test_topic}, 3 个 handlers")

        # 发布消息
        await client.raw.publish(test_topic, b"test")
        await asyncio.sleep(1)

        assert received_count["count"] == 3, "3 个 handler 都应该被调用"
        print(f"[成功] 所有 handler 都被调用: {received_count['count']} 次")


@pytest.mark.integration
async def test_wildcard_subscription(mqtt_config):
    """测试通配符订阅 (+ 和 #)"""
    print("\n[测试] 通配符订阅")

    async with MQTTClient(mqtt_config) as client:
        await asyncio.sleep(1)

        received_plus = asyncio.Event()
        received_wildcard = asyncio.Event()

        # 订阅 sensors/+/temperature
        async def handler_plus(topic: str, payload: bytes):
            if "temperature" in topic:
                received_plus.set()
                print(f"[+] 收到温度消息: {topic}")

        client.subscribe("sensors/+/temperature", handler_plus)

        # 订阅 sensors/#
        async def handler_wildcard(topic: str, payload: bytes):
            received_wildcard.set()
            print(f"[#] 收到传感器消息: {topic}")

        client.subscribe("sensors/#", handler_wildcard)
        await asyncio.sleep(0.5)

        # 测试单级通配符
        test_topic = "sensors/room1/temperature"
        await client.raw.publish(test_topic, b"25.5")
        await asyncio.wait_for(received_plus.wait(), timeout=3.0)
        print(f"[发布] {test_topic}")

        # 测试多级通配符
        test_topic2 = "sensors/room2/humidity"
        received_wildcard.clear()
        await client.raw.publish(test_topic2, b"60.0")
        await asyncio.wait_for(received_wildcard.wait(), timeout=3.0)
        print(f"[发布] {test_topic2}")

        print("[成功] 通配符订阅测试通过")


@pytest.mark.integration
async def test_unsubscribe(mqtt_config):
    """测试取消订阅"""
    print("\n[测试] 取消订阅")

    async with MQTTClient(mqtt_config) as client:
        await asyncio.sleep(1)

        test_topic = f"test/unsubscribe/{mqtt_config.client_id}"
        received_after = asyncio.Event()

        # 第一次订阅
        async def handler(topic: str, payload: bytes):
            if not received_after.is_set():
                received_after.set()

        client.subscribe(test_topic, handler)
        await asyncio.sleep(0.5)

        # 发布消息，应该收到
        await client.raw.publish(test_topic, b"first")
        await asyncio.wait_for(received_after.wait(), timeout=3.0)
        print("[第一次] 收到消息")

        # 取消订阅
        client.unsubscribe(test_topic)
        received_after.clear()
        await asyncio.sleep(0.5)
        print(f"[取消订阅] {test_topic}")

        # 再次发布，不应该收到
        await client.raw.publish(test_topic, b"second")
        try:
            await asyncio.wait_for(received_after.wait(), timeout=2.0)
            assert False, "取消订阅后不应该收到消息"
        except asyncio.TimeoutError:
            print("[成功] 取消订阅后未收到消息")


@pytest.mark.integration
async def test_context_manager(mqtt_config):
    """测试 async with 上下文管理器"""
    print("\n[测试] async with 上下文管理器")

    client = MQTTClient(mqtt_config)
    assert not client.is_connected

    async with client:
        # 在上下文内应该已连接
        await asyncio.sleep(1)
        assert client.is_connected
        print("[上下文内] 客户端已连接")

    # 退出上下文后应该断开
    assert not client.is_connected
    print("[上下文外] 客户端已断开")
    print("[成功] 上下文管理器测试通过")
