# 约定式 RPC 管理器 - 去角色设计

from typing import Any, Optional
from loguru import logger

from .client import MQTTClient
from .config import RPCConfig
from .rpc import RPCManager, AuthCallback


class ConventionalRPCManager(RPCManager):
    """约定式 RPC 管理器

    设计原则：
    - 约定优于配置
    - 自动订阅本地 topic
    - 自动注入 reply_to

    核心功能：
    1. 初始化时自动订阅 `my_topic`
    2. 调用时自动将 `my_topic` 注入到 `reply_to`

    适用场景：
    - 边缘设备 ↔ 云端（edge/xxx ↔ cloud/xxx）
    - 微服务之间（auth-service ↔ user-service）
    - IoT 网关 ↔ 设备（gateway/001 ↔ device/123）
    - 任何需要简化 RPC 调用的场景

    示例:
        # 边缘设备
        rpc = ConventionalRPCManager(client, my_topic="edge/device_123")

        @rpc.register("get_status")
        async def get_status(params):
            return {"status": "online"}

        # 调用云端（自动注入 reply_to="edge/device_123"）
        config = await rpc.call("cloud/config-service", "get_config")

        # 云端服务
        rpc = ConventionalRPCManager(client, my_topic="cloud/config-service")

        # 调用边缘设备（自动注入 reply_to="cloud/config-service"）
        status = await rpc.call("edge/device_123", "execute_command")
    """

    def __init__(
        self,
        client: MQTTClient,
        my_topic: str,
        config: Optional[RPCConfig] = None,
        auth_callback: Optional[AuthCallback] = None,
    ):
        """初始化约定式 RPC 管理器

        Args:
            client: MQTTClient 实例
            my_topic: 本节点的 topic（自动订阅，自动注入到 reply_to）
            config: RPC 配置（可选）
            auth_callback: 权限检查回调（可选）

        自动行为：
        - 自动订阅 my_topic
        - 自动绑定消息处理器

        示例:
            # 边缘设备
            rpc = ConventionalRPCManager(client, my_topic="edge/device_123")

            # 云端服务
            rpc = ConventionalRPCManager(client, my_topic="cloud/server_001")

            # 微服务
            rpc = ConventionalRPCManager(client, my_topic="auth-service")

            # 多层级
            rpc = ConventionalRPCManager(client, my_topic="region/zone/device")
        """
        super().__init__(client, config, auth_callback)

        self._my_topic = my_topic

        # 自动订阅
        client.subscribe(my_topic, self.handle_rpc_message)

        logger.info(f"ConventionalRPCManager 已初始化 - my_topic: {my_topic}")

    async def call(
        self,
        topic: str,
        method: str,
        params: Any = None,
        timeout: Optional[float] = None,
        reply_to: Optional[str] = None,
    ) -> Any:
        """调用远程方法（自动注入 reply_to）

        Args:
            topic: 对方的 topic
            method: 方法名
            params: 参数（可选）
            timeout: 超时时间（可选）
            reply_to: 响应 topic（可选，默认使用 my_topic）

        Returns:
            方法返回值

        Raises:
            MQTTXError: 客户端未连接
            RPCTimeoutError: 调用超时
            RPCRemoteError: 远程执行失败

        示例:
            # 边缘设备调用云端
            rpc = ConventionalRPCManager(client, my_topic="edge/device_123")
            result = await rpc.call("cloud/server_001", "get_config")
            # 等价于：await super().call("cloud/server_001", "get_config", reply_to="edge/device_123")

            # 云端调用边缘设备
            rpc = ConventionalRPCManager(client, my_topic="cloud/server_001")
            result = await rpc.call("edge/device_123", "execute_command", params={"cmd": "restart"})

            # 微服务调用
            rpc = ConventionalRPCManager(client, my_topic="auth-service")
            user = await rpc.call("user-service", "get_user", params={"id": 123})
        """
        # 自动注入 reply_to
        reply_to = reply_to or self._my_topic

        return await super().call(
            topic=topic,
            method=method,
            params=params,
            timeout=timeout,
            reply_to=reply_to,
        )

    @property
    def my_topic(self) -> str:
        """获取当前节点的 topic

        Returns:
            当前节点订阅的 topic
        """
        return self._my_topic
