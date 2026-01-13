# GraphQL 客户端使用指南

> **版本**: v3.38.0 | **更新**: 2025-12-24
> **引入版本**: v3.11.0
> **推荐导入**: `from df_test_framework import GraphQLClient`

## 概述

GraphQL 客户端提供标准 GraphQL 协议的 HTTP 传输支持，包括：
- 查询（Query）和变更（Mutation）操作
- 批量查询
- 文件上传（multipart/form-data）
- 查询构建器（QueryBuilder）
- 中间件系统（v3.33.0 重构）

> **重要变更 v3.33.0**：集成中间件系统（洋葱模型），支持 `middlewares=[]` 和 `.use()` 链式调用，与 HTTP/gRPC 客户端保持一致。

## 快速开始

### 基本用法

```python
from df_test_framework import GraphQLClient

# 创建客户端
client = GraphQLClient("https://api.example.com/graphql")

# 设置认证
client.set_header("Authorization", "Bearer YOUR_TOKEN")

# 执行查询
query = """
    query GetUser($id: ID!) {
        user(id: $id) {
            id
            name
            email
        }
    }
"""
response = client.execute(query, {"id": "123"})

# 处理响应
if response.is_success:
    user = response.get_field("user")
    print(f"User: {user['name']}")
else:
    print(f"Errors: {response.errors}")
```

### 使用上下文管理器

```python
with GraphQLClient("https://api.example.com/graphql") as client:
    client.set_header("Authorization", "Bearer TOKEN")
    response = client.execute("{ users { id name } }")
    # 客户端会自动关闭
```

## API 详解

### GraphQLClient

#### 构造函数

```python
GraphQLClient(
    url: str,                    # GraphQL 端点 URL
    headers: dict | None = None, # 默认请求头
    timeout: int = 30,           # 超时时间（秒）
    verify_ssl: bool = True,     # 是否验证 SSL
    middlewares: list[GraphQLMiddleware] | None = None,  # 中间件列表（v3.33.0）
    event_bus: EventBus | None = None,  # 事件总线（v3.33.0）
)
```

#### 方法

| 方法 | 描述 |
|------|------|
| `execute(query, variables, operation_name)` | 执行单个 GraphQL 操作（v3.33.0 集成中间件） |
| `execute_batch(operations)` | 批量执行多个操作（暂不支持中间件） |
| `upload_file(query, variables, files)` | 文件上传（暂不支持中间件） |
| `set_header(key, value)` | 设置请求头 |
| `remove_header(key)` | 移除请求头 |
| `use(middleware)` | 添加中间件（v3.33.0，链式调用） |
| `close()` | 关闭客户端 |

### GraphQLResponse

| 属性/方法 | 类型 | 描述 |
|----------|------|------|
| `data` | `dict | None` | 响应数据 |
| `errors` | `list[GraphQLError] | None` | 错误列表 |
| `is_success` | `bool` | 是否成功（无错误）|
| `has_data` | `bool` | 是否有数据 |
| `get_field(name)` | `Any` | 获取数据字段 |
| `raise_for_errors()` | `None` | 有错误时抛出异常 |

## 进阶用法

### 使用中间件

框架提供多种内置中间件（v3.33.0 新增）：

```python
from df_test_framework.capabilities.clients.graphql import GraphQLClient
from df_test_framework.capabilities.clients.graphql.middleware import (
    GraphQLMiddleware,
    GraphQLLoggingMiddleware,
    GraphQLRetryMiddleware,
)

# 方式1: 构造函数传入
client = GraphQLClient(
    "https://api.example.com/graphql",
    middlewares=[
        GraphQLLoggingMiddleware(),
        GraphQLRetryMiddleware(max_retries=3),
    ],
)

# 方式2: 链式调用
client = (
    GraphQLClient("https://api.example.com/graphql")
    .use(GraphQLLoggingMiddleware())
    .use(GraphQLRetryMiddleware(max_retries=3))
)

# 执行查询（自动经过中间件）
response = client.execute(query, variables)
```

#### 内置中间件

| 中间件 | 描述 | 默认优先级 |
|--------|------|------------|
| `GraphQLLoggingMiddleware` | 记录请求和响应日志 | 0（最先执行） |
| `GraphQLRetryMiddleware` | 自动重试失败请求 | 10 |
| `GraphQLEventPublisherMiddleware` | 发布 GraphQL 事件（自动添加） | 999（最内层） |

#### 自定义中间件

```python
from df_test_framework.capabilities.clients.graphql.middleware import GraphQLMiddleware
from df_test_framework.capabilities.clients.graphql.models import GraphQLRequest, GraphQLResponse
import time

class TimingMiddleware(GraphQLMiddleware):
    """计时中间件"""

    def __init__(self):
        super().__init__(name="TimingMiddleware", priority=50)

    async def __call__(
        self,
        request: GraphQLRequest,
        call_next,
    ) -> GraphQLResponse:
        # 前置处理 - 记录开始时间
        start = time.time()
        print(f"GraphQL Request: {request.operation_name or 'Anonymous'}")

        # 调用下一个中间件
        response = await call_next(request)

        # 后置处理 - 计算耗时
        elapsed = time.time() - start
        print(f"Request took {elapsed:.3f}s")

        return response

# 使用自定义中间件
client = GraphQLClient(url).use(TimingMiddleware())
```

### 批量查询

```python
operations = [
    ("query { user(id: 1) { name } }", None),
    ("query { user(id: 2) { name } }", None),
    ("query GetUser($id: ID!) { user(id: $id) { name } }", {"id": "3"}),
]

responses = client.execute_batch(operations)

for i, response in enumerate(responses):
    if response.is_success:
        print(f"Response {i}: {response.data}")
```

### 文件上传

遵循 [GraphQL multipart request specification](https://github.com/jaydenseric/graphql-multipart-request-spec)。

```python
mutation = """
    mutation UploadAvatar($file: Upload!) {
        uploadAvatar(file: $file) {
            url
        }
    }
"""

# 读取文件
with open("avatar.png", "rb") as f:
    file_content = f.read()

files = {
    "file": ("avatar.png", file_content, "image/png"),
}

response = client.upload_file(
    mutation,
    variables={"file": None},  # 文件变量设为 null
    files=files,
)

if response.is_success:
    url = response.get_field("uploadAvatar")["url"]
    print(f"Uploaded: {url}")
```

### 使用 QueryBuilder

QueryBuilder 提供流畅的 API 构建 GraphQL 查询。

```python
from df_test_framework.clients.graphql import QueryBuilder

# 简单查询
query = (QueryBuilder()
    .query("users")
    .field("id", "name", "email")
    .build())

# 输出: query { users { id name email } }

# 带变量的查询
query = (QueryBuilder()
    .query("user")
    .variable("id", "ID!")
    .argument("id", "$id")
    .field("id", "name")
    .nested("posts", ["id", "title", "content"])
    .build())

# 输出: query($id: ID!) { user(id: $id) { id name posts { id title content } } }

# 执行
response = client.execute(query, {"id": "123"})
```

#### QueryBuilder 方法

| 方法 | 描述 |
|------|------|
| `query(name)` | 设置查询操作 |
| `mutation(name)` | 设置变更操作 |
| `field(*fields)` | 添加字段 |
| `nested(name, fields)` | 添加嵌套字段 |
| `variable(name, type)` | 声明变量 |
| `argument(name, value)` | 添加参数 |
| `alias(name)` | 设置别名 |
| `fragment(name, on_type, fields)` | 添加片段 |
| `build()` | 构建查询字符串 |

## 测试示例

### 基本 API 测试

```python
import pytest
from df_test_framework.clients.graphql import GraphQLClient

@pytest.fixture
def graphql_client(runtime):
    """GraphQL 客户端 fixture"""
    client = GraphQLClient(
        runtime.settings.graphql_url,
        headers={"Authorization": f"Bearer {runtime.settings.api_token}"},
    )
    yield client
    client.close()

def test_get_user(graphql_client):
    """测试获取用户"""
    query = """
        query GetUser($id: ID!) {
            user(id: $id) {
                id
                name
                email
            }
        }
    """

    response = graphql_client.execute(query, {"id": "1"})

    assert response.is_success
    user = response.get_field("user")
    assert user["id"] == "1"
    assert user["name"] is not None

def test_create_user(graphql_client, cleanup_users):
    """测试创建用户"""
    mutation = """
        mutation CreateUser($input: CreateUserInput!) {
            createUser(input: $input) {
                id
                name
            }
        }
    """

    response = graphql_client.execute(mutation, {
        "input": {"name": "Test User", "email": "test@example.com"}
    })

    assert response.is_success
    user = response.get_field("createUser")
    cleanup_users.append(user["id"])  # 注册清理

    assert user["name"] == "Test User"
```

### 错误处理测试

```python
def test_graphql_error_handling(graphql_client):
    """测试 GraphQL 错误处理"""
    query = "query { nonExistentField }"

    response = graphql_client.execute(query)

    assert not response.is_success
    assert response.errors is not None
    assert len(response.errors) > 0

    # 可以检查具体错误
    error = response.errors[0]
    assert "nonExistentField" in error.message

def test_raise_for_errors(graphql_client):
    """测试 raise_for_errors 方法"""
    query = "query { invalidQuery }"

    response = graphql_client.execute(query)

    with pytest.raises(RuntimeError) as exc_info:
        response.raise_for_errors()

    assert "GraphQL request failed" in str(exc_info.value)
```

## 最佳实践

### 1. 使用变量而非字符串拼接

```python
# ✅ 好：使用变量
query = "query GetUser($id: ID!) { user(id: $id) { name } }"
response = client.execute(query, {"id": user_id})

# ❌ 差：字符串拼接（有注入风险）
query = f"query {{ user(id: \"{user_id}\") {{ name }} }}"
```

### 2. 复用客户端实例

```python
# ✅ 好：使用 fixture 复用
@pytest.fixture(scope="module")
def graphql_client():
    client = GraphQLClient(url)
    yield client
    client.close()

# ❌ 差：每个测试创建新实例
def test_something():
    client = GraphQLClient(url)  # 每次都创建
```

### 3. 合理处理错误

```python
response = client.execute(query, variables)

# 方式1：检查 is_success
if response.is_success:
    process(response.data)
else:
    log_errors(response.errors)

# 方式2：使用 raise_for_errors
response.raise_for_errors()  # 有错误时抛出
process(response.data)
```

### 4. 使用 QueryBuilder 构建复杂查询

```python
# 复杂查询推荐使用 QueryBuilder
query = (QueryBuilder()
    .query("searchProducts")
    .variable("query", "String!")
    .variable("first", "Int")
    .argument("query", "$query")
    .argument("first", "$first")
    .field("totalCount")
    .nested("edges", [
        "cursor",
        {"node": ["id", "name", "price"]}
    ])
    .build())
```

## 常见问题

### Q: 如何处理认证？

```python
# Bearer Token
client.set_header("Authorization", "Bearer YOUR_TOKEN")

# API Key
client.set_header("X-API-Key", "YOUR_API_KEY")

# 自定义认证
client.set_header("X-Custom-Auth", "custom_value")
```

### Q: 如何禁用 SSL 验证？

```python
client = GraphQLClient(
    url="https://api.example.com/graphql",
    verify_ssl=False,  # 仅在开发/测试环境使用
)
```

### Q: 如何设置超时？

```python
client = GraphQLClient(
    url="https://api.example.com/graphql",
    timeout=60,  # 60 秒超时
)
```

## 参考

- [GraphQL 官方规范](https://spec.graphql.org/)
- [GraphQL multipart request specification](https://github.com/jaydenseric/graphql-multipart-request-spec)
- [API 参考文档](../api-reference/clients.md)
