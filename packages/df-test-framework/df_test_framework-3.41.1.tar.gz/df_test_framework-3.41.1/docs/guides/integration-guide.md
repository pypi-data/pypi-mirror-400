# 现有项目接入指南

> **版本**: v3.38.0 | **更新**: 2025-12-24

本文档介绍如何将现有测试项目接入 df-test-framework v3.38.0。

## 目录

1. [安装依赖](#1-安装依赖)
2. [配置系统](#2-配置系统)
3. [conftest.py 配置](#3-conftestpy-配置)
4. [pytest.ini 配置](#4-pytestini-配置)
5. [编写测试](#5-编写测试)
6. [常见问题](#6-常见问题)

---

## 1. 安装依赖

### 使用 uv（推荐）

```bash
# 添加框架依赖
uv add df-test-framework

# 或指定版本
uv add df-test-framework==3.35.5
```

### 使用 pip

```bash
pip install df-test-framework==3.35.5
```

### 使用 pyproject.toml

```toml
[project]
dependencies = [
    "df-test-framework>=3.35.5",
]
```

---

## 2. 配置系统

v3.35.0+ 推荐使用 **YAML 分层配置**，也支持 **.env 回退模式**。

### 方式一：YAML 分层配置（推荐）

创建配置目录结构：

```
your-project/
├── config/
│   ├── base.yaml              # 基础配置（所有环境共享）
│   ├── environments/
│   │   ├── dev.yaml           # 开发环境
│   │   ├── test.yaml          # 测试环境（默认）
│   │   ├── staging.yaml       # 预发布环境
│   │   ├── prod.yaml          # 生产环境
│   │   └── local.yaml         # 本地调试（不提交git）
│   └── secrets/
│       └── .env.local         # 敏感信息（不提交git）
├── tests/
│   └── conftest.py
└── pytest.ini
```

#### config/base.yaml

```yaml
# 基础配置（所有环境共享）
env: dev

http:
  base_url: http://localhost:8000/api
  timeout: 30
  max_retries: 3

observability:
  enabled: true
  debug_output: false
  allure_recording: true

logging:
  level: INFO

# 数据库配置（可选）
# db:
#   host: localhost
#   port: 3306
#   name: test_db
#   user: root
#   password: password
#   charset: utf8mb4

# Redis 配置（可选）
# redis:
#   host: localhost
#   port: 6379
#   db: 0
```

#### config/environments/test.yaml

```yaml
# 测试环境配置
env: test

http:
  base_url: http://test-api.example.com/api
  timeout: 30

observability:
  debug_output: false
```

#### config/environments/local.yaml

```yaml
# 本地调试配置
# _extends 表示继承另一个环境配置
_extends: test

observability:
  debug_output: true  # 本地开启调试输出
```

#### 更新 .gitignore

```gitignore
# 敏感配置（不提交）
config/environments/local.yaml
config/secrets/
```

### 方式二：.env 回退模式

如果 `config/base.yaml` 不存在，框架会自动回退到 .env 模式。

#### .env 文件

```env
# 基础配置
ENV=test

# HTTP 配置
HTTP__BASE_URL=http://test-api.example.com/api
HTTP__TIMEOUT=30
HTTP__MAX_RETRIES=3

# 可观测性配置
OBSERVABILITY__ENABLED=true
OBSERVABILITY__DEBUG_OUTPUT=false
OBSERVABILITY__ALLURE_RECORDING=true

# 日志配置
LOGGING__LEVEL=INFO
```

> **注意**：v3.34.1+ 移除了 `APP_` 前缀，使用 `__` 作为嵌套分隔符。

---

## 3. conftest.py 配置

在项目根目录的 `tests/conftest.py` 中配置：

```python
"""Pytest 全局配置和 Fixtures (v3.35.5)

基于 df-test-framework v3.35.5 提供测试运行时环境。

配置系统:
- YAML 分层配置: config/base.yaml + config/environments/{env}.yaml
- --env 参数切换环境: pytest tests/ --env=local
"""

import pytest
from loguru import logger

# ========== 启用框架的 pytest 插件 ==========
pytest_plugins = [
    "df_test_framework.testing.plugins.env_plugin",      # 环境管理（--env 参数）
    "df_test_framework.testing.fixtures.core",           # 核心 fixtures
    "df_test_framework.testing.fixtures.allure",         # Allure 自动记录
    "df_test_framework.testing.fixtures.debugging",      # 调试工具
    "df_test_framework.testing.fixtures.metrics",        # 指标收集
    "df_test_framework.testing.plugins.logging_plugin",  # loguru 桥接
]


# ============================================================
# Pytest 配置钩子
# ============================================================

def pytest_configure(config: pytest.Config) -> None:
    """注册自定义标记"""
    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "regression: 回归测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "slow: 慢速测试")


def pytest_sessionstart(session: pytest.Session) -> None:
    """配置 Allure 环境信息"""
    try:
        from df_test_framework.infrastructure.config import ConfigRegistry
        from df_test_framework.testing.reporting.allure import AllureHelper

        if ConfigRegistry.is_initialized():
            registry = ConfigRegistry.get_instance()
            settings = registry.settings
            current_env = registry.current_env

            AllureHelper.add_environment_info({
                "环境": current_env,
                "API地址": settings.http.base_url,
                "Python版本": "3.12+",
                "框架版本": "df-test-framework v3.35.5",
            })
    except Exception as e:
        logger.warning(f"无法加载 Allure 环境信息: {e}")
```

### 框架自动提供的 Fixtures

| Fixture | 作用域 | 说明 |
|---------|--------|------|
| `settings` | session | 框架配置对象 |
| `config_registry` | session | 配置注册中心 |
| `current_env` | session | 当前环境名称 |
| `runtime` | session | 运行时上下文 |
| `http_client` | session | HTTP 客户端（支持中间件） |
| `database` | session | 数据库连接 |
| `redis_client` | session | Redis 客户端 |
| `uow` | function | Unit of Work（事务管理） |
| `cleanup` | function | 数据清理工具 |
| `console_debugger` | function | 控制台调试器 |
| `debug_mode` | function | 调试模式 |
| `allure_observer` | function | Allure 事件记录 |

---

## 4. pytest.ini 配置

创建 `pytest.ini`：

```ini
[pytest]
# 测试目录
testpaths = tests

# 默认选项
addopts = -v --tb=short

# 自定义配置（可选）
# df_settings_class = myproject.config.MySettings

# 标记
markers =
    smoke: 冒烟测试
    regression: 回归测试
    integration: 集成测试
    slow: 慢速测试
```

---

## 5. 编写测试

### 基本 API 测试

```python
"""tests/api/test_users.py"""

import pytest


class TestUserAPI:
    """用户 API 测试"""

    def test_get_user_list(self, http_client, settings):
        """测试获取用户列表"""
        response = http_client.get("/users")

        assert response.status_code == 200
        assert "data" in response.json()

    def test_create_user(self, http_client, cleanup):
        """测试创建用户"""
        user_data = {
            "username": "test_user_001",
            "email": "test@example.com",
        }

        response = http_client.post("/users", json=user_data)

        assert response.status_code == 201

        # 注册清理（测试结束后自动清理）
        user_id = response.json()["data"]["id"]
        cleanup.add("users", user_id)

    @pytest.mark.debug
    def test_with_debug_output(self, http_client):
        """启用调试输出的测试（需要 pytest -s）"""
        response = http_client.get("/users/123")
        assert response.status_code in [200, 404]
```

### 使用环境配置

```python
def test_environment_specific(settings, current_env):
    """根据环境执行不同逻辑"""
    print(f"当前环境: {current_env}")
    print(f"API 地址: {settings.http.base_url}")

    if current_env == "prod":
        pytest.skip("跳过生产环境")
```

### 运行测试

```bash
# 使用默认环境（test）
pytest tests/ -v

# 使用本地调试配置
pytest tests/ --env=local -v -s

# 使用预发布环境
pytest tests/ --env=staging -v

# 只运行冒烟测试
pytest tests/ -m smoke -v
```

---

## 6. 常见问题

### Q1: 调试输出不显示？

**检查清单**：

1. 配置中启用了 `observability.debug_output: true`
2. 使用 `-s` 参数运行：`pytest -v -s`
3. 使用正确的环境：`pytest --env=local -s`

### Q2: 配置不生效？

**检查优先级**（从高到低）：

1. 环境变量
2. `config/secrets/.env.local`
3. `config/environments/{env}.yaml`
4. `config/base.yaml`
5. 代码默认值

### Q3: 如何自定义 Settings 类？

创建自定义配置类：

```python
# myproject/config.py
from df_test_framework.infrastructure.config import FrameworkSettings, HTTPConfig
from pydantic import Field


class MySettings(FrameworkSettings):
    """自定义项目配置"""

    http: HTTPConfig = Field(
        default_factory=lambda: HTTPConfig(
            base_url="http://my-api.example.com",
            timeout=60,
        )
    )

    # 自定义业务字段
    my_custom_field: str = "default_value"
```

在 `pytest.ini` 中指定：

```ini
[pytest]
df_settings_class = myproject.config.MySettings
```

### Q4: 如何迁移旧项目？

1. **配置迁移**：将 `.env` 转换为 YAML 格式
2. **前缀移除**：删除 `APP_` 前缀（v3.34.1+）
3. **插件更新**：添加 `env_plugin` 到 `pytest_plugins`
4. **Fixture 更新**：使用框架提供的 `settings` fixture

### Q5: 如何在 CI/CD 中使用？

```yaml
# GitHub Actions 示例
- name: Run Tests
  run: |
    pytest tests/ --env=test -v --alluredir=allure-results
  env:
    # 通过环境变量覆盖敏感配置
    DB__PASSWORD: ${{ secrets.DB_PASSWORD }}
    SIGNATURE__SECRET: ${{ secrets.SIGNATURE_SECRET }}
```

---

## 快速检查清单

- [ ] 安装 `df-test-framework>=3.35.5`
- [ ] 创建 `config/` 目录和配置文件
- [ ] 更新 `tests/conftest.py`
- [ ] 添加 `pytest.ini`
- [ ] 更新 `.gitignore`（排除敏感配置）
- [ ] 运行测试验证：`pytest tests/ --env=test -v`

---

## 相关文档

- [架构设计](../architecture/)
- [配置系统](./config-system.md)
- [中间件系统](./middleware-system.md)
- [版本发布说明](../releases/)
