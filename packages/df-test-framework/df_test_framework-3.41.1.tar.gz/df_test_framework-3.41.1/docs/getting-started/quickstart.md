# 5 分钟快速上手

本指南演示如何在 5 分钟内创建一个全新的 DF Test Framework 项目、运行示例测试，并体验 v3 核心能力。

---

## 📝 前提条件

- Python **3.10+**
- 已安装框架（参见 [安装指南](installation.md)）
- 命令行能执行 `df-test --help`

---

## 🚀 生成标准项目骨架

```bash
# 创建默认的 API 测试项目
df-test init my-first-project

# 其他类型
# df-test init my-first-project --type ui    # Playwright UI 项目
# df-test init my-first-project --type full  # API + UI 混合项目

cd my-first-project
```

目录结构（API 项目示例）：
```
my-first-project/
├── src/my_first_project/        # 业务代码
│   ├── apis/                    # API 封装（继承 BaseAPI）
│   ├── config/                  # FrameworkSettings 定制
│   ├── fixtures/                # 自定义 fixtures
│   └── ...
├── tests/                       # 示例测试（API、conftest.py）
├── config/                      # v3.35.0+ YAML 分层配置
│   ├── base.yaml                # 基础配置
│   ├── environments/            # 环境配置
│   │   ├── dev.yaml
│   │   ├── test.yaml
│   │   ├── staging.yaml
│   │   └── local.yaml.example
│   └── secrets/                 # 敏感信息
│       └── .env.local.example
├── docs/                        # 项目文档模板
├── reports/                     # Allure / 日志输出目录
├── scripts/                     # 实用脚本（run_tests.sh 等）
└── pyproject.toml               # v3.37.0+ pytest 9.0 原生 TOML 配置
```

> ✅ 脚手架已预置：Allure 集成、`cleanup` 配置驱动清理、请求/响应示例、常量与工具函数模板。

---

## ⚙️ 配置基础环境（v3.35.0+ YAML 配置）

```bash
# 复制本地配置模板
cp config/environments/local.yaml.example config/environments/local.yaml
cp config/secrets/.env.local.example config/secrets/.env.local
```

编辑 `config/environments/local.yaml`，至少指定后端地址：
```yaml
# 继承 test 环境配置
_extends: test

# 覆盖 HTTP 配置
http:
  base_url: https://jsonplaceholder.typicode.com
  timeout: 30

# 本地调试启用
observability:
  debug_output: true
```

敏感信息放在 `config/secrets/.env.local`：
```bash
# 签名密钥
SIGNATURE__SECRET=your_secret_key

# 数据库密码
DB__PASSWORD=your_password
```

**配置优先级**（从高到低）：
1. `config/environments/local.yaml`（不提交 git）
2. `config/environments/{env}.yaml`（dev/test/staging/prod）
3. `config/base.yaml`（基础配置）

如需扩展配置，可修改 `src/my_first_project/config/settings.py` 中的 `MyFirstProjectSettings`。

详见：[环境配置指南](../user-guide/env-config.md)

---

## ▶️ 运行示例测试

```bash
pytest -v
```

期望输出：
```
tests/api/test_example.py::TestExample::test_framework_init PASSED
tests/api/test_example.py::TestExample::test_http_client PASSED
```

恭喜！框架已完成初始化并能运行示例用例。

---

## ✍️ 编写第一个 API 测试

示例：验证用户详情接口（`tests/api/test_example.py`）。

```python
import pytest
import allure
from df_test_framework import step

@allure.feature("用户模块")
@allure.story("用户详情")
@pytest.mark.smoke
def test_get_user(http_client, allure_observer):
    """http_client fixture 来自框架的 core fixtures

    allure_observer 会自动记录所有 HTTP 请求/响应到 Allure 报告
    """

    with step("请求用户详情"):
        response = http_client.get("/users/1")

    with step("断言响应"):
        assert response.status_code == 200
        user = response.json()
        assert user["id"] == 1
        assert "name" in user
```

运行指定用例：
```bash
pytest tests/api/test_example.py::test_get_user -v
```

> ℹ️ `HttpClient` 默认开启 **自动重试**（5xx、超时会指数退避重试）与 **敏感信息脱敏日志**，可通过 `FrameworkSettings.http` 配置超时、重试次数等参数。

---

## ♻️ 使用 `cleanup` 配置驱动清理（v3.18.0+）

框架提供配置驱动的数据清理机制，测试结束后自动清理数据。

**步骤 1：配置清理映射** (`config/base.yaml`)

```yaml
cleanup:
  enabled: true
  mappings:
    users:
      table: user_table
      field: user_id
    orders:
      table: order_table
      field: order_no
```

**步骤 2：在测试中使用**

```python
from df_test_framework import DataGenerator

def test_create_and_verify_user(http_client, cleanup, database):
    # 生成测试标识符
    user_id = DataGenerator.test_id("TEST_USER")

    # 创建用户
    response = http_client.post("/users", json={
        "id": user_id,
        "name": "测试用户",
        "email": "tester@example.com",
    })
    assert response.status_code == 201

    # 注册清理（测试结束后自动删除）
    cleanup.add("users", user_id)

    # 数据库验证
    result = database.execute("SELECT * FROM user_table WHERE user_id = %s", (user_id,))
    user = result.fetchone()
    assert user is not None
    assert user["name"] == "测试用户"

    # ✅ 测试结束后 cleanup 自动清理数据（除非 --keep-test-data）
```

**保留测试数据**（调试用）：

```bash
pytest tests/ --keep-test-data  # 跳过数据清理
```

> 延伸阅读：[测试数据清理指南](../guides/test_data_cleanup.md) / [Testing API 文档](../api-reference/testing.md)。

---

## 🧱 扩展 Repository 与 Builder

使用 CLI 可快速生成常见模式样板：
```bash
df-test gen repo user          # 生成 Repository 类
df-test gen builder user       # 生成 Builder 类
df-test gen test user_login    # 生成测试文件
```

生成的文件会放置在 `src/<project>/repositories/`、`src/<project>/builders/` 等目录，可在测试中直接引用：
```python
from my_first_project.builders import UserBuilder

def test_create_user_with_builder(http_client):
    payload = UserBuilder().with_name("张三").with_age(30).build()
    response = http_client.post("/users", json=payload)
    assert response.status_code == 201
```

更多最佳实践：[用户指南 · Builder & Repository](../user-guide/BEST_PRACTICES.md#5-测试数据管理最佳实践)。 

---

## 🧠 封装业务 API 并执行业务校验

使用 `BaseAPI` 可以为业务接口提供统一的请求封装和业务错误检查：

```python
from df_test_framework import BaseAPI, BusinessError

class UserAPI(BaseAPI):
    """用户服务 API 封装"""

    def _check_business_error(self, data: dict) -> None:
        # 统一检查返回中的 success / code 字段
        if not data.get("success", True):
            raise BusinessError(
                message=data.get("message", "未知错误"),
                code=data.get("code"),
                data=data,
            )

    def get_user(self, user_id: int) -> dict:
        return self.get(f"/users/{user_id}")
```

在测试中使用：
```python
@pytest.fixture
def user_api(http_client):
    return UserAPI(http_client)

def test_business_error_check(user_api):
    with pytest.raises(BusinessError):
        user_api.get_user(-1)
```

这样可以把业务校验统一放在 API 层，测试逻辑更简洁。

---

## 🔍 启用 HTTP/DB 调试

框架内置 `HTTPDebugger` 和 `DBDebugger`，可通过 fixture 或临时开关启用：

```python
from df_test_framework.testing.debug import enable_http_debug

def test_with_debug(http_client):
    debugger = enable_http_debug()
    response = http_client.get("/users/1")
    assert response.status_code == 200
    debugger.print_summary()
```

或在测试中直接引用脚手架提供的 `http_debugger`、`db_debugger` fixture。

---

## 📂 常见文件速查

| 位置 | 作用 |
|------|------|
| `src/<project>/config/settings.py` | 项目级 FrameworkSettings |
| `src/<project>/fixtures/__init__.py` | 将自定义 fixtures 暴露给测试 |
| `src/<project>/fixtures/data_cleaners.py` | `db_transaction` Fixture |
| `src/<project>/apis/` | 业务 API 封装（继承 BaseAPI） |
| `tests/conftest.py` | 注册框架 fixtures、插件 |
| `scripts/run_tests.sh` | 示例测试脚本 |

---

## 📈 下一步建议

1. [30 分钟教程](tutorial.md) — 深入了解项目结构与扩展能力  
2. [用户手册](../user-guide/USER_MANUAL.md) — Fixtures、调试器、扩展系统详解  
3. [最佳实践](../user-guide/BEST_PRACTICES.md) — 测试组织、数据管理、项目规范  
4. [API 参考](../api-reference/README.md) — 查看各能力层的导入与用法  
5. [架构总览](../architecture/overview.md) — 理解 v3 五层架构与能力层划分  

---

## ❓ 常见问题

### 如何配置数据库连接？

在 `.env` 中设置连接信息：
```ini
DB_HOST=localhost
DB_PORT=3306
DB_NAME=test_db
DB_USER=root
DB_PASSWORD=secret
```
框架会自动将其加载到 `FrameworkSettings.db`。

### 可以自定义配置字段吗？

可以，修改项目中的 `MyFirstProjectSettings`：
```python
from df_test_framework import FrameworkSettings
from pydantic import Field

class MyFirstProjectSettings(FrameworkSettings):
    admin_token: str = Field(default="")
    report_bucket: str | None = None
```

### 如何查看 HTTP/SQL 调试信息？

在测试中启用调试 fixtures：
```python
def test_debug_sample(http_client, http_debugger, db_debugger):
    response = http_client.get("/users/1")
    assert response.status_code == 200
```
更多说明见 [调试指南](../troubleshooting/debugging-guide.md)。

### 脚手架生成的文件可以改吗？

可以。脚手架提供的是推荐起点，你可以自由修改 API 封装、fixtures、目录结构，只需保持 pytest 能正常发现 fixtures 与测试即可。

---

## 🔗 参考资料

- [安装指南](installation.md)
- [用户手册](../user-guide/USER_MANUAL.md)
- [API 参考](../api-reference/README.md)
- [示例代码](../../examples/README.md)
- [GitHub 仓库](https://github.com/yourorg/test-framework)

---

返回：[快速开始首页](README.md) · [文档首页](../README.md)
