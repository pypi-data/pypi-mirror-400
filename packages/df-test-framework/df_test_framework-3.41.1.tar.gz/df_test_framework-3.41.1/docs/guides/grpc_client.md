# gRPC 客户端使用指南

> **版本**: v3.38.0 | **更新**: 2025-12-24
> **引入版本**: v3.11.0
> **推荐导入**: `from df_test_framework import GrpcClient`

## 概述

gRPC 客户端提供 gRPC 服务测试能力，支持：
- Unary RPC（一元调用）
- Server Streaming RPC（服务端流式）
- 元数据（Metadata）管理
- 中间件（Middleware）支持（v3.32.0 重构）
- 健康检查

> **重要变更 v3.32.0**：已从 Interceptor（拦截器）重构为 Middleware（中间件）模式，与 HTTP 客户端保持一致。

> **注意**：Client Streaming 和 Bidirectional Streaming 计划在后续版本实现。

## 前置要求

### 安装依赖

```bash
# gRPC 核心库
pip install grpcio grpcio-tools

# 健康检查支持（可选）
pip install grpcio-health-checking
```

### 生成 Stub 代码

```bash
# 从 .proto 文件生成 Python 代码
python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    service.proto
```

## 快速开始

### 基本用法

```python
from df_test_framework import GrpcClient

# 导入生成的 stub
from service_pb2_grpc import GreeterStub
from service_pb2 import HelloRequest

# 创建客户端
client = GrpcClient(
    target="localhost:50051",
    stub_class=GreeterStub,
)

# 连接服务器
client.connect()

# 执行一元调用
request = HelloRequest(name="World")
response = client.unary_call("SayHello", request)

if response.is_success:
    print(f"Response: {response.data.message}")
else:
    print(f"Error: {response.message}")

# 关闭连接
client.close()
```

### 使用上下文管理器

```python
with GrpcClient("localhost:50051", GreeterStub) as client:
    request = HelloRequest(name="World")
    response = client.unary_call("SayHello", request)
    print(response.data.message)
    # 自动关闭连接
```

## API 详解

### GrpcClient

#### 构造函数

```python
GrpcClient(
    target: str,                          # 服务器地址 "host:port"
    stub_class: type | None = None,       # gRPC stub 类
    secure: bool = False,                 # 是否使用 TLS
    credentials: Any = None,              # gRPC 凭证
    options: ChannelOptions | None = None, # 通道选项
    middlewares: list[GrpcMiddleware] | None = None,  # 中间件列表（v3.32.0）
    enable_events: bool = True,           # 是否启用事件发布（v3.32.0）
    service_name: str = "",               # 服务名称（v3.32.0）
)
```

#### 方法

| 方法 | 描述 |
|------|------|
| `connect()` | 建立连接 |
| `close()` | 关闭连接 |
| `unary_call(method, request, timeout, metadata)` | 一元调用 |
| `server_streaming_call(method, request, timeout, metadata)` | 服务端流式调用 |
| `add_metadata(key, value)` | 添加元数据 |
| `clear_metadata()` | 清除元数据 |
| `use(middleware)` | 添加中间件（v3.32.0，链式调用） |
| `health_check(service)` | 健康检查 |

### GrpcResponse

| 属性/方法 | 类型 | 描述 |
|----------|------|------|
| `data` | `T | None` | 响应数据 |
| `status_code` | `GrpcStatusCode` | 状态码 |
| `message` | `str` | 状态消息 |
| `metadata` | `dict` | 响应元数据 |
| `is_success` | `bool` | 是否成功 |
| `raise_for_status()` | `None` | 失败时抛出异常 |

### GrpcStatusCode

```python
from df_test_framework.clients.grpc.models import GrpcStatusCode

GrpcStatusCode.OK                 # 0 - 成功
GrpcStatusCode.CANCELLED          # 1 - 已取消
GrpcStatusCode.UNKNOWN            # 2 - 未知错误
GrpcStatusCode.INVALID_ARGUMENT   # 3 - 参数无效
GrpcStatusCode.DEADLINE_EXCEEDED  # 4 - 超时
GrpcStatusCode.NOT_FOUND          # 5 - 未找到
GrpcStatusCode.ALREADY_EXISTS     # 6 - 已存在
GrpcStatusCode.PERMISSION_DENIED  # 7 - 权限拒绝
GrpcStatusCode.UNAUTHENTICATED    # 16 - 未认证
# ... 更多状态码
```

## 进阶用法

### 服务端流式调用

```python
# 假设有一个返回数据流的方法
request = ListUsersRequest(page_size=10)

for response in client.server_streaming_call("ListUsers", request):
    if response.is_success:
        user = response.data
        print(f"User: {user.name}")
    else:
        print(f"Stream error: {response.message}")
        break
```

### 使用元数据

```python
# 添加全局元数据
client.add_metadata("authorization", "Bearer TOKEN")
client.add_metadata("x-request-id", "req-123")

# 单次调用的元数据
response = client.unary_call(
    "GetUser",
    request,
    metadata=[("x-trace-id", "trace-456")],
)

# 清除全局元数据
client.clear_metadata()
```

### 使用中间件

框架提供多种内置中间件（v3.32.0 重构）：

```python
from df_test_framework.capabilities.clients.grpc import (
    GrpcClient,
    GrpcLoggingMiddleware,
    GrpcMetadataMiddleware,
    GrpcRetryMiddleware,
    GrpcTimingMiddleware,
)

# 日志中间件 - 记录请求和响应
logging_middleware = GrpcLoggingMiddleware(
    log_request=True,
    log_response=True,
)

# 元数据中间件 - 自动添加元数据
metadata_middleware = GrpcMetadataMiddleware({
    "authorization": "Bearer token",
    "x-client-version": "1.0.0",
    "x-request-source": "test",
})

# 重试中间件 - 自动重试失败请求
retry_middleware = GrpcRetryMiddleware(
    max_retries=3,
    retry_on_status=[GrpcStatusCode.UNAVAILABLE],
)

# 计时中间件 - 记录请求耗时
timing_middleware = GrpcTimingMiddleware()

# 创建带中间件的客户端
client = GrpcClient(
    target="localhost:50051",
    stub_class=GreeterStub,
    middlewares=[
        logging_middleware,
        metadata_middleware,
        retry_middleware,
        timing_middleware,
    ],
)

# 或者链式添加
client = (
    GrpcClient(target="localhost:50051", stub_class=GreeterStub)
    .use(GrpcLoggingMiddleware())
    .use(GrpcMetadataMiddleware({"authorization": "Bearer token"}))
    .use(GrpcRetryMiddleware(max_retries=3))
)
```

#### 自定义中间件

```python
from df_test_framework.capabilities.clients.grpc.middleware import GrpcMiddleware
from df_test_framework.capabilities.clients.grpc.models import GrpcRequest, GrpcResponse
import time

class TimingMiddleware(GrpcMiddleware):
    """计时中间件"""

    def __init__(self):
        super().__init__(name="TimingMiddleware", priority=50)

    async def __call__(self, request: GrpcRequest, call_next) -> GrpcResponse:
        # 前置处理 - 记录开始时间
        start = time.time()

        # 调用下一个中间件
        response = await call_next(request)

        # 后置处理 - 计算耗时
        elapsed = time.time() - start
        print(f"Method {request.method} took {elapsed:.3f}s")

        return response
```

### TLS/SSL 连接

```python
import grpc

# 使用默认 SSL 凭证
client = GrpcClient(
    target="api.example.com:443",
    stub_class=MyServiceStub,
    secure=True,
)

# 使用自定义证书
with open("ca.crt", "rb") as f:
    ca_cert = f.read()

credentials = grpc.ssl_channel_credentials(root_certificates=ca_cert)

client = GrpcClient(
    target="api.example.com:443",
    stub_class=MyServiceStub,
    secure=True,
    credentials=credentials,
)
```

### 通道选项

```python
from df_test_framework.clients.grpc.models import ChannelOptions

options = ChannelOptions(
    max_send_message_length=10 * 1024 * 1024,    # 10MB
    max_receive_message_length=10 * 1024 * 1024, # 10MB
    keepalive_time_ms=30000,                      # 30s
    keepalive_timeout_ms=10000,                   # 10s
)

client = GrpcClient(
    target="localhost:50051",
    stub_class=MyServiceStub,
    options=options,
)
```

### 健康检查

```python
# 检查服务器整体健康状态
is_healthy = client.health_check()
print(f"Server healthy: {is_healthy}")

# 检查特定服务
is_service_healthy = client.health_check("my.service.Name")
print(f"Service healthy: {is_service_healthy}")
```

## 测试示例

### 基本测试

```python
import pytest
from df_test_framework.clients.grpc import GrpcClient

# 假设已生成 stub
from user_pb2_grpc import UserServiceStub
from user_pb2 import GetUserRequest, CreateUserRequest

@pytest.fixture
def grpc_client(runtime):
    """gRPC 客户端 fixture"""
    client = GrpcClient(
        target=runtime.settings.grpc_target,
        stub_class=UserServiceStub,
    )
    client.connect()
    client.add_metadata("authorization", f"Bearer {runtime.settings.api_token}")
    yield client
    client.close()

def test_get_user(grpc_client):
    """测试获取用户"""
    request = GetUserRequest(user_id="123")

    response = grpc_client.unary_call("GetUser", request)

    assert response.is_success
    assert response.data.user_id == "123"
    assert response.data.name is not None

def test_create_user(grpc_client, cleanup_users):
    """测试创建用户"""
    request = CreateUserRequest(
        name="Test User",
        email="test@example.com",
    )

    response = grpc_client.unary_call("CreateUser", request)

    assert response.is_success
    user = response.data
    cleanup_users.append(user.user_id)  # 注册清理

    assert user.name == "Test User"
```

### 错误处理测试

```python
from df_test_framework.clients.grpc.models import GrpcStatusCode

def test_not_found_error(grpc_client):
    """测试未找到错误"""
    request = GetUserRequest(user_id="non-existent")

    response = grpc_client.unary_call("GetUser", request)

    assert not response.is_success
    assert response.status_code == GrpcStatusCode.NOT_FOUND

def test_invalid_argument(grpc_client):
    """测试参数无效错误"""
    request = CreateUserRequest(name="", email="invalid")

    response = grpc_client.unary_call("CreateUser", request)

    assert not response.is_success
    assert response.status_code == GrpcStatusCode.INVALID_ARGUMENT
```

### 流式调用测试

```python
def test_list_users_streaming(grpc_client):
    """测试流式获取用户列表"""
    request = ListUsersRequest(page_size=5)

    users = []
    for response in grpc_client.server_streaming_call("ListUsers", request):
        assert response.is_success
        users.append(response.data)

    assert len(users) <= 5
```

## 最佳实践

### 1. 使用 Fixture 管理连接

```python
@pytest.fixture(scope="module")
def grpc_client():
    """模块级别的 gRPC 客户端"""
    client = GrpcClient(target, stub_class)
    client.connect()
    yield client
    client.close()
```

### 2. 合理设置超时

```python
# 快速操作
response = client.unary_call("GetUser", request, timeout=5)

# 慢速操作
response = client.unary_call("ProcessData", request, timeout=60)
```

### 3. 使用中间件统一处理

```python
# 统一添加认证、日志、重试
client = GrpcClient(
    target=target,
    stub_class=stub_class,
    middlewares=[
        GrpcMetadataMiddleware({"authorization": "Bearer TOKEN"}),
        GrpcLoggingMiddleware(),
        GrpcRetryMiddleware(max_retries=3),
    ],
)
```

### 4. 正确处理错误

```python
response = client.unary_call("GetUser", request)

if response.is_success:
    process(response.data)
elif response.status_code == GrpcStatusCode.NOT_FOUND:
    handle_not_found()
elif response.status_code == GrpcStatusCode.PERMISSION_DENIED:
    handle_permission_denied()
else:
    handle_unknown_error(response)
```

## 常见问题

### Q: 如何处理大消息？

```python
options = ChannelOptions(
    max_send_message_length=100 * 1024 * 1024,    # 100MB
    max_receive_message_length=100 * 1024 * 1024, # 100MB
)
client = GrpcClient(target, stub_class, options=options)
```

### Q: 连接超时怎么办？

```python
# 设置 keepalive
options = ChannelOptions(
    keepalive_time_ms=10000,      # 10秒发送一次 keepalive
    keepalive_timeout_ms=5000,    # 5秒超时
    keepalive_permit_without_calls=True,
)
```

### Q: 如何 Mock gRPC 服务？

参考 [Mock 工具使用指南](./mocking.md) 中的 gRPC Mock 部分。

## 参考

- [gRPC 官方文档](https://grpc.io/docs/)
- [gRPC Python 教程](https://grpc.io/docs/languages/python/)
- [gRPC 状态码](https://grpc.github.io/grpc/core/md_doc_statuscodes.html)
