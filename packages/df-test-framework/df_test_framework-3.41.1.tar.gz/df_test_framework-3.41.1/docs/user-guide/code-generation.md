# 代码生成工具使用指南

> 📚 **版本**: v3.41.0
> 🎯 **目标**: 使用代码生成工具快速创建测试代码，提升开发效率

---

## 📖 目录

- [简介](#简介)
- [功能成熟度对比](#功能成熟度对比)
- [快速开始](#快速开始)
- [生成命令详解](#生成命令详解)
  - [生成测试文件](#生成测试文件)
  - [生成 API 客户端类](#生成-api-客户端类)
  - [生成 Builder 类](#生成-builder-类)
  - [生成 Repository 类](#生成-repository-类)
  - [从 JSON 生成模型](#从-json-生成模型)
  - [生成 GraphQL 相关](#生成-graphql-相关)
  - [生成 Redis Fixture](#生成-redis-fixture)
  - [从 OpenAPI 生成](#从-openapi-生成)
- [实战示例](#实战示例)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

---

## 简介

DF Test Framework 提供了强大的代码生成工具 (`df-test gen`)，可以快速生成：

| 类型 | 命令 | 用途 | 成熟度 |
|------|------|------|--------|
| **OpenAPI 生成** | `df-test gen from-swagger` | 从 Swagger/OpenAPI 自动生成完整代码 | ⭐⭐⭐⭐⭐ |
| **测试文件** | `df-test gen test` | 生成标准的 API 测试文件模板 | ⭐⭐⭐ |
| **API 客户端** | `df-test gen api` | 生成 API 调用封装类模板 | ⭐⭐⭐ |
| **Builder 类** | `df-test gen builder` | 生成数据构造器类模板 | ⭐⭐⭐ |
| **Repository 类** | `df-test gen repo` | 生成数据仓库类模板 | ⭐⭐⭐ |
| **Pydantic 模型** | `df-test gen models` | 从 JSON 响应生成模型 | ⭐⭐⭐⭐ |
| **GraphQL 客户端** | `df-test gen graphql-client` | 生成 GraphQL 客户端模板 | ⭐⭐ |
| **Redis Fixture** | `df-test gen redis-fixture` | 生成 Redis 使用示例 | ⭐⭐ |

---

## 功能成熟度对比

### 智能生成器 vs 模板生成器

框架的代码生成工具分为两类：

#### 1. 智能生成器（推荐）

**`df-test gen from-swagger`** - 从 OpenAPI 规范自动生成完整代码

```
成熟度: ⭐⭐⭐⭐⭐ (100%)
```

- ✅ **自动化程度高**: 解析 API 规范，自动生成 API 客户端、Request/Response 模型、测试用例
- ✅ **智能特性**: 自动识别分页字段、生成前置查询、中文测试标题
- ✅ **增量更新**: `--force` 支持保留用户扩展代码
- ✅ **持续迭代**: v3.35 → v3.41+ 持续增强

**适用场景**: 有 Swagger/OpenAPI 文档的后端 API

#### 2. 模板生成器

其他 `df-test gen` 命令 - 生成带占位符的代码骨架

```
成熟度: ⭐⭐⭐ (40%-60%)
```

- ⚠️ **模板填充**: 生成的是标准模板，需要手动完善业务逻辑
- ⚠️ **不自动分析**: 不会分析现有 API 或数据库结构
- ✅ **符合规范**: 遵循框架最佳实践和命名规范
- ✅ **快速启动**: 秒级生成代码骨架

**适用场景**: 快速创建符合框架规范的代码骨架，手动开发时使用

### 选择建议

| 场景 | 推荐方式 |
|------|----------|
| 有 Swagger 文档 | `df-test gen from-swagger` |
| 无 Swagger，手动开发 | `df-test gen test` + `df-test gen api` |
| 需要 Builder/Repository | `df-test gen builder` + `df-test gen repo` |
| 需要从 JSON 推断模型 | `df-test gen models` |

### 功能状态说明

> **v3.41.0 状态**: 所有模板生成器均可正常工作，代码模板已更新至框架最新版本（v3.38.7）。
>
> - ✅ **无需修复**: 模板代码使用最新的 fixtures（cleanup、allure_observer）和装饰器（@api_class）
> - ✅ **持续维护**: `init` 和 `gen from-swagger` 功能持续迭代增强
> - ⚠️ **模板性质**: 其他生成器（test、api、builder、repo、graphql、redis）为模板填充工具，生成代码骨架后需手动完善业务逻辑
>
> **未来增强方向**（如有需求）：
> - 数据库 Schema → Repository/Builder 自动生成
> - GraphQL Schema → 强类型客户端自动生成
> - Postman/HAR → 测试用例自动生成

---

## 快速开始

### 前提条件

#### 1. 创建项目（如果还没有）

使用 `df-test init` 命令创建测试项目：

```bash
# 创建 API 测试项目（默认）
df-test init my-project

# 或指定项目类型
df-test init my-project --type api     # API 测试项目
df-test init my-project --type ui      # UI 测试项目（基于 Playwright）
df-test init my-project --type full    # 完整项目（API + UI）
```

#### 2. 确保在项目根目录下运行

代码生成命令需要在项目根目录（包含 `src/` 目录）下执行：

```bash
cd my-project
df-test gen test user_login  # ✅ 正确
```

### 基本用法

```bash
# 查看帮助
df-test gen --help

# 生成测试文件
df-test gen test user_login

# 生成 API 客户端类
df-test gen api user

# 生成 Builder 类
df-test gen builder user

# 生成 Repository 类
df-test gen repo user

# 从 OpenAPI 生成（推荐）
df-test gen from-swagger swagger.json
```

---

## 生成命令详解

### 生成测试文件

#### 命令格式

```bash
df-test gen test <名称> [选项]
```

#### 参数说明

| 参数 | 类型 | 必需 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<名称>` | string | ✅ | 测试名称（如：user_login） | - |
| `--feature` | string | ❌ | Allure feature 名称 | 根据名称生成 |
| `--story` | string | ❌ | Allure story 名称 | 根据名称生成 |
| `--output-dir` | string | ❌ | 输出目录 | `tests/api/` |
| `--template` | string | ❌ | 模板类型：basic/complete | `basic` |
| `--force` | flag | ❌ | 强制覆盖已存在的文件 | `false` |

#### 使用示例

```bash
# 基本用法
df-test gen test user_login

# 指定 Allure 信息
df-test gen test user_login --feature "用户模块" --story "登录功能"

# 指定输出目录
df-test gen test payment_refund --output-dir tests/api/payment/

# 完整模板（包含更多示例）
df-test gen test user_create --template complete
```

#### 生成的文件内容 (v3.38.7)

```python
"""测试文件: user_login

使用 df-test-framework v3.38.7 进行 API 测试。

v3.38.7 最佳实践:
- ✅ allure_observer: 自动记录 HTTP 请求/响应到 Allure 报告
- ✅ cleanup fixture: 配置驱动的数据清理（v3.18.0+）
- ✅ skip_auth/token: 请求级认证控制（v3.19.0+）
- ✅ DataGenerator.test_id(): 生成测试标识符
"""

import pytest
import allure
from df_test_framework import DataGenerator, attach_json, step


@allure.feature("UserLogin")
@allure.story("UserLogin功能")
class TestUserLogin:
    """UserLogin 测试类

    使用 allure_observer fixture 自动记录所有 HTTP 请求到 Allure 报告。
    使用 cleanup fixture 进行配置驱动的数据清理。
    """

    @allure.title("测试user login")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_user_login(self, http_client, cleanup, allure_observer):
        """测试user login

        Fixtures:
        - http_client: HTTP 客户端（自动添加签名/Token）
        - cleanup: 配置驱动的数据清理
        - allure_observer: 自动记录请求/响应到 Allure

        数据清理说明:
        - cleanup.add("type", id): 注册清理项
        - 测试结束后自动清理（除非 --keep-test-data）
        - 需在 config/base.yaml 配置 cleanup.mappings
        """
        with step("准备测试数据"):
            # 使用 DataGenerator 生成测试标识符（推荐）
            order_no = DataGenerator.test_id("TEST_ORD")
            pass

        with step("调用API"):
            # 中间件自动添加签名/Token
            # response = http_client.post("/api/orders", json={"order_no": order_no})
            # cleanup.add("orders", order_no)  # 注册数据清理
            pass

        with step("验证响应"):
            # data = response.json()
            # attach_json(data, name="响应数据")
            # assert data["code"] == 200
            pass

        # ✅ 测试结束后:
        # - allure_observer 已自动记录所有请求/响应
        # - cleanup 自动清理数据（除非 --keep-test-data）
```

---

### 生成 API 客户端类

#### 命令格式

```bash
df-test gen api <API名称> [选项]
```

#### 参数说明

| 参数 | 类型 | 必需 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<API名称>` | string | ✅ | API 名称（如：user） | - |
| `--api-path` | string | ❌ | API 路径前缀 | `<API名称>s` |
| `--output-dir` | string | ❌ | 输出目录 | `src/<project>/apis/` |
| `--force` | flag | ❌ | 强制覆盖 | `false` |

#### 使用示例

```bash
# 基本用法（API 路径为 /api/users）
df-test gen api user

# 指定 API 路径
df-test gen api user --api-path admin/users
```

#### 生成的文件内容 (v3.38.0)

```python
"""API客户端: user

封装 user 相关的 API 调用。

v3.38.0 最佳实践:
- ✅ @api_class 装饰器自动注册 fixture
- ✅ 强类型方法签名（Pydantic Model 参数和返回值）
- ✅ skip_auth/token 请求级认证控制
"""

from typing import Any

from df_test_framework import BaseAPI, HttpClient
from df_test_framework.capabilities.clients.http.rest.httpx import BusinessError
from df_test_framework.testing.decorators import api_class


@api_class("user_api", scope="session")
class UserAPI(BaseAPI):
    """User API 客户端

    封装 user 相关的 HTTP API 调用。

    v3.38.0 特性:
    - @api_class 自动注册为 pytest fixture（user_api）
    - 支持 skip_auth/token 请求级认证控制

    使用方式（在测试中）:
        def test_example(user_api):
            result = user_api.get_user(1)
            assert result["code"] == 200
    """

    def __init__(self, http_client: HttpClient):
        super().__init__(http_client)
        self.base_path = "/api/users"

    def get_user(
        self,
        user_id: int,
        *,
        skip_auth: bool = False,
        token: str | None = None,
    ) -> dict[str, Any]:
        """获取单个 user"""
        response = self.http_client.get(
            f"{self.base_path}/{user_id}",
            skip_auth=skip_auth,
            token=token,
        )
        data = response.json()
        self._check_business_error(data)
        return data

    def list_users(
        self,
        page: int = 1,
        size: int = 10,
        *,
        skip_auth: bool = False,
        token: str | None = None,
    ) -> list[dict[str, Any]]:
        """获取 user 列表"""
        response = self.http_client.get(
            self.base_path,
            params={"page": page, "size": size},
            skip_auth=skip_auth,
            token=token,
        )
        data = response.json()
        self._check_business_error(data)
        return data.get("data", [])

    def create_user(
        self,
        request_data: dict[str, Any],
        *,
        skip_auth: bool = False,
        token: str | None = None,
    ) -> dict[str, Any]:
        """创建 user"""
        response = self.http_client.post(
            self.base_path,
            json=request_data,
            skip_auth=skip_auth,
            token=token,
        )
        data = response.json()
        self._check_business_error(data)
        return data

    def _check_business_error(self, response_data: dict) -> None:
        """检查业务错误"""
        code = response_data.get("code")
        if code != 200:
            message = response_data.get("message", "未知错误")
            raise BusinessError(message=message, code=code, data=response_data)
```

**重要**: 生成的 API 客户端使用 `@api_class` 装饰器自动注册为 pytest fixture，需要在 `conftest.py` 中调用 `load_api_fixtures(globals())` 加载。

---

### 生成 Builder 类

#### 命令格式

```bash
df-test gen builder <实体名称> [选项]
```

#### 使用示例

```bash
df-test gen builder user
df-test gen builder order
```

#### 生成的文件内容

```python
"""Builder: user

使用Builder模式构建user测试数据。
"""

from df_test_framework import DictBuilder


class UserBuilder(DictBuilder):
    """User数据构建器

    使用链式调用构建user数据。

    Example:
        >>> builder = UserBuilder()
        >>> data = (
        ...     builder
        ...     .with_name("示例名称")
        ...     .with_status("active")
        ...     .build()
        ... )
    """

    def __init__(self):
        super().__init__()
        self._data = {
            "name": "user_default",
            "status": "active",
            "created_at": None,
            "updated_at": None,
        }

    def with_name(self, name: str) -> "UserBuilder":
        """设置名称"""
        self._data["name"] = name
        return self

    def with_status(self, status: str) -> "UserBuilder":
        """设置状态"""
        self._data["status"] = status
        return self

    # TODO: 添加更多字段的设置方法
```

---

### 生成 Repository 类

#### 命令格式

```bash
df-test gen repo <实体名称> [选项]
```

#### 参数说明

| 参数 | 类型 | 必需 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<实体名称>` | string | ✅ | 实体名称（如：user） | - |
| `--table-name` | string | ❌ | 数据库表名 | `<实体名称>s` |
| `--output-dir` | string | ❌ | 输出目录 | `src/<project>/repositories/` |
| `--force` | flag | ❌ | 强制覆盖 | `false` |

#### 使用示例

```bash
# 基本用法（表名默认为 users）
df-test gen repo user

# 指定表名
df-test gen repo user --table-name sys_user
```

#### 生成的文件内容 (v3.8.0+)

```python
"""Repository: user

使用Repository模式封装user的数据库操作。

v3.8.0+ 特性：
- ✅ 接收 Session 而非 Database
- ✅ 配合 UnitOfWork 使用
- ✅ 支持自动事务管理和回滚
"""

from typing import Any
from sqlalchemy.orm import Session
from df_test_framework import BaseRepository


class UserRepository(BaseRepository):
    """User数据仓库

    封装user的数据库CRUD操作。

    v3.8.0+ 变更：
    - 🔴 构造函数接收 Session 而非 Database
    - ✅ 与 UnitOfWork 配合使用
    - ✅ 支持自动回滚

    使用示例：
        >>> with uow:
        ...     repo = uow.repository(UserRepository)
        ...     item = repo.find_by_id(1)
        ...     new_id = repo.create({"name": "test"})
        ...     uow.commit()
    """

    def __init__(self, session: Session):
        super().__init__(session, table_name="users")

    def find_by_name(self, name: str) -> dict[str, Any] | None:
        """根据名称查询"""
        return self.find_one({"name": name})

    def find_by_status(self, status: str) -> list[dict[str, Any]]:
        """根据状态查询"""
        return self.find_all({"status": status})

    # TODO: 添加更多业务查询方法
```

---

### 从 JSON 生成模型

#### 命令格式

```bash
df-test gen models <json_file> [选项]
```

#### 使用示例

```bash
# 从 JSON 文件生成模型
df-test gen models response.json --name UserResponse
```

#### 说明

从真实 API 响应的 JSON 文件自动推断字段类型，生成 Pydantic 模型。

---

### 生成 GraphQL 相关

```bash
# 生成 GraphQL 客户端模板
df-test gen graphql-client

# 生成 GraphQL 测试示例
df-test gen graphql-test
```

**注意**: 这些是基础模板，不会解析 GraphQL Schema。

---

### 生成 Redis Fixture

```bash
# 生成 Redis fixture 和测试示例
df-test gen redis-fixture
```

---

### 从 OpenAPI 生成

**这是最推荐的方式**，能够自动生成完整的测试代码。

#### 命令格式

```bash
df-test gen from-swagger <规范文件> [选项]

# 命令别名（以下方式均可）:
# df-test gen from-swagger ...
# df-test gen swagger ...
# df-test gen openapi ...
```

#### 参数说明

| 参数 | 类型 | 必需 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<规范文件>` | string | ✅ | Swagger/OpenAPI 文件路径或 URL | - |
| `--tags` | string | ❌ | 过滤的 API 标签（支持逗号或空格分隔） | 全部 |
| `--output` | string | ❌ | 输出目录 | 当前目录 |
| `--force` | flag | ❌ | 更新已存在文件（保留用户扩展） | `false` |
| `--no-merge` | flag | ❌ | 与 --force 配合，完全覆盖 | `false` |

#### 使用示例

```bash
# 从 Swagger 文件生成
df-test gen from-swagger swagger.json

# 指定多个标签（v3.41.0+ 支持逗号分隔）
df-test gen from-swagger swagger.json --tags user-controller,order-controller

# 更新已存在文件（保留用户扩展代码）
df-test gen from-swagger swagger.json --force

# 完全覆盖（不保留用户修改）
df-test gen from-swagger swagger.json --force --no-merge
```

#### v3.41.0 智能生成特性

| 特性 | 说明 |
|------|------|
| **智能请求示例** | 自动识别分页/排序字段，生成有意义的默认值 |
| **前置查询自动生成** | 详情/更新/删除接口自动获取有效 ID |
| **中文测试标题** | 根据 operationId 智能生成中文标题 |
| **智能 pytest.mark** | 根据操作类型自动区分 smoke/regression/e2e |
| **E2E 和负向测试** | 自动生成完整 CRUD 流程和边界条件测试 |

> 📖 **详细文档**: [OpenAPI 代码生成器使用指南](../guides/openapi_guide.md)

---

## 实战示例

### 场景1: 有 Swagger 文档（推荐）

```bash
# 一键生成完整代码
df-test gen from-swagger https://api.example.com/swagger.json

# 生成的文件：
# - src/my_project/apis/user_api.py
# - src/my_project/models/requests/user.py
# - src/my_project/models/responses/user.py
# - tests/api/test_user_api.py
```

### 场景2: 无 Swagger，手动开发

```bash
# 1. 生成用户相关代码骨架
df-test gen api user --api-path users
df-test gen builder user
df-test gen repo user --table-name sys_user
df-test gen test user_create --feature "用户管理" --story "创建用户"

# 2. 手动完善生成的代码
vim src/my_project/apis/user_api.py
vim tests/api/test_user_create.py
```

### 场景3: 从 JSON 响应生成模型

```bash
# 1. 保存 API 响应到文件
curl https://api.example.com/users/1 > response.json

# 2. 生成 Pydantic 模型
df-test gen models response.json --name UserResponse
```

---

## 最佳实践

### 1. 优先使用 OpenAPI 生成

如果后端提供 Swagger 文档，优先使用 `df-test gen from-swagger`：

```bash
# ✅ 推荐：自动生成完整代码
df-test gen from-swagger swagger.json

# ⚠️ 备选：手动生成模板
df-test gen test user_login
```

### 2. 命名规范

```bash
# ✅ 好的命名（使用下划线分隔）
df-test gen test user_login
df-test gen api user
df-test gen builder order

# ❌ 不好的命名
df-test gen test UserLogin    # 避免驼峰命名
df-test gen api users         # 避免复数
```

### 3. 配置 conftest.py

生成的 API 客户端使用 `@api_class` 装饰器，需要在 `conftest.py` 中加载：

```python
# conftest.py
from df_test_framework.testing.decorators import load_api_fixtures

# 导入 API 类（触发 @api_class 装饰器注册）
from my_project.apis.user_api import UserAPI  # noqa: F401

# 加载所有已注册的 API fixtures
load_api_fixtures(globals())
```

### 4. 使用 cleanup 而非 db_transaction

v3.18.0+ 推荐使用配置驱动的 `cleanup` fixture：

```python
# ✅ v3.18.0+ 推荐
def test_create_user(http_client, cleanup):
    user_id = DataGenerator.test_id("TEST_USER")
    response = http_client.post("/api/users", json={"id": user_id})
    cleanup.add("users", user_id)  # 配置驱动清理
```

---

## 常见问题

### Q1: 生成代码时提示"无法检测项目名称"？

确保在项目根目录下运行，且存在 `src/<project_name>/` 目录结构。

### Q2: 如何选择使用哪个生成器？

- **有 Swagger 文档** → `df-test gen from-swagger`
- **无 Swagger，需要完整 API 客户端** → `df-test gen api` + 手动完善
- **只需要测试骨架** → `df-test gen test`

### Q3: 生成的 API 客户端在测试中找不到？

确保：
1. API 类使用了 `@api_class` 装饰器
2. 在 `conftest.py` 中导入了 API 类
3. 调用了 `load_api_fixtures(globals())`

### Q4: 如何更新已生成的代码？

```bash
# 保留用户扩展代码
df-test gen from-swagger swagger.json --force

# 完全覆盖
df-test gen from-swagger swagger.json --force --no-merge
```

---

## 相关资源

- **📖 OpenAPI 生成器**: [OpenAPI 代码生成器使用指南](../guides/openapi_guide.md)
- **📖 脚手架 CLI**: [脚手架 CLI 工具指南](../guides/scaffold_cli_guide.md)
- **📚 API 参考**: [Testing API 参考](../api-reference/testing.md)
- **📚 模式文档**: [Builder & Repository 模式](../api-reference/patterns.md)

---

**文档版本**: v3.41.0
**最后更新**: 2025-12-31
**维护者**: DF Test Framework Team
