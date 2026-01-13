# 断言系统使用指南

> **版本**: v3.38.0 | **更新**: 2025-12-24
> **引入版本**: v3.30.0
> **模块**: `df_test_framework.testing.assertions`

断言系统提供丰富的断言辅助方法，简化 API 测试代码。包含 HTTP 响应断言、JSON Schema 验证、自定义匹配器三大功能模块。

---

## 快速开始

### 安装依赖

```bash
# JSONPath 支持（可选）
uv add jsonpath-ng

# JSON Schema 验证（已内置）
# jsonschema 已作为框架依赖
```

### 基本使用

```python
from df_test_framework.testing.assertions import (
    # HTTP 响应断言
    ResponseAssertions,
    assert_status,
    assert_json_has,
    # Schema 验证
    SchemaValidator,
    assert_schema,
    # 匹配器
    matches_regex,
    in_range,
    is_string,
)

def test_get_user(http_client):
    response = http_client.get("/users/1")

    # 方式1: 静态方法
    assert_status(response, 200)
    assert_json_has(response, "id", "name", "email")

    # 方式2: 链式调用
    ResponseAssertions(response) \
        .status(200) \
        .json_has("id", "name") \
        .json_path_equals("$.data.id", 1)

    # 方式3: 匹配器
    data = response.json()
    assert is_string.matches(data["name"])
    assert in_range(1, 100).matches(data["age"])
```

---

## HTTP 响应断言

### ResponseAssertions 类

支持两种使用方式：静态方法和链式调用。

#### 静态方法

```python
from df_test_framework.testing.assertions import (
    assert_status,
    assert_success,
    assert_client_error,
    assert_server_error,
    assert_json_has,
    assert_json_not_has,
    assert_json_equals,
    assert_json_path_equals,
    assert_json_schema,
    assert_header_has,
    assert_content_type,
    assert_response_time_lt,
)

def test_api_response(http_client):
    response = http_client.post("/users", json={"name": "Alice"})

    # 状态码断言
    assert_status(response, 201)

    # 成功响应（2xx）
    assert_success(response)

    # 检查字段存在
    assert_json_has(response, "id", "name", "created_at")

    # 检查字段不存在
    assert_json_not_has(response, "password", "secret_key")

    # 检查字段值
    assert_json_equals(response, {"name": "Alice"})  # 包含即可
    assert_json_equals(response, {"name": "Alice"}, strict=True)  # 完全相等

    # JSONPath 断言（需要 jsonpath-ng）
    assert_json_path_equals(response, "$.data.user.id", 1)
    assert_json_path_equals(response, "$.items[0].name", "Product A")

    # 响应头断言
    assert_header_has(response, "X-Request-Id")
    assert_content_type(response, "application/json")

    # 响应时间断言
    assert_response_time_lt(response, 1000)  # 小于 1000ms

def test_error_responses(http_client):
    # 测试客户端错误（4xx）
    response = http_client.get("/users/not-found")
    assert_client_error(response)  # 断言 4xx 状态码

    # 测试服务端错误（5xx）
    response = http_client.post("/internal-error")
    assert_server_error(response)  # 断言 5xx 状态码
```

#### 链式调用

```python
from df_test_framework.testing.assertions import ResponseAssertions

def test_user_api(http_client):
    response = http_client.get("/users/1")

    # 链式调用更加简洁
    ResponseAssertions(response) \
        .status(200) \
        .success() \
        .json_has("id", "name", "email") \
        .json_equals({"status": "active"}) \
        .json_path_equals("$.data.role", "user") \
        .header_has("Content-Type", "application/json") \
        .response_time_lt(500)
```

### 常用断言速查

| 断言方法 | 说明 |
|----------|------|
| `assert_status(resp, 200)` | 状态码等于 200 |
| `assert_success(resp)` | 状态码是 2xx |
| `assert_client_error(resp)` | 状态码是 4xx（客户端错误） |
| `assert_server_error(resp)` | 状态码是 5xx（服务端错误） |
| `assert_json_has(resp, "a", "b")` | JSON 包含字段 a 和 b |
| `assert_json_not_has(resp, "x", "y")` | JSON 不包含字段 x 和 y |
| `assert_json_equals(resp, {...})` | JSON 包含指定键值对 |
| `assert_json_path_equals(resp, "$.x.y", val)` | JSONPath 值匹配 |
| `assert_json_schema(resp, schema)` | 符合 JSON Schema |
| `assert_header_has(resp, "X-Id")` | 存在响应头 |
| `assert_content_type(resp, "json")` | Content-Type 包含 |
| `assert_response_time_lt(resp, 1000)` | 响应时间 < 1000ms |

---

## JSON Schema 验证

### SchemaValidator 类

提供完整的 JSON Schema (Draft 7) 验证功能。

```python
from df_test_framework.testing.assertions import (
    SchemaValidator,
    SchemaValidationError,
    assert_schema,
    validate_response_schema,
)

# 定义 Schema
user_schema = {
    "type": "object",
    "required": ["id", "name", "email"],
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "name": {"type": "string", "minLength": 1},
        "email": {"type": "string", "format": "email"},
        "age": {"type": "integer", "minimum": 0, "maximum": 150},
        "roles": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
        },
    },
}

def test_user_schema():
    # 方式1: 快捷函数
    data = {"id": 1, "name": "Alice", "email": "alice@example.com"}
    assert_schema(data, user_schema)

    # 方式2: SchemaValidator 类
    validator = SchemaValidator(user_schema)

    # 验证（失败时抛出 SchemaValidationError）
    validator.validate(data)

    # 检查是否有效（不抛异常）
    is_valid = validator.is_valid(data)

    # 获取所有错误
    errors = validator.get_errors({"id": "invalid"})
    # [{"path": ["id"], "message": "'invalid' is not of type 'integer'", ...}]

def test_response_schema(http_client):
    response = http_client.get("/users/1")

    # 直接验证响应
    validate_response_schema(response, user_schema)
```

### 从文件加载 Schema

```python
# 支持 JSON 和 YAML 格式
validator = SchemaValidator.from_file("schemas/user.json")
validator = SchemaValidator.from_file("schemas/order.yaml")

# 从字符串加载
schema_str = '{"type": "object", "required": ["id"]}'
validator = SchemaValidator.from_string(schema_str)
validator = SchemaValidator.from_string(yaml_str, format="yaml")
```

### Schema 构建器

提供便捷的 Schema 构建函数。

```python
from df_test_framework.testing.assertions import (
    create_object_schema,
    create_array_schema,
    COMMON_SCHEMAS,
)

# 使用预定义 Schema 片段
user_schema = create_object_schema(
    properties={
        "id": COMMON_SCHEMAS["id"],           # {"type": "integer", "minimum": 1}
        "name": COMMON_SCHEMAS["non_empty_string"],
        "email": COMMON_SCHEMAS["email"],
        "phone": COMMON_SCHEMAS["phone_cn"],  # 中国手机号格式
        "created_at": COMMON_SCHEMAS["datetime"],
    },
    required=["id", "name", "email"],
)

# 数组 Schema
users_schema = create_array_schema(
    items=user_schema,
    min_items=1,
    max_items=100,
    unique_items=False,
)
```

### 预定义 Schema 片段

`COMMON_SCHEMAS` 包含常用的 Schema 定义：

| 名称 | 说明 |
|------|------|
| `id` | 正整数 ID |
| `uuid` | UUID 格式字符串 |
| `email` | 邮箱格式 |
| `datetime` | ISO 8601 日期时间 |
| `date` | ISO 8601 日期 |
| `url` | URL 格式 |
| `phone_cn` | 中国手机号（1开头11位） |
| `non_empty_string` | 非空字符串 |
| `positive_number` | 正数 |
| `non_negative_number` | 非负数 |
| `pagination` | 分页对象 |
| `api_response` | 标准 API 响应 |

---

## 自定义匹配器

匹配器提供灵活的值匹配能力，支持组合使用。

### 基础匹配器

```python
from df_test_framework.testing.assertions import (
    matches_regex,
    contains,
    in_range,
    equals,
    is_type,
    has_length,
    starts_with,
    ends_with,
    greater_than,
    less_than,
)

# 正则匹配
assert matches_regex(r"^TEST_\d{3}$").matches("TEST_123")
assert matches_regex(r"hello", re.IGNORECASE).matches("HELLO")

# 包含匹配
assert contains("world").matches("hello world")  # 字符串
assert contains(1).matches([1, 2, 3])            # 列表
assert contains("key").matches({"key": "val"})   # 字典

# 范围匹配
assert in_range(1, 100).matches(50)
assert in_range(1, 100, inclusive=False).matches(50)  # 不包含边界

# 相等匹配
assert equals(42).matches(42)

# 类型匹配
assert is_type(int).matches(42)
assert is_type(str, int).matches(42)  # 任一类型

# 长度匹配
assert has_length(3).matches("abc")
assert has_length(min_len=1, max_len=10).matches([1, 2])

# 前后缀匹配
assert starts_with("TEST_").matches("TEST_001")
assert ends_with(".json", ignore_case=True).matches("data.JSON")

# 比较匹配
assert greater_than(10).matches(20)
assert less_than(100, or_equal=True).matches(100)
```

### 预定义匹配器实例

```python
from df_test_framework.testing.assertions import (
    # 空值匹配
    is_none,
    is_not_none,
    is_true,
    is_false,
    is_empty,
    is_not_empty,
    # 类型匹配
    is_string,
    is_int,
    is_float,
    is_number,
    is_bool,
    is_list,
    is_dict,
    is_date,
)

# 直接使用，无需创建
assert is_none.matches(None)
assert is_not_none.matches("value")
assert is_string.matches("hello")
assert is_number.matches(3.14)
assert is_empty.matches([])
assert is_not_empty.matches([1, 2, 3])
```

### 组合匹配器

```python
from df_test_framework.testing.assertions import (
    all_of,
    any_of,
    not_matcher,
    predicate,
)

# AND 组合（全部满足）
username_matcher = all_of(
    is_string,
    has_length(min_len=3, max_len=20),
    matches_regex(r"^[a-zA-Z][a-zA-Z0-9_]*$"),
)
assert username_matcher.matches("user_123")

# OR 组合（任一满足）
nullable_string = any_of(is_none, is_string)
assert nullable_string.matches(None)
assert nullable_string.matches("hello")

# NOT 取反
not_empty_list = not_matcher(is_empty)
assert not_empty_list.matches([1, 2])

# 自定义谓词
is_even = predicate(lambda x: x % 2 == 0, "是偶数")
assert is_even.matches(4)
```

### 操作符重载

匹配器支持 `&`（AND）、`|`（OR）、`~`（NOT）操作符。

```python
# 使用操作符组合
valid_id = is_int & in_range(1, 1000000)
assert valid_id.matches(12345)

optional_name = is_none | (is_string & has_length(min_len=1))
assert optional_name.matches(None)
assert optional_name.matches("Alice")

not_null = ~is_none
assert not_null.matches("value")
```

### assert_matches 方法

匹配器提供 `assert_matches` 方法，失败时给出详细错误信息。

```python
matcher = in_range(1, 100)

# 断言匹配
matcher.assert_matches(50)  # 通过

# 失败时抛出 AssertionError
try:
    matcher.assert_matches(200)
except AssertionError as e:
    print(e)  # "期望 在范围 [1, 100] 内，实际值: 200"

# 自定义错误消息
matcher.assert_matches(50, message="年龄必须在 1-100 之间")
```

---

## 实战示例

### 完整的 API 测试

```python
import pytest
from df_test_framework.testing.assertions import (
    ResponseAssertions,
    SchemaValidator,
    assert_status,
    assert_json_has,
    matches_regex,
    in_range,
    is_string,
    create_object_schema,
    COMMON_SCHEMAS,
)

# 定义 Schema
USER_SCHEMA = create_object_schema(
    properties={
        "id": COMMON_SCHEMAS["id"],
        "username": {"type": "string", "minLength": 3},
        "email": COMMON_SCHEMAS["email"],
        "role": {"type": "string", "enum": ["user", "admin", "vip"]},
        "created_at": COMMON_SCHEMAS["datetime"],
    },
    required=["id", "username", "email"],
)

class TestUserAPI:

    def test_create_user(self, http_client):
        """创建用户"""
        response = http_client.post("/users", json={
            "username": "alice",
            "email": "alice@example.com",
        })

        # 链式断言
        ResponseAssertions(response) \
            .status(201) \
            .json_has("id", "username", "created_at") \
            .json_equals({"username": "alice"})

        # Schema 验证
        SchemaValidator(USER_SCHEMA).validate(response.json())

        # 匹配器验证
        data = response.json()
        assert in_range(1, 1000000).matches(data["id"])
        assert matches_regex(r"^\d{4}-\d{2}-\d{2}").matches(data["created_at"])

    def test_get_user(self, http_client):
        """获取用户"""
        response = http_client.get("/users/1")

        # 静态方法断言
        assert_status(response, 200)
        assert_json_has(response, "id", "username", "email")

        # JSONPath 断言
        ResponseAssertions(response) \
            .json_path_equals("$.id", 1) \
            .json_path_equals("$.role", "user")

    def test_list_users(self, http_client):
        """用户列表"""
        response = http_client.get("/users?page=1&size=10")

        ResponseAssertions(response) \
            .status(200) \
            .json_has("items", "total", "page")

        data = response.json()

        # 验证分页
        assert in_range(0, 1000).matches(data["total"])
        assert is_list.matches(data["items"])

        # 验证每个用户
        for user in data["items"]:
            SchemaValidator(USER_SCHEMA).is_valid(user)
```

### 自定义匹配器

```python
from df_test_framework.testing.assertions import BaseMatcher

class PhoneNumberMatcher(BaseMatcher):
    """中国手机号匹配器"""

    def matches(self, actual):
        if not isinstance(actual, str):
            return False
        import re
        return bool(re.match(r"^1[3-9]\d{9}$", actual))

    def describe(self):
        return "是有效的中国手机号"

# 使用
phone_matcher = PhoneNumberMatcher()
assert phone_matcher.matches("13800138000")

# 组合使用
valid_phone = any_of(is_none, PhoneNumberMatcher())
```

---

## API 参考

### 响应断言

| 函数/方法 | 说明 |
|-----------|------|
| `assert_status(resp, code)` | 断言状态码 |
| `assert_success(resp)` | 断言 2xx 成功响应 |
| `assert_client_error(resp)` | 断言 4xx 客户端错误 |
| `assert_server_error(resp)` | 断言 5xx 服务端错误 |
| `assert_json_has(resp, *keys)` | 断言 JSON 包含字段 |
| `assert_json_not_has(resp, *keys)` | 断言 JSON 不包含字段 |
| `assert_json_equals(resp, expected, strict)` | 断言 JSON 匹配 |
| `assert_json_path_equals(resp, path, value)` | 断言 JSONPath |
| `assert_json_schema(resp, schema)` | 断言符合 Schema |
| `assert_header_has(resp, name, value)` | 断言响应头 |
| `assert_content_type(resp, expected)` | 断言 Content-Type |
| `assert_response_time_lt(resp, ms)` | 断言响应时间 |

### Schema 验证

| 类/函数 | 说明 |
|---------|------|
| `SchemaValidator(schema)` | Schema 验证器 |
| `SchemaValidator.from_file(path)` | 从文件加载 |
| `validator.validate(data)` | 验证（抛异常） |
| `validator.is_valid(data)` | 验证（返回布尔） |
| `validator.get_errors(data)` | 获取所有错误 |
| `assert_schema(data, schema)` | 快捷验证函数 |
| `validate_response_schema(resp, schema)` | 验证响应 |
| `create_object_schema(...)` | 创建对象 Schema |
| `create_array_schema(...)` | 创建数组 Schema |

### 匹配器

| 匹配器 | 说明 |
|--------|------|
| `matches_regex(pattern)` | 正则匹配 |
| `contains(value)` | 包含匹配 |
| `in_range(min, max)` | 范围匹配 |
| `equals(expected)` | 相等匹配 |
| `is_type(*types)` | 类型匹配 |
| `has_length(exact/min/max)` | 长度匹配 |
| `starts_with(prefix)` | 前缀匹配 |
| `ends_with(suffix)` | 后缀匹配 |
| `greater_than(value)` | 大于匹配 |
| `less_than(value)` | 小于匹配 |
| `all_of(*matchers)` | AND 组合 |
| `any_of(*matchers)` | OR 组合 |
| `not_matcher(matcher)` | NOT 取反 |
| `predicate(func, desc)` | 自定义谓词 |

---

## 相关文档

- [Factory 系统指南](factory_guide.md) - 测试数据生成
- [Mock 指南](mocking.md) - 测试替身
- [HTTP 客户端指南](httpx_advanced_usage.md) - HTTP 请求
