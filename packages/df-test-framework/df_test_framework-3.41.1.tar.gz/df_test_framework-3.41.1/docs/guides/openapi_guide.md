# OpenAPI 代码生成器使用指南

> **版本**: v3.41.0 | **更新**: 2025-12-31

本指南介绍如何使用 df-test-framework 的 OpenAPI 代码生成器，从 Swagger/OpenAPI 规范自动生成测试代码。

## v3.41.0 新特性亮点

- **文件更新模式优化** - `--force` 更新已存在文件并保留用户扩展，`--force --no-merge` 完全覆盖
- **智能请求示例** - 自动识别分页/排序字段，生成有意义的默认值
- **前置查询自动生成** - 详情/更新/删除接口自动获取有效 ID
- **中文测试标题** - 根据 operationId 智能生成中文标题（含驼峰拆分）
- **智能 pytest.mark** - 根据操作类型自动区分 smoke/regression/e2e
- **E2E 和负向测试** - 自动生成完整 CRUD 流程和边界条件测试
- **--tags 参数增强** - 支持逗号分隔多个标签

## 概述

OpenAPI 代码生成器可以从 Swagger 2.0 或 OpenAPI 3.0 规范文件自动生成：

- **Pydantic 模型** - 请求和响应数据模型
- **API 客户端** - 强类型的 API 调用类
- **测试用例** - 基于 pytest 的测试模板

## 快速开始

### 前置条件

```bash
# 确保安装了 pyyaml（OpenAPI 解析依赖）
pip install pyyaml
```

### 基本用法

```bash
# 从本地文件生成
uv run df-test generate openapi swagger.json

# 从 URL 生成
uv run df-test generate openapi https://api.example.com/swagger.json

# 指定输出目录
uv run df-test generate openapi swagger.json --output ./my_project
```

## 命令行选项

```bash
uv run df-test gen from-swagger <spec_path> [OPTIONS]

# 命令别名（以下方式均可）:
# df-test gen from-swagger ...
# df-test gen swagger ...
# df-test gen openapi ...
# df-test generate openapi ...

参数:
  spec_path           OpenAPI 规范文件路径或 URL

选项:
  --output, -o        输出目录（默认: 当前目录）
  --tags, -t          过滤的 API 标签（支持逗号或空格分隔）
  --models-only       只生成模型
  --clients-only      只生成客户端
  --tests-only        只生成测试
  --force             更新已存在的文件（默认保留用户扩展代码）
  --no-merge          与 --force 配合，完全覆盖不保留用户修改
```

### 示例

```bash
# 只生成用户和订单相关的 API（逗号分隔 - v3.41.0+）
uv run df-test gen from-swagger swagger.json --tags user-controller,order-controller

# 空格分隔也支持
uv run df-test gen from-swagger swagger.json --tags user-controller order-controller

# 只生成模型文件
uv run df-test gen from-swagger swagger.json --models-only

# 更新已存在的文件（保留用户扩展代码）
uv run df-test gen from-swagger swagger.json --force

# 完全覆盖（不保留用户修改）
uv run df-test gen from-swagger swagger.json --force --no-merge
```

### 文件更新模式（v3.41.0）

| 参数 | 行为 |
|------|------|
| (无参数) | 只生成新文件，跳过已存在的文件 |
| `--force` | 更新已存在文件，保留 USER EXTENSIONS |
| `--force --no-merge` | 完全覆盖，不保留任何用户修改 |

```bash
# 首次生成
uv run df-test generate openapi swagger.json

# API 变更后更新（保留用户扩展代码）
uv run df-test generate openapi swagger.json --force

# 完全重新生成（放弃用户修改）
uv run df-test generate openapi swagger.json --force --no-merge
```

**工作原理**：生成的文件包含分区标记：

```python
# ========== AUTO-GENERATED START ==========
# 此区域由脚手架自动生成，重新生成时会被更新

class UserAPI(BaseAPI):
    def get_user(self, user_id: int) -> dict:
        return self.get(f"/users/{user_id}")

# ========== AUTO-GENERATED END ==========


# ========== USER EXTENSIONS ==========
# 在此区域添加自定义代码，重新生成时会保留

def custom_helper():
    """用户自定义的辅助函数 - 不会被覆盖"""
    pass
```

使用 `--force` 时的合并行为：
- `AUTO-GENERATED` 区域会被新生成的代码替换
- `USER EXTENSIONS` 区域的内容会被保留

使用 `--force --no-merge` 时：
- 整个文件完全覆盖，不保留任何用户修改

## 代码方式调用

```python
from df_test_framework.cli.generators import generate_from_openapi

# 基本调用
generate_from_openapi("swagger.json")

# 完整参数
generate_from_openapi(
    "https://api.example.com/swagger.json",
    output_dir=Path("./my_project"),
    generate_tests=True,
    generate_clients=True,
    generate_models=True,
    tags=["user", "order"],
    force=False,
)
```

## 生成的文件结构

```
src/{project_name}/
├── models/
│   ├── __init__.py          # 导出通用模型
│   ├── base.py              # Result[T]、PageInfo[T] 通用包装
│   ├── requests/
│   │   ├── __init__.py
│   │   ├── user.py          # 用户相关请求模型
│   │   └── order.py         # 订单相关请求模型
│   └── responses/
│       ├── __init__.py
│       ├── user.py          # 用户相关响应模型
│       └── order.py         # 订单相关响应模型
├── apis/
│   ├── user_api.py          # 用户 API 客户端
│   └── order_api.py         # 订单 API 客户端
tests/
└── api/
    └── test_user_api.py     # 用户 API 测试（v3.41.0 包含多个测试类）
```

### v3.41.0 生成的测试文件结构

```python
# tests/api/test_supplier_controller_api.py

class TestSupplierControllerAPI:        # 单接口测试
    def test_find_supplier_list         # smoke - 列表查询
    def test_find_supplier_by_id        # smoke - 详情查询（含前置查询）
    def test_add_supplier               # smoke - 创建（含 cleanup）
    def test_update_supplier            # regression - 更新（含前置查询）
    def test_delete_supplier            # regression - 删除（含前置查询）

class TestSupplierControllerE2E:        # E2E 流程测试
    def test_crud_flow                  # e2e - 完整 CRUD 流程

class TestSupplierControllerNegative:   # 负向测试
    def test_find_non_existent          # regression - 查询不存在的数据
    def test_delete_non_existent        # regression - 删除不存在的数据
```

## 生成的代码详解

### 1. 通用响应包装类

`models/base.py` 提供常用的响应包装：

```python
from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")

class Result(BaseModel, Generic[T]):
    """通用响应包装

    适用于格式:
        {"code": 200, "message": "success", "data": {...}}
    """
    code: int = Field(..., description="业务状态码")
    message: str = Field(..., description="响应消息")
    data: T | None = Field(None, description="响应数据")


class PageInfo(BaseModel, Generic[T]):
    """分页响应

    适用于格式:
        {"total": 100, "current": 1, "size": 20, "records": [...]}
    """
    total: int = Field(..., description="总记录数")
    current: int = Field(default=1, description="当前页码")
    size: int = Field(default=20, description="每页大小")
    records: list[T] = Field(default_factory=list, description="记录列表")
```

### 2. 请求/响应模型

生成的模型自动处理 Java/Python 命名转换：

```python
# models/requests/user.py
from pydantic import BaseModel, ConfigDict, Field

class CreateUserRequest(BaseModel):
    """创建用户请求"""

    model_config = ConfigDict(populate_by_name=True)

    # Java camelCase 自动转换为 Python snake_case
    # alias 保留原始名称用于 JSON 序列化
    user_name: str = Field(..., description="用户名", alias="userName")
    email: str = Field(..., description="邮箱", alias="email")
    phone_number: str | None = Field(None, description="手机号", alias="phoneNumber")
```

**命名转换规则**：
- `userName` → `user_name`（alias="userName"）
- `phoneNumber` → `phone_number`（alias="phoneNumber"）
- `email` → `email`（名称相同，无 alias）

### 3. 强类型 API 客户端

```python
# apis/user_api.py
from df_test_framework import BaseAPI, HttpClient
from df_test_framework.testing.decorators import api_class
from ..models.requests.user import CreateUserRequest
from ..models.responses.user import CreateUserResponse

@api_class("user_api", scope="function")
class UserAPI(BaseAPI):
    """用户 API 客户端

    Fixture 名称: user_api
    """

    def __init__(self, http_client: HttpClient):
        super().__init__(http_client)
        self.base_path = "/api/v1/users"

    def create_user(self, request: CreateUserRequest) -> CreateUserResponse:
        """创建用户

        Args:
            request: CreateUserRequest 请求模型

        Returns:
            CreateUserResponse: 响应数据
        """
        return self.post(self.base_path, json=request, model=CreateUserResponse)

    def get_user(self, user_id: int) -> UserDetailResponse:
        """获取用户详情"""
        return self.get(f"{self.base_path}/{user_id}", model=UserDetailResponse)
```

### 4. 测试用例模板（v3.41.0 智能增强）

**v3.41.0 生成的测试包含智能特性**：

#### 列表查询测试（智能请求示例 + 增强断言）

```python
# tests/api/test_supplier_controller_api.py
import pytest
import allure
from assertpy import assert_that
from df_test_framework import step

@allure.feature("supplier-controller")
@allure.story("API 测试")
class TestSupplierControllerAPI:
    """supplier-controller API 测试"""

    @allure.title("查询Supplier List")  # 中文标题
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke  # 列表查询 = smoke
    def test_find_supplier_list(self, supplier_controller_api):
        from my_project.models.requests.supplier_controller import FindSupplierListRequest

        # Arrange - 准备测试数据
        with step("准备测试数据"):
            # v3.41.0: 智能请求示例，自动填充分页/排序字段
            request = FindSupplierListRequest(
                pagination={"pageSize": 10, "current": 1},
                sort_name="id",
                sort_type="desc",
            )

        # Act - 执行操作
        with step("调用接口"):
            response = supplier_controller_api.find_supplier_list(request)

        # Assert - 验证结果
        with step("验证响应"):
            # v3.41.0: 增强断言
            assert_that(response.status).is_in("ok", "success")
            assert_that(response.data).is_not_none()
            if "list" in response.data:
                assert_that(response.data["list"]).is_instance_of(list)
            if "pagination" in response.data:
                assert_that(response.data["pagination"]).contains_key("total")
                assert_that(response.data["pagination"]["total"]).is_greater_than_or_equal_to(0)
```

#### 详情查询测试（前置查询自动生成）

```python
    @allure.title("查询Supplier By Id")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_find_supplier_by_id(self, supplier_controller_api):
        from my_project.models.requests.supplier_controller import (
            FindSupplierListRequest, FindSupplierByIdRequest
        )

        # Arrange - 准备测试数据
        with step("准备测试数据"):
            # v3.41.0: 前置查询 - 自动获取有效 ID
            list_request = FindSupplierListRequest(pagination={"pageSize": 1, "current": 1})
            list_response = supplier_controller_api.find_supplier_list(list_request)
            assert_that(list_response.status).is_in("ok", "success")
            if not list_response.data or not list_response.data.get("list"):
                pytest.skip("没有可用的测试数据")
            id = list_response.data["list"][0].get("id")

            # 构造详情查询请求
            request = FindSupplierByIdRequest(id=id)

        # Act - 执行操作
        with step("调用接口"):
            response = supplier_controller_api.find_supplier_by_id(request)

        # Assert - 验证结果
        with step("验证响应"):
            assert_that(response.status).is_in("ok", "success")
            assert_that(response.data).is_not_none()
```

#### 智能 pytest.mark 区分

| 操作类型 | pytest.mark | 说明 |
|----------|-------------|------|
| 列表查询 (findList) | smoke | 核心功能 |
| 详情查询 (findById) | smoke | 核心功能 |
| 创建操作 (add/create) | smoke | 核心功能 |
| 更新操作 (update/modify) | regression | 次要功能 |
| 删除操作 (delete) | regression | 次要功能 |
| 导出操作 (export) | regression | 辅助功能 |

```bash
# 运行不同级别的测试
pytest tests/api/ -v -k "smoke"       # 仅核心测试
pytest tests/api/ -v -k "regression"  # 仅回归测试
pytest tests/api/ -v -k "e2e"         # 仅 E2E 测试
```

**v3.41.0 智能特性说明**：

1. **智能请求示例** - 自动识别 pagination、sort_name、sort_type 等常见字段并生成默认值
2. **前置查询自动生成** - 详情/更新/删除接口自动调用列表接口获取有效 ID
3. **中文测试标题** - find → 查询, add → 新增, update → 更新, delete → 删除
4. **智能 pytest.mark** - 根据操作类型自动标记 smoke/regression/e2e
5. **增强列表断言** - 自动验证列表结构和分页信息

## 集成到项目

### 1. 配置 conftest.py

```python
# conftest.py
from df_test_framework.testing.decorators import load_api_fixtures

# 导入 API 类（触发 @api_class 装饰器注册）
from my_project.apis.user_api import UserAPI  # noqa: F401
from my_project.apis.order_api import OrderAPI  # noqa: F401

# 加载所有已注册的 API fixtures
load_api_fixtures(globals())
```

### 2. 编写测试

```python
# tests/api/test_user_api.py
from my_project.models.requests.user import CreateUserRequest

def test_create_user(user_api):
    """user_api fixture 由 @api_class 自动注册"""
    request = CreateUserRequest(
        user_name="Alice",
        email="alice@example.com"
    )
    response = user_api.create_user(request)

    assert response.code == 200
    assert response.data.user_name == "Alice"
```

### 3. 运行测试

```bash
# 运行所有 API 测试
uv run pytest tests/api/ -v

# 运行冒烟测试
uv run pytest tests/api/ -m smoke -v
```

## 高级用法

### 自定义模型

生成的模型可以根据需要进行扩展：

```python
# 扩展生成的模型
from my_project.models.requests.user import CreateUserRequest

class CreateUserRequestWithValidation(CreateUserRequest):
    """添加自定义验证"""

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v.endswith("@company.com"):
            raise ValueError("必须使用公司邮箱")
        return v
```

### 使用 Result[T] 包装

```python
from my_project.models.base import Result
from my_project.models.responses.user import UserData

# 定义带包装的响应类型
class CreateUserResponse(Result[UserData]):
    """创建用户响应 = Result[UserData]"""
    pass

# 使用时自动解析
response = user_api.create_user(request)
print(response.code)        # 200
print(response.message)     # "success"
print(response.data.id)     # 1
print(response.data.name)   # "Alice"
```

### 处理分页响应

```python
from my_project.models.base import PageInfo

class UserListResponse(PageInfo[UserData]):
    """用户列表响应"""
    pass

# 使用
response = user_api.list_users(page=1, size=20)
print(response.total)       # 100
print(response.current)     # 1
print(response.size)        # 20
for user in response.records:
    print(user.name)
```

## 支持的规范格式

### Swagger 2.0

```json
{
  "swagger": "2.0",
  "info": {"title": "API", "version": "1.0"},
  "host": "api.example.com",
  "basePath": "/api/v1",
  "paths": {
    "/users": {
      "post": {
        "operationId": "createUser",
        "parameters": [
          {
            "in": "body",
            "name": "body",
            "schema": {"$ref": "#/definitions/CreateUserRequest"}
          }
        ],
        "responses": {
          "200": {
            "schema": {"$ref": "#/definitions/CreateUserResponse"}
          }
        }
      }
    }
  }
}
```

### OpenAPI 3.0

```yaml
openapi: 3.0.0
info:
  title: API
  version: 1.0.0
paths:
  /users:
    post:
      operationId: createUser
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CreateUserResponse'
```

## 常见问题

### Q: 生成的模型字段为空？

检查 Swagger 文档中的 `$ref` 引用是否正确。生成器会自动解析引用，但如果引用路径错误，可能导致字段为空。

### Q: 如何处理不规范的 Swagger 文档？

生成器使用宽松模式解析，会跳过严格的 OpenAPI 规范验证。如果仍有问题，可以尝试手动修复 Swagger 文档。

### Q: 如何更新已生成的代码？

**推荐方式（v3.39.0+）**：使用 `--merge` 选项增量合并，保留用户自定义代码：

```bash
uv run df-test generate openapi swagger.json --merge
```

**传统方式**：使用 `--force` 选项强制覆盖（会丢失自定义修改）：

```bash
uv run df-test generate openapi swagger.json --force
```

如果使用 `--force`，建议先备份自定义修改，或使用继承扩展生成的类。

## 相关文档

- [v3.41.0 发布说明](../releases/v3.41.0.md) - 智能代码生成增强
- [v3.39.0 发布说明](../releases/v3.39.0.md) - 增量合并功能
- [v3.38.0 发布说明](../releases/v3.38.0.md)
- [脚手架 CLI 工具指南](scaffold_cli_guide.md)
- [HTTP 客户端使用指南](async_http_client.md)
- [测试数据生成指南](test_data.md)
