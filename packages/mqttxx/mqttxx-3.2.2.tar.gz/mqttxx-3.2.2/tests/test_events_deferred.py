# EventChannelManager 延迟注册功能测试

import asyncio
import pytest
from mqttxx import EventChannelManager, event_subscribe


@pytest.mark.integration
async def test_deferred_registration(connected_client):
    """测试延迟注册的处理器自动导入"""
    print("\n[测试] 延迟注册自动导入")

    # 在测试函数内使用 @event_subscribe 注册处理器
    test_topic = f"test/deferred/{connected_client.config.client_id}"
    received = asyncio.Event()

    @event_subscribe(test_topic)
    async def deferred_handler(topic: str, message: dict):
        print(f"[收到] topic: {topic}, message: {message}")
        received.set()

    # 创建 EventChannelManager（应自动导入上面的处理器）
    events = EventChannelManager(connected_client)

    await asyncio.sleep(0.5)

    # 发布测试消息
    await events.publish(test_topic, {"test": "deferred"})

    # 等待处理器执行
    await asyncio.wait_for(received.wait(), timeout=5.0)

    assert received.is_set(), "延迟注册的处理器应该被调用"
    print("[成功] 延迟注册测试通过")


@pytest.mark.integration
async def test_deferred_with_normal(connected_client):
    """测试延迟注册与普通注册共存"""
    print("\n[测试] 延迟注册与普通注册共存")

    deferred_received = asyncio.Event()
    normal_received = asyncio.Event()

    # 延迟注册
    deferred_topic = f"test/mixed/deferred/{connected_client.config.client_id}"

    @event_subscribe(deferred_topic)
    async def deferred_handler(topic: str, message: dict):
        print(f"[延迟注册] 收到: {topic}")
        deferred_received.set()

    # 普通注册（先创建实例，关闭自动导入）
    events = EventChannelManager(connected_client, auto_import=False)

    normal_topic = f"test/mixed/normal/{connected_client.config.client_id}"

    @events.subscribe(normal_topic)
    async def normal_handler(topic: str, message: dict):
        print(f"[普通注册] 收到: {topic}")
        normal_received.set()

    # 手动导入延迟注册
    events._import_pending_subscriptions()
    await asyncio.sleep(0.5)

    # 发布测试消息
    await events.publish(deferred_topic, {"test": 1})
    await events.publish(normal_topic, {"test": 2})

    # 等待两个处理器都执行
    await asyncio.wait_for(deferred_received.wait(), timeout=5.0)
    await asyncio.wait_for(normal_received.wait(), timeout=5.0)

    assert deferred_received.is_set(), "延迟注册的处理器应该被调用"
    assert normal_received.is_set(), "普通注册的处理器应该被调用"
    print("[成功] 延迟注册与普通注册共存测试通过")


@pytest.mark.integration
async def test_auto_import_can_be_disabled(connected_client):
    """测试可以关闭自动导入"""
    print("\n[测试] 关闭自动导入")

    received = asyncio.Event()
    test_topic = f"test/no_import/{connected_client.config.client_id}"

    @event_subscribe(test_topic)
    async def handler(topic: str, message: dict):
        received.set()

    # 关闭自动导入
    events = EventChannelManager(connected_client, auto_import=False)

    await asyncio.sleep(0.5)

    # 此时发布消息，处理器不应该被调用（因为还未导入）
    await events.publish(test_topic, {"test": 1})
    await asyncio.sleep(0.5)

    assert not received.is_set(), "未导入时不应该收到消息"

    # 手动导入
    events._import_pending_subscriptions()
    await asyncio.sleep(0.5)

    # 再次发布，应该收到
    await events.publish(test_topic, {"test": 2})
    await asyncio.wait_for(received.wait(), timeout=5.0)

    assert received.is_set(), "手动导入后应该收到消息"
    print("[成功] 关闭自动导入测试通过")


@pytest.mark.integration
async def test_multiple_deferred_handlers(connected_client):
    """测试多个延迟注册的处理器"""
    print("\n[测试] 多个延迟注册处理器")

    received1 = asyncio.Event()
    received2 = asyncio.Event()
    received3 = asyncio.Event()

    base_topic = f"test/multi/{connected_client.config.client_id}"

    @event_subscribe(f"{base_topic}/sensor1")
    async def handler1(topic: str, message: dict):
        print(f"[处理器1] {topic}")
        received1.set()

    @event_subscribe(f"{base_topic}/sensor2")
    async def handler2(topic: str, message: dict):
        print(f"[处理器2] {topic}")
        received2.set()

    @event_subscribe(f"{base_topic}/sensor3")
    async def handler3(topic: str, message: dict):
        print(f"[处理器3] {topic}")
        received3.set()

    # 创建 EventChannelManager
    events = EventChannelManager(connected_client)
    await asyncio.sleep(0.5)

    # 发布消息到所有 topic
    await events.publish(f"{base_topic}/sensor1", {"value": 1})
    await events.publish(f"{base_topic}/sensor2", {"value": 2})
    await events.publish(f"{base_topic}/sensor3", {"value": 3})

    # 等待所有处理器
    await asyncio.wait_for(received1.wait(), timeout=5.0)
    await asyncio.wait_for(received2.wait(), timeout=5.0)
    await asyncio.wait_for(received3.wait(), timeout=5.0)

    assert received1.is_set() and received2.is_set() and received3.is_set()
    print("[成功] 多个延迟注册处理器测试通过")
