# MQTTX

基于 [aiomqtt](https://github.com/sbtinstruments/aiomqtt) 的高级 MQTT 客户端和 RPC 框架。

**核心特性：**
- ✅ 纯 async/await，无回调
- ✅ 自动重连、订阅队列化
- ✅ 双向对等 RPC（带权限控制）
- ✅ TLS/SSL、认证支持
- ✅ 约定式 RPC（零配置）

---

## 安装

```bash
pip install mqttxx
```

---

## 快速开始

### 1. MQTT 基础用法

```python
import asyncio
from mqttxx import MQTTClient, MQTTConfig

async def main():
    config = MQTTConfig(
        broker_host="localhost",
        broker_port=1883,
        client_id="device_123"
    )

    async with MQTTClient(config) as client:
        # 订阅主题
        def on_message(topic, message):
            print(f"{topic}: {message}")

        client.subscribe("sensors/#", on_message)

        # 发布消息
        await client.publish("sensors/temperature", "25.5", qos=1)

        await asyncio.sleep(60)

asyncio.run(main())
```

---

### 2. 约定式 RPC（零配置）

**推荐**：使用 `ConventionalRPCManager`，自动订阅 + 自动注入 reply_to。

```python
from mqttxx import MQTTClient, MQTTConfig, ConventionalRPCManager

# 边缘设备
async def edge_device():
    client_id = "device_123"
    config = MQTTConfig(
        broker_host="localhost",
        client_id=client_id,
    )

    async with MQTTClient(config) as client:
        # 自动订阅 edge/device_123
        rpc = ConventionalRPCManager(client, my_topic=f"edge/{client_id}")

        @rpc.register("get_status")
        async def get_status(params):
            return {"status": "online"}

        # 调用云端（自动注入 reply_to="edge/device_123"）
        config = await rpc.call("cloud/config-service", "get_device_config")
        print(config)

        await asyncio.sleep(60)

# 云端服务
async def cloud_service():
    client_id = "config-service"
    config = MQTTConfig(
        broker_host="localhost",
        client_id=client_id,
    )

    async with MQTTClient(config) as client:
        # 自动订阅 cloud/config-service
        rpc = ConventionalRPCManager(client, my_topic=f"cloud/{client_id}")

        @rpc.register("get_device_config")
        async def get_device_config(params):
            return {"update_interval": 60, "servers": ["s1", "s2"]}

        # 调用边缘设备（自动注入 reply_to="cloud/config-service"）
        status = await rpc.call("edge/device_123", "execute_command", params={"cmd": "restart"})
        print(status)

        await asyncio.sleep(60)

# 运行边缘设备或云端
asyncio.run(edge_device())  # 或 asyncio.run(cloud_service())
```

**对比传统 RPC：**

| 场景 | 传统 RPC | 约定式 RPC |
|-----|---------|-----------|
| 初始化 | `rpc = RPCManager(client)`<br>`client.subscribe("edge/123", rpc.handle_rpc_message)` | `rpc = ConventionalRPCManager(client, my_topic="edge/123")`<br>→ 自动订阅 |
| 调用 | `await rpc.call(topic="cloud/svc", method="get", reply_to="edge/123")` | `await rpc.call("cloud/svc", "get")` |
| 代码量 | 100% | **60%** ↓ |

---

### 3. RPC 基础用法（传统模式）

需要手动订阅和传递 `reply_to`，适用于需要精细控制的场景。

```python
from mqttxx import MQTTClient, MQTTConfig, RPCManager

async def main():
    config = MQTTConfig(broker_host="localhost", client_id="device_001")

    async with MQTTClient(config) as client:
        rpc = RPCManager(client)

        # 注册本地方法
        @rpc.register("get_status")
        async def get_status(params):
            return {"status": "online", "cpu": 45.2}

        # 订阅 RPC 主题
        client.subscribe(
            "server/device_001",
            rpc.handle_rpc_message
        )

        # 调用远程方法
        result = await rpc.call(
            topic="bots/device_002",
            method="get_data",
            reply_to="server/device_001",
            timeout=5
        )
        print(result)  # {"data": [1, 2, 3]}

        await asyncio.sleep(60)

asyncio.run(main())
```

---

### 4. RPC 权限控制

```python
from mqttxx import RPCManager, RPCRequest

async def auth_check(caller_id: str, method: str, request: RPCRequest) -> bool:
    # 敏感方法只允许管理员
    if method in ["delete_user", "reset_system"]:
        return caller_id in ["admin_001", "admin_002"]
    return True

rpc = RPCManager(client, auth_callback=auth_check)

@rpc.register("delete_user")
async def delete_user(params):
    return {"result": "user deleted"}

# 未授权调用会返回 "Permission denied"
```

---

### 5. TLS/SSL 和认证

```python
from mqttxx import MQTTConfig, TLSConfig, AuthConfig
from pathlib import Path

config = MQTTConfig(
    broker_host="secure.mqtt.example.com",
    broker_port=8883,
    tls=TLSConfig(
        enabled=True,
        ca_certs=Path("ca.crt"),
        certfile=Path("client.crt"),
        keyfile=Path("client.key"),
    ),
    auth=AuthConfig(
        username="mqtt_user",
        password="mqtt_password",
    ),
)

async with MQTTClient(config) as client:
    await client.publish("secure/topic", "encrypted message")
```

---

## API 速查

### MQTTClient

```python
class MQTTClient:
    def __init__(self, config: MQTTConfig)
    async def connect(self) -> None
    async def disconnect(self) -> None
    def subscribe(self, topic: str, handler: Callable) -> None
    async def publish(self, topic: str, payload: str, qos: int = 0) -> None

    @property
    def is_connected(self) -> bool
```

---

### RPCManager（传统 RPC）

```python
class RPCManager:
    def __init__(self, client: MQTTClient, config: RPCConfig = None, auth_callback: AuthCallback = None)

    def register(self, method_name: str)  # 装饰器
    def unregister(self, method_name: str) -> None
    def handle_rpc_message(self, topic: str, message: RPCRequest | RPCResponse) -> None

    async def call(
        self,
        topic: str,
        method: str,
        params: Any = None,
        reply_to: str = None,  # 必填
        timeout: float = None,
    ) -> Any
```

---

### ConventionalRPCManager（约定式 RPC）

```python
class ConventionalRPCManager(RPCManager):
    def __init__(
        self,
        client: MQTTClient,
        my_topic: str,  # 本节点 topic（自动订阅，自动注入到 reply_to）
        config: RPCConfig = None,
        auth_callback: AuthCallback = None,
    )

    async def call(
        self,
        topic: str,        # 对方的 topic
        method: str,
        params: Any = None,
        timeout: float = None,
        reply_to: str = None,  # 可选，默认使用 my_topic
    ) -> Any

    # 属性
    my_topic: str      # 当前 topic（只读）
```

**使用示例：**

```python
# 边缘设备
rpc = ConventionalRPCManager(client, my_topic="edge/device_123")
config = await rpc.call("cloud/config-service", "get_config")

# 云端服务
rpc = ConventionalRPCManager(client, my_topic="cloud/config-service")
status = await rpc.call("edge/device_123", "execute_command")

# 微服务
rpc = ConventionalRPCManager(client, my_topic="auth-service")
user = await rpc.call("user-service", "get_user", params={"id": 123})
```

---

## 配置对象

### MQTTConfig

```python
@dataclass
class MQTTConfig:
    broker_host: str
    broker_port: int = 1883
    client_id: str = ""                    # 空字符串 = 自动生成
    keepalive: int = 60
    clean_session: bool = False
    tls: TLSConfig = field(default_factory=TLSConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    reconnect: ReconnectConfig = field(default_factory=ReconnectConfig)
    max_queued_messages: int = 0           # 0 = 无限
    max_payload_size: int = 1024 * 1024    # 1MB
```

### TLSConfig

```python
@dataclass
class TLSConfig:
    enabled: bool = False
    ca_certs: Optional[Path] = None
    certfile: Optional[Path] = None
    keyfile: Optional[Path] = None
    verify_mode: str = "CERT_REQUIRED"     # CERT_REQUIRED | CERT_OPTIONAL | CERT_NONE
    check_hostname: bool = True
```

### AuthConfig

```python
@dataclass
class AuthConfig:
    username: Optional[str] = None
    password: Optional[str] = None
```

### ReconnectConfig

```python
@dataclass
class ReconnectConfig:
    enabled: bool = True
    interval: int = 5                      # 初始重连间隔（秒）
    max_attempts: int = 0                  # 0 = 无限重试
    backoff_multiplier: float = 1.5        # 指数退避倍数
    max_interval: int = 60                 # 最大重连间隔（秒）
```

### RPCConfig

```python
@dataclass
class RPCConfig:
    default_timeout: float = 30.0          # 默认超时时间（秒）
    max_concurrent_calls: int = 100        # 最大并发调用数
```

---

## 异常系统

```python
# 基础异常
class MQTTXError(Exception)
class ConnectionError(MQTTXError)
class MessageError(MQTTXError)
class RPCError(MQTTXError)

# RPC 异常
class RPCTimeoutError(RPCError)            # RPC 调用超时
class RPCRemoteError(RPCError)             # 远程方法执行失败
class RPCMethodNotFoundError(RPCError)     # 方法未找到
class PermissionDeniedError(RPCError)      # 权限拒绝
class TooManyConcurrentCallsError(RPCError)  # 并发调用超限

# 错误码
class ErrorCode(IntEnum):
    NOT_CONNECTED = 1001
    RPC_TIMEOUT = 3002
    PERMISSION_DENIED = 4001
    # ... 更多错误码见源码
```

**使用示例：**

```python
from mqttxx import RPCTimeoutError, RPCRemoteError

try:
    result = await rpc.call_bot("456", "get_data", timeout=5)
except RPCTimeoutError:
    print("调用超时")
except RPCRemoteError as e:
    print(f"远程方法执行失败: {e}")
```

---

## RPC 消息协议

### 请求

```json
{
  "type": "rpc_request",
  "request_id": "uuid-string",
  "method": "get_status",
  "params": {"id": 123},
  "reply_to": "server/device_001",
  "caller_id": "device_002"
}
```

### 响应（成功）

```json
{
  "type": "rpc_response",
  "request_id": "uuid-string",
  "result": {"status": "online"}
}
```

### 响应（错误）

```json
{
  "type": "rpc_response",
  "request_id": "uuid-string",
  "error": "Permission denied"
}
```

---

## v2.0.0 重大变更

从 v2.0.0 开始，完全重写为基于 aiomqtt（纯 async/await），**不兼容** v0.x.x（gmqtt）。

**主要变化：**
- ✅ aiomqtt 替代 gmqtt
- ✅ 原生 dataclass 替代 python-box（性能提升 6 倍）
- ✅ 修复所有 P0 缺陷（并发竞态、连接状态、RPC 超时兜底）
- ✅ 新增约定式 RPC（`ConventionalRPCManager`）
- ✅ 新增权限控制（`auth_callback`）
- ✅ 新增 TLS/SSL 支持

**迁移关键点：**
1. 使用 `MQTTConfig` 配置对象
2. 使用 `async with` 上下文管理器
3. `publish_message()` → `publish()`
4. 移除 `EventEmitter`（改用 dict）

---

## 依赖

- Python >= 3.10
- aiomqtt >= 2.0.0, < 3.0.0
- loguru >= 0.7.0

---

## 开发

```bash
git clone https://github.com/yourusername/mqttx.git
cd mqttx
pip install -e ".[dev]"
pytest tests/
```

---

## License

MIT
