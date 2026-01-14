# MQTT 客户端配置对象

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class TLSConfig:
    """TLS/SSL 配置

    用于配置 MQTT 连接的加密传输层

    Attributes:
        enabled: 是否启用 TLS/SSL
        ca_certs: CA 证书路径（用于验证服务器证书）
        certfile: 客户端证书路径（双向认证）
        keyfile: 客户端私钥路径（双向认证）
        verify_mode: 证书验证模式（"CERT_REQUIRED" | "CERT_OPTIONAL" | "CERT_NONE"）
        check_hostname: 是否验证服务器主机名

    示例:
        # 单向 TLS（仅验证服务器）
        tls = TLSConfig(
            enabled=True,
            ca_certs=Path("/path/to/ca.crt")
        )

        # 双向 TLS（客户端证书认证）
        tls = TLSConfig(
            enabled=True,
            ca_certs=Path("/path/to/ca.crt"),
            certfile=Path("/path/to/client.crt"),
            keyfile=Path("/path/to/client.key")
        )
    """

    enabled: bool = False
    ca_certs: Optional[Path] = None
    certfile: Optional[Path] = None
    keyfile: Optional[Path] = None
    verify_mode: str = "CERT_REQUIRED"
    check_hostname: bool = True


@dataclass
class AuthConfig:
    """MQTT 认证配置

    用于配置 MQTT Broker 的用户名密码认证

    Attributes:
        username: MQTT 用户名
        password: MQTT 密码

    示例:
        auth = AuthConfig(
            username="device_123",
            password="secret_password"
        )
    """

    username: Optional[str] = None
    password: Optional[str] = None


@dataclass
class ReconnectConfig:
    """重连配置

    配置 MQTT 连接断开后的自动重连行为

    Attributes:
        enabled: 是否启用自动重连
        interval: 初始重连间隔（秒）
        max_attempts: 最大重连次数（0 = 无限重试）
        backoff_multiplier: 指数退避倍数（每次重连失败后，间隔乘以此倍数）
        max_interval: 最大重连间隔（秒）

    示例:
        # 无限重试，指数退避
        reconnect = ReconnectConfig(
            enabled=True,
            interval=5,
            max_attempts=0,
            backoff_multiplier=1.5,
            max_interval=60
        )

        # 固定间隔，最多重试 10 次
        reconnect = ReconnectConfig(
            interval=5,
            max_attempts=10,
            backoff_multiplier=1.0  # 不使用指数退避
        )
    """

    enabled: bool = True
    interval: int = 5
    max_attempts: int = 0
    backoff_multiplier: float = 1.5
    max_interval: int = 60


@dataclass
class MQTTConfig:
    """MQTT 客户端完整配置

    所有 MQTT 连接相关的配置参数

    Attributes:
        broker_host: MQTT Broker 地址
        broker_port: MQTT Broker 端口（1883=明文, 8883=TLS）
        client_id: 客户端标识符（空字符串=自动生成）
        keepalive: 心跳保活时间（秒）
        clean_session: 是否清除会话（False=服务器保持订阅）
        tls: TLS/SSL 配置
        auth: 认证配置
        reconnect: 重连配置
        max_queued_messages: 最大排队消息数（0=无限）
        max_payload_size: 最大消息载荷大小（字节，防止 DoS 攻击）
        message_queue_maxsize: 消息队列大小限制（默认 100,000）
            - 语义："几乎无限"，仅作保险丝防止 OOM
            - 队列满时行为：阻塞等待（背压信号）
            - 触发背压时：CPU/延迟升高 → 扩容信号
            - Python 字面量分隔符：100_000 = 100000（下划线仅用于可读性）
        num_workers: Worker 数量（默认 None = CPU核数×2）
            - None（默认）：CPU核数 × 2（适合 IO-bound 负载）
            - 自定义值：根据 handler 类型调整
                - CPU-bound handler：设为 CPU核数
                - IO-bound handler：设为 CPU核数 × 2~4
        log_level: 日志级别（DEBUG|INFO|WARNING|ERROR）

    示例:
        # 基础配置（明文连接）
        config = MQTTConfig(
            broker_host="localhost",
            client_id="device_123"
        )

        # 生产配置（TLS + 认证 + 自动重连）
        config = MQTTConfig(
            broker_host="mqtt.example.com",
            broker_port=8883,
            client_id="device_123",
            clean_session=False,  # 保持会话
            tls=TLSConfig(
                enabled=True,
                ca_certs=Path("/etc/ssl/ca.crt")
            ),
            auth=AuthConfig(
                username="device_123",
                password="secret"
            ),
            reconnect=ReconnectConfig(
                interval=5,
                max_attempts=0  # 无限重试
            )
        )
    """

    # 连接参数
    broker_host: str
    broker_port: int = 1883
    client_id: str = ""
    keepalive: int = 60
    clean_session: bool = False

    # 子配置对象
    tls: TLSConfig = field(default_factory=TLSConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    reconnect: ReconnectConfig = field(default_factory=ReconnectConfig)

    # 消息限制
    max_queued_messages: int = 0  # 0 = 无限
    max_payload_size: int = 1024 * 1024  # 1MB

    # 消息处理（修复 P0-A）
    message_queue_maxsize: int = 100_000  # 10W 条 队列最大容量（保险丝）
    num_workers: Optional[int] = None  # Worker 数量（None = CPU核数×2）

    # 日志级别
    log_level: str = "INFO"


@dataclass
class RPCConfig:
    """RPC 配置

    RPC 调用相关的配置参数

    Attributes:
        default_timeout: 默认超时时间（秒）
        max_concurrent_calls: 最大并发 RPC 调用数

    示例:
        rpc_config = RPCConfig(
            default_timeout=30.0,
            max_concurrent_calls=100
        )
    """

    default_timeout: float = 30.0
    max_concurrent_calls: int = 100
