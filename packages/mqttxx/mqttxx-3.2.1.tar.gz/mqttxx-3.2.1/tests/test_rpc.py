# RPCManager 功能测试

import asyncio
import pytest
from mqttxx import RPCManager, RPCTimeoutError, RPCRemoteError


@pytest.mark.integration
async def test_rpc_call_success(two_clients):
    """测试 RPC 调用成功"""
    print("\n[测试] RPC 调用成功")

    client_a, client_b = two_clients

    # 客户端 A 注册方法
    rpc_a = RPCManager(client_a, my_topic=f"rpc/a/{client_a.config.client_id}")

    @rpc_a.register("add")
    async def add(params):
        a = params.get("a", 0)
        b = params.get("b", 0)
        print(f"[服务端] 执行加法: {a} + {b}")
        return {"result": a + b}

    await asyncio.sleep(0.5)

    # 客户端 B 调用
    rpc_b = RPCManager(client_b, my_topic=f"rpc/b/{client_b.config.client_id}")

    result = await rpc_b.call(
        topic=f"rpc/a/{client_a.config.client_id}",
        method="add",
        params={"a": 10, "b": 20},
        timeout=5,
    )

    print(f"[客户端] 收到结果: {result}")
    assert result["result"] == 30, "结果应该是 30"
    print("[成功] RPC 调用成功")


@pytest.mark.integration
async def test_rpc_method_not_found(two_clients):
    """测试调用未注册的方法"""
    print("\n[测试] 方法未找到")

    client_a, client_b = two_clients

    # 客户端 A 注册 RPC（但不注册 nonexistent_method）
    rpc_a = RPCManager(client_a, my_topic=f"rpc/a/{client_a.config.client_id}")

    # 注册一个其他方法，让 RPC 处理器正常工作
    @rpc_a.register("some_other_method")
    async def some_other_method(params):
        return {"result": "ok"}

    await asyncio.sleep(0.5)

    # 客户端 B 调用不存在的方法
    rpc_b = RPCManager(client_b, my_topic=f"rpc/b/{client_b.config.client_id}")

    try:
        _ = await rpc_b.call(
            topic=f"rpc/a/{client_a.config.client_id}",
            method="nonexistent_method",
            params={},
            timeout=5,
        )
        assert False, "应该抛出异常"
    except RPCRemoteError as e:
        print(f"[预期异常] {e}")
        assert "未找到" in str(e) or "not found" in str(e).lower(), "错误信息应该包含'未找到'"
        print("[成功] 方法未找到异常正确")


@pytest.mark.integration
async def test_rpc_timeout(two_clients):
    """测试 RPC 超时"""
    print("\n[测试] RPC 超时")

    client_a, client_b = two_clients

    # 客户端 A 注册慢速方法
    rpc_a = RPCManager(client_a, my_topic=f"rpc/a/{client_a.config.client_id}")

    @rpc_a.register("slow_task")
    async def slow_task(params):
        print("[服务端] 执行慢速任务，等待 10 秒...")
        await asyncio.sleep(10)
        return {"done": True}

    await asyncio.sleep(0.5)

    # 客户端 B 调用（2秒超时）
    rpc_b = RPCManager(client_b, my_topic=f"rpc/b/{client_b.config.client_id}")

    try:
        _ = await rpc_b.call(
            topic=f"rpc/a/{client_a.config.client_id}",
            method="slow_task",
            params={},
            timeout=2,
        )
        assert False, "应该抛出超时异常"
    except RPCTimeoutError as e:
        print(f"[预期超时] {e}")
        print("[成功] RPC 超时异常正确")


@pytest.mark.integration
async def test_rpc_register_unregister(connected_client):
    """测试 RPC 方法注册和注销"""
    print("\n[测试] RPC 方法注册和注销")

    rpc = RPCManager(connected_client, my_topic=f"rpc/test/{connected_client.config.client_id}")

    # 注册方法
    @rpc.register("test_method")
    async def test_method(params):
        return {"status": "ok"}

    await asyncio.sleep(0.5)
    assert "test_method" in rpc._handlers, "方法应该已注册"
    print("[注册] 方法 test_method")

    # 注销方法
    rpc.unregister("test_method")
    assert "test_method" not in rpc._handlers, "方法应该已注销"
    print("[注销] 方法 test_method")

    print("[成功] 注册和注销测试通过")


@pytest.mark.integration
async def test_rpc_concurrent_calls(two_clients):
    """测试并发 RPC 调用"""
    print("\n[测试] 并发 RPC 调用")

    client_a, client_b = two_clients

    # 客户端 A 注册方法
    rpc_a = RPCManager(client_a, my_topic=f"rpc/a/{client_a.config.client_id}")

    @rpc_a.register("multiply")
    async def multiply(params):
        x = params.get("x", 1)
        await asyncio.sleep(0.5)  # 模拟耗时操作
        return {"result": x * 2}

    await asyncio.sleep(0.5)

    # 客户端 B 并发调用
    rpc_b = RPCManager(client_b, my_topic=f"rpc/b/{client_b.config.client_id}")

    tasks = []
    for i in range(5):
        task = rpc_b.call(
            topic=f"rpc/a/{client_a.config.client_id}",
            method="multiply",
            params={"x": i + 1},
            timeout=5,
        )
        tasks.append(task)

    # 等待所有调用完成
    results = await asyncio.gather(*tasks)

    print(f"[结果] 收到 {len(results)} 个响应")
    assert len(results) == 5, "应该收到 5 个结果"

    for i, result in enumerate(results):
        expected = (i + 1) * 2
        assert result["result"] == expected, f"结果 {i} 应该是 {expected}"

    print("[成功] 并发调用测试通过")


@pytest.mark.integration
async def test_rpc_permission_control(two_clients):
    """测试 RPC 权限控制"""
    print("\n[测试] RPC 权限控制")

    client_a, client_b = two_clients

    # 定义权限回调：拒绝 delete_user 方法
    async def auth_callback(caller_id: str, method: str, request) -> bool:
        if method == "delete_user":
            print(f"[权限拒绝] caller={caller_id}, method={method}")
            return False
        print(f"[权限允许] caller={caller_id}, method={method}")
        return True

    # 客户端 A 带权限控制
    rpc_a = RPCManager(
        client_a,
        my_topic=f"rpc/a/{client_a.config.client_id}",
        auth_callback=auth_callback,
    )

    @rpc_a.register("delete_user")
    async def delete_user(params):
        return {"deleted": True}

    @rpc_a.register("get_user")
    async def get_user(params):
        return {"user": "test"}

    await asyncio.sleep(0.5)

    # 客户端 B 调用
    rpc_b = RPCManager(client_b, my_topic=f"rpc/b/{client_b.config.client_id}")

    # 测试被拒绝的方法
    try:
        result = await rpc_b.call(
            topic=f"rpc/a/{client_a.config.client_id}",
            method="delete_user",
            params={},
            timeout=5,
        )
        assert False, "应该抛出权限拒绝异常"
    except RPCRemoteError as e:
        print(f"[预期拒绝] {e}")
        assert "Permission denied" in str(e) or "权限" in str(e), "应该包含权限拒绝信息"
        print("[成功] delete_user 被正确拒绝")

    # 测试允许的方法
    result = await rpc_b.call(
        topic=f"rpc/a/{client_a.config.client_id}",
        method="get_user",
        params={},
        timeout=5,
    )
    assert result["user"] == "test", "get_user 应该成功"
    print("[成功] get_user 被正确允许")


@pytest.mark.integration
async def test_rpc_auto_reply_to(two_clients):
    """测试 my_topic 自动注入 reply_to"""
    print("\n[测试] my_topic 自动注入 reply_to")

    client_a, client_b = two_clients

    # 客户端 A 设置 my_topic
    topic_a = f"rpc/a/{client_a.config.client_id}"
    rpc_a = RPCManager(client_a, my_topic=topic_a)

    @rpc_a.register("echo")
    async def echo(params):
        message = params.get("message", "")
        return {"echo": message}

    await asyncio.sleep(0.5)

    # 客户端 B 设置 my_topic
    topic_b = f"rpc/b/{client_b.config.client_id}"
    rpc_b = RPCManager(client_b, my_topic=topic_b)

    # 调用时不指定 reply_to，应该自动注入
    result = await rpc_b.call(
        topic=topic_a,
        method="echo",
        params={"message": "hello"},
        timeout=5,
    )

    print(f"[结果] {result}")
    assert result["echo"] == "hello", "echo 应该返回原消息"
    print("[成功] my_topic 自动注入测试通过")
