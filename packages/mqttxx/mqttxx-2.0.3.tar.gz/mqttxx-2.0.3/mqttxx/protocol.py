# MQTT RPC 消息协议定义

from dataclasses import dataclass
from typing import Any, Optional, Literal

from .exceptions import MessageError, ErrorCode


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
            "params": self.params,
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
            data["result"] = self.result

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


def parse_message(data: dict) -> RPCRequest | RPCResponse:
    """解析 RPC 消息（带类型验证）

    根据消息的 type 字段自动判断消息类型并解析

    Args:
        data: JSON 解析后的字典

    Returns:
        RPCRequest 或 RPCResponse 实例

    Raises:
        MessageError: 未知消息类型或解析失败

    示例:
        data = json.loads(payload)
        message = parse_message(data)

        if isinstance(message, RPCRequest):
            # 处理请求
            pass
        elif isinstance(message, RPCResponse):
            # 处理响应
            pass
    """
    msg_type = data.get("type")

    if msg_type == "rpc_request":
        return RPCRequest.from_dict(data)
    elif msg_type == "rpc_response":
        return RPCResponse.from_dict(data)
    else:
        raise MessageError(
            f"未知消息类型: {msg_type}",
            ErrorCode.INVALID_MESSAGE_TYPE
        )
