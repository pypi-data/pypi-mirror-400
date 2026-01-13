# 脚手架 CLI 工具指南

> **版本**: v3.39.0 | **更新**: 2025-12-30

本指南介绍 df-test-framework 提供的 CLI 工具，用于快速创建测试项目和生成测试代码。

## 概述

df-test-framework 提供了 `df-test` CLI 工具，支持：

- **项目初始化** - 创建完整的测试项目结构
- **代码生成** - 生成测试、API 客户端、模型等
- **CI/CD 配置** - 生成 GitHub Actions、GitLab CI 等配置
- **环境管理** - 管理测试环境配置

## 安装

```bash
# 安装框架后自动可用
pip install df-test-framework

# 或使用 uv
uv add df-test-framework
```

## 命令概览

```bash
# 查看帮助
uv run df-test --help

# 可用命令
df-test init      # 初始化测试项目
df-test generate  # 生成测试代码
df-test env       # 环境管理
```

---

## 项目初始化 (init)

### 基本用法

```bash
# 在当前目录初始化 API 测试项目
uv run df-test init .

# 在指定目录初始化
uv run df-test init my_test_project

# 指定项目类型
uv run df-test init . --type api     # API 测试项目（默认）
uv run df-test init . --type ui      # UI 测试项目
uv run df-test init . --type full    # 完整项目（API + UI）
```

### 命令选项

```bash
uv run df-test init <path> [OPTIONS]

参数:
  path                项目路径

选项:
  --type, -t          项目类型: api, ui, full（默认: api）
  --ci                CI/CD 平台: github-actions, gitlab-ci, jenkins, none
  --force, -f         强制覆盖已存在的文件
```

### 生成的项目结构

#### API 测试项目 (--type api)

```
my_project/
├── .vscode/
│   ├── settings.json        # VSCode 配置
│   └── extensions.json      # 推荐扩展
├── config/
│   ├── base.yaml            # 基础配置
│   └── environments/
│       ├── local.yaml       # 本地环境
│       ├── dev.yaml         # 开发环境
│       ├── test.yaml        # 测试环境
│       ├── staging.yaml     # 预发布环境
│       └── prod.yaml        # 生产环境
├── src/{project_name}/
│   ├── __init__.py
│   ├── apis/
│   │   ├── __init__.py
│   │   └── base_api.py      # 基础 API 类
│   ├── models/
│   │   └── __init__.py
│   ├── fixtures/
│   │   └── __init__.py
│   ├── constants/
│   │   └── error_codes.py   # 错误码常量
│   └── utils/
│       ├── converters.py    # 数据转换工具
│       └── validators.py    # 验证工具
├── tests/
│   ├── conftest.py          # pytest 配置
│   └── api/
│       └── test_example.py  # 示例测试
├── docs/
│   └── api.md               # API 文档
├── scripts/
│   └── run_tests.sh         # 测试脚本
├── .editorconfig            # 编辑器配置
├── .gitattributes           # Git 属性
├── .gitignore               # Git 忽略
├── pyproject.toml           # 项目配置
└── README.md                # 项目说明
```

#### UI 测试项目 (--type ui)

```
my_project/
├── src/{project_name}/
│   ├── pages/
│   │   ├── __init__.py
│   │   └── base_page.py     # 基础页面类
│   └── fixtures/
│       └── __init__.py      # UI fixtures
├── tests/
│   ├── conftest.py          # UI 测试配置
│   └── ui/
│       └── test_example.py  # UI 示例测试
└── ...
```

#### 完整项目 (--type full)

包含 API 和 UI 两种测试类型的完整结构。

### CI/CD 配置

```bash
# 生成 GitHub Actions 配置
uv run df-test init . --ci github-actions

# 生成 GitLab CI 配置
uv run df-test init . --ci gitlab-ci

# 生成 Jenkins Pipeline
uv run df-test init . --ci jenkins
```

---

## 代码生成 (generate)

### 生成测试文件

```bash
# 基础测试模板
uv run df-test generate test user_login

# 指定 Allure 标签
uv run df-test generate test user_login --feature "用户模块" --story "登录功能"

# 完整测试模板（包含更多示例代码）
uv run df-test generate test user_create --template complete

# 指定 API 路径
uv run df-test generate test user_create --api-path users
```

### 生成 API 客户端

```bash
# 生成 API 客户端类
uv run df-test generate api-client user

# 指定基础路径
uv run df-test generate api-client user --base-path /api/v1/users
```

### 生成 GraphQL 客户端

```bash
# 生成 GraphQL 客户端
uv run df-test generate graphql-client user

# 生成 GraphQL 测试示例
uv run df-test generate graphql-test user
```

### 生成 Redis Fixture

```bash
# 生成 Redis fixture 和测试示例
uv run df-test generate redis-fixture
uv run df-test generate redis-test
```

### 生成 Pydantic 模型

```bash
# 从 JSON 示例生成模型
uv run df-test generate model UserResponse --json '{"id": 1, "name": "Alice"}'

# 从文件生成
uv run df-test generate model UserResponse --file response.json
```

### 从 OpenAPI 生成

```bash
# 生成完整的测试代码
uv run df-test generate openapi swagger.json

# 只生成模型
uv run df-test generate openapi swagger.json --models-only

# 过滤指定标签
uv run df-test generate openapi swagger.json --tags user,order

# 增量合并（v3.39.0+）- 保留用户自定义代码
uv run df-test generate openapi swagger.json --merge
```

详细用法请参考 [OpenAPI 代码生成器使用指南](openapi_guide.md)。

### 生成 Repository

```bash
# 生成数据库 Repository
uv run df-test generate repository User --table users
```

### 生成 Builder

```bash
# 生成测试数据 Builder
uv run df-test generate builder User
```

---

## 环境管理 (env)

### 查看环境配置

```bash
# 列出所有环境
uv run df-test env list

# 查看当前环境
uv run df-test env show

# 查看指定环境配置
uv run df-test env show --env dev
```

### 生成环境文件

```bash
# 生成环境配置文件
uv run df-test env init

# 生成增强版配置（包含更多选项）
uv run df-test env init --enhanced
```

---

## 配置文件说明

### YAML 分层配置

v3.38.0 推荐使用 YAML 分层配置：

```yaml
# config/base.yaml - 基础配置
http:
  timeout: 30
  verify_ssl: true

database:
  pool_size: 5

# config/environments/dev.yaml - 开发环境
_extends: base  # 继承基础配置

http:
  base_url: "https://dev-api.example.com"

database:
  host: "dev-db.example.com"
```

### 环境继承

```yaml
# config/environments/staging.yaml
_extends: dev  # 继承开发环境配置

http:
  base_url: "https://staging-api.example.com"
```

### pyproject.toml

生成的 `pyproject.toml` 包含：

```toml
[project]
name = "my-test-project"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "df-test-framework>=3.38.0",
]

[tool.pytest]
minversion = "9.0"
testpaths = ["tests"]
timeout = "30"
asyncio_mode = "auto"
addopts = ["-v", "--strict-markers", "--tb=short"]

[tool.ruff]
line-length = 100
target-version = "py312"
```

---

## 生成的文件详解

### conftest.py

**v3.38.0+ 核心 fixtures 自动注册**：

从 v3.37.0 开始，框架使用 pytest11 Entry Points 自动注册核心 fixtures（如 `settings`、`http_client`、`database`、`redis_client`、`cleanup`、`allure_observer` 等），无需手动定义。

```python
"""pytest 配置文件

v3.38.0+：核心 fixtures 已通过 pytest11 Entry Points 自动注册
不再需要手动定义 settings、http_client 等基础 fixtures
"""
from df_test_framework.testing.decorators import load_api_fixtures

# 导入 API 类（触发 @api_class 装饰器注册）
# from my_project.apis.user_api import UserAPI  # noqa: F401

# 加载所有已注册的 API fixtures
load_api_fixtures(globals())


# ✅ 核心 fixtures 自动可用（无需手动定义）：
# - settings: 框架配置
# - http_client: HTTP 客户端
# - database: 数据库连接
# - redis_client: Redis 客户端
# - cleanup: 配置驱动数据清理
# - allure_observer: Allure 报告自动记录

# ℹ️ 你只需定义项目特定的自定义 fixtures
```

### base_api.py

```python
"""基础 API 类"""
from df_test_framework import BaseAPI, HttpClient
from df_test_framework.testing.decorators import api_class


class ProjectBaseAPI(BaseAPI):
    """项目基础 API 类

    所有 API 客户端应继承此类。
    """

    def __init__(self, http_client: HttpClient):
        super().__init__(http_client)

    def handle_response(self, response):
        """统一响应处理"""
        data = response.json()
        if data.get("code") != 200:
            raise BusinessError(
                code=data.get("code"),
                message=data.get("message"),
            )
        return data
```

### test_example.py

**v3.38.0+ 最佳实践示例**：

```python
"""示例测试文件 - v3.38.0

展示框架最新特性：
- allure_observer: 自动记录 HTTP 请求/响应到 Allure 报告
- cleanup: 配置驱动的数据清理
- skip_auth/token: 请求级别认证控制
- DataGenerator: 测试数据生成器
"""
import pytest
import allure
from assertpy import assert_that
from df_test_framework import step, DataGenerator


@allure.feature("用户管理")
class TestUserAPI:
    """用户 API 测试"""

    @allure.title("创建用户并自动清理")
    @allure.story("用户注册")
    @pytest.mark.smoke
    def test_create_user_with_cleanup(self, http_client, cleanup, allure_observer):
        """测试用户创建 - 演示自动清理和 Allure 集成

        Args:
            http_client: HTTP 客户端（自动注册）
            cleanup: 数据清理管理器（自动注册）
            allure_observer: Allure 观察者（自动记录请求/响应）
        """
        # 生成测试标识符
        user_id = DataGenerator.test_id("TEST_USER")

        with step("创建测试用户"):
            response = http_client.post("/api/users", json={
                "id": user_id,
                "name": "测试用户",
                "email": f"{user_id}@example.com",
            })

        with step("验证创建成功"):
            assert_that(response.status_code).is_equal_to(201)
            user = response.json()
            assert_that(user["id"]).is_equal_to(user_id)

        # 注册清理（测试结束后自动删除）
        cleanup.add("users", user_id)
        # ✅ allure_observer 自动记录了请求/响应详情

    @allure.title("跳过认证的公开接口")
    @allure.story("健康检查")
    def test_public_endpoint(self, http_client):
        """测试公开接口 - 演示 skip_auth 参数"""
        with step("调用公开接口（跳过认证）"):
            response = http_client.get("/api/health", skip_auth=True)

        with step("验证响应"):
            assert_that(response.status_code).is_equal_to(200)
            assert_that(response.json()["status"]).is_equal_to("ok")

    @allure.title("使用自定义 token")
    @allure.story("管理员操作")
    def test_with_custom_token(self, http_client):
        """测试管理员接口 - 演示自定义 token"""
        admin_token = "admin-secret-token"

        with step("调用管理员接口"):
            response = http_client.get("/api/admin/stats", token=admin_token)

        with step("验证响应"):
            assert_that(response.status_code).is_equal_to(200)
```

**新特性说明**：

1. **allure_observer** (v3.17.0+)
   - 自动订阅 EventBus，记录所有 HTTP 请求/响应
   - 包含 trace_id、span_id、correlation_id
   - 无需手动调用 `allure.attach()`

2. **cleanup** (v3.18.0+)
   - 配置驱动的数据清理（`config/base.yaml` 中定义 mappings）
   - 测试结束后自动清理，除非使用 `--keep-test-data`
   - 支持数据库、API、文件等多种清理方式

3. **skip_auth / token** (v3.19.0+)
   - 请求级别的认证控制
   - `skip_auth=True` 跳过全局认证中间件
   - `token="xxx"` 使用自定义 token 覆盖全局配置

4. **DataGenerator.test_id()** (v3.11.1+)
   - 生成唯一测试标识符
   - 格式：`{prefix}_{timestamp}_{random}`
   - 自动清理时作为唯一标识符
```

---

## 最佳实践

### 1. 项目结构

```
my_project/
├── src/{project_name}/
│   ├── apis/          # API 客户端
│   ├── models/        # 数据模型
│   │   ├── requests/  # 请求模型
│   │   └── responses/ # 响应模型
│   ├── fixtures/      # 自定义 fixtures
│   └── utils/         # 工具函数
├── tests/
│   ├── api/           # API 测试
│   ├── ui/            # UI 测试
│   └── integration/   # 集成测试
└── config/            # 配置文件
```

### 2. 命名规范

| 类型 | 命名规范 | 示例 |
|------|----------|------|
| API 客户端 | `{Entity}API` | `UserAPI` |
| 请求模型 | `{Action}{Entity}Request` | `CreateUserRequest` |
| 响应模型 | `{Action}{Entity}Response` | `CreateUserResponse` |
| 测试文件 | `test_{entity}_{feature}.py` | `test_user_login.py` |
| 测试类 | `Test{Entity}{Feature}` | `TestUserLogin` |

### 3. 使用 @api_class 装饰器

```python
from df_test_framework.testing.decorators import api_class

@api_class("user_api", scope="function")
class UserAPI(BaseAPI):
    """自动注册为 user_api fixture"""
    pass
```

### 4. 配置环境切换

```bash
# 使用不同环境运行测试
uv run pytest --env=dev      # 开发环境
uv run pytest --env=test     # 测试环境
uv run pytest --env=staging  # 预发布环境
```

---

## 常见问题

### Q: 如何更新已存在的文件？

**OpenAPI 生成的代码（v3.39.0+）**：使用 `--merge` 选项保留用户自定义代码：

```bash
uv run df-test generate openapi swagger.json --merge
```

**项目初始化**：使用 `--force` 选项强制覆盖：

```bash
uv run df-test init . --force
```

### Q: 什么是增量合并？

v3.39.0 新增的增量合并功能允许你在重新生成代码时保留自定义扩展：

```python
# ========== AUTO-GENERATED START ==========
# 此区域会被更新

class UserAPI(BaseAPI):
    ...

# ========== AUTO-GENERATED END ==========


# ========== USER EXTENSIONS ==========
# 此区域在 --merge 模式下会被保留

def my_custom_function():
    """你的自定义代码不会被覆盖"""
    pass
```

### Q: 如何只生成特定文件？

目前不支持单独生成特定文件。建议：
1. 先初始化完整项目
2. 删除不需要的文件
3. 或使用 `generate` 命令生成特定类型的代码

### Q: 如何自定义模板？

目前不支持自定义模板。可以：
1. 生成后手动修改（建议放在 `USER EXTENSIONS` 区域）
2. 创建自己的基类继承生成的代码

## 相关文档

- [OpenAPI 代码生成器使用指南](openapi_guide.md)
- [v3.39.0 发布说明](../releases/v3.39.0.md) - 增量合并功能
- [v3.38.0 发布说明](../releases/v3.38.0.md)
- [环境配置指南](env_config_guide.md)
- [测试数据生成指南](test_data.md)
