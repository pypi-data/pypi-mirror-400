# MQTT RPC 模块 - 基于 aiomqtt 的双向对等 RPC 调用

import asyncio
import json
import uuid
from typing import Any, Callable, Optional
from loguru import logger

from .client import MQTTClient
from .config import RPCConfig
from .exceptions import (
    RPCTimeoutError,
    RPCRemoteError,
    TooManyConcurrentCallsError,
    MQTTXError,
    ErrorCode,
)
from .protocol import RPCRequest, RPCResponse


# 权限检查回调类型
AuthCallback = Callable[[str, str, RPCRequest], bool]


class RPCManager:
    """RPC 调用管理器（基于 aiomqtt 客户端）

    核心改进（相对 gmqtt 版本）：
    1. 适配纯 async/await 模式（不依赖 EventEmitter）
    2. 权限控制（auth_callback 参数，修复 P0-4）
    3. 并发限制（max_concurrent_calls）
    4. 注销机制（unregister 方法，修复 P0-3）
    5. 方法拆分（降低复杂度）

    职责：
    - 发起远程 RPC 调用（通过 call 方法）
    - 注册本地方法供远程调用（通过 register 装饰器）
    - 处理 RPC 请求和响应消息
    - 管理并发调用的 Future 对象

    设计决策：
    - 不再依赖 EventEmitter，直接注册消息处理器到 MQTTClient
    - 使用 handle_rpc_message 作为消息处理入口
    - 权限检查在请求处理前进行（可拒绝执行）

    示例:
        # 创建 RPC 管理器（带权限控制）
        async def auth_check(caller_id, method, request):
            if method in ["delete_user"]:
                return caller_id in ADMIN_LIST
            return True

        rpc = RPCManager(client, auth_callback=auth_check)

        # 注册本地方法
        @rpc.register("get_status")
        async def get_status(params):
            return {"status": "online", "temperature": 25.5}

        # 订阅 RPC 主题并绑定处理器
        client.subscribe(
            "my/rpc/topic",
            lambda t, m: rpc.handle_rpc_message(t, m)
        )

        # 远程调用
        result = await rpc.call(
            topic="remote/rpc/topic",
            method="get_status",
            reply_to="my/rpc/topic"
        )
    """

    def __init__(
        self,
        client: MQTTClient,
        config: Optional[RPCConfig] = None,
        auth_callback: Optional[AuthCallback] = None
    ):
        """初始化 RPC 管理器

        Args:
            client: MQTTClient 实例（用于底层消息收发）
            config: RPC 配置（可选，默认使用标准配置）
            auth_callback: 权限检查回调函数（可选）
                签名：async def auth_callback(caller_id: str, method: str, request: RPCRequest) -> bool
                返回：True = 允许，False = 拒绝

        使用示例：
            client = MQTTClient(...)
            await client.connect()

            # 基础用法（无权限控制）
            rpc = RPCManager(client)

            # 带权限控制
            async def auth_check(caller_id, method, request):
                return caller_id in ALLOWED_CLIENTS

            rpc = RPCManager(client, auth_callback=auth_check)
        """
        self._client = client
        self.config = config or RPCConfig()
        self._auth_callback = auth_callback

        # RPC 状态
        self._pending_calls: dict[str, asyncio.Future] = {}  # request_id → Future
        self._handlers: dict[str, Callable] = {}  # method_name → handler
        self._pending_calls_lock = asyncio.Lock()  # 修复 P0-1：保护 _pending_calls 并发访问

        logger.info("RPCManager 已初始化")

    def register(self, method_name: str):
        """装饰器：注册本地 RPC 方法供远程调用

        Args:
            method_name: 方法名称（远程节点通过此名称调用）

        Returns:
            装饰器函数

        使用示例：
            @rpc.register("get_status")
            async def get_status(params):
                return {"status": "online", "temperature": 25.5}

            @rpc.register("process_command")
            def process_command(params):
                # 同步方法也支持
                return {"result": "ok"}
        """
        def decorator(func: Callable):
            self._handlers[method_name] = func
            logger.success(f"RPC 方法已注册: {method_name}")
            return func

        return decorator

    def unregister(self, method_name: str):
        """注销 RPC 方法

        修复点：
        - ✅ P0-3: 提供注销机制，防止内存泄漏

        Args:
            method_name: 方法名称

        使用示例：
            rpc.unregister("get_status")
        """
        if method_name in self._handlers:
            del self._handlers[method_name]
            logger.info(f"RPC 方法已注销: {method_name}")

    def handle_rpc_message(self, topic: str, message: RPCRequest | RPCResponse):
        """处理 RPC 消息（由 MQTTClient 调用）

        这是 RPC 消息的处理入口，替代 gmqtt 版本的 EventEmitter.emit

        Args:
            topic: MQTT 主题
            message: RPC 请求或响应消息

        使用示例：
            # 订阅主题并绑定 RPC 处理器
            client.subscribe(
                "my/rpc/topic",
                lambda t, m: rpc.handle_rpc_message(t, m)
            )
        """
        if isinstance(message, RPCRequest):
            asyncio.create_task(
                self._handle_request(topic, message),
                name=f"rpc_req_{message.request_id[:8]}"
            )
        elif isinstance(message, RPCResponse):
            asyncio.create_task(
                self._handle_response(topic, message),
                name=f"rpc_resp_{message.request_id[:8]}"
            )

    async def call(
        self,
        topic: str,
        method: str,
        params: Any = None,
        timeout: Optional[float] = None,
        reply_to: str = None,
    ) -> Any:
        """远程调用 RPC 方法

        修复点：
        - ✅ 新增并发限制检查

        Args:
            topic: 目标 MQTT 主题（例如：bots/456）
            method: 远程方法名
            params: 方法参数（可选）
            timeout: 超时时间（秒，None 则使用配置的默认值）
            reply_to: 响应主题（必需，例如：server/device_123）

        Returns:
            远程方法的返回值

        Raises:
            MQTTXError: 客户端未连接
            ValueError: reply_to 参数缺失
            TooManyConcurrentCallsError: 并发调用超限
            RPCTimeoutError: 调用超时
            RPCRemoteError: 远程执行失败

        使用示例：
            # 基础调用
            result = await rpc.call(
                topic="bots/456",
                method="get_status",
                reply_to="server/device_123"
            )

            # 带参数调用
            result = await rpc.call(
                topic="bots/456",
                method="process_command",
                params={"command": "restart"},
                reply_to="server/device_123",
                timeout=60.0
            )
        """
        if not self._client.is_connected:
            raise MQTTXError("MQTT 客户端未连接", ErrorCode.NOT_CONNECTED)

        if reply_to is None:
            raise ValueError("reply_to 参数是必需的，不能为 None")

        # 生成请求
        request_id = str(uuid.uuid4())
        timeout = timeout or self.config.default_timeout

        request = RPCRequest(
            request_id=request_id,
            method=method,
            params=params,
            reply_to=reply_to,
            caller_id=self._client.config.client_id,
        )

        # 修复 P0-1：原子性检查并发限制 + 注册 Future
        async with self._pending_calls_lock:
            if len(self._pending_calls) >= self.config.max_concurrent_calls:
                raise TooManyConcurrentCallsError(
                    f"并发 RPC 调用超限: {len(self._pending_calls)}/{self.config.max_concurrent_calls}"
                )
            # 创建 Future
            future = asyncio.get_event_loop().create_future()
            self._pending_calls[request_id] = future

        # 发送请求
        await self._client.publish(topic, json.dumps(request.to_dict()), qos=1)
        logger.debug(f"RPC 请求已发送 - method: {method}, request_id: {request_id[:8]}")

        try:
            # 等待响应
            result = await asyncio.wait_for(future, timeout=timeout)
            logger.debug(f"RPC 调用成功 - method: {method}")
            return result
        except asyncio.TimeoutError:
            logger.error(f"RPC 超时 - method: {method}, timeout: {timeout}s")
            raise RPCTimeoutError(f"RPC 调用超时: {method}")
        finally:
            # 清理 Future（修复 P0-1：使用锁保护）
            async with self._pending_calls_lock:
                self._pending_calls.pop(request_id, None)

    async def _handle_response(self, topic: str, message: RPCResponse):
        """处理 RPC 响应

        Args:
            topic: MQTT 主题
            message: RPC 响应消息
        """
        # 修复 P0-1：使用锁保护读取
        async with self._pending_calls_lock:
            future = self._pending_calls.get(message.request_id)

        if not future or future.done():
            logger.warning(f"收到未知/过期响应 - request_id: {message.request_id[:8]}")
            return

        if message.error:
            future.set_exception(RPCRemoteError(message.error))
        else:
            future.set_result(message.result)

    async def _handle_request(self, topic: str, message: RPCRequest):
        """处理 RPC 请求

        修复点：
        - ✅ P0-4: 添加权限检查
        - ✅ 重构为子方法（降低复杂度）

        Args:
            topic: MQTT 主题
            message: RPC 请求消息

        执行流程：
        1. 权限检查（如果配置了 auth_callback）
        2. 查找处理器
        3. 执行方法
        4. 发送响应
        """
        # 权限检查
        if self._auth_callback:
            allowed = await self._check_permission(message)
            if not allowed:
                logger.warning(
                    f"RPC 权限拒绝 - caller: {message.caller_id}, method: {message.method}"
                )
                response = RPCResponse(
                    request_id=message.request_id,
                    error="Permission denied"
                )
                await self._send_response(message.reply_to, response)
                return

        # 查找处理器
        handler = self._handlers.get(message.method)

        if not handler:
            logger.warning(f"方法未找到 - method: {message.method}")
            response = RPCResponse(
                request_id=message.request_id,
                error=f"方法未找到: {message.method}"
            )
        else:
            # 执行方法
            response = await self._execute_handler(handler, message)

        # 发送响应
        await self._send_response(message.reply_to, response)

    async def _check_permission(self, message: RPCRequest) -> bool:
        """检查 RPC 调用权限

        Args:
            message: RPC 请求消息

        Returns:
            True = 允许，False = 拒绝

        异常处理：
        - 如果 auth_callback 抛出异常，默认拒绝（fail-safe）
        """
        try:
            if asyncio.iscoroutinefunction(self._auth_callback):
                allowed = await self._auth_callback(
                    message.caller_id,
                    message.method,
                    message
                )
            else:
                allowed = self._auth_callback(
                    message.caller_id,
                    message.method,
                    message
                )
            return bool(allowed)
        except Exception as e:
            logger.exception(f"权限检查失败: {e}")
            return False  # 默认拒绝

    async def _execute_handler(self, handler: Callable, message: RPCRequest) -> RPCResponse:
        """执行 RPC 方法处理器

        Args:
            handler: 注册的方法处理器
            message: RPC 请求消息

        Returns:
            RPC 响应消息（包含结果或错误）

        异常处理：
        - asyncio.CancelledError: 向上传播（任务被取消）
        - 其他异常: 捕获并封装到 RPCResponse.error
        """
        try:
            # 自动处理同步/异步函数
            if asyncio.iscoroutinefunction(handler):
                result = await handler(message.params)
            else:
                result = handler(message.params)

            logger.debug(f"RPC 方法执行成功 - method: {message.method}")
            return RPCResponse(
                request_id=message.request_id,
                result=result
            )

        except asyncio.CancelledError:
            # 任务被取消，向上传播
            raise

        except Exception as e:
            logger.exception(f"RPC 方法执行失败 - method: {message.method}")
            return RPCResponse(
                request_id=message.request_id,
                error=str(e)
            )

    async def _send_response(self, topic: str, response: RPCResponse):
        """发送 RPC 响应

        Args:
            topic: 响应主题
            response: RPC 响应消息
        """
        await self._client.publish(topic, json.dumps(response.to_dict()), qos=1)
        logger.debug(f"RPC 响应已发送 - request_id: {response.request_id[:8]}")
