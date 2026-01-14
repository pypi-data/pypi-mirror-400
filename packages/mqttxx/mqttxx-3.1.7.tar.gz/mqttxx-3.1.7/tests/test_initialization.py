# MQTT 初始化流程测试 - 模拟实际业务场景

import asyncio
import pytest
from mqttxx import (
    MQTTClient,
    MQTTConfig,
    ReconnectConfig,
    RPCManager,
    EventChannelManager,
)


@pytest.mark.integration
async def test_initialization_with_reconnect():
    """测试带重连配置的完整初始化流程"""
    print("\n[测试] 完整初始化流程（带重连配置）")

    # 模拟 settings 配置
    broker_host = "163.61.102.47"
    broker_port = 1883
    device_name = "test_device_init"

    # 创建带重连的配置
    config = MQTTConfig(
        broker_host=broker_host,
        broker_port=broker_port,
        client_id=device_name,
        reconnect=ReconnectConfig(
            enabled=True,
            interval=5,
            max_attempts=10,
            backoff_multiplier=1.5,
            max_interval=60,
        ),
    )

    # 初始化 MQTT 客户端并连接
    mqtt = MQTTClient(config)
    await mqtt.connect()

    assert mqtt.is_connected, "MQTT 应该连接成功"
    print(f"[MQTT] 连接成功 - {device_name}")

    # 初始化 RPC Manager（自动订阅 whale/{device_id}）
    rpc_topic = f"whale/{device_name}"
    rpc_manager = RPCManager(client=mqtt, my_topic=rpc_topic)

    assert rpc_manager._client is mqtt, "RPC 应该绑定到正确的客户端"
    assert rpc_manager.my_topic == rpc_topic, "RPC topic 应该匹配"
    print(f"[RPC] 初始化成功，订阅 topic: {rpc_topic}")

    # 初始化 Event Channel Manager
    events = EventChannelManager(client=mqtt)

    assert events._client is mqtt, "EventChannel 应该绑定到正确的客户端"
    print("[Event] 初始化成功")

    # 验证重连配置已生效
    assert mqtt.config.reconnect.enabled is True, "重连应该启用"
    assert mqtt.config.reconnect.interval == 5, "重连间隔应该是 5"
    assert mqtt.config.reconnect.max_attempts == 10, "最大重连次数应该是 10"
    print("[Reconnect] 重连配置已生效")

    # 清理
    await mqtt.disconnect()
    print("[成功] 完整初始化流程测试通过")


@pytest.mark.integration
async def test_rpc_auto_subscription():
    """测试 RPC Manager 自动订阅 whale/{device_id}"""
    print("\n[测试] RPC 自动订阅")

    device_name = "test_device_rpc_sub"

    config = MQTTConfig(
        broker_host="163.61.102.47",
        broker_port=1883,
        client_id=device_name,
    )

    async with MQTTClient(config) as mqtt:
        await asyncio.sleep(1)

        # 初始化 RPC Manager
        rpc_topic = f"whale/{device_name}"
        rpc_manager = RPCManager(client=mqtt, my_topic=rpc_topic)

        # 注册一个测试方法
        method_called = asyncio.Event()

        @rpc_manager.register("test_method")
        async def test_method(params):
            method_called.set()
            return {"result": "ok"}

        await asyncio.sleep(0.5)

        # 创建另一个客户端调用 RPC
        caller_config = MQTTConfig(
            broker_host="163.61.102.47",
            broker_port=1883,
            client_id=f"caller_{device_name}",
        )

        async with MQTTClient(caller_config) as caller:
            await asyncio.sleep(1)

            caller_rpc = RPCManager(
                caller, my_topic=f"caller/{caller_config.client_id}"
            )

            # 调用测试方法
            result = await caller_rpc.call(
                topic=rpc_topic,
                method="test_method",
                params={},
                timeout=5,
            )

            assert result["result"] == "ok", "RPC 调用应该成功"
            assert method_called.is_set(), "方法应该被调用"
            print(f"[成功] RPC 自动订阅正常工作: {rpc_topic}")


@pytest.mark.integration
async def test_events_and_rpc_coexist():
    """测试 Event 和 RPC 在同一初始化流程中共存"""
    print("\n[测试] Event 和 RPC 共存")

    device_name = "test_device_coexist"

    config = MQTTConfig(
        broker_host="163.61.102.47",
        broker_port=1883,
        client_id=device_name,
        reconnect=ReconnectConfig(
            enabled=True,
            interval=5,
            max_attempts=10,
        ),
    )

    async with MQTTClient(config) as mqtt:
        await asyncio.sleep(1)

        # 同时初始化 RPC 和 Event
        rpc_manager = RPCManager(client=mqtt, my_topic=f"whale/{device_name}")
        events = EventChannelManager(client=mqtt)

        await asyncio.sleep(0.5)

        # RPC 端：注册方法
        rpc_called = asyncio.Event()

        @rpc_manager.register("get_status")
        async def get_status(params):
            rpc_called.set()
            return {"status": "online"}

        # Event 端：订阅事件
        event_received = asyncio.Event()
        test_event_topic = f"test/coexist/{device_name}"

        @events.subscribe(test_event_topic)
        async def event_handler(topic: str, message: dict):
            event_received.set()

        await asyncio.sleep(0.5)

        # 创建测试客户端
        test_config = MQTTConfig(
            broker_host="163.61.102.47",
            broker_port=1883,
            client_id=f"test_client_{device_name}",
        )

        async with MQTTClient(test_config) as test_client:
            await asyncio.sleep(1)

            test_rpc = RPCManager(test_client, my_topic=f"test/{test_config.client_id}")
            test_events = EventChannelManager(test_client)

            # 同时执行 RPC 调用和 Event 发布
            rpc_task = test_rpc.call(
                topic=f"whale/{device_name}",
                method="get_status",
                params={},
                timeout=5,
            )

            event_task = test_events.publish(
                test_event_topic,
                {"test": "data"},
            )

            await asyncio.gather(rpc_task, event_task)
            await asyncio.sleep(0.5)

            assert rpc_called.is_set(), "RPC 应该被调用"
            assert event_received.is_set(), "Event 应该被接收"
            print("[成功] RPC 和 Event 共存工作正常")


@pytest.mark.integration
async def test_reconnect_config_validation():
    """测试重连配置参数验证"""
    print("\n[测试] 重连配置验证")

    config = MQTTConfig(
        broker_host="163.61.102.47",
        broker_port=1883,
        client_id="test_reconnect_config",
        reconnect=ReconnectConfig(
            enabled=True,
            interval=5,
            max_attempts=10,
            backoff_multiplier=1.5,
            max_interval=60,
        ),
    )

    async with MQTTClient(config) as mqtt:
        await asyncio.sleep(1)

        # 验证配置已正确设置
        assert mqtt.config.reconnect.enabled is True
        assert mqtt.config.reconnect.interval == 5
        assert mqtt.config.reconnect.max_attempts == 10
        assert mqtt.config.reconnect.backoff_multiplier == 1.5
        assert mqtt.config.reconnect.max_interval == 60

        print("[配置] enabled=True")
        print("[配置] interval=5")
        print("[配置] max_attempts=10")
        print("[配置] backoff_multiplier=1.5")
        print("[配置] max_interval=60")
        print("[成功] 重连配置验证通过")


@pytest.mark.integration
async def test_initialization_idempotency():
    """测试初始化的可重复性（幂等性）"""
    print("\n[测试] 初始化幂等性")

    device_name = "test_device_idempotent"

    config = MQTTConfig(
        broker_host="163.61.102.47",
        broker_port=1883,
        client_id=device_name,
    )

    # 多次初始化应该都能成功
    for i in range(3):
        mqtt = MQTTClient(config)
        await mqtt.connect()
        await asyncio.sleep(1)

        assert mqtt.is_connected, f"第 {i + 1} 次连接应该成功"

        rpc = RPCManager(mqtt, my_topic=f"whale/{device_name}")
        events = EventChannelManager(mqtt)

        assert rpc._client is mqtt
        assert events._client is mqtt

        await mqtt.disconnect()
        await asyncio.sleep(0.5)
        print(f"[第{i + 1}次] 初始化成功")

    print("[成功] 初始化幂等性测试通过")
