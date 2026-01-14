# MQTT RPC 消息协议定义

import json
from dataclasses import dataclass
from dataclasses import asdict, is_dataclass
from typing import Any, Optional, Literal
from .exceptions import MessageError, ErrorCode


def _to_jsonable(obj: Any) -> Any:
    if obj is None:
        return None

    if is_dataclass(obj):
        return _to_jsonable(asdict(obj))

    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set)):
        return [_to_jsonable(v) for v in obj]

    if hasattr(obj, "model_dump") and callable(getattr(obj, "model_dump")):
        return _to_jsonable(obj.model_dump(mode="json"))

    if hasattr(obj, "dict") and callable(getattr(obj, "dict")):
        return _to_jsonable(obj.dict())

    return obj


@dataclass
class RPCRequest:
    """RPC 请求消息

    客户端发起 RPC 调用时构造的消息格式

    Attributes:
        request_id: 请求唯一标识符（UUID）
        method: 远程方法名
        type: 消息类型（固定为 "rpc_request"）
        params: 方法参数（任意类型）
        reply_to: 响应主题（用于接收响应）
        caller_id: 调用者标识符（用于权限检查）

    示例:
        request = RPCRequest(
            request_id="123e4567-e89b-12d3-a456-426614174000",
            method="get_status",
            params={"device_id": "dev_001"},
            reply_to="client/response",
            caller_id="client_123"
        )

        # 序列化为字典（用于 JSON 发送）
        data = request.to_dict()
    """

    # 必填字段（无默认值）
    request_id: str
    method: str
    # 可选字段（有默认值）
    type: Literal["rpc_request"] = "rpc_request"
    params: Any = None
    reply_to: str = ""
    caller_id: str = ""

    def to_dict(self) -> dict:
        """转为字典（用于 JSON 序列化）

        Returns:
            包含所有字段的字典
        """
        return {
            "type": self.type,
            "request_id": self.request_id,
            "method": self.method,
            "params": _to_jsonable(self.params),
            "reply_to": self.reply_to,
            "caller_id": self.caller_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RPCRequest":
        """从字典构造（用于 JSON 反序列化）

        Args:
            data: 包含消息字段的字典

        Returns:
            RPCRequest 实例

        Raises:
            MessageError: 缺少必需字段时抛出
        """
        try:
            return cls(
                request_id=data["request_id"],
                method=data["method"],
                params=data.get("params"),
                reply_to=data.get("reply_to", ""),
                caller_id=data.get("caller_id", ""),
            )
        except KeyError as e:
            raise MessageError(
                f"RPC 请求缺少必需字段: {e}", ErrorCode.MISSING_REQUIRED_FIELD
            )

    def encode(self) -> bytes:
        """编码为 bytes（JSON 格式）

        Returns:
            UTF-8 编码的 JSON bytes
        """
        return json.dumps(self.to_dict()).encode("utf-8")

    @classmethod
    def decode(cls, data: bytes) -> "RPCRequest":
        """从 bytes 解码（JSON 格式）

        Args:
            data: UTF-8 编码的 JSON bytes

        Returns:
            RPCRequest 对象

        Raises:
            MessageError: 解码失败或缺少必需字段
            UnicodeDecodeError: UTF-8 解码失败
            json.JSONDecodeError: JSON 解析失败
        """
        obj = json.loads(data.decode("utf-8"))
        return cls.from_dict(obj)


@dataclass
class RPCResponse:
    """RPC 响应消息

    服务端处理 RPC 请求后返回的消息格式

    Attributes:
        type: 消息类型（固定为 "rpc_response"）
        request_id: 对应请求的唯一标识符
        result: 方法返回值（成功时）
        error: 错误消息（失败时）

    注意:
        result 和 error 只能有一个非空

    示例:
        # 成功响应
        response = RPCResponse(
            request_id="123e4567-e89b-12d3-a456-426614174000",
            result={"status": "online", "temperature": 25.5}
        )

        # 错误响应
        response = RPCResponse(
            request_id="123e4567-e89b-12d3-a456-426614174000",
            error="方法未找到: unknown_method"
        )
    """

    type: Literal["rpc_response"] = "rpc_response"
    request_id: str = ""
    result: Any = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """转为字典（用于 JSON 序列化）

        Returns:
            包含所有字段的字典
        """
        data = {
            "type": self.type,
            "request_id": self.request_id,
        }

        if self.error is not None:
            data["error"] = self.error
        else:
            data["result"] = _to_jsonable(self.result)

        return data

    @classmethod
    def from_dict(cls, data: dict) -> "RPCResponse":
        """从字典构造（用于 JSON 反序列化）

        Args:
            data: 包含消息字段的字典

        Returns:
            RPCResponse 实例

        Raises:
            MessageError: 缺少必需字段时抛出
        """
        try:
            return cls(
                request_id=data["request_id"],
                result=data.get("result"),
                error=data.get("error"),
            )
        except KeyError as e:
            raise MessageError(
                f"RPC 响应缺少必需字段: {e}", ErrorCode.MISSING_REQUIRED_FIELD
            )

    def encode(self) -> bytes:
        """编码为 bytes（JSON 格式）

        Returns:
            UTF-8 编码的 JSON bytes
        """
        return json.dumps(self.to_dict()).encode("utf-8")

    @classmethod
    def decode(cls, data: bytes) -> "RPCResponse":
        """从 bytes 解码（JSON 格式）

        Args:
            data: UTF-8 编码的 JSON bytes

        Returns:
            RPCResponse 对象

        Raises:
            MessageError: 解码失败或缺少必需字段
            UnicodeDecodeError: UTF-8 解码失败
            json.JSONDecodeError: JSON 解析失败
        """
        obj = json.loads(data.decode("utf-8"))
        return cls.from_dict(obj)


def parse_message_from_bytes(data: bytes) -> RPCRequest | RPCResponse:
    """从 bytes 解析 RPC 消息（JSON 格式）

    Args:
        data: UTF-8 编码的 JSON bytes

    Returns:
        RPCRequest 或 RPCResponse 对象

    Raises:
        MessageError: 解码失败或消息类型无效
        UnicodeDecodeError: UTF-8 解码失败
        json.JSONDecodeError: JSON 解析失败

    示例:
        payload = b'{"type":"rpc_request","request_id":"123",...}'
        message = parse_message_from_bytes(payload)

        if isinstance(message, RPCRequest):
            # 处理请求
            pass
        elif isinstance(message, RPCResponse):
            # 处理响应
            pass
    """
    obj = json.loads(data.decode("utf-8"))
    msg_type = obj.get("type")

    if msg_type == "rpc_request":
        return RPCRequest.from_dict(obj)
    elif msg_type == "rpc_response":
        return RPCResponse.from_dict(obj)
    else:
        raise MessageError(f"未知消息类型: {msg_type}", ErrorCode.INVALID_MESSAGE_TYPE)
