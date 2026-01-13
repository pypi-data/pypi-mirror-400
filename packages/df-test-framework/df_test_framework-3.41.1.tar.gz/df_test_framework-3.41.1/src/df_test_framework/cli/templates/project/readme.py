"""README模板

v3.38.6: 更新配置格式（移除 APP_ 前缀）、添加本地调试说明

提供三种类型的 README 模板：
- README_API_TEMPLATE: API 测试项目
- README_UI_TEMPLATE: UI 测试项目
- README_FULL_TEMPLATE: 完整项目（API + UI）
"""

README_API_TEMPLATE = """# {ProjectName}

{ProjectName} 的 API 自动化测试项目，基于 df-test-framework 构建。

## 覆盖系统

| 系统 | 说明 | 测试目录 |
|------|------|----------|
| API | 核心 API 接口测试 | `tests/api/` |

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e .
```

### 2. 配置环境

```bash
# 复制配置文件
cp config/environments/local.yaml.example config/environments/local.yaml
cp config/secrets/.env.local.example config/secrets/.env.local

# 编辑配置文件，填写 API 地址、数据库配置等
# - local.yaml: 通用配置
# - .env.local: 敏感信息（密码、密钥等）
```

### 3. 运行测试

```bash
# 运行所有测试
uv run pytest tests/ -v

# 运行冒烟测试
uv run pytest -m smoke -v

# 生成 Allure 报告
uv run pytest tests/ --alluredir=reports/allure-results
allure serve reports/allure-results
```

## 项目结构

```
{project_name}/
├── src/{project_name}/
│   ├── apis/                    # API 客户端封装
│   ├── models/                  # Pydantic 数据模型
│   │   ├── requests/            # 请求模型
│   │   └── responses/           # 响应模型
│   ├── repositories/            # 数据库仓储层
│   ├── builders/                # 测试数据构建器
│   ├── fixtures/                # 项目 Fixtures
│   └── config/settings.py       # 配置（含中间件）
├── tests/
│   ├── api/                     # API 测试
│   └── conftest.py              # Fixtures 定义
├── .env                         # 环境配置
└── pyproject.toml               # 项目配置（含 pytest）
```

## 编写测试

### 核心 Fixtures

| Fixture | 说明 |
|---------|------|
| `http_client` | HTTP 客户端（自动签名/Token） |
| `uow` | Unit of Work（数据库操作，自动回滚） |
| `settings` | 配置对象 |
| `cleanup` | 配置驱动的数据清理（v3.18.0+） |

### 数据清理机制

测试数据有两种来源，清理方式不同：

#### 1. Repository 直接创建的数据

通过 `uow` 直接操作数据库创建的数据，**自动回滚**：

```python
def test_example(uow):
    # 直接通过 Repository 创建
    uow.users.create({{"name": "test_user", ...}})
    # ✅ 测试结束后自动回滚，无需手动清理
```

#### 2. API 创建的数据（重要）

通过 API 调用创建的数据由后端事务提交，**需要显式清理**：

```python
from df_test_framework import DataGenerator

def test_example(http_client, cleanup):
    # 生成测试订单号
    order_no = DataGenerator.test_id("TEST_ORD")

    # 通过 API 创建数据
    response = http_client.post("/orders", json={{"order_no": order_no}})
    assert response.status_code == 200

    # ✅ 记录订单号，测试结束后自动清理
    cleanup.add("orders", order_no)
```

### 示例测试

```python
import allure
import pytest
from df_test_framework import DataGenerator
from df_test_framework import attach_json, step


@allure.feature("订单管理")
@allure.story("创建订单")
class TestOrderCreate:

    @allure.title("创建订单-成功")
    @pytest.mark.smoke
    def test_create_order_success(self, http_client, settings, cleanup):
        \"\"\"测试创建订单\"\"\"

        with step("准备测试数据"):
            order_no = DataGenerator.test_id("TEST_ORD")
            request_data = {{
                "order_no": order_no,
                "user_id": "test_user_001",
                "amount": 100.00
            }}
            attach_json(request_data, name="请求数据")

        with step("调用创建订单 API"):
            response = http_client.post("/orders", json=request_data)
            attach_json(response.json(), name="响应数据")

        with step("验证响应"):
            assert response.status_code == 200
            assert response.json()["code"] == 200

        # 记录需要清理的订单号
        cleanup.add("orders", order_no)
```

## 运行测试

### 常用命令

```bash
# 运行所有测试
uv run pytest tests/ -v

# 失败时停止
uv run pytest tests/ -x

# 按标记运行
uv run pytest -m smoke           # 冒烟测试
uv run pytest -m "not slow"      # 排除慢速测试
```

### 本地调试

```bash
# 使用 local 环境（推荐）
uv run pytest tests/ --env=local -v

# 启用 DEBUG 日志
uv run pytest tests/ --env=local --log-cli-level=DEBUG -v -s

# 失败时进入调试器
uv run pytest tests/ --env=local --pdb -v -s

# 保留测试数据
uv run pytest tests/ --env=local --keep-test-data -v
```

> 详见 [本地调试快速指南](https://github.com/user/df-test-framework/docs/guides/local_debug_quickstart.md)

### 测试标记

| 标记 | 说明 |
|------|------|
| `@pytest.mark.smoke` | 冒烟测试 |
| `@pytest.mark.regression` | 回归测试 |
| `@pytest.mark.slow` | 慢速测试 |
| `@pytest.mark.debug` | 启用调试输出（需要 -s） |
| `@pytest.mark.keep_data` | 保留该测试的数据 |

## 配置说明

### YAML 配置（推荐）

框架支持分层 YAML 配置，配置文件位于 `config/` 目录：

```yaml
# config/base.yaml - 基础配置（所有环境共享）
http:
  base_url: http://localhost:8000/api
  timeout: 30

# config/environments/local.yaml - 本地调试配置
_extends: environments/dev.yaml
env: local
debug: true
logging:
  level: DEBUG
  sanitize: false
observability:
  debug_output: true
test:
  keep_test_data: true
```

```bash
# config/secrets/.env.local - 敏感信息（不提交 git）
SIGNATURE__SECRET=your_secret_key
DB__PASSWORD=your_db_password
```

### 环境变量格式（v3.34.1+）

```bash
# ✅ 正确格式（无 APP_ 前缀）
HTTP__BASE_URL=https://api.example.com
HTTP__TIMEOUT=30
SIGNATURE__SECRET=your_secret
DB__HOST=localhost
DB__PASSWORD=password

# ❌ 旧格式（已废弃）
# APP_HTTP__BASE_URL=...
```

### 配置优先级

```
环境变量 > secrets/.env.local > environments/{env}.yaml > base.yaml
```

## 常见问题

### Q: API 创建的数据没有清理

1. 确保已配置清理映射（`config/base.yaml` 或 `.env`）：

```yaml
# config/base.yaml
cleanup:
  enabled: true
  mappings:
    orders:
      table: order_table
      field: order_no
```

2. 测试中使用 `cleanup` fixture 注册需要清理的数据：

```python
def test_example(http_client, cleanup):
    order_no = DataGenerator.test_id("TEST_ORD")
    http_client.post("/orders", json={{"order_no": order_no}})
    cleanup.add("orders", order_no)  # 测试结束后自动清理
```

### Q: 订单号重复错误

使用 `DataGenerator.test_id("TEST_ORD")` 生成唯一订单号。

### Q: 数据库连接失败

检查 `config/secrets/.env.local` 中的数据库配置是否正确。

### Q: 签名验证失败

检查 `SIGNATURE__SECRET` 是否与服务端一致（注意：v3.34.1+ 无 APP_ 前缀）。

### Q: 日志没有显示

```bash
# 启用实时日志
uv run pytest tests/ --log-cli-level=DEBUG -v -s

# 或使用 local 环境（已配置 DEBUG 日志）
uv run pytest tests/ --env=local -v -s
```

### Q: 调试时想保留测试数据

```bash
# 方式1: 使用 local 环境（已配置 keep_test_data: true）
uv run pytest tests/ --env=local -v

# 方式2: 命令行参数
uv run pytest --keep-test-data

# 方式3: 测试标记
@pytest.mark.keep_data
def test_debug():
    ...
```
"""

README_UI_TEMPLATE = """# {ProjectName}

{ProjectName} 的 UI 自动化测试项目，基于 df-test-framework + Playwright 构建。

## 覆盖系统

| 系统 | 说明 | 测试目录 |
|------|------|----------|
| Web UI | 网页界面自动化测试 | `tests/ui/` |

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 安装 Playwright 浏览器驱动
playwright install

# 或使用 pip
pip install -e .
playwright install
```

### 2. 配置环境

```bash
# 复制配置文件
cp config/environments/local.yaml.example config/environments/local.yaml
cp config/secrets/.env.local.example config/secrets/.env.local

# 编辑配置文件，填写测试站点 URL 等
# - local.yaml: 通用配置
# - .env.local: 敏感信息（账号密码等）
```

### 3. 运行测试

```bash
# 运行所有 UI 测试
uv run pytest tests/ui/ -v

# 显示浏览器界面（有头模式）
uv run pytest tests/ui/ --headed

# 指定浏览器
uv run pytest tests/ui/ --browser firefox

# 生成 Allure 报告
uv run pytest tests/ui/ --alluredir=reports/allure-results
allure serve reports/allure-results
```

## 项目结构

```
{project_name}/
├── src/{project_name}/
│   ├── pages/                   # 页面对象（Page Object）
│   ├── fixtures/                # 项目 Fixtures
│   └── config/settings.py       # 配置
├── tests/
│   ├── ui/                      # UI 测试
│   └── conftest.py              # Fixtures 定义
├── config/                      # YAML 配置文件
├── reports/
│   ├── screenshots/             # 失败截图
│   └── allure-results/          # Allure 报告
└── pyproject.toml               # 项目配置（含 pytest）
```

## 编写测试

### 核心 Fixtures

| Fixture | 说明 |
|---------|------|
| `page` | Playwright Page 对象 |
| `browser_context` | 浏览器上下文 |
| `settings` | 配置对象 |

### 页面对象模式

使用 Page Object 模式组织页面元素和操作：

```python
# src/{project_name}/pages/login_page.py
from playwright.sync_api import Page

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.login_button = page.locator("button[type='submit']")

    def navigate(self):
        self.page.goto("/login")

    def login(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
```

### 示例测试

```python
import allure
import pytest
from df_test_framework.testing.plugins import step

from {project_name}.pages.home_page import HomePage


@allure.feature("首页")
@allure.story("页面加载")
class TestHomePage:

    @allure.title("首页加载成功")
    @pytest.mark.smoke
    def test_home_page_loads(self, page, settings):
        \"\"\"测试首页能够正常加载\"\"\"

        with step("打开首页"):
            home_page = HomePage(page)
            home_page.navigate()

        with step("验证页面标题"):
            assert home_page.get_title() == "欢迎"

        with step("验证关键元素可见"):
            assert home_page.is_logo_visible()
```

## 运行测试

### 常用命令

```bash
# 运行所有 UI 测试
uv run pytest tests/ui/ -v

# 失败时停止
uv run pytest tests/ui/ -x

# 按标记运行
uv run pytest -m smoke           # 冒烟测试
uv run pytest -m "not slow"      # 排除慢速测试

# 显示浏览器界面
uv run pytest tests/ui/ --headed

# 慢速模式（方便调试）
uv run pytest tests/ui/ --headed --slowmo 1000
```

### 本地调试

```bash
# 使用 local 环境 + 显示浏览器
uv run pytest tests/ui/ --env=local --headed -v

# 启用 DEBUG 日志
uv run pytest tests/ui/ --env=local --log-cli-level=DEBUG -v -s

# Playwright Inspector 调试
PWDEBUG=1 uv run pytest tests/ui/test_example.py --env=local

# 失败时进入调试器
uv run pytest tests/ui/ --env=local --pdb -v
```

### 测试标记

| 标记 | 说明 |
|------|------|
| `@pytest.mark.smoke` | 冒烟测试 |
| `@pytest.mark.regression` | 回归测试 |
| `@pytest.mark.slow` | 慢速测试 |
| `@pytest.mark.debug` | 启用调试输出（需要 -s） |

## 配置说明

### YAML 配置（推荐）

```yaml
# config/environments/local.yaml - 本地调试配置
_extends: environments/dev.yaml
env: local
debug: true

app:
  base_url: "https://example.com"  # 测试站点 URL

playwright:
  headless: false                   # 本地调试显示浏览器
  timeout: 60000                    # 调试时延长超时
  slow_mo: 500                      # 慢速模式，方便观察

logging:
  level: DEBUG
observability:
  debug_output: true
```

```bash
# config/secrets/.env.local - 敏感信息（不提交 git）
TEST_USERNAME=test_user
TEST_PASSWORD=test_password
```

### 环境变量格式（v3.34.1+）

```bash
# ✅ 正确格式（无 APP_ 前缀）
TEST_USERNAME=test_user
TEST_PASSWORD=test_password

# ❌ 旧格式（已废弃）
# APP_TEST_USERNAME=...
```

## 常见问题

### Q: 浏览器未安装

```bash
playwright install
```

### Q: 元素定位失败

使用 Playwright Inspector 调试：

```bash
PWDEBUG=1 uv run pytest tests/ui/test_example.py
```

### Q: 测试失败时想看截图

失败截图自动保存在 `reports/screenshots/` 目录。

### Q: 想在真实浏览器中看测试过程

```bash
# 显示浏览器
uv run pytest tests/ui/ --headed

# 或使用 local 环境（已配置 headless: false）
uv run pytest tests/ui/ --env=local
```

### Q: 日志没有显示

```bash
uv run pytest tests/ui/ --env=local --log-cli-level=DEBUG -v -s
```
"""

README_FULL_TEMPLATE = """# {ProjectName}

{ProjectName} 的完整自动化测试项目（API + UI），基于 df-test-framework 构建。

## 覆盖系统

| 系统 | 说明 | 测试目录 |
|------|------|----------|
| API | 核心 API 接口测试 | `tests/api/` |
| Web UI | 网页界面自动化测试 | `tests/ui/` |

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 安装 Playwright 浏览器驱动（UI 测试需要）
playwright install

# 或使用 pip
pip install -e .
playwright install
```

### 2. 配置环境

```bash
# 复制配置文件
cp config/environments/local.yaml.example config/environments/local.yaml
cp config/secrets/.env.local.example config/secrets/.env.local

# 编辑配置文件，填写 API 地址、数据库配置、测试站点 URL 等
# - local.yaml: 通用配置
# - .env.local: 敏感信息（密码、密钥等）
```

### 3. 运行测试

```bash
# 运行 API 测试
uv run pytest tests/api/ -v

# 运行 UI 测试
uv run pytest tests/ui/ -v

# 运行所有测试
uv run pytest tests/ -v

# 生成 Allure 报告
uv run pytest tests/ --alluredir=reports/allure-results
allure serve reports/allure-results
```

## 项目结构

```
{project_name}/
├── src/{project_name}/
│   ├── apis/                    # API 客户端封装
│   ├── models/                  # Pydantic 数据模型
│   │   ├── requests/            # 请求模型
│   │   └── responses/           # 响应模型
│   ├── pages/                   # 页面对象（Page Object）
│   ├── repositories/            # 数据库仓储层
│   ├── builders/                # 测试数据构建器
│   ├── fixtures/                # 项目 Fixtures
│   └── config/settings.py       # 配置（含中间件）
├── tests/
│   ├── api/                     # API 测试
│   ├── ui/                      # UI 测试
│   └── conftest.py              # Fixtures 定义
├── config/                      # YAML 配置文件
├── reports/
│   ├── screenshots/             # UI 失败截图
│   └── allure-results/          # Allure 报告
└── pyproject.toml               # 项目配置（含 pytest）
```

## 编写测试

### API 测试

#### 核心 Fixtures

| Fixture | 说明 |
|---------|------|
| `http_client` | HTTP 客户端（自动签名/Token） |
| `uow` | Unit of Work（数据库操作，自动回滚） |
| `settings` | 配置对象 |
| `cleanup` | 配置驱动的数据清理（v3.18.0+） |

#### 示例 API 测试

```python
import allure
import pytest
from df_test_framework import DataGenerator
from df_test_framework import attach_json, step


@allure.feature("订单管理")
@allure.story("创建订单")
class TestOrderCreate:

    @allure.title("创建订单-成功")
    @pytest.mark.smoke
    def test_create_order_success(self, http_client, cleanup):
        \"\"\"测试创建订单\"\"\"

        with step("准备测试数据"):
            order_no = DataGenerator.test_id("TEST_ORD")
            request_data = {{
                "order_no": order_no,
                "amount": 100.00
            }}
            attach_json(request_data, name="请求数据")

        with step("调用创建订单 API"):
            response = http_client.post("/orders", json=request_data)
            attach_json(response.json(), name="响应数据")

        with step("验证响应"):
            assert response.status_code == 200

        # 记录需要清理的订单号
        cleanup.add("orders", order_no)
```

### UI 测试

#### 核心 Fixtures

| Fixture | 说明 |
|---------|------|
| `page` | Playwright Page 对象 |
| `browser_context` | 浏览器上下文 |
| `settings` | 配置对象 |

#### 示例 UI 测试

```python
import allure
import pytest
from df_test_framework.testing.plugins import step

from {project_name}.pages.home_page import HomePage


@allure.feature("首页")
@allure.story("页面加载")
class TestHomePage:

    @allure.title("首页加载成功")
    @pytest.mark.smoke
    def test_home_page_loads(self, page):
        \"\"\"测试首页能够正常加载\"\"\"

        with step("打开首页"):
            home_page = HomePage(page)
            home_page.navigate()

        with step("验证页面标题"):
            assert home_page.get_title() == "欢迎"
```

## 运行测试

### 常用命令

```bash
# API 测试
uv run pytest tests/api/ -v

# UI 测试（显示浏览器）
uv run pytest tests/ui/ -v --headed

# 运行所有测试
uv run pytest tests/ -v

# 按标记运行
uv run pytest -m smoke           # 冒烟测试
uv run pytest -m "not slow"      # 排除慢速测试
```

### 本地调试

```bash
# 使用 local 环境
uv run pytest tests/ --env=local -v

# 启用 DEBUG 日志
uv run pytest tests/ --env=local --log-cli-level=DEBUG -v -s

# UI 测试 + 显示浏览器
uv run pytest tests/ui/ --env=local --headed -v

# 失败时进入调试器
uv run pytest tests/ --env=local --pdb -v -s

# Playwright Inspector 调试
PWDEBUG=1 uv run pytest tests/ui/test_example.py --env=local
```

> 详见 [本地调试快速指南](https://github.com/user/df-test-framework/docs/guides/local_debug_quickstart.md)

### 测试标记

| 标记 | 说明 |
|------|------|
| `@pytest.mark.smoke` | 冒烟测试 |
| `@pytest.mark.regression` | 回归测试 |
| `@pytest.mark.slow` | 慢速测试 |
| `@pytest.mark.debug` | 启用调试输出（需要 -s） |
| `@pytest.mark.keep_data` | 保留该测试的数据 |

## 配置说明

### YAML 配置（推荐）

```yaml
# config/environments/local.yaml - 本地调试配置
_extends: environments/dev.yaml
env: local
debug: true

http:
  base_url: "https://api.example.com"  # API 地址

app:
  base_url: "https://example.com"      # Web 站点 URL

playwright:
  headless: false                       # 本地调试显示浏览器
  slow_mo: 500                          # 慢速模式

logging:
  level: DEBUG
  sanitize: false
observability:
  debug_output: true
test:
  keep_test_data: true
```

```bash
# config/secrets/.env.local - 敏感信息（不提交 git）
SIGNATURE__SECRET=your_secret_key
DB__PASSWORD=your_db_password
TEST_USERNAME=test_user
TEST_PASSWORD=test_password
```

### 环境变量格式（v3.34.1+）

```bash
# ✅ 正确格式（无 APP_ 前缀）
HTTP__BASE_URL=https://api.example.com
SIGNATURE__SECRET=your_secret
DB__PASSWORD=password

# ❌ 旧格式（已废弃）
# APP_HTTP__BASE_URL=...
```

### 配置优先级

```
环境变量 > secrets/.env.local > environments/{env}.yaml > base.yaml
```

## 常见问题

### API 测试

#### Q: API 创建的数据没有清理

1. 确保已配置清理映射（`config/base.yaml` 或 `.env`）：

```yaml
# config/base.yaml
cleanup:
  enabled: true
  mappings:
    orders:
      table: order_table
      field: order_no
```

2. 测试中使用 `cleanup` fixture 注册需要清理的数据：

```python
def test_example(http_client, cleanup):
    order_no = DataGenerator.test_id("TEST_ORD")
    http_client.post("/orders", json={{"order_no": order_no}})
    cleanup.add("orders", order_no)  # 测试结束后自动清理
```

#### Q: 签名验证失败

检查 `SIGNATURE__SECRET` 是否与服务端一致（注意：v3.34.1+ 无 APP_ 前缀）。

### UI 测试

#### Q: 浏览器未安装

```bash
playwright install
```

#### Q: 测试失败时想看截图

失败截图自动保存在 `reports/screenshots/` 目录。

### 通用

#### Q: 日志没有显示

```bash
uv run pytest tests/ --env=local --log-cli-level=DEBUG -v -s
```

#### Q: 调试时想保留测试数据

```bash
# 方式1: 使用 local 环境（已配置 keep_test_data: true）
uv run pytest tests/ --env=local -v

# 方式2: 命令行参数
uv run pytest --keep-test-data

# 方式3: 测试标记
@pytest.mark.keep_data
def test_debug():
    ...
```
"""

__all__ = ["README_API_TEMPLATE", "README_UI_TEMPLATE", "README_FULL_TEMPLATE"]
