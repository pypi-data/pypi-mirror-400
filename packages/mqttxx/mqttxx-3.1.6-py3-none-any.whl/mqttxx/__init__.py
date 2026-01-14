"""MQTTX - 基于 aiomqtt 的高级 MQTT 客户端和 RPC 框架

提供：
- MQTTClient: MQTT 连接管理（自动重连、订阅队列化、TLS/SSL 支持）
- RPCManager: 双向对等 RPC 调用（超时控制、权限检查、并发限制）
- EventChannelManager: 高吞吐事件广播通道（单向、无返回值）
- 配置对象: MQTTConfig, TLSConfig, AuthConfig, RPCConfig 等
- 协议定义: RPCRequest, RPCResponse, EventMessage
- 异常系统: 统一错误码和异常层次
"""

__version__ = "3.1.0"
__author__ = "MQTTX Team"

# 核心客户端
from .client import MQTTClient

# RPC 管理器
from .rpc import RPCManager

# Event Channel 管理器
from .events import EventChannelManager, EventMessage

# 配置对象
from .config import (
    MQTTConfig,
    TLSConfig,
    AuthConfig,
    ReconnectConfig,
    RPCConfig,
)

# 协议定义
from .protocol import (
    RPCRequest,
    RPCResponse,
    # parse_message 是内部 API，不再导出
)

# 异常系统
from .exceptions import (
    # 错误码
    ErrorCode,
    # 基础异常
    MQTTXError,
    ConnectionError,
    MessageError,
    RPCError,
    # RPC 异常
    RPCTimeoutError,
    RPCRemoteError,
    RPCMethodNotFoundError,
    PermissionDeniedError,
    TooManyConcurrentCallsError,
)

__all__ = [
    # MQTT 客户端
    "MQTTClient",
    # RPC 管理器
    "RPCManager",
    # Event Channel 管理器
    "EventChannelManager",
    "EventMessage",
    # 配置对象
    "MQTTConfig",
    "TLSConfig",
    "AuthConfig",
    "ReconnectConfig",
    "RPCConfig",
    # 协议定义
    "RPCRequest",
    "RPCResponse",
    # parse_message 已移除 - 内部 API
    # 异常系统
    "ErrorCode",
    "MQTTXError",
    "ConnectionError",
    "MessageError",
    "RPCError",
    "RPCTimeoutError",
    "RPCRemoteError",
    "RPCMethodNotFoundError",
    "PermissionDeniedError",
    "TooManyConcurrentCallsError",
]
