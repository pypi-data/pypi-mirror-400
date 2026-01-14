# MQTT RPC 消息协议定义

import json
from dataclasses import dataclass
from typing import Any, Optional, Literal, Protocol as TypingProtocol, Type, runtime_checkable

from .exceptions import MessageError, ErrorCode


# ============================================================================
# 编解码器接口（可插拔协议支持）
# ============================================================================

@runtime_checkable
class Codec(TypingProtocol):
    """编解码器接口（协议无关）

    实现此接口可支持不同的序列化协议（JSON、MessagePack、Protobuf 等）
    """

    @staticmethod
    def encode(obj: Any) -> bytes:
        """对象 → bytes

        Args:
            obj: 要编码的对象（RPCRequest/RPCResponse/EventMessage/dict）

        Returns:
            编码后的 bytes

        Raises:
            ValueError: 无法编码的类型
        """
        ...

    @staticmethod
    def decode(data: bytes) -> dict:
        """bytes → dict

        Args:
            data: 原始 bytes 数据

        Returns:
            解码后的 dict

        Raises:
            UnicodeDecodeError: UTF-8 解码失败
            JSONDecodeError: JSON 解析失败（或其他格式解析失败）
        """
        ...


class JSONCodec:
    """JSON 编解码器（默认实现）

    使用标准 JSON 格式进行序列化/反序列化
    支持 Pydantic BaseModel 自动序列化
    """

    @staticmethod
    def encode(obj: Any) -> bytes:
        """对象 → bytes

        支持：
        - 有 to_dict() 方法的对象（RPCRequest/RPCResponse/EventMessage）
        - Pydantic BaseModel（自动调用 model_dump()）
        - dict 对象

        Args:
            obj: 要编码的对象

        Returns:
            UTF-8 编码的 JSON bytes

        Raises:
            ValueError: 无法编码的类型
        """
        if hasattr(obj, 'to_dict'):
            data = obj.to_dict()
        elif hasattr(obj, 'model_dump'):
            data = obj.model_dump()
        elif isinstance(obj, dict):
            data = obj
        else:
            raise ValueError(f"无法编码类型: {type(obj)}")

        return json.dumps(data).encode('utf-8')

    @staticmethod
    def decode(data: bytes) -> dict:
        """bytes → dict

        Args:
            data: UTF-8 编码的 JSON bytes

        Returns:
            解码后的 dict

        Raises:
            UnicodeDecodeError: UTF-8 解码失败
            json.JSONDecodeError: JSON 解析失败
        """
        text = data.decode('utf-8')
        return json.loads(text)


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
        # 处理 Pydantic 模型
        params = self.params
        if hasattr(params, 'model_dump'):
            params = params.model_dump()

        return {
            "type": self.type,
            "request_id": self.request_id,
            "method": self.method,
            "params": params,
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
                f"RPC 请求缺少必需字段: {e}",
                ErrorCode.MISSING_REQUIRED_FIELD
            )

    def encode(self, codec: Type[Codec] = JSONCodec) -> bytes:
        """编码为 bytes

        Args:
            codec: 编解码器（默认 JSONCodec）

        Returns:
            编码后的 bytes

        示例:
            request = RPCRequest(request_id="123", method="test")
            payload = request.encode()  # 使用默认 JSONCodec
            # 或自定义 codec
            payload = request.encode(MessagePackCodec)
        """
        return codec.encode(self)

    @classmethod
    def decode(cls, data: bytes, codec: Type[Codec] = JSONCodec) -> "RPCRequest":
        """从 bytes 解码

        Args:
            data: 原始 bytes 数据
            codec: 编解码器（默认 JSONCodec）

        Returns:
            RPCRequest 对象

        Raises:
            MessageError: 解码失败或缺少必需字段

        示例:
            payload = b'{"type":"rpc_request","request_id":"123",...}'
            request = RPCRequest.decode(payload)
        """
        obj = codec.decode(data)
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
            # 处理 Pydantic 模型
            result = self.result
            if hasattr(result, 'model_dump'):
                result = result.model_dump()
            data["result"] = result

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
                f"RPC 响应缺少必需字段: {e}",
                ErrorCode.MISSING_REQUIRED_FIELD
            )

    def encode(self, codec: Type[Codec] = JSONCodec) -> bytes:
        """编码为 bytes

        Args:
            codec: 编解码器（默认 JSONCodec）

        Returns:
            编码后的 bytes
        """
        return codec.encode(self)

    @classmethod
    def decode(cls, data: bytes, codec: Type[Codec] = JSONCodec) -> "RPCResponse":
        """从 bytes 解码

        Args:
            data: 原始 bytes 数据
            codec: 编解码器（默认 JSONCodec）

        Returns:
            RPCResponse 对象

        Raises:
            MessageError: 解码失败或缺少必需字段
        """
        obj = codec.decode(data)
        return cls.from_dict(obj)


def parse_message_from_bytes(data: bytes, codec: Type[Codec] = JSONCodec) -> RPCRequest | RPCResponse:
    """从 bytes 解析 RPC 消息

    Args:
        data: 原始 bytes 数据
        codec: 编解码器（默认 JSONCodec）

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
    obj = codec.decode(data)
    msg_type = obj.get("type")

    if msg_type == "rpc_request":
        return RPCRequest.from_dict(obj)
    elif msg_type == "rpc_response":
        return RPCResponse.from_dict(obj)
    else:
        raise MessageError(
            f"未知消息类型: {msg_type}",
            ErrorCode.INVALID_MESSAGE_TYPE
        )
