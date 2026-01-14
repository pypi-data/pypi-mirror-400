# 连接管理测试

import pytest
import asyncio
from mqttxx import MQTTClient, MQTTConfig
from mqttxx.config import ReconnectConfig


pytestmark = [pytest.mark.integration, pytest.mark.p0]


class TestBasicConnection:
    """基础连接测试"""

    @pytest.mark.asyncio
    async def test_basic_connect(self, mqtt_client):
        """测试基础连接功能"""
        # Fixture 已验证连接
        assert mqtt_client.is_connected

    @pytest.mark.asyncio
    async def test_context_manager(self, mqtt_client_context):
        """测试上下文管理器"""
        client = mqtt_client_context
        assert client.is_connected
        # 退出时会自动清理

    @pytest.mark.asyncio
    async def test_disconnect(self, mqtt_client):
        """测试断开连接"""
        assert mqtt_client.is_connected
        await mqtt_client.disconnect()
        await asyncio.sleep(0.2)
        assert not mqtt_client.is_connected

    @pytest.mark.asyncio
    async def test_multiple_connect_calls(self, mqtt_client):
        """测试多次调用 connect（幂等性）"""
        assert mqtt_client.is_connected
        await mqtt_client.connect()  # 第二次调用
        assert mqtt_client.is_connected

    @pytest.mark.asyncio
    async def test_is_connected_property(self, mqtt_client):
        """测试 is_connected 属性"""
        # 连接状态
        assert mqtt_client.is_connected is True

        # 断开后
        await mqtt_client.disconnect()
        await asyncio.sleep(0.2)
        assert mqtt_client.is_connected is False


class TestConnectionWithConfig:
    """使用不同配置的连接测试"""

    @pytest.mark.asyncio
    async def test_connect_with_custom_keepalive(self, unique_client_id, mqtt_broker_config):
        """测试自定义 keepalive 参数"""
        config = MQTTConfig(
            broker_host=mqtt_broker_config["host"],
            broker_port=mqtt_broker_config["port"],
            client_id=unique_client_id,
            keepalive=30,
        )
        async with MQTTClient(config) as client:
            await asyncio.sleep(0.5)  # 等待连接建立
            assert client.is_connected

    @pytest.mark.asyncio
    async def test_connect_with_clean_session(self, unique_client_id, mqtt_broker_config):
        """测试 clean_session 参数"""
        config = MQTTConfig(
            broker_host=mqtt_broker_config["host"],
            broker_port=mqtt_broker_config["port"],
            client_id=unique_client_id,
            clean_session=True,
        )
        async with MQTTClient(config) as client:
            await asyncio.sleep(0.5)  # 等待连接建立
            assert client.is_connected

    @pytest.mark.asyncio
    async def test_connect_with_custom_workers(self, unique_client_id, mqtt_broker_config):
        """测试自定义 worker 数量"""
        config = MQTTConfig(
            broker_host=mqtt_broker_config["host"],
            broker_port=mqtt_broker_config["port"],
            client_id=unique_client_id,
            num_workers=4,
        )
        async with MQTTClient(config) as client:
            await asyncio.sleep(0.5)  # 等待连接建立
            assert client.is_connected
            # 验证 worker 创建
            assert len(client._workers) == 4
