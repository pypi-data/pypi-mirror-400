# 集成测试 - RPC 和 Event 混合场景

import asyncio
import pytest
from mqttxx import MQTTClient, MQTTConfig, RPCManager, EventChannelManager, EventMessage


@pytest.mark.integration
async def test_rpc_and_event_coexist(mqtt_config):
    """测试 RPC 和 Event 在同一客户端共存"""
    print("\n[测试] RPC 和 Event 共存")

    async with MQTTClient(mqtt_config) as client:
        await asyncio.sleep(1)

        # 创建 RPC 和 Event 管理器
        rpc = RPCManager(client, my_topic=f"rpc/test/{client.config.client_id}")
        events = EventChannelManager(client)

        rpc_received = asyncio.Event()
        event_received = asyncio.Event()

        # 注册 RPC 方法
        @rpc.register("get_status")
        async def get_status(params):
            rpc_received.set()
            print("[RPC] 收到调用: get_status")
            return {"status": "online", "cpu": 45.2}

        # 订阅事件
        test_event_topic = f"test/integration/{client.config.client_id}"

        @events.subscribe(test_event_topic)
        async def event_handler(topic: str, message: dict):
            event_received.set()
            print(f"[Event] 收到事件: {topic}")

        await asyncio.sleep(0.5)

        # 创建另一个客户端进行调用
        caller_config = mqtt_config.__class__(
            broker_host=mqtt_config.broker_host,
            broker_port=mqtt_config.broker_port,
            client_id=f"test_caller_{mqtt_config.client_id}",
        )

        async with MQTTClient(caller_config) as caller:
            await asyncio.sleep(1)

            caller_rpc = RPCManager(
                caller, my_topic=f"rpc/caller/{caller.config.client_id}"
            )
            caller_events = EventChannelManager(caller)

            # 并发执行 RPC 调用和 Event 发布
            rpc_task = caller_rpc.call(
                topic=f"rpc/test/{client.config.client_id}",
                method="get_status",
                params={},
                timeout=5,
            )

            event_task = caller_events.publish(
                test_event_topic,
                {"test": "integration"},
            )

            # 等待两者完成
            await asyncio.gather(rpc_task, event_task)
            await asyncio.sleep(0.5)

            assert rpc_received.is_set(), "RPC 应该被调用"
            assert event_received.is_set(), "Event 应该被接收"
            print("[成功] RPC 和 Event 共存测试通过")


@pytest.mark.integration
async def test_bidirectional_rpc(two_clients):
    """测试双向 RPC 调用"""
    print("\n[测试] 双向 RPC 调用")

    client_a, client_b = two_clients

    # 客户端 A
    rpc_a = RPCManager(client_a, my_topic=f"rpc/a/{client_a.config.client_id}")

    @rpc_a.register("method_a")
    async def method_a(params):
        print("[A] 收到来自 B 的调用")
        return {"from": "A", "value": params.get("x", 0) * 2}

    # 客户端 B
    rpc_b = RPCManager(client_b, my_topic=f"rpc/b/{client_b.config.client_id}")

    @rpc_b.register("method_b")
    async def method_b(params):
        print("[B] 收到来自 A 的调用")
        return {"from": "B", "value": params.get("y", 0) + 10}

    await asyncio.sleep(0.5)

    # A 调用 B
    print("[调用] A → B: method_b")
    result_a = await rpc_a.call(
        topic=f"rpc/b/{client_b.config.client_id}",
        method="method_b",
        params={"y": 5},
        timeout=5,
    )
    assert result_a["from"] == "B", "应该来自 B"
    assert result_a["value"] == 15, "5 + 10 = 15"
    print(f"[结果] A 收到: {result_a}")

    # B 调用 A
    print("[调用] B → A: method_a")
    result_b = await rpc_b.call(
        topic=f"rpc/a/{client_a.config.client_id}",
        method="method_a",
        params={"x": 3},
        timeout=5,
    )
    assert result_b["from"] == "A", "应该来自 A"
    assert result_b["value"] == 6, "3 * 2 = 6"
    print(f"[结果] B 收到: {result_b}")

    print("[成功] 双向 RPC 调用测试通过")


@pytest.mark.integration
async def test_device_server_scenario():
    """测试设备-服务器场景 (RPC 配置下发 + Event 心跳上报)"""
    print("\n[测试] 设备-服务器场景")

    # 设备端配置
    device_config = MQTTConfig(
        broker_host="163.61.102.47",
        broker_port=1883,
        client_id=f"test_device_{asyncio.get_event_loop().time():.0f}",
    )

    # 服务器端配置
    server_config = MQTTConfig(
        broker_host="163.61.102.47",
        broker_port=1883,
        client_id=f"test_server_{asyncio.get_event_loop().time():.0f}",
    )

    device = MQTTClient(device_config)
    server = MQTTClient(server_config)

    await device.connect()
    await server.connect()
    await asyncio.sleep(1)

    # === 设备端 ===
    device_rpc = RPCManager(device, my_topic=f"device/{device_config.client_id}")
    device_events = EventChannelManager(device)

    @device_rpc.register("get_config")
    async def get_config(params):
        print("[设备] 收到配置请求")
        return {"interval": 60, "log_level": "INFO"}

    heartbeat_count = {"count": 0}

    # === 服务器端 ===
    server_rpc = RPCManager(server, my_topic=f"server/{server_config.client_id}")
    server_events = EventChannelManager(server)

    server_received_heartbeat = asyncio.Event()

    @server_events.subscribe("device/+/heartbeat")
    async def on_heartbeat(topic: str, message: dict):
        heartbeat_count["count"] += 1
        server_received_heartbeat.set()
        print(f"[服务器] 收到心跳 #{heartbeat_count['count']}: {topic}")

    await asyncio.sleep(0.5)

    # 场景 1: 服务器调用设备获取配置
    print("\n[场景1] 服务器 → 设备: 获取配置")
    config_result = await server_rpc.call(
        topic=f"device/{device_config.client_id}",
        method="get_config",
        params={},
        timeout=5,
    )
    assert config_result["interval"] == 60, "配置应该正确"
    print(f"[结果] 配置获取成功: {config_result}")

    # 场景 2: 设备发布心跳，服务器接收
    print("\n[场景2] 设备 → 服务器: 心跳上报")
    for i in range(3):
        server_received_heartbeat.clear()
        await device_events.publish(
            f"device/{device_config.client_id}/heartbeat",
            EventMessage(
                event_type="heartbeat",
                data={"sequence": i, "cpu": 45.2 + i},
                source=device_config.client_id,
            ),
        )
        print(f"[设备] 发送心跳 #{i + 1}")
        await asyncio.wait_for(server_received_heartbeat.wait(), timeout=5.0)

    assert heartbeat_count["count"] == 3, "应该收到 3 个心跳"
    print(f"[结果] 收到 {heartbeat_count['count']} 个心跳")

    # 清理
    await device.disconnect()
    await server.disconnect()

    print("[成功] 设备-服务器场景测试通过")
