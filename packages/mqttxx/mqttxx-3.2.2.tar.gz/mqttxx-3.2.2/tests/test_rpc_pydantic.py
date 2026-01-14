# RPC + Pydantic 集成测试

import asyncio
import pytest
from pydantic import BaseModel, Field

from mqttxx import RPCManager, RPCRemoteError


# ========== Pydantic 模型定义 ==========

class UserRequest(BaseModel):
    """用户查询请求"""
    user_id: int = Field(..., ge=1, description="用户 ID")


class UserResponse(BaseModel):
    """用户信息响应"""
    user_id: int
    username: str
    email: str
    is_active: bool


class CalculatorRequest(BaseModel):
    """计算请求"""
    a: float
    b: float
    operation: str = Field(..., pattern="^(add|subtract|multiply|divide)$")


class CalculatorResponse(BaseModel):
    """计算响应"""
    result: float
    operation: str


# ========== 测试用例 ==========

@pytest.mark.integration
async def test_rpc_pydantic_user_query(two_clients):
    """测试 Pydantic 模型的 RPC 调用 - 用户查询"""
    print("\n[测试] Pydantic 用户查询 RPC")

    client_a, client_b = two_clients

    # 服务端：注册带 Pydantic 验证的方法
    rpc_server = RPCManager(client_a, my_topic=f"rpc/server/{client_a.config.client_id}")

    @rpc_server.register("get_user")
    async def get_user(params):
        # 使用 Pydantic 验证输入
        request = UserRequest(**params)

        # 直接返回 Pydantic 实例（RPC 层自动序列化）
        return UserResponse(
            user_id=request.user_id,
            username=f"user_{request.user_id}",
            email=f"user{request.user_id}@example.com",
            is_active=True,
        )

    await asyncio.sleep(0.5)

    # 客户端：调用并验证响应
    rpc_client = RPCManager(client_b, my_topic=f"rpc/client/{client_b.config.client_id}")

    result = await rpc_client.call(
        topic=f"rpc/server/{client_a.config.client_id}",
        method="get_user",
        params={"user_id": 123},
        timeout=5,
    )

    # 使用 Pydantic 验证响应
    response = UserResponse(**result)
    print(f"[响应] {response}")

    assert response.user_id == 123
    assert response.username == "user_123"
    assert response.is_active is True
    print("[成功] Pydantic 用户查询测试通过")


@pytest.mark.integration
async def test_rpc_pydantic_calculator(two_clients):
    """测试 Pydantic 模型的 RPC 调用 - 计算器"""
    print("\n[测试] Pydantic 计算器 RPC")

    client_a, client_b = two_clients

    # 服务端
    rpc_server = RPCManager(client_a, my_topic=f"rpc/server/{client_a.config.client_id}")

    @rpc_server.register("calculate")
    async def calculate(params):
        # Pydantic 验证请求
        req = CalculatorRequest(**params)

        match req.operation:
            case "add":
                result = req.a + req.b
            case "subtract":
                result = req.a - req.b
            case "multiply":
                result = req.a * req.b
            case "divide":
                if req.b == 0:
                    raise ValueError("除数不能为零")
                result = req.a / req.b
            case _:
                raise ValueError(f"未知操作: {req.operation}")

        return CalculatorResponse(
            result=result,
            operation=req.operation,
        )

    await asyncio.sleep(0.5)

    # 客户端：测试多种运算
    rpc_client = RPCManager(client_b, my_topic=f"rpc/client/{client_b.config.client_id}")

    test_cases = [
        ({"a": 10, "b": 5, "operation": "add"}, 15),
        ({"a": 10, "b": 3, "operation": "subtract"}, 7),
        ({"a": 4, "b": 5, "operation": "multiply"}, 20),
        ({"a": 20, "b": 4, "operation": "divide"}, 5),
    ]

    for params, expected in test_cases:
        result = await rpc_client.call(
            topic=f"rpc/server/{client_a.config.client_id}",
            method="calculate",
            params=params,
            timeout=5,
        )

        response = CalculatorResponse(**result)
        print(f"[运算] {params['operation']}: {params['a']} {params['operation']} {params['b']} = {response.result}")
        assert abs(response.result - expected) < 0.001

    print("[成功] Pydantic 计算器测试通过")


@pytest.mark.integration
async def test_rpc_pydantic_validation_error(two_clients):
    """测试 Pydantic 验证错误的传递"""
    print("\n[测试] Pydantic 验证错误处理")

    client_a, client_b = two_clients

    # 服务端
    rpc_server = RPCManager(client_a, my_topic=f"rpc/server/{client_a.config.client_id}")

    @rpc_server.register("strict_user")
    async def strict_user(params):
        # 这里会抛出 Pydantic 验证错误
        request = UserRequest(**params)
        return UserResponse(
            user_id=request.user_id,
            username="test",
            email="test@example.com",
            is_active=True,
        )

    await asyncio.sleep(0.5)

    # 客户端：发送无效数据
    rpc_client = RPCManager(client_b, my_topic=f"rpc/client/{client_b.config.client_id}")

    try:
        await rpc_client.call(
            topic=f"rpc/server/{client_a.config.client_id}",
            method="strict_user",
            # user_id 为负数，违反 Pydantic 验证（ge=1）
            params={"user_id": -1},
            timeout=5,
        )
        assert False, "应该抛出验证错误异常"
    except RPCRemoteError as e:
        print(f"[预期异常] {e}")
        # 错误信息应包含验证相关信息
        assert "user_id" in str(e).lower() or "validation" in str(e).lower()
        print("[成功] Pydantic 验证错误正确传递")


@pytest.mark.integration
async def test_rpc_pydantic_complex_nested(two_clients):
    """测试 Pydantic 嵌套模型"""
    print("\n[测试] Pydantic 嵌套模型 RPC")

    # 定义嵌套模型
    class Address(BaseModel):
        street: str
        city: str
        zipcode: str

    class Company(BaseModel):
        name: str
        address: Address

    class EmployeeRequest(BaseModel):
        employee_id: int

    class EmployeeResponse(BaseModel):
        employee_id: int
        name: str
        company: Company

    client_a, client_b = two_clients

    # 服务端
    rpc_server = RPCManager(client_a, my_topic=f"rpc/server/{client_a.config.client_id}")

    @rpc_server.register("get_employee")
    async def get_employee(params):
        req = EmployeeRequest(**params)
        return EmployeeResponse(
            employee_id=req.employee_id,
            name=f"Employee {req.employee_id}",
            company=Company(
                name="Tech Corp",
                address=Address(
                    street="123 Main St",
                    city="San Francisco",
                    zipcode="94102",
                ),
            ),
        )

    await asyncio.sleep(0.5)

    # 客户端
    rpc_client = RPCManager(client_b, my_topic=f"rpc/client/{client_b.config.client_id}")

    result = await rpc_client.call(
        topic=f"rpc/server/{client_a.config.client_id}",
        method="get_employee",
        params={"employee_id": 42},
        timeout=5,
    )

    response = EmployeeResponse(**result)
    print(f"[响应] 员工: {response.name}, 公司: {response.company.name}")
    print(f"[响应] 地址: {response.company.address.city}, {response.company.address.street}")

    assert response.employee_id == 42
    assert response.company.name == "Tech Corp"
    assert response.company.address.city == "San Francisco"
    print("[成功] Pydantic 嵌套模型测试通过")


@pytest.mark.integration
async def test_rpc_pydantic_raw_db_response(two_clients):
    """测试服务端直接返回数据库原始数据，客户端验证（实际场景）"""
    print("\n[测试] 真实场景：数据库原始数据返回 + 客户端 Pydantic 验证")

    class GetUserRequest(BaseModel):
        user_id: int = Field(..., ge=1)

    class GetUserResponse(BaseModel):
        user_id: int
        username: str
        email: str
        role: str
        created_at: str

    # 模拟数据库
    fake_db = {
        1: {
            "user_id": 1,
            "username": "admin",
            "email": "admin@system.local",
            "role": "administrator",
            "created_at": "2024-01-01T00:00:00Z",
            # 数据库可能有额外字段，客户端不需要
            "password_hash": "scrypt:...",
            "last_login": "2024-06-15T10:30:00Z",
        },
        2: {
            "user_id": 2,
            "username": "alice",
            "email": "alice@example.com",
            "role": "user",
            "created_at": "2024-02-15T08:20:00Z",
            "password_hash": "scrypt:...",
            "last_login": None,
        },
    }

    client_a, client_b = two_clients

    # 服务端：直接返回数据库查询结果（不转 Pydantic）
    rpc_server = RPCManager(client_a, my_topic=f"rpc/server/{client_a.config.client_id}")

    @rpc_server.register("db_get_user")
    async def db_get_user(params):
        # 使用 model_validate（比 **params 更健壮）
        req = GetUserRequest.model_validate(params)

        # 模拟数据库查询
        if req.user_id not in fake_db:
            raise ValueError(f"用户不存在: {req.user_id}")

        # 直接返回数据库记录（可能包含额外字段）
        return fake_db[req.user_id]

    await asyncio.sleep(0.5)

    # 客户端：验证响应（过滤掉额外字段）
    rpc_client = RPCManager(client_b, my_topic=f"rpc/client/{client_b.config.client_id}")

    result = await rpc_client.call(
        topic=f"rpc/server/{client_a.config.client_id}",
        method="db_get_user",
        params={"user_id": 1},
        timeout=5,
    )

    # Pydantic 会自动忽略额外字段（password_hash, last_login）
    response = GetUserResponse.model_validate(result)
    print(f"[响应] 用户: {response.username}, 角色: {response.role}")
    print("[响应] 数据库有额外字段，但 Pydantic 自动过滤")

    assert response.user_id == 1
    assert response.username == "admin"
    assert response.role == "administrator"
    print("[成功] 真实数据库场景测试通过")


@pytest.mark.integration
async def test_rpc_pydantic_response_roundtrip(two_clients):
    """测试完整的请求-响应往返验证"""
    print("\n[测试] Pydantic 完整往返验证")

    class EchoRequest(BaseModel):
        message: str
        timestamp: int

    class EchoResponse(BaseModel):
        original: str
        reversed_msg: str
        received_at: int

    client_a, client_b = two_clients

    # 服务端
    rpc_server = RPCManager(client_a, my_topic=f"rpc/server/{client_a.config.client_id}")

    @rpc_server.register("echo")
    async def echo(params):
        req = EchoRequest(**params)
        return EchoResponse(
            original=req.message,
            reversed_msg=req.message[::-1],
            received_at=req.timestamp,
        )

    await asyncio.sleep(0.5)

    # 客户端
    rpc_client = RPCManager(client_b, my_topic=f"rpc/client/{client_b.config.client_id}")

    import time
    test_msg = "Hello MQTT RPC with Pydantic!"
    timestamp = int(time.time())

    result = await rpc_client.call(
        topic=f"rpc/server/{client_a.config.client_id}",
        method="echo",
        params={"message": test_msg, "timestamp": timestamp},
        timeout=5,
    )

    response = EchoResponse(**result)
    print(f"[请求] {test_msg}")
    print(f"[响应] 反转: {response.reversed_msg}")

    assert response.original == test_msg
    assert response.reversed_msg == test_msg[::-1]
    assert response.received_at == timestamp
    print("[成功] Pydantic 往返验证测试通过")
