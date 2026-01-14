# MQTTX 异常定义和错误码

from enum import IntEnum


class ErrorCode(IntEnum):
    """错误码定义（遵循 HTTP 风格分类）

    错误码范围：
    - 1xxx: 连接错误
    - 2xxx: 消息错误
    - 3xxx: RPC 错误
    - 4xxx: 权限错误
    """

    # 连接错误 (1xxx)
    NOT_CONNECTED = 1001
    CONNECTION_FAILED = 1002
    CONNECTION_LOST = 1003
    SUBSCRIBE_FAILED = 1004
    PUBLISH_FAILED = 1005

    # 消息错误 (2xxx)
    INVALID_JSON = 2001
    INVALID_UTF8 = 2002
    PAYLOAD_TOO_LARGE = 2003
    INVALID_MESSAGE_TYPE = 2004
    MISSING_REQUIRED_FIELD = 2005

    # RPC 错误 (3xxx)
    METHOD_NOT_FOUND = 3001
    RPC_TIMEOUT = 3002
    RPC_EXECUTION_ERROR = 3003
    TOO_MANY_PENDING_CALLS = 3004
    INVALID_RPC_REQUEST = 3005
    INVALID_RPC_RESPONSE = 3006

    # 权限错误 (4xxx)
    PERMISSION_DENIED = 4001
    AUTHENTICATION_FAILED = 4002


class MQTTXError(Exception):
    """MQTTX 基础异常

    所有 MQTTX 异常的基类，包含错误码和消息

    Attributes:
        message: 错误消息
        code: 错误码（ErrorCode 枚举）

    示例:
        raise MQTTXError("连接失败", ErrorCode.CONNECTION_FAILED)
    """

    def __init__(self, message: str, code: ErrorCode):
        super().__init__(message)
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return f"[{self.code.name}] {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code}, message={self.message!r})"


class ConnectionError(MQTTXError):
    """连接相关异常

    用于表示 MQTT 连接、订阅、发布等操作失败

    示例:
        raise ConnectionError("客户端未连接", ErrorCode.NOT_CONNECTED)
    """
    pass


class MessageError(MQTTXError):
    """消息处理异常

    用于表示消息解析、验证失败

    示例:
        raise MessageError("JSON 解析失败", ErrorCode.INVALID_JSON)
    """
    pass


class RPCError(MQTTXError):
    """RPC 基础异常

    所有 RPC 相关异常的基类
    """
    pass


class RPCTimeoutError(RPCError):
    """RPC 超时异常

    当 RPC 调用超过指定时间未收到响应时抛出

    示例:
        raise RPCTimeoutError("RPC 调用超时: get_status")
    """

    def __init__(self, message: str):
        super().__init__(message, ErrorCode.RPC_TIMEOUT)


class RPCRemoteError(RPCError):
    """远程执行失败异常

    当远程方法执行过程中抛出异常时，封装该异常并返回

    示例:
        raise RPCRemoteError("远程方法执行失败: division by zero")
    """

    def __init__(self, message: str):
        super().__init__(message, ErrorCode.RPC_EXECUTION_ERROR)


class RPCMethodNotFoundError(RPCError):
    """方法未找到异常

    当调用的 RPC 方法未在远程节点注册时抛出

    示例:
        raise RPCMethodNotFoundError("方法未找到: unknown_method")
    """

    def __init__(self, message: str):
        super().__init__(message, ErrorCode.METHOD_NOT_FOUND)


class PermissionDeniedError(RPCError):
    """权限拒绝异常

    当 RPC 调用未通过权限检查时抛出

    示例:
        raise PermissionDeniedError("权限拒绝: delete_user")
    """

    def __init__(self, message: str):
        super().__init__(message, ErrorCode.PERMISSION_DENIED)


class TooManyConcurrentCallsError(RPCError):
    """并发调用过多异常

    当并发 RPC 调用数量超过限制时抛出

    示例:
        raise TooManyConcurrentCallsError("并发调用超限: 100/100")
    """

    def __init__(self, message: str):
        super().__init__(message, ErrorCode.TOO_MANY_PENDING_CALLS)
