"""测试 messages/# 通配符路由事件捕获"""

import asyncio
import pytest
from mqttxx import EventChannelManager


@pytest.mark.integration
async def test_messages_wildcard_subscription(connected_client):
    """测试 @events.subscribe("messages/#") 捕获所有 messages 路由的事件"""
    print("\n[测试] messages/# 通配符订阅")

    events = EventChannelManager(connected_client)

    # 记录所有接收到的消息
    received_messages = []

    @events.subscribe("messages/#")
    async def handler(topic: str, message: dict):
        """捕获所有 messages/ 开头的消息"""
        received_messages.append({
            "topic": topic,
            "message": message
        })
        print(f"[捕获] topic: {topic}")

    # 等待订阅生效
    await asyncio.sleep(0.5)
    print("[订阅] 已订阅 messages/#，等待接收来自其他设备的消息...")

    # 等待接收来自其他设备的消息（最多等待 10 秒）
    timeout = 10.0
    min_messages = 3  # 至少接收 3 条消息才算通过

    start_time = asyncio.get_event_loop().time()
    while len(received_messages) < min_messages:
        if asyncio.get_event_loop().time() - start_time > timeout:
            pytest.fail(
                f"超时：{timeout}秒内只接收到 {len(received_messages)} 条消息，"
                f"预期至少 {min_messages} 条"
            )
        await asyncio.sleep(0.1)

    # 验证所有消息都符合 messages/# 模式
    for msg in received_messages:
        assert msg["topic"].startswith("messages/"), \
            f"接收到不匹配的消息：{msg['topic']}"

    print(f"[成功] 成功接收 {len(received_messages)} 条 messages/# 消息")


@pytest.mark.integration
async def test_messages_wildcard_with_event_message(connected_client):
    """测试 messages/# 订阅捕获结构化消息"""
    print("\n[测试] messages/# 订阅捕获真实消息")

    events = EventChannelManager(connected_client)

    received_messages = []

    @events.subscribe("messages/#")
    async def handler(topic: str, message: dict):
        """捕获结构化事件消息"""
        received_messages.append({
            "topic": topic,
            "message": message
        })
        print(f"[捕获] {topic}")

    await asyncio.sleep(0.5)
    print("[订阅] 等待接收消息...")

    # 等待接收消息
    timeout = 10.0
    min_messages = 2

    start_time = asyncio.get_event_loop().time()
    while len(received_messages) < min_messages:
        if asyncio.get_event_loop().time() - start_time > timeout:
            pytest.fail(f"超时：{timeout}秒内只接收到 {len(received_messages)} 条消息")
        await asyncio.sleep(0.1)

    # 验证消息都是有效的 dict
    for msg in received_messages:
        assert isinstance(msg["message"], dict), "消息应该是 dict 类型"
        assert msg["topic"].startswith("messages/"), "topic 应该以 messages/ 开头"

    print(f"[成功] 成功接收 {len(received_messages)} 条有效消息")


@pytest.mark.integration
async def test_messages_wildcard_vs_non_messages(connected_client):
    """测试 messages/# 不会捕获其他路由的消息"""
    print("\n[测试] messages/# 只捕获 messages 路由")

    events = EventChannelManager(connected_client)

    captured_topics = []

    @events.subscribe("messages/#")
    async def handler(topic: str, message: dict):
        """只应该捕获 messages/ 开头的消息"""
        captured_topics.append(topic)
        print(f"[捕获] {topic}")

    await asyncio.sleep(0.5)

    # 发布非 messages 路由的消息（不应该被捕获）
    non_messages_topics = ["sensors/temp", "events/user", "other/path"]
    for topic in non_messages_topics:
        await events.publish(topic, {"msg": "should NOT capture"})
        print(f"[发布] {topic}")

    # 等待一段时间收集消息（包括外部消息）
    await asyncio.sleep(2.0)

    # 验证捕获的消息中没有我们发布的非 messages/ 消息
    for topic in captured_topics:
        assert topic not in non_messages_topics, \
            f"不应该捕获非 messages/ 的消息：{topic}"
        assert topic.startswith("messages/"), \
            f"所有捕获的消息都应该以 messages/ 开头：{topic}"

    print(f"[成功] messages/# 过滤测试通过，共捕获 {len(captured_topics)} 条 messages/ 消息")
