# 测试执行生命周期 (v3.37.0)

本文档详细描述安装 df-test-framework 后，运行 `pytest` 测试时的完整执行流程。

## 目录

1. [执行流程总览](#执行流程总览)
2. [阶段一：pytest 启动与插件发现](#阶段一pytest-启动与插件发现)
3. [阶段二：配置加载](#阶段二配置加载)
4. [阶段三：pytest_configure Hooks](#阶段三pytest_configure-hooks)
5. [阶段四：测试收集](#阶段四测试收集)
6. [阶段五：Fixture 解析与创建](#阶段五fixture-解析与创建)
7. [阶段六：测试执行](#阶段六测试执行)
8. [阶段七：资源清理](#阶段七资源清理)
9. [关键机制详解](#关键机制详解)

---

## 执行流程总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         pytest 测试执行完整流程                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  用户执行: pytest tests/ --env=local -v -s                                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 阶段一: pytest 启动与插件发现                                         │   │
│  │   └─ setuptools 扫描 pytest11 Entry Points                          │   │
│  │   └─ pluggy 加载所有已注册插件模块                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 阶段二: 配置加载                                                      │   │
│  │   └─ env_plugin: 解析 --env 参数                                     │   │
│  │   └─ 加载 YAML 配置 (base.yaml → _extends → {env}.yaml)             │   │
│  │   └─ 环境变量覆盖                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 阶段三: pytest_configure Hooks                                        │   │
│  │   └─ env_plugin (tryfirst): 存储配置到 config._df_settings           │   │
│  │   └─ core: 创建 RuntimeContext, 存储到 config._df_runtime            │   │
│  │   └─ logging_plugin: 配置 loguru → logging 桥接                      │   │
│  │   └─ markers: 注册自定义 markers                                      │   │
│  │   └─ allure: 配置 Allure 报告                                         │   │
│  │   └─ debugging/metrics/monitoring: 初始化可观测性                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 阶段四: 测试收集                                                       │   │
│  │   └─ 扫描 testpaths 目录                                              │   │
│  │   └─ 解析 conftest.py                                                 │   │
│  │   └─ 收集测试函数/类/模块                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 阶段五: pytest_sessionstart                                           │   │
│  │   └─ 项目 conftest.py: 添加 Allure 环境信息                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 阶段六: 测试执行 (每个测试用例)                                         │   │
│  │   ┌───────────────────────────────────────────────────────────────┐ │   │
│  │   │ Setup 阶段                                                     │ │   │
│  │   │   └─ 解析 fixture 依赖图                                       │ │   │
│  │   │   └─ 创建 Session 级别 fixtures (首次)                         │ │   │
│  │   │   └─ 创建 Function 级别 fixtures                               │ │   │
│  │   │   └─ autouse fixtures 自动执行                                 │ │   │
│  │   └───────────────────────────────────────────────────────────────┘ │   │
│  │   ┌───────────────────────────────────────────────────────────────┐ │   │
│  │   │ Call 阶段 (测试函数执行)                                        │ │   │
│  │   │   └─ HTTP 请求 → 中间件链 → 事件发布                           │ │   │
│  │   │   └─ 数据库操作 → UoW 事务                                     │ │   │
│  │   │   └─ Allure/调试 Observer 记录                                 │ │   │
│  │   └───────────────────────────────────────────────────────────────┘ │   │
│  │   ┌───────────────────────────────────────────────────────────────┐ │   │
│  │   │ Teardown 阶段                                                  │ │   │
│  │   │   └─ 数据清理 (cleanup fixture)                                │ │   │
│  │   │   └─ UoW commit/rollback                                       │ │   │
│  │   │   └─ 清理 Function 级别 fixtures                               │ │   │
│  │   │   └─ 清理测试 EventBus                                         │ │   │
│  │   └───────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 阶段七: 资源清理                                                       │   │
│  │   └─ pytest_sessionfinish: 生成报告                                   │   │
│  │   └─ pytest_unconfigure: 关闭 RuntimeContext                         │   │
│  │   └─ 释放数据库连接、Redis 连接、HTTP 客户端                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 阶段一：pytest 启动与插件发现

### 1.1 Entry Points 自动发现

当执行 `pytest` 命令时，pluggy 自动扫描所有已安装包的 `pytest11` Entry Points：

```
pip install df-test-framework
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│           pyproject.toml [project.entry-points.pytest11]     │
├─────────────────────────────────────────────────────────────┤
│  df_test_framework_core       → fixtures.core               │
│  df_test_framework_env        → plugins.env_plugin          │
│  df_test_framework_logging    → plugins.logging_plugin      │
│  df_test_framework_markers    → plugins.markers             │
│  df_test_framework_allure     → fixtures.allure             │
│  df_test_framework_debugging  → fixtures.debugging          │
│  df_test_framework_metrics    → fixtures.metrics            │
│  df_test_framework_monitoring → fixtures.monitoring         │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│              pluggy 加载插件模块                              │
│  import df_test_framework.testing.fixtures.core             │
│  import df_test_framework.testing.plugins.env_plugin        │
│  import ...                                                 │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 插件模块导入顺序

```python
# 导入顺序由 pluggy 控制，但 Hook 执行顺序可通过 @hookimpl 控制
# tryfirst=True  → 最先执行
# trylast=True   → 最后执行
# 默认           → 按注册顺序
```

---

## 阶段二：配置加载

### 2.1 配置加载优先级

```
优先级（从高到低）:

1. 环境变量
   └─ OBSERVABILITY__DEBUG_OUTPUT=true
   └─ HTTP__TIMEOUT=60

2. Secrets 文件
   └─ config/secrets/.env.local
   └─ DB__PASSWORD=xxx

3. 环境 YAML（支持 _extends 继承）
   └─ config/environments/{env}.yaml
   └─ 例: local.yaml extends test.yaml

4. 基础 YAML
   └─ config/base.yaml

5. .env 文件（回退模式）
   └─ .env + .env.{env}

6. 代码默认值
   └─ FrameworkSettings 类属性默认值
```

### 2.2 _extends 继承机制

```yaml
# config/environments/local.yaml
_extends: environments/test.yaml  # 继承 test.yaml
env: local
debug: true

observability:
  debug_output: true  # 覆盖 test.yaml 中的 false

test:
  keep_test_data: true
```

**继承解析流程**：

```
local.yaml
    │
    ├─ _extends: environments/test.yaml
    │       │
    │       ▼
    │   test.yaml
    │       │
    │       └─ (无 _extends，终止)
    │
    ▼
深度合并: test.yaml ← local.yaml
    │
    ▼
最终配置
```

### 2.3 深度合并规则

```python
def _deep_merge(base: dict, override: dict) -> dict:
    """
    递归合并嵌套字典，override 中的值覆盖 base 中的值。

    规则：
    - 两个都是 dict → 递归合并
    - 否则 → override 覆盖 base
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
```

**示例**：

```yaml
# base.yaml
observability:
  enabled: true
  debug_output: false
  allure_recording: true

# local.yaml (只覆盖 debug_output)
observability:
  debug_output: true

# 合并结果
observability:
  enabled: true           # 保留 base
  debug_output: true      # 被 local 覆盖
  allure_recording: true  # 保留 base
```

---

## 阶段三：pytest_configure Hooks

### 3.1 Hook 执行顺序

```
pytest_addoption (注册命令行选项)
        │
        ▼
pytest_configure (按优先级顺序执行)
        │
        ├─ 1. env_plugin (tryfirst=True) ─────────────────────┐
        │      ├─ 解析 --env 参数                              │
        │      ├─ clear_settings_cache()                      │
        │      ├─ os.environ["ENV"] = env                     │
        │      ├─ settings = get_settings_for_class(...)      │
        │      ├─ config._df_settings = settings              │
        │      └─ config._df_current_env = env                │
        │                                                      │
        ├─ 2. core (默认顺序) ─────────────────────────────────┐
        │      ├─ 检查 config._df_settings 是否存在            │
        │      ├─ RuntimeBuilder().with_settings().build()    │
        │      ├─ config._df_runtime = runtime_context        │
        │      └─ 注册 keep_data marker                        │
        │                                                      │
        ├─ 3. logging_plugin (默认顺序) ───────────────────────┐
        │      └─ 配置 loguru → logging 桥接                   │
        │         (pytest live log 可显示 loguru 日志)         │
        │                                                      │
        ├─ 4. markers (默认顺序) ──────────────────────────────┐
        │      └─ 注册环境相关 markers                          │
        │                                                      │
        ├─ 5. allure (默认顺序) ───────────────────────────────┐
        │      └─ 配置 Allure 报告                              │
        │                                                      │
        ├─ 6. debugging (默认顺序) ────────────────────────────┐
        │      └─ 注册 _auto_debug_by_marker fixture          │
        │                                                      │
        ├─ 7. metrics (默认顺序) ──────────────────────────────┐
        │      └─ 注册 metrics_manager, metrics_observer      │
        │                                                      │
        └─ 8. monitoring (默认顺序) ───────────────────────────┐
               └─ 注册 monitoring_observer, db_monitoring     │
```

### 3.2 config 对象属性

```python
# pytest_configure 后，config 对象包含以下属性：

config._df_settings      # FrameworkSettings 实例
config._df_current_env   # 当前环境名称 (如 "local")
config._df_env_name      # --env 参数原始值
config._df_config_dir    # 配置目录路径
config._df_runtime       # RuntimeContext 实例
config._df_cache_cleared # 配置缓存是否已清理
config._df_test_buses    # 测试隔离的 EventBus 字典 (延迟创建)
```

---

## 阶段四：测试收集

### 4.1 收集流程

```
pytest tests/ --env=local
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    测试收集阶段                               │
├─────────────────────────────────────────────────────────────┤
│  1. 扫描 testpaths (pyproject.toml 配置)                     │
│     └─ testpaths = ["tests"]                                │
│                                                             │
│  2. 解析 conftest.py 层级                                    │
│     └─ tests/conftest.py                                    │
│     └─ tests/api/conftest.py                                │
│     └─ tests/api/orders/conftest.py                         │
│                                                             │
│  3. 收集测试项                                               │
│     └─ python_files = ["test_*.py"]                         │
│     └─ python_classes = ["Test*"]                           │
│     └─ python_functions = ["test_*"]                        │
│                                                             │
│  4. 应用 markers 过滤                                        │
│     └─ pytest -m smoke  → 只运行 @pytest.mark.smoke         │
│     └─ pytest -m "not slow"  → 排除 @pytest.mark.slow       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 阶段五：Fixture 解析与创建

### 5.1 Fixture 依赖图

```
┌─────────────────────────────────────────────────────────────┐
│                   Session 级别 Fixtures                      │
│                   (整个测试 Session 只创建一次)               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  runtime ◄──────────────────────────────────────────────┐   │
│     │ (从 config._df_runtime 获取)                       │   │
│     │                                                    │   │
│     ├─► http_client ◄─────────────────────────────────┐ │   │
│     │      └─ runtime.http_client()                   │ │   │
│     │                                                 │ │   │
│     ├─► database ◄───────────────────────────────────┐│ │   │
│     │      └─ runtime.database()                     ││ │   │
│     │                                                ││ │   │
│     ├─► redis_client ◄──────────────────────────────┐││ │   │
│     │      └─ runtime.redis()                       │││ │   │
│     │                                               │││ │   │
│     └─► settings ◄─────────────────────────────────┐│││ │   │
│            └─ runtime.settings                     ││││ │   │
│                                                    ││││ │   │
│  metrics_manager ◄─────────────────────────────────┘│││ │   │
│  metrics_observer ◄─────────────────────────────────┘││ │   │
│  monitoring_plugin ◄─────────────────────────────────┘│ │   │
│                                                       │ │   │
└───────────────────────────────────────────────────────┼─┼───┘
                                                        │ │
┌───────────────────────────────────────────────────────┼─┼───┐
│                   Function 级别 Fixtures              │ │   │
│                   (每个测试函数创建一次)               │ │   │
├───────────────────────────────────────────────────────┼─┼───┤
│                                                       │ │   │
│  uow ◄────────────────────────────────────────────────┼─┘   │
│     │ 依赖: runtime, database                         │     │
│     │ 创建: 独立的 EventBus + UnitOfWork              │     │
│     │                                                 │     │
│  cleanup ◄────────────────────────────────────────────┘     │
│     │ 依赖: settings, uow                                   │
│     │ 创建: CleanupManager                                  │
│     │                                                       │
│  event_bus ◄────────────────────────────────────────────────│
│     │ 创建: 测试隔离的 EventBus                              │
│     │                                                       │
│  allure_observer ◄──────────────────────────────────────────│
│     │ autouse=True                                          │
│     │ 订阅 event_bus，记录到 Allure                          │
│     │                                                       │
│  _auto_debug_by_marker ◄────────────────────────────────────│
│       autouse=True                                          │
│       检查 debug_output 配置，创建 ConsoleDebugObserver     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Fixture 创建时机

```python
# Session 级别: 首个测试用例 setup 时创建，session 结束时销毁
@pytest.fixture(scope="session")
def runtime(request):
    return request.config._df_runtime  # 从 config 获取，不创建

@pytest.fixture(scope="session")
def http_client(runtime):
    return runtime.http_client()  # 首次调用时创建

# Function 级别: 每个测试函数 setup 时创建，teardown 时销毁
@pytest.fixture
def uow(request, runtime, database):
    # 获取测试隔离的 EventBus
    test_id = request.node.nodeid
    event_bus = _get_test_event_bus(request.config, test_id)

    # 创建 UnitOfWork
    uow = UnitOfWork(database.session_factory, event_bus=event_bus)

    yield uow

    # Teardown: 提交或回滚
    if request.node.get_closest_marker("keep_data"):
        uow.commit()
    else:
        uow.rollback()

    # 清理 EventBus
    _cleanup_test_event_bus(request.config, test_id)
```

### 5.3 autouse Fixtures

以下 fixtures 会自动执行，无需显式声明：

| Fixture | Scope | 作用 |
|---------|-------|------|
| `allure_observer` | function | 自动订阅事件，记录到 Allure 报告 |
| `_auto_debug_by_marker` | function | 根据配置/marker 启用调试输出 |

---

## 阶段六：测试执行

### 6.1 单个测试执行流程

```
test_create_order(http_client, cleanup, uow)
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                      Setup 阶段                              │
├─────────────────────────────────────────────────────────────┤
│  1. 解析 fixture 依赖                                        │
│     └─ http_client → runtime → config._df_runtime           │
│     └─ cleanup → settings, uow                              │
│     └─ uow → runtime, database                              │
│                                                             │
│  2. 创建 Session fixtures (如果尚未创建)                      │
│     └─ runtime: 从 config 获取                               │
│     └─ http_client: runtime.http_client()                   │
│     └─ database: runtime.database()                         │
│                                                             │
│  3. 创建 Function fixtures                                   │
│     └─ event_bus: 测试隔离的 EventBus                        │
│     └─ uow: UnitOfWork(session_factory, event_bus)          │
│     └─ cleanup: CleanupManager(settings, uow)               │
│                                                             │
│  4. 执行 autouse fixtures                                    │
│     └─ allure_observer: 订阅 event_bus                       │
│     └─ _auto_debug_by_marker: 检查 debug_output             │
│        ├─ @pytest.mark.debug → 强制启用                      │
│        ├─ observability.debug_output=true → 启用            │
│        └─ 创建 ConsoleDebugObserver，订阅 event_bus         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                      Call 阶段                               │
├─────────────────────────────────────────────────────────────┤
│  def test_create_order(http_client, cleanup, uow):          │
│      # HTTP 请求                                             │
│      response = http_client.post("/orders", json=data)      │
│          │                                                  │
│          ├─► 中间件链执行 (洋葱模型)                          │
│          │   ┌─────────────────────────────────────────┐    │
│          │   │ RetryMiddleware                         │    │
│          │   │   └─► SignatureMiddleware               │    │
│          │   │         └─► BearerTokenMiddleware       │    │
│          │   │               └─► LoggingMiddleware     │    │
│          │   │                     └─► [HTTP 请求]     │    │
│          │   │                     ◄── [HTTP 响应]     │    │
│          │   │               ◄── LoggingMiddleware     │    │
│          │   │         ◄── BearerTokenMiddleware       │    │
│          │   │   ◄── SignatureMiddleware               │    │
│          │   │ ◄── RetryMiddleware                     │    │
│          │   └─────────────────────────────────────────┘    │
│          │                                                  │
│          └─► 事件发布                                        │
│              ├─ HttpRequestStartEvent                       │
│              │   └─► AllureObserver.handle_start()         │
│              │   └─► ConsoleDebugObserver.on_request()     │
│              │                                              │
│              └─ HttpRequestEndEvent                         │
│                  └─► AllureObserver.handle_end()           │
│                  └─► ConsoleDebugObserver.on_response()    │
│                                                             │
│      # 数据库操作                                            │
│      order = uow.orders.create(order_data)                  │
│          │                                                  │
│          └─► 事件发布: RepositoryEvent                       │
│                                                             │
│      # 注册清理                                              │
│      cleanup.add("orders", order.id)                        │
│                                                             │
│      # 断言                                                  │
│      assert response.status_code == 201                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Teardown 阶段                             │
├─────────────────────────────────────────────────────────────┤
│  1. cleanup fixture teardown                                 │
│     ├─ 如果有 --keep-test-data 或 @pytest.mark.keep_data    │
│     │   └─ 记录保留的数据，不执行清理                         │
│     └─ 否则                                                  │
│         └─ 执行注册的清理操作                                 │
│                                                             │
│  2. uow fixture teardown                                     │
│     ├─ 如果 keep_data                                        │
│     │   └─ uow.commit()                                     │
│     └─ 否则                                                  │
│         └─ uow.rollback()                                   │
│                                                             │
│  3. 清理 autouse fixtures                                    │
│     └─ allure_observer: 取消订阅                             │
│     └─ _auto_debug_by_marker: 取消订阅                       │
│                                                             │
│  4. 清理测试 EventBus                                        │
│     └─ _cleanup_test_event_bus(config, test_id)             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 HTTP 中间件链执行

```
http_client.post("/orders", json=data)
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    中间件链 (洋葱模型)                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  请求流向 ──────────────────────────────────────────►        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 1. RetryMiddleware                                   │   │
│  │    ├─ 记录重试次数                                    │   │
│  │    └─ 调用 next(request)                             │   │
│  │    ┌─────────────────────────────────────────────┐   │   │
│  │    │ 2. SignatureMiddleware                       │   │   │
│  │    │    ├─ 检查 include_paths 匹配                 │   │   │
│  │    │    ├─ 计算签名 (MD5/SHA256/HMAC)             │   │   │
│  │    │    ├─ 添加 X-Sign, X-Timestamp 头             │   │   │
│  │    │    └─ 调用 next(request)                     │   │   │
│  │    │    ┌─────────────────────────────────────┐   │   │   │
│  │    │    │ 3. BearerTokenMiddleware             │   │   │   │
│  │    │    │    ├─ 检查 include_paths 匹配         │   │   │   │
│  │    │    │    ├─ 添加 Authorization: Bearer xxx │   │   │   │
│  │    │    │    └─ 调用 next(request)             │   │   │   │
│  │    │    │    ┌─────────────────────────────┐   │   │   │   │
│  │    │    │    │ 4. [实际 HTTP 请求]          │   │   │   │   │
│  │    │    │    │    └─► httpx.request()      │   │   │   │   │
│  │    │    │    │    ◄── HTTP Response        │   │   │   │   │
│  │    │    │    └─────────────────────────────┘   │   │   │   │
│  │    │    │    ◄── 返回 response                 │   │   │   │
│  │    │    └─────────────────────────────────────┘   │   │   │
│  │    │    ◄── 返回 response                         │   │   │
│  │    └─────────────────────────────────────────────┘   │   │
│  │    ◄── 如果失败且可重试，重新执行                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ◄────────────────────────────────────────── 响应流向        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 事件发布与订阅

```
┌─────────────────────────────────────────────────────────────┐
│                    EventBus 发布/订阅                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  HttpClient.request()                                       │
│      │                                                      │
│      ├─► event_bus.publish_sync(HttpRequestStartEvent)      │
│      │       │                                              │
│      │       ├─► AllureObserver.handle_start()              │
│      │       │   └─ allure.attach(request_body)             │
│      │       │                                              │
│      │       └─► ConsoleDebugObserver.on_request()          │
│      │           └─ 彩色打印请求信息                          │
│      │                                                      │
│      ├─► [执行 HTTP 请求]                                    │
│      │                                                      │
│      └─► event_bus.publish_sync(HttpRequestEndEvent)        │
│              │                                              │
│              ├─► AllureObserver.handle_end()                │
│              │   └─ allure.attach(response_body)            │
│              │                                              │
│              └─► ConsoleDebugObserver.on_response()         │
│                  └─ 彩色打印响应信息                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 阶段七：资源清理

### 7.1 pytest_sessionfinish

```python
def pytest_sessionfinish(session, exitstatus):
    """测试 Session 结束时执行"""
    # 生成测试报告
    # Allure 报告已通过 allure-pytest 插件自动生成
```

### 7.2 pytest_unconfigure

```
pytest_unconfigure 执行顺序 (与 pytest_configure 相反):

1. core.py
   ├─ 关闭 RuntimeContext
   │   ├─ http_client.close()
   │   ├─ database.close()
   │   └─ redis_client.close()
   │
   └─ 清理所有测试 EventBus
       └─ config._df_test_buses.clear()

2. 其他插件的清理...
```

---

## 关键机制详解

### 调试输出生效条件

```python
def _is_global_debug_enabled() -> bool:
    """检查是否全局启用调试输出"""
    settings = get_settings()
    obs = settings.observability
    return obs.enabled and obs.debug_output

# 调试输出启用优先级:
# 1. @pytest.mark.debug → 强制启用 (最高优先级)
# 2. console_debugger fixture 显式使用 → 启用
# 3. observability.debug_output=true → 全局启用
# 4. observability.debug_output=false → 禁用 (默认)
```

### 测试数据保留机制

```python
# 方式1: 命令行参数
pytest tests/ --keep-test-data

# 方式2: marker
@pytest.mark.keep_data
def test_example():
    pass

# 方式3: 配置文件
# config/environments/local.yaml
test:
  keep_test_data: true

# 生效流程:
# 1. cleanup fixture 检查 keep_test_data 配置
# 2. 如果为 true，跳过清理操作
# 3. uow fixture 检查 keep_data marker
# 4. 如果有，执行 commit() 而不是 rollback()
```

### 测试隔离机制

```python
# 每个测试用例有独立的 EventBus

def _get_test_event_bus(config: pytest.Config, test_id: str) -> EventBus:
    """获取测试专用 EventBus"""
    if not hasattr(config, "_df_test_buses"):
        config._df_test_buses = {}

    if test_id not in config._df_test_buses:
        config._df_test_buses[test_id] = EventBus()

    return config._df_test_buses[test_id]

# 好处:
# 1. 测试 A 的事件不会影响测试 B
# 2. 每个测试可以有独立的订阅者
# 3. pytest-xdist 并行执行时不会冲突
```

---

## 参考文档

- [PLUGIN_SYSTEM_V3.37.md](./PLUGIN_SYSTEM_V3.37.md) - pytest 插件系统架构
- [OVERVIEW_V3.17.md](./OVERVIEW_V3.17.md) - 五层架构总览
- [配置管理分析](./config-management-analysis.md) - 配置系统详解
- [中间件系统指南](../guides/middleware_guide.md) - HTTP 中间件使用
- [测试数据清理](../guides/test_data_cleanup.md) - 数据清理机制