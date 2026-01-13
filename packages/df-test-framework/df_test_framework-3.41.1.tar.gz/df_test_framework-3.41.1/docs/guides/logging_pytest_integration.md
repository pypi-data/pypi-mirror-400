# pytest 日志集成指南

> **版本要求**: df-test-framework >= 3.38.7
> **更新日期**: 2025-12-26

---

## 概述

本指南介绍 structlog 与 pytest 的集成方案。v3.38.6 实现了两阶段初始化机制，确保从框架加载开始就使用统一的日志格式。

### 核心特性

- **两阶段初始化** - 模块加载时即完成 structlog 早期配置（v3.38.6）
- **统一日志格式** - pytest live log 使用 ProcessorFormatter 渲染
- **无重复输出** - structlog 不直接输出，由 pytest 统一控制
- **彩色显示** - 开发环境支持彩色日志输出
- **第三方库支持** - httpx、sqlalchemy 等库的日志格式统一

---

## 架构设计

### v3.38.6 架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│  pytest + structlog 集成架构 (v3.38.6)                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  logger.info("message", key=value)    ← structlog API                  │
│          │                                                              │
│          ▼                                                              │
│  structlog Processors 管道:                                            │
│     ├─ merge_contextvars              (合并上下文)                       │
│     ├─ add_logger_name                (添加 logger 名称)                │
│     ├─ add_log_level                  (添加级别)                        │
│     ├─ PositionalArgumentsFormatter   (处理 % 格式化，v3.38.5)          │
│     ├─ ExtraAdder                     (处理 extra 参数，v3.38.5)        │
│     ├─ _sanitize_sensitive_data       (脱敏)                            │
│     ├─ TimeStamper                    (时间戳)                          │
│     ├─ _add_trace_info                (OpenTelemetry)                  │
│     └─ wrap_for_formatter             (包装给 ProcessorFormatter)      │
│          │                                                              │
│          ▼                                                              │
│  stdlib logging.Logger                ← structlog 使用 stdlib 后端      │
│          │                                                              │
│          ▼                                                              │
│  pytest logging-plugin handlers:                                       │
│     ├─ log_cli_handler (实时显示)     ← 使用 ProcessorFormatter         │
│     └─ log_file_handler (文件日志)    ← 使用 ProcessorFormatter         │
│          │                                                              │
│          ▼                                                              │
│  ProcessorFormatter 渲染输出:                                           │
│     ├─ text: ConsoleRenderer (彩色)                                    │
│     ├─ json: JSONRenderer                                              │
│     └─ logfmt: LogfmtRenderer (v3.38.5)                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 关键设计决策

1. **两阶段初始化** - 模块加载时即配置 structlog（v3.38.6）
2. **禁用 structlog 控制台输出** - 避免与 pytest 输出冲突
3. **替换 pytest handler formatter** - 使用 ProcessorFormatter 统一格式
4. **通过 pluginmanager 访问** - structlog 官方推荐方式

---

## 配置方式

### 自动配置（推荐）

通过 Entry Points 自动加载，无需手动配置：

```python
# conftest.py - 插件自动加载
# 如需显式声明：
pytest_plugins = ["df_test_framework.testing.plugins.logging_plugin"]
```

### pyproject.toml 配置

```toml
[tool.pytest]
# Live logging: 实时显示日志
log_cli = true
log_cli_level = "INFO"

# 注意：log_cli_format 会被 ProcessorFormatter 覆盖
# 以下配置仅作为备用
log_cli_format = "%(message)s"
log_cli_date_format = "%Y-%m-%d %H:%M:%S"

# 捕获日志（测试失败时显示）
log_level = "DEBUG"
```

### YAML 配置

```yaml
# config/base.yaml
logging:
  level: DEBUG
  format: text       # text（开发）/ json（生产）/ logfmt（Loki）
  sanitize: true     # 敏感信息脱敏
  # pytest 环境下 enable_console 会自动设为 false
```

---

## 日志输出效果

### 开发环境 (format: text)

```
-------------------------- live log sessionstart --------------------------
2025-12-25 10:27:55.139176 [info] 环境信息已添加到Allure报告 [allure.helper]

tests/api/test_example.py::TestExample::test_uow_pattern
----------------------------- live log setup ------------------------------
2025-12-25 10:27:55.451533 [info] 数据库连接已建立 [databases.database]
PASSED
---------------------------- live log teardown ----------------------------
2025-12-25 10:27:55.479190 [info] UnitOfWork: 数据已回滚 [databases.uow]
```

### 生产环境 (format: json)

```
{"timestamp": "2025-12-25T10:27:55.139176Z", "level": "info", "event": "环境信息已添加到Allure报告", "logger": "allure.helper"}
```

### Loki/Prometheus (format: logfmt)

```
timestamp=2025-12-25T10:27:55.139176Z level=info logger=allure.helper event="环境信息已添加到Allure报告"
```

---

## 使用指南

### 基础使用

```python
from df_test_framework.infrastructure.logging import get_logger

logger = get_logger(__name__)

def test_example():
    logger.info("测试开始", test_id=123)
    # ... 测试逻辑
    logger.info("测试完成", result="success")
```

### 上下文绑定

```python
from df_test_framework.infrastructure.logging import (
    bind_contextvars,
    clear_contextvars,
    get_logger,
)

def test_with_context():
    # 绑定请求上下文
    bind_contextvars(request_id="req_123", user_id=456)

    logger = get_logger(__name__)
    logger.info("处理请求")  # 自动包含 request_id, user_id

    # 清理上下文
    clear_contextvars()
```

### 第三方库日志

v3.38.5 自动处理第三方库的日志格式：

```python
import logging

def test_third_party_logging():
    # 第三方库使用标准 logging
    stdlib_logger = logging.getLogger("httpx")

    # % 格式化自动处理
    stdlib_logger.info("Request %s %s", "GET", "/api/users")

    # extra 参数自动处理
    stdlib_logger.info("Response", extra={"status": 200, "duration": 45.5})
```

---

## 实现原理

### logging_plugin.py 核心逻辑（v3.38.6）

```python
# 阶段 1：模块加载时（_early_init_logging）
def _early_init_logging() -> None:
    """早期初始化 - 模块加载时立即执行"""
    default_config = LoggingConfig(
        level="DEBUG",
        format="text",
        sanitize=True,
        enable_console=False,  # 由 pytest 统一处理
    )
    configure_logging(default_config)

# 模块加载时立即执行
_early_init_logging()

# 阶段 2：pytest 配置阶段
@hookimpl(trylast=True)
def pytest_configure(config: pytest.Config) -> None:
    """配置阶段：从 settings 读取配置，禁用 structlog 控制台输出"""
    logging_config = logging_config.model_copy(update={"enable_console": False})
    configure_logging(logging_config)

# 阶段 3：Session 开始
@hookimpl(tryfirst=True)
def pytest_sessionstart(session: pytest.Session) -> None:
    """Session 开始：替换 pytest handlers 的 formatter"""
    processor_formatter = create_processor_formatter(_logging_config)

    # 官方推荐：通过 pluginmanager 访问 pytest 的 logging 插件
    logging_plugin = session.config.pluginmanager.get_plugin("logging-plugin")
    if logging_plugin is not None:
        logging_plugin.log_cli_handler.setFormatter(processor_formatter)
```

**两阶段初始化的优势**：
- 阶段 1 确保任何 `get_logger()` 调用都能正常工作
- 阶段 2 根据实际配置重新初始化
- 阶段 3 统一 pytest 的日志格式

### ProcessorFormatter 说明

```python
from df_test_framework.infrastructure.logging import create_processor_formatter

# 创建 ProcessorFormatter（用于自定义 handler）
formatter = create_processor_formatter(logging_config)

# ProcessorFormatter 包含：
# - foreign_pre_chain: 处理第三方库日志（ExtraAdder、PositionalArgumentsFormatter）
# - processors: 最终渲染（ConsoleRenderer/JSONRenderer/LogfmtRenderer）
```

---

## 常见问题

### Q1: 日志没有显示？

检查以下配置：

```toml
[tool.pytest]
log_cli = true           # 必须启用
log_cli_level = "DEBUG"  # 级别足够低
```

### Q2: 日志重复显示？

确认使用 v3.38.5+，旧版本可能有此问题。

### Q3: 日志显示为 dict 格式？

确认 logging_plugin 已正确加载：

```python
# conftest.py
pytest_plugins = ["df_test_framework.testing.plugins.logging_plugin"]
```

### Q4: 如何在测试中断言日志？

方式 1：使用 Mock

```python
from unittest.mock import Mock
from df_test_framework.infrastructure.logging import Logger

def test_with_mock():
    mock_logger = Mock(spec=Logger)
    service = MyService(mock_logger)

    service.do_something()

    mock_logger.info.assert_called_once_with("操作完成", result="success")
```

方式 2：使用 pytest-structlog 插件（可选）

```bash
pip install pytest-structlog
```

```python
def test_with_structlog(log):
    my_function()
    assert log.has("expected message", key="value")
```

### Q5: 如何禁用实时日志？

```bash
pytest --log-cli-level=CRITICAL  # 只显示 CRITICAL 级别
```

或在配置中：

```toml
[tool.pytest]
log_cli = false
```

---

## 与 pytest-structlog 对比

| 特性 | 框架内置方案 | pytest-structlog |
|------|-------------|-----------------|
| 日志断言 | Mock 或 caplog | `log.has()` |
| 统一输出格式 | ProcessorFormatter | 自定义 |
| 与框架集成 | 自动 | 需配置 |
| 额外依赖 | 无 | 需安装 |
| 配置驱动 | LoggingConfig | 需手动 |

**建议**：一般场景使用框架内置方案，需要复杂日志断言时考虑 pytest-structlog。

---

## 参考资料

### 官方文档
- [structlog Standard Library Logging](https://www.structlog.org/en/stable/standard-library.html)
- [pytest logging documentation](https://docs.pytest.org/en/stable/how-to/logging.html)
- [pytest-structlog PyPI](https://pypi.org/project/pytest-structlog/)

### 框架文档
- [日志配置指南](logging_configuration.md)
- [现代化日志最佳实践](modern_logging_best_practices.md)
- [可观测性架构设计](../architecture/observability-architecture.md) - 控制台日志架构（LoggingMiddleware vs ObservabilityLogger）
- [v3.38.6 发布说明](../releases/v3.38.6.md)

---

## 版本历史

| 版本 | 变更 |
|------|------|
| v3.38.7 | 简化架构：日志级别由消息性质决定，全局配置控制过滤 |
| v3.38.6 | 两阶段初始化：模块加载时即完成 structlog 早期配置，确保日志格式统一 |
| v3.38.5 | 修复 pytest 集成：禁用 structlog 控制台输出，替换 pytest handler formatter |
| v3.38.2 | 从 loguru 迁移到 structlog，使用 stdlib logging 后端 |
| v3.26.0 | loguru → logging 桥接方案（已废弃） |
