# EventChannelManager 功能测试

import asyncio
import pytest
from mqttxx import EventChannelManager, EventMessage


@pytest.mark.integration
async def test_publish_structured_event(connected_client):
    """测试发布结构化事件 (EventMessage)"""
    print("\n[测试] 发布结构化事件")

    events = EventChannelManager(connected_client)
    received = asyncio.Event()
    received_data = {}

    # 订阅事件
    test_topic = f"test/structured/{connected_client.config.client_id}"

    @events.subscribe(test_topic)
    async def handler(topic: str, message: dict):
        received_data["topic"] = topic
        received_data["message"] = message
        received.set()
        print(f"[收到] topic: {topic}, message: {message}")

    await asyncio.sleep(0.5)

    # 发布结构化事件
    event = EventMessage(
        event_type="sensor.temperature",
        data={"value": 25.5, "unit": "C"},
        source="test_sensor",
    )
    await events.publish(test_topic, event)
    print(f"[发布] 事件类型: {event.event_type}, 数据: {event.data}")

    # 等待接收
    await asyncio.wait_for(received.wait(), timeout=5.0)

    assert received.is_set(), "应该收到事件"
    assert received_data["message"]["type"] == "event", "type 应该是 event"
    assert received_data["message"]["event_type"] == "sensor.temperature", "event_type 应该匹配"
    assert received_data["message"]["data"]["value"] == 25.5, "数据应该匹配"
    assert "timestamp" in received_data["message"], "应该有时间戳"
    print("[成功] 结构化事件测试通过")


@pytest.mark.integration
async def test_publish_raw_dict(connected_client):
    """测试发布原始字典 (零开销)"""
    print("\n[测试] 发布原始字典")

    events = EventChannelManager(connected_client)
    received = asyncio.Event()
    received_data = {}

    # 订阅事件
    test_topic = f"test/raw/{connected_client.config.client_id}"

    @events.subscribe(test_topic)
    async def handler(topic: str, message: dict):
        received_data["message"] = message
        received.set()
        print(f"[收到] topic: {topic}, message: {message}")

    await asyncio.sleep(0.5)

    # 发布原始字典
    raw_data = {"value": 60.2, "unit": "%", "sensor": "humidity"}
    await events.publish(test_topic, raw_data)
    print(f"[发布] 原始数据: {raw_data}")

    # 等待接收
    await asyncio.wait_for(received.wait(), timeout=5.0)

    assert received.is_set(), "应该收到事件"
    assert received_data["message"] == raw_data, "数据应该完全匹配"
    print("[成功] 原始字典测试通过")


@pytest.mark.integration
async def test_event_wildcard_match(connected_client):
    """测试事件通配符匹配"""
    print("\n[测试] 事件通配符匹配")

    events = EventChannelManager(connected_client)
    received_plus = asyncio.Event()
    received_wildcard = asyncio.Event()

    # 订阅 sensors/+/temperature
    @events.subscribe("sensors/+/temperature")
    async def handler_plus(topic: str, message: dict):
        received_plus.set()
        print(f"[+] 收到温度事件: {topic}")

    # 订阅 sensors/#
    @events.subscribe("sensors/#")
    async def handler_wildcard(topic: str, message: dict):
        received_wildcard.set()
        print(f"[#] 收到传感器事件: {topic}")

    await asyncio.sleep(0.5)

    # 测试单级通配符
    test_topic1 = "sensors/room1/temperature"
    await events.publish(test_topic1, {"value": 25.5})
    await asyncio.wait_for(received_plus.wait(), timeout=3.0)
    print(f"[发布] {test_topic1}")

    # 测试多级通配符
    received_wildcard.clear()
    test_topic2 = "sensors/room2/humidity"
    await events.publish(test_topic2, {"value": 60.0})
    await asyncio.wait_for(received_wildcard.wait(), timeout=3.0)
    print(f"[发布] {test_topic2}")

    print("[成功] 通配符匹配测试通过")


@pytest.mark.integration
async def test_event_multiple_subscribers(connected_client):
    """测试一个事件多个订阅者"""
    print("\n[测试] 多个订阅者")

    events = EventChannelManager(connected_client)
    test_topic = f"test/multi_sub/{connected_client.config.client_id}"
    received_count = {"count": 0}

    # 注册多个订阅者
    @events.subscribe(test_topic)
    async def handler1(topic: str, message: dict):
        received_count["count"] += 1
        print("[订阅者1] 收到事件")

    @events.subscribe(test_topic)
    async def handler2(topic: str, message: dict):
        received_count["count"] += 1
        print("[订阅者2] 收到事件")

    @events.subscribe(test_topic)
    async def handler3(topic: str, message: dict):
        received_count["count"] += 1
        print("[订阅者3] 收到事件")

    await asyncio.sleep(0.5)
    print(f"[订阅] topic: {test_topic}, 3 个订阅者")

    # 发布事件
    await events.publish(test_topic, {"test": "data"})
    await asyncio.sleep(1)

    assert received_count["count"] == 3, "3 个订阅者都应该收到事件"
    print(f"[成功] 所有订阅者都收到事件: {received_count['count']} 次")


@pytest.mark.integration
async def test_event_unsubscribe(connected_client):
    """测试取消事件订阅"""
    print("\n[测试] 取消事件订阅")

    events = EventChannelManager(connected_client)
    test_topic = f"test/event_unsub/{connected_client.config.client_id}"
    received_after = asyncio.Event()

    # 订阅事件
    @events.subscribe(test_topic)
    async def handler(topic: str, message: dict):
        if not received_after.is_set():
            received_after.set()
            print(f"[收到] 事件: {topic}")

    await asyncio.sleep(0.5)

    # 发布事件，应该收到
    await events.publish(test_topic, {"first": "event"})
    await asyncio.wait_for(received_after.wait(), timeout=3.0)
    print("[第一次] 收到事件")

    # 取消订阅
    events.unsubscribe(test_topic)
    received_after.clear()
    await asyncio.sleep(0.5)
    print(f"[取消订阅] {test_topic}")

    # 再次发布，不应该收到
    await events.publish(test_topic, {"second": "event"})
    try:
        await asyncio.wait_for(received_after.wait(), timeout=2.0)
        assert False, "取消订阅后不应该收到事件"
    except asyncio.TimeoutError:
        print("[成功] 取消订阅后未收到事件")
