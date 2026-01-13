# 环境配置使用指南

> **版本**: v3.38.6
> **更新日期**: 2025-12-26
> **模块**: `df_test_framework.infrastructure.config`

环境管理系统提供完整的多环境配置支持，包括 YAML 分层配置、深度合并、`_extends` 继承、统一配置访问等功能。

---

## 快速开始

### 初始化配置目录

使用 CLI 命令快速创建配置目录结构：

```bash
# 初始化配置目录
df-test env init

# 指定自定义目录
df-test env init --config-dir=my_config
```

生成的目录结构：

```
config/
├── base.yaml              # 基础配置（所有环境共享）
├── environments/
│   ├── local.yaml         # 本地开发环境
│   ├── dev.yaml           # 开发环境
│   ├── test.yaml          # 测试环境
│   ├── staging.yaml       # 预发布环境
│   └── prod.yaml          # 生产环境
└── secrets/               # 敏感配置（已 .gitignore）
    └── .env.local         # 本地敏感配置
```

### 基本使用

```python
from df_test_framework.infrastructure.config import (
    load_config,
    get_settings,
    get_config,
)

# 方式1: load_config - 加载 YAML 配置
settings = load_config("staging")
print(settings.http.base_url)

# 方式2: get_settings - 惰性加载 + 单例缓存（推荐）
settings = get_settings(env="staging")
timeout = settings.http.timeout
base_url = settings.http.base_url
print(settings.env)  # "staging"

# 方式3: get_config - 点号路径访问
timeout = get_config("http.timeout")
base_url = get_config("http.base_url")
```

### 在 pytest 中使用

```bash
# 在 staging 环境运行测试
pytest tests/ --env=staging

# 在 prod 环境运行冒烟测试
pytest tests/ --env=prod -m smoke

# 使用自定义配置目录
pytest tests/ --env=staging --config-dir=my_config
```

---

## 配置文件格式

### base.yaml（基础配置）

所有环境共享的默认配置：

```yaml
# config/base.yaml

# 环境名称（会被环境配置覆盖）
env: test

# HTTP 客户端配置
http:
  base_url: http://localhost:8080
  timeout: 30
  max_retries: 3
  verify_ssl: true

# 数据库配置
db:
  host: localhost
  port: 3306
  database: test_db
  charset: utf8mb4
  pool_size: 5
  pool_max_overflow: 10

# Redis 配置
redis:
  host: localhost
  port: 6379
  db: 0
  password: null

# 日志配置
logging:
  level: INFO
  format: "{time} | {level} | {message}"
  console: true
  file: false

# 测试执行配置
test:
  keep_test_data: false
  parallel_workers: 4
  screenshot_on_failure: true

# 可观测性配置
observability:
  enable_tracing: false
  enable_metrics: false
  debug_output: false
```

### environments/{env}.yaml（环境配置）

环境特定的配置覆盖：

```yaml
# config/environments/staging.yaml

# 只覆盖需要变更的配置
http:
  base_url: https://staging-api.example.com
  timeout: 60

db:
  host: staging-db.example.com
  database: staging_db

redis:
  host: staging-redis.example.com

logging:
  level: DEBUG

observability:
  enable_tracing: true
```

### secrets 管理

敏感配置放在 `config/secrets/` 目录：

```bash
# config/secrets/.env.local
DB_PASSWORD=your_secret_password
API_KEY=your_api_key
REDIS_PASSWORD=your_redis_password
```

> **注意**: `secrets/` 目录已在 `.gitignore` 中，不会提交到版本控制。

---

## 配置优先级

配置加载优先级（从高到低）：

```
1. 环境变量               ← 最高优先级
2. config/secrets/.env.local
3. config/environments/{env}.yaml
4. config/base.yaml
5. .env + .env.{env}      ← 回退模式（无 config/ 目录时）
6. 代码默认值             ← 最低优先级
```

示例：

```yaml
# base.yaml
http:
  timeout: 30

# environments/staging.yaml
http:
  timeout: 60
```

```bash
# 环境变量覆盖
export HTTP__TIMEOUT=120
```

最终 `http.timeout = 120`（环境变量优先）

### YAML 深度合并

v3.35.5 使用 `LayeredYamlSettingsSource` 实现 YAML 文件之间的**深度合并**。环境配置只需写覆盖字段：

```yaml
# base.yaml
db:
  port: 3306
  pool_size: 10
  charset: utf8mb4

# environments/test.yaml - ✅ 只写差异字段
db:
  host: "test-db.example.com"
  name: "test_db"
  user: "test_user"
  # port=3306, pool_size=10, charset=utf8mb4 自动从 base.yaml 继承
```

### 配置继承（_extends）

使用 `_extends` 字段实现环境之间的继承：

```yaml
# environments/dev.yaml
env: dev
http:
  base_url: "http://dev-api.example.com"
db:
  host: "dev-db.example.com"
  name: "dev_db"
  user: "dev_user"

# environments/staging.yaml - 继承 dev，只覆盖差异
_extends: environments/dev.yaml
env: staging
http:
  base_url: "https://staging-api.example.com"
# db 配置完全继承自 dev.yaml

# environments/local.yaml - 继承 dev，启用调试
_extends: environments/dev.yaml
env: local
debug: true
observability:
  debug_output: true
test:
  keep_test_data: true
```

继承链示例：

```
base.yaml → dev.yaml → staging.yaml
                    → local.yaml
```

> **提示**：`_extends` 支持多级继承，自动检测循环继承。

---

## 配置 API（v3.36.0+）

### 基础 API

```python
from df_test_framework.infrastructure.config import (
    get_settings,
    get_settings_for_class,
    get_config,
    clear_settings_cache,
)

# get_settings() - 惰性加载 + 单例缓存（推荐）
settings = get_settings()                    # 自动检测环境
settings = get_settings(env="staging")       # 指定环境
settings = get_settings(env="staging", config_dir="my_config")

# 访问配置（类型安全）
base_url = settings.http.base_url
db_config = settings.db
timeout = settings.http.timeout

# 环境检查
print(settings.env)          # "staging"
print(settings.debug)        # False
print(settings.is_prod)      # False

# get_config() - 点号路径访问
timeout = get_config("http.timeout")
host = get_config("db.host")
missing = get_config("nonexistent", default="fallback")

# clear_settings_cache() - 清除缓存（测试用）
clear_settings_cache()  # 下次调用 get_settings() 将重新加载
```

### 自定义配置类

```python
from df_test_framework.infrastructure.config import (
    FrameworkSettings,
    get_settings_for_class,
)

# 定义项目配置类
class MySettings(FrameworkSettings):
    api_key: str = ""
    feature_flags: dict = {}

# 加载自定义配置
settings = get_settings_for_class(MySettings, env="staging")
print(settings.api_key)
```

### load_config() - YAML 配置加载

```python
from df_test_framework.infrastructure.config import load_config

# 从 YAML 加载配置
settings = load_config("staging")
settings = load_config("staging", config_dir="my_config")
settings = load_config()  # 使用 ENV 环境变量
```

---

## pytest 集成

### 启用插件

**v3.37.0+**: 插件通过 Entry Points 自动加载，无需手动配置。

如需显式声明（向后兼容）：

```python
# conftest.py
pytest_plugins = [
    "df_test_framework.testing.plugins.env_plugin",
]
```

### 命令行参数

```bash
# 指定环境
pytest tests/ --env=staging

# 指定配置目录
pytest tests/ --env=staging --config-dir=my_config

# 组合使用
pytest tests/ --env=prod -m smoke -v
```

### 提供的 Fixtures

```python
import pytest

def test_with_config(settings, current_env):
    """使用配置 fixtures"""

    # settings: FrameworkSettings 实例（session scope）
    base_url = settings.http.base_url
    timeout = settings.http.timeout

    # current_env: 当前环境名称（session scope）
    if current_env == "prod":
        pytest.skip("跳过生产环境")
```

### 环境条件跳过

```python
import pytest

def test_dev_only(current_env):
    """仅在开发环境运行"""
    if current_env not in ("local", "dev"):
        pytest.skip("仅在开发环境运行")

    # 测试逻辑...

def test_skip_prod(settings):
    """跳过生产环境"""
    if settings.is_prod:
        pytest.skip("不在生产环境运行")

    # 测试逻辑...
```

---

## CLI 命令

### df-test env show

显示当前环境配置：

```bash
# 显示默认环境配置
df-test env show

# 显示指定环境配置
df-test env show --env=staging
```

### df-test env init

初始化配置目录：

```bash
# 创建默认配置目录结构
df-test env init

# 指定目录
df-test env init --config-dir=my_config
```

### df-test env validate

验证配置完整性：

```bash
# 验证 staging 环境配置
df-test env validate --env=staging

# 验证所有环境
df-test env validate --all
```

---

## 向后兼容

### .env 文件模式

如果 `config/` 目录不存在，系统自动回退到 `.env` 文件模式：

```
project/
├── .env              # 默认配置
├── .env.staging      # staging 环境配置
├── .env.prod         # prod 环境配置
└── tests/
```

```python
# 回退模式自动生效
settings = FrameworkSettings.for_environment("staging")
# 加载 .env + .env.staging
```

### 迁移到 YAML 配置

1. 运行 `df-test env init` 创建配置目录
2. 将 `.env` 文件的配置迁移到 `base.yaml`
3. 将 `.env.{env}` 的差异配置迁移到 `environments/{env}.yaml`
4. 敏感信息保留在 `secrets/.env.local`

---

## 最佳实践

### 1. 配置分层

`load_config()` 自动深度合并 `base.yaml` + `environments/{env}.yaml`：

```yaml
# base.yaml - 通用默认值
http:
  timeout: 30
  max_retries: 3
  verify_ssl: true
db:
  port: 3306
  pool_size: 10

# environments/dev.yaml - 开发环境（只覆盖差异）
http:
  base_url: http://localhost:8080
  verify_ssl: false
db:
  host: dev-db.example.com
  name: dev_db
# port=3306, pool_size=10 自动继承

# environments/staging.yaml - 继承 dev 环境
_extends: environments/dev.yaml
http:
  base_url: https://staging-api.example.com
# db 配置完全继承自 dev.yaml

# environments/local.yaml - 继承 dev，启用调试
_extends: environments/dev.yaml
debug: true
observability:
  debug_output: true
```

> **提示**: v3.35.5 支持 `_extends` 环境间继承，减少配置重复。

### 2. 敏感信息处理

```yaml
# base.yaml - 不包含敏感信息
db:
  host: localhost
  database: test_db
  # 密码通过环境变量或 secrets 注入
```

```bash
# secrets/.env.local
DB_PASSWORD=my_secret_password
```

### 3. 测试中使用

```python
# conftest.py
import pytest

# v3.37.0+ 插件自动加载（通过 pytest11 Entry Points）
# 无需手动注册，但也可以显式声明（向后兼容）：
pytest_plugins = [
    "df_test_framework.testing.plugins.env_plugin",
]

@pytest.fixture(scope="session")
def api_client(settings):
    """创建 API 客户端"""
    from df_test_framework import HttpClient

    return HttpClient(
        base_url=settings.http.base_url,
        timeout=settings.http.timeout,
    )
```

### 4. CI/CD 环境变量覆盖

```yaml
# .github/workflows/test.yml
jobs:
  test:
    runs-on: ubuntu-latest
    env:
      ENV: staging
      HTTP__BASE_URL: ${{ secrets.STAGING_API_URL }}
      DB__PASSWORD: ${{ secrets.DB_PASSWORD }}

    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: pytest tests/ --env=staging
```

---

## 配置参考

### FrameworkSettings 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `env` | str | 环境名称 |
| `debug` | bool | 调试模式 |
| `http` | HTTPConfig | HTTP 客户端配置 |
| `db` | DatabaseConfig | 数据库配置 |
| `redis` | RedisConfig | Redis 配置 |
| `storage` | StorageConfig | 存储配置 |
| `test` | TestConfig | 测试执行配置 |
| `logging` | LoggingConfig | 日志配置 |
| `observability` | ObservabilityConfig | 可观测性配置 |

### HTTPConfig 字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `base_url` | str | "" | 基础 URL |
| `timeout` | int | 30 | 超时时间（秒） |
| `max_retries` | int | 3 | 最大重试次数 |
| `verify_ssl` | bool | True | 是否验证 SSL |

### DatabaseConfig 字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `host` | str | "localhost" | 数据库主机 |
| `port` | int | 3306 | 端口 |
| `database` | str | "" | 数据库名 |
| `username` | str | "" | 用户名 |
| `password` | str | "" | 密码 |
| `charset` | str | "utf8mb4" | 字符集 |

---

## 相关文档

- [中间件系统指南](middleware_guide.md) - HTTP 中间件配置
- [日志集成指南](logging_pytest_integration.md) - 日志配置
- [可观测性指南](telemetry_guide.md) - 追踪和指标配置
