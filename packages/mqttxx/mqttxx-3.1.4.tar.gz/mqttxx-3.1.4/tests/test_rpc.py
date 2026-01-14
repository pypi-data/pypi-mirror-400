# RPC 系统测试

import pytest
import asyncio
from mqttxx import RPCManager, ConventionalRPCManager


pytestmark = [pytest.mark.integration, pytest.mark.p0]


class TestRPCBasic:
    """RPC 基础功能测试"""

    @pytest.mark.asyncio
    async def test_rpc_method_registration(self, rpc_manager):
        """测试 RPC 方法注册"""
        rpc = rpc_manager

        @rpc.register("test_method")
        async def test_handler(params):
            return {"result": "ok"}

        # 验证方法已注册
        assert "test_method" in rpc._handlers

    @pytest.mark.asyncio
    async def test_rpc_call(self, two_mqtt_clients, test_topic_namespace):
        """测试 RPC 调用"""
        client1, client2 = two_mqtt_clients

        # 服务端
        rpc_server = RPCManager(client1)
        server_topic = f"{test_topic_namespace}/rpc/server"
        rpc_server.setup(server_topic)

        @rpc_server.register("get_status")
        async def get_status(params):
            return {"status": "online", "cpu": 45.2}

        # 客户端
        rpc_client = RPCManager(client2)
        client_topic = f"{test_topic_namespace}/rpc/client"
        rpc_client.setup(client_topic)

        await asyncio.sleep(0.5)

        # 调用
        result = await rpc_client.call(
            topic=server_topic,
            method="get_status",
            reply_to=client_topic,
            timeout=5.0
        )

        assert result["status"] == "online"
        assert result["cpu"] == 45.2

    @pytest.mark.asyncio
    async def test_rpc_with_params(self, two_mqtt_clients, test_topic_namespace):
        """测试带参数的 RPC 调用"""
        client1, client2 = two_mqtt_clients

        rpc_server = RPCManager(client1)
        server_topic = f"{test_topic_namespace}/rpc/server2"
        rpc_server.setup(server_topic)

        @rpc_server.register("add")
        async def add_numbers(params):
            a = params.get("a", 0)
            b = params.get("b", 0)
            return {"sum": a + b}

        rpc_client = RPCManager(client2)
        client_topic = f"{test_topic_namespace}/rpc/client2"
        rpc_client.setup(client_topic)

        await asyncio.sleep(0.5)

        # 调用
        result = await rpc_client.call(
            topic=server_topic,
            method="add",
            params={"a": 10, "b": 20},
            reply_to=client_topic,
            timeout=5.0
        )

        assert result["sum"] == 30

    @pytest.mark.asyncio
    async def test_rpc_bidirectional(self, two_mqtt_clients, test_topic_namespace):
        """测试双向 RPC 调用"""
        client1, client2 = two_mqtt_clients

        # 双方都注册方法
        rpc1 = RPCManager(client1)
        topic1 = f"{test_topic_namespace}/rpc/peer1"
        rpc1.setup(topic1)

        @rpc1.register("method1")
        async def method1(params):
            return {"from": "peer1"}

        rpc2 = RPCManager(client2)
        topic2 = f"{test_topic_namespace}/rpc/peer2"
        rpc2.setup(topic2)

        @rpc2.register("method2")
        async def method2(params):
            return {"from": "peer2"}

        await asyncio.sleep(0.5)

        # Peer1 调用 Peer2
        result1 = await rpc1.call(topic2, "method2", reply_to=topic1, timeout=5.0)
        assert result1["from"] == "peer2"

        # Peer2 调用 Peer1
        result2 = await rpc2.call(topic1, "method1", reply_to=topic2, timeout=5.0)
        assert result2["from"] == "peer1"

    @pytest.mark.asyncio
    async def test_rpc_concurrent_calls(self, two_mqtt_clients, test_topic_namespace):
        """测试并发 RPC 调用"""
        client1, client2 = two_mqtt_clients

        rpc_server = RPCManager(client1)
        server_topic = f"{test_topic_namespace}/rpc/server3"
        rpc_server.setup(server_topic)

        @rpc_server.register("delayed_response")
        async def delayed_response(params):
            delay = params.get("delay", 0.1)
            await asyncio.sleep(delay)
            return {"delay": delay}

        rpc_client = RPCManager(client2)
        client_topic = f"{test_topic_namespace}/rpc/client3"
        rpc_client.setup(client_topic)

        await asyncio.sleep(0.5)

        # 并发调用
        tasks = [
            rpc_client.call(server_topic, "delayed_response",
                          params={"delay": 0.1}, reply_to=client_topic, timeout=5.0)
            for _ in range(5)
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 5
        for r in results:
            assert "delay" in r


class TestRPCConventional:
    """约定式 RPC 测试"""

    @pytest.mark.asyncio
    async def test_conventional_rpc_auto_setup(self, mqtt_client, test_topic_namespace):
        """测试约定式 RPC 自动设置"""
        my_topic = f"{test_topic_namespace}/conv/client"
        rpc = ConventionalRPCManager(mqtt_client, my_topic=my_topic)

        # 验证自动订阅
        assert rpc.my_topic == my_topic

        @rpc.register("test_method")
        async def test_method(params):
            return {"ok": True}

        # 方法已注册
        assert "test_method" in rpc._handlers

    @pytest.mark.asyncio
    async def test_conventional_rpc_call(self, two_mqtt_clients, test_topic_namespace):
        """测试约定式 RPC 调用（自动注入 reply_to）"""
        client1, client2 = two_mqtt_clients

        # Peer 1
        rpc1 = ConventionalRPCManager(client1, my_topic=f"{test_topic_namespace}/conv/peer1")

        @rpc1.register("get_config")
        async def get_config(params):
            return {"interval": 60, "retries": 3}

        # Peer 2
        rpc2 = ConventionalRPCManager(client2, my_topic=f"{test_topic_namespace}/conv/peer2")

        @rpc2.register("get_status")
        async def get_status(params):
            return {"status": "online"}

        await asyncio.sleep(0.5)

        # Peer 1 调用 Peer 2（无需指定 reply_to）
        result = await rpc1.call(
            topic=f"{test_topic_namespace}/conv/peer2",
            method="get_status",
            timeout=5.0
        )

        assert result["status"] == "online"

        # Peer 2 调用 Peer 1
        result = await rpc2.call(
            topic=f"{test_topic_namespace}/conv/peer1",
            method="get_config",
            timeout=5.0
        )

        assert result["interval"] == 60

    @pytest.mark.asyncio
    async def test_conventional_rpc_microservice_pattern(self, mqtt_client, test_topic_namespace):
        """测试微服务模式"""
        # 创建多个服务
        auth_service = ConventionalRPCManager(
            mqtt_client,
            my_topic=f"{test_topic_namespace}/services/auth"
        )

        user_service = ConventionalRPCManager(
            mqtt_client,
            my_topic=f"{test_topic_namespace}/services/user"
        )

        @auth_service.register("validate_token")
        async def validate_token(params):
            return {"valid": True, "user_id": 123}

        @user_service.register("get_user")
        async def get_user(params):
            user_id = params.get("user_id", 0)
            return {"id": user_id, "name": "Alice"}

        await asyncio.sleep(0.3)

        # 服务间调用
        result = await auth_service.call(
            topic=f"{test_topic_namespace}/services/user",
            method="get_user",
            params={"user_id": 123},
            timeout=5.0
        )

        assert result["name"] == "Alice"


class TestRPCTimeout:
    """RPC 超时测试"""

    @pytest.mark.asyncio
    async def test_rpc_timeout(self, two_mqtt_clients, test_topic_namespace):
        """测试 RPC 调用超时"""
        from mqttxx.exceptions import RPCTimeoutError

        client1, client2 = two_mqtt_clients

        rpc_server = RPCManager(client1)
        server_topic = f"{test_topic_namespace}/rpc/slow"
        rpc_server.setup(server_topic)

        @rpc_server.register("slow_method")
        async def slow_method(params):
            await asyncio.sleep(10)  # 模拟慢方法
            return {"ok": True}

        rpc_client = RPCManager(client2)
        client_topic = f"{test_topic_namespace}/rpc/fast_client"
        rpc_client.setup(client_topic)

        await asyncio.sleep(0.5)

        # 调用并设置短超时
        with pytest.raises(RPCTimeoutError):
            await rpc_client.call(
                topic=server_topic,
                method="slow_method",
                reply_to=client_topic,
                timeout=1.0  # 1 秒超时
            )


class TestRPCUnregister:
    """RPC 方法注销测试"""

    @pytest.mark.asyncio
    async def test_unregister_method(self, rpc_manager):
        """测试方法注销"""
        rpc = rpc_manager

        @rpc.register("temp_method")
        async def temp_method(params):
            return {"ok": True}

        assert "temp_method" in rpc._handlers

        # 注销
        rpc.unregister("temp_method")

        assert "temp_method" not in rpc._handlers
