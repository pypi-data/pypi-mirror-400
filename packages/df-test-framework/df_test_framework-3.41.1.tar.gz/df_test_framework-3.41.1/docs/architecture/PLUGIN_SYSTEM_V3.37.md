# pytest 插件系统架构 (v3.37.0)

本文档描述 df-test-framework v3.36.0 - v3.37.0 的配置和插件系统现代化重构。

## 目录

1. [演进背景](#演进背景)
2. [v3.36.0: 配置 API 现代化](#v3360-配置-api-现代化)
3. [v3.37.0: pytest 插件现代化](#v3370-pytest-插件现代化)
4. [核心原理](#核心原理)
5. [状态管理设计](#状态管理设计)
6. [Hook 执行顺序](#hook-执行顺序)
7. [测试隔离机制](#测试隔离机制)

---

## 演进背景

### 问题分析

v3.35.x 存在以下技术债务：

1. **ConfigRegistry 单例模式**
   - 全局状态难以测试
   - 多 pytest session 之间状态泄漏
   - 与 pydantic-settings 最佳实践不符

2. **手动插件声明**
   - 用户需要在 conftest.py 中声明 `pytest_plugins`
   - 容易遗漏或写错
   - 不符合"安装即用"的设计理念

3. **自定义管理器类**
   - RuntimeContextManager、CacheManager 等增加复杂度
   - 与 pytest 官方推荐方式不符
   - 状态管理分散在多个类中

### 解决方案

| 版本 | 改进 | 删除代码量 |
|------|------|-----------|
| v3.36.0 | 移除 ConfigRegistry，统一配置 API | ~1870 行 |
| v3.37.0 | pytest11 Entry Points + config 属性 | ~1000 行 |

---

## v3.36.0: 配置 API 现代化

### 核心变更

移除 ConfigRegistry 单例，改用函数式 API：

```python
# 旧方式（已移除）
from df_test_framework.infrastructure.config import ConfigRegistry
registry = ConfigRegistry.get_instance()
timeout = registry.get("http.timeout")

# 新方式
from df_test_framework.infrastructure.config import get_config, get_settings
timeout = get_config("http.timeout")
settings = get_settings()
```

### 配置加载流程

```
┌─────────────────────────────────────────────────────────────┐
│                    配置加载流程 (v3.36.0)                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 环境变量                                                 │
│     └─► os.environ                                         │
│                                                             │
│  2. Secrets 文件                                            │
│     └─► config/secrets/.env.local                          │
│                                                             │
│  3. 环境 YAML                                               │
│     └─► config/environments/{env}.yaml                     │
│                                                             │
│  4. 基础 YAML                                               │
│     └─► config/base.yaml                                   │
│                                                             │
│  5. .env 文件（回退）                                        │
│     └─► .env + .env.{env}                                  │
│                                                             │
│  6. 代码默认值                                               │
│     └─► FrameworkSettings 类默认值                          │
│                                                             │
│         ▼ 优先级从高到低                                     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              get_settings() / get_config()          │   │
│  │                   惰性加载 + 单例缓存                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### API 设计

```python
# settings.py 提供的函数式 API

def get_settings() -> FrameworkSettings:
    """获取框架配置（惰性加载 + 单例缓存）"""

def get_config(path: str, default: Any = None) -> Any:
    """点号路径访问配置值

    Example:
        timeout = get_config("http.timeout", default=30)
        host = get_config("db.host")
    """

def get_settings_for_class(
    cls: type[FrameworkSettings],
    env: str | None = None,
    config_dir: str = "config"
) -> FrameworkSettings:
    """使用自定义配置类加载配置"""

def clear_settings_cache() -> None:
    """清理配置缓存（测试用）"""
```

---

## v3.37.0: pytest 插件现代化

### 1. pytest11 Entry Points

插件通过 `pyproject.toml` 的 Entry Points 自动注册：

```toml
# pyproject.toml
[project.entry-points.pytest11]
df_test_framework_core = "df_test_framework.testing.fixtures.core"
df_test_framework_env = "df_test_framework.testing.plugins.env_plugin"
df_test_framework_logging = "df_test_framework.testing.plugins.logging_plugin"
df_test_framework_markers = "df_test_framework.testing.plugins.markers"
df_test_framework_allure = "df_test_framework.testing.fixtures.allure"
df_test_framework_debugging = "df_test_framework.testing.fixtures.debugging"
df_test_framework_metrics = "df_test_framework.testing.fixtures.metrics"
df_test_framework_monitoring = "df_test_framework.testing.fixtures.monitoring"
```

**工作原理**：

```
pip install df-test-framework
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                   setuptools Entry Points                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ [project.entry-points.pytest11]                       │  │
│  │   df_test_framework_core = "...fixtures.core"         │  │
│  │   df_test_framework_env = "...plugins.env_plugin"     │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                      pytest 启动时                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ pluggy 自动发现并加载所有 pytest11 入口点              │  │
│  │   → 无需用户在 conftest.py 中声明 pytest_plugins      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    插件 Hook 自动调用                        │
│  pytest_addoption → pytest_configure → pytest_unconfigure   │
└─────────────────────────────────────────────────────────────┘
```

### 2. pytest 9.0 原生 TOML 配置

使用 `[tool.pytest]` 替代 `[tool.pytest.ini_options]`：

```toml
# 旧方式（pytest < 9.0）
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
timeout = 30

# 新方式（pytest 9.0+）
[tool.pytest]
minversion = "9.0"
testpaths = ["tests"]
timeout = "30"  # 注意：pytest-timeout 需要字符串类型
```

**主要差异**：

| 配置项 | ini_options | 原生 TOML |
|--------|-------------|-----------|
| 布尔值 | `"true"` | `true` |
| 列表 | `"a b c"` | `["a", "b", "c"]` |
| timeout | `30` | `"30"` (字符串) |

### 3. config 对象属性状态管理

使用 `config` 对象属性替代自定义管理器类：

```python
# 旧方式（v3.36.1）
class RuntimeContextManager:
    _instance: RuntimeContext | None = None

    @classmethod
    def get(cls) -> RuntimeContext:
        if cls._instance is None:
            raise RuntimeError("未初始化")
        return cls._instance

# 新方式（v3.37.0）
def pytest_configure(config: pytest.Config) -> None:
    config._df_runtime = runtime_context  # 存储到 config 对象

@pytest.fixture(scope="session")
def runtime(request: pytest.FixtureRequest) -> RuntimeContext:
    return request.config._df_runtime  # 从 config 对象读取
```

---

## 核心原理

### config 对象生命周期

pytest 的 `config` 对象在整个测试 session 中保持存在：

```
pytest 启动
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                  pytest.Config 对象创建                      │
│                                                             │
│  pytest_addoption(parser)   ← 注册命令行选项                 │
│           │                                                 │
│           ▼                                                 │
│  pytest_configure(config)   ← 初始化，存储状态到 config      │
│           │                   config._df_runtime = ...      │
│           │                   config._df_settings = ...     │
│           ▼                                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              测试 Session 执行                       │   │
│  │                                                     │   │
│  │  @pytest.fixture(scope="session")                   │   │
│  │  def runtime(request):                              │   │
│  │      return request.config._df_runtime              │   │
│  │                                                     │   │
│  │  @pytest.fixture                                    │   │
│  │  def uow(request, runtime):                         │   │
│  │      test_id = request.node.nodeid                  │   │
│  │      bus = _get_test_event_bus(request.config, id)  │   │
│  │      ...                                            │   │
│  └─────────────────────────────────────────────────────┘   │
│           │                                                 │
│           ▼                                                 │
│  pytest_unconfigure(config) ← 清理，释放资源                 │
│                               config._df_runtime.close()    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
pytest 退出
```

### 为什么使用 config 属性？

1. **官方推荐**：pytest 文档推荐使用 config 对象存储插件状态
2. **生命周期明确**：config 对象与 session 生命周期一致
3. **无全局状态**：避免模块级别的全局变量
4. **易于测试**：可以通过 mock config 对象进行单元测试
5. **多 session 隔离**：每个 pytest session 有独立的 config 对象

---

## 状态管理设计

### config 属性命名规范

所有框架属性使用 `_df_` 前缀，避免与其他插件冲突：

| 属性 | 设置位置 | 用途 |
|------|----------|------|
| `config._df_settings` | env_plugin | FrameworkSettings 实例 |
| `config._df_current_env` | env_plugin | 当前环境名称 |
| `config._df_env_name` | env_plugin | 命令行 --env 参数 |
| `config._df_config_dir` | env_plugin | 配置目录路径 |
| `config._df_runtime` | core | RuntimeContext 实例 |
| `config._df_test_buses` | core | 测试隔离的 EventBus 字典 |
| `config._df_cache_cleared` | env_plugin | 配置缓存清理标记 |

### 属性设置时序

```python
# env_plugin.py (tryfirst=True)
@hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    # 1. 清理配置缓存（每个 session 只执行一次）
    if not hasattr(config, "_df_cache_cleared"):
        clear_settings_cache()
        config._df_cache_cleared = True

    # 2. 加载配置
    settings = get_settings_for_class(settings_class, env=env)

    # 3. 存储到 config
    config._df_settings = settings
    config._df_current_env = env or settings.env

# core.py (默认顺序，在 env_plugin 之后)
def pytest_configure(config: pytest.Config) -> None:
    # 4. 检查 env_plugin 是否已加载配置
    if hasattr(config, "_df_settings"):
        settings = config._df_settings
        # 使用已加载的配置
    else:
        # 回退：使用 Bootstrap 加载
        ...

    # 5. 创建 RuntimeContext
    runtime_context = RuntimeBuilder().with_settings(settings).build()

    # 6. 存储到 config
    config._df_runtime = runtime_context
```

---

## Hook 执行顺序

### @hookimpl 优先级控制

```python
from pytest import hookimpl

@hookimpl(tryfirst=True)   # 最先执行
def pytest_configure(config):
    pass

@hookimpl                   # 默认顺序
def pytest_configure(config):
    pass

@hookimpl(trylast=True)    # 最后执行
def pytest_configure(config):
    pass
```

### 框架插件执行顺序

```
pytest_configure 执行顺序:

1. env_plugin (tryfirst=True)
   ├─ 清理配置缓存
   ├─ 加载 YAML/环境配置
   └─ 设置 config._df_settings, config._df_current_env

2. core.py (默认)
   ├─ 检测 config._df_settings
   ├─ 创建 RuntimeContext
   └─ 设置 config._df_runtime

3. logging_plugin (默认)
   └─ 配置 loguru → logging 桥接

4. markers (默认)
   └─ 注册自定义 markers

5. allure (默认)
   └─ 配置 Allure 报告

6. debugging (默认)
   └─ 自动调试输出 (_auto_debug_by_marker autouse fixture)

7. metrics (默认)
   └─ Prometheus 指标收集 (metrics_manager, metrics_observer)

8. monitoring (默认)
   └─ 监控插件 (monitoring_observer, db_monitoring)

pytest_unconfigure 执行顺序（逆序）:

1. core.py
   ├─ 关闭 RuntimeContext
   └─ 清理所有测试 EventBus

2. env_plugin
   └─ 可选：清理环境状态
```

---

## 测试隔离机制

### EventBus 测试隔离

每个测试用例拥有独立的 EventBus 实例：

```python
def _get_test_event_bus(config: pytest.Config, test_id: str) -> EventBus:
    """获取测试专用 EventBus"""
    # 延迟初始化字典
    if not hasattr(config, "_df_test_buses"):
        config._df_test_buses = {}

    buses = config._df_test_buses

    # 按 test_id 隔离
    if test_id not in buses:
        buses[test_id] = EventBus()
        logger.debug(f"创建测试 EventBus: {test_id}")

    return buses[test_id]


def _cleanup_test_event_bus(config: pytest.Config, test_id: str) -> None:
    """清理测试专用 EventBus"""
    if hasattr(config, "_df_test_buses"):
        buses = config._df_test_buses
        if test_id in buses:
            buses[test_id].clear()
            del buses[test_id]
            logger.debug(f"清理测试 EventBus: {test_id}")
```

### 隔离流程图

```
Test: tests/api/test_orders.py::test_create_order
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                      uow fixture                             │
│                                                             │
│  test_id = request.node.nodeid                              │
│  # "tests/api/test_orders.py::test_create_order"            │
│                                                             │
│  event_bus = _get_test_event_bus(config, test_id)           │
│  # 创建独立的 EventBus 实例                                  │
│                                                             │
│  uow = UnitOfWork(session_factory, event_bus=event_bus)     │
│  # EventBus 注入到 UoW                                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   测试执行                           │   │
│  │  uow.orders.create(...)  → 发布事件到隔离的 bus      │   │
│  │  uow.commit()            → 发布 TransactionCommit    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  _cleanup_test_event_bus(config, test_id)                   │
│  # 清理，防止事件泄漏                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 为什么需要测试隔离？

1. **事件不泄漏**：测试 A 发布的事件不会影响测试 B
2. **订阅者隔离**：每个测试可以有独立的事件处理器
3. **并行测试安全**：pytest-xdist 并行执行时不会冲突
4. **调试友好**：可以只关注当前测试的事件

---

## 参考资料

- [pytest Plugin Registration](https://docs.pytest.org/en/stable/how-to/writing_plugins.html#making-your-plugin-installable-by-others)
- [pytest 9.0 TOML Configuration](https://docs.pytest.org/en/stable/reference/customize.html#pyproject-toml)
- [pluggy Documentation](https://pluggy.readthedocs.io/)
- [pydantic-settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

---

**相关文档**:
- [v3.36.0 发布说明](../releases/v3.36.0.md)
- [v3.37.0 发布说明](../releases/v3.37.0.md)
- [配置管理分析](config-management-analysis.md)
