# 现代化日志系统使用指南

> **版本**: v3.38.7
> **更新日期**: 2025-12-26
> **适用范围**: df-test-framework >= 3.38.7

---

## 📋 目录

1. [概述](#概述)
2. [快速开始](#快速开始)
3. [核心架构](#核心架构)
4. [使用指南](#使用指南)
5. [配置管理](#配置管理)
6. [pytest 集成](#pytest-集成)
7. [可观测性集成](#可观测性集成)
8. [最佳实践](#最佳实践)
9. [常见问题](#常见问题)

---

## 概述

### v3.38.7 最新更新

v3.38.7 版本简化日志系统架构，遵循 structlog 最佳实践：

- ✅ **日志级别由消息性质决定** - 使用 `debug()`/`info()`/`error()` 等方法
- ✅ **全局配置控制过滤** - YAML `logging.level` 统一控制显示级别
- ✅ **直接使用 structlog** - `get_logger()` 返回原生 BoundLogger，无包装器
- ✅ **Logger Protocol 精简** - 只定义 structlog.BoundLogger 原生方法签名

### v3.38.5 更新

v3.38.5 版本按照 structlog 25.5.0 官方最佳实践进行了优化：

- ✅ **PositionalArgumentsFormatter** - 支持第三方库 % 格式化日志
- ✅ **ExtraAdder** - 支持第三方库 extra 参数
- ✅ **LogfmtRenderer** - 新增 logfmt 输出格式（Loki/Prometheus）
- ✅ **pytest 集成修复** - 统一日志格式，无重复输出

### v3.38.2 重大更新

v3.38.2 版本对日志系统进行了完全重写：

- ✅ **从 loguru 迁移到 structlog** - 更好的结构化日志支持
- ✅ **统一日志接口** - 所有模块使用 `get_logger(__name__)`
- ✅ **pytest 原生支持** - structlog 使用 stdlib logging，无需桥接
- ✅ **时间格式统一** - 使用 `%Y-%m-%d %H:%M:%S.%f` 格式
- ✅ **OpenTelemetry 集成** - 自动注入 trace_id/span_id

### 核心特性

| 特性 | 说明 |
|------|------|
| **结构化日志** | JSON/logfmt 格式，机器可读，便于日志聚合 |
| **上下文传播** | request_id/user_id 自动关联 |
| **OpenTelemetry** | trace_id/span_id 自动注入 |
| **敏感信息脱敏** | 自动过滤密码、token 等 |
| **第三方库支持** | httpx、sqlalchemy 等库日志格式统一 |
| **pytest 集成** | ProcessorFormatter 统一格式，无重复 |

---

## 快速开始

### 基础使用

```python
from df_test_framework.infrastructure.logging import get_logger

# 获取模块级 logger
logger = get_logger(__name__)

# 结构化日志
logger.info("用户登录", user_id=123, username="alice")
logger.debug("SQL 查询", sql="SELECT * FROM users", params={"id": 123})
logger.error("请求失败", error="timeout", retry_count=3)
```

### 配置日志

```python
from df_test_framework.infrastructure.logging import configure_logging

# 开发环境（彩色输出）
configure_logging(env="dev", level="DEBUG")

# 生产环境（JSON 输出）
configure_logging(env="prod", level="INFO")
```

---

## 核心架构

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│  日志系统架构 (v3.38.7)                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  应用代码 / 第三方库 (httpx, sqlalchemy...)                │
│     ↓                                                       │
│  get_logger(__name__) → structlog.get_logger()             │
│     ↓                                                       │
│  structlog.BoundLogger (满足 Logger Protocol 类型注解)      │
│     ↓                                                       │
│  Processors 处理管道 (v3.38.5 顺序):                        │
│     ├─ merge_contextvars (上下文合并)                       │
│     ├─ add_logger_name (添加 logger 名称)                   │
│     ├─ add_log_level (添加日志级别)                         │
│     ├─ PositionalArgumentsFormatter (% 格式化) ← v3.38.5   │
│     ├─ ExtraAdder (extra 参数) ← v3.38.5                   │
│     ├─ _sanitize_sensitive_data (敏感信息脱敏)              │
│     ├─ TimeStamper (时间戳)                                 │
│     ├─ CallsiteParameterAdder (调用位置，可选)             │
│     ├─ _add_trace_info (OpenTelemetry 集成)                 │
│     ├─ StackInfoRenderer (堆栈信息)                         │
│     └─ UnicodeDecoder (Unicode 解码)                        │
│     ↓                                                       │
│  ProcessorFormatter 渲染:                                   │
│     ├─ text: ConsoleRenderer (彩色)                         │
│     ├─ json: JSONRenderer (orjson 可选)                     │
│     └─ logfmt: LogfmtRenderer ← v3.38.5                    │
│     ↓                                                       │
│  stdlib logging → pytest handlers                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件

| 组件 | 文件 | 职责 |
|------|------|------|
| Logger Protocol | `interface.py` | 类型注解接口（定义 structlog.BoundLogger 方法签名） |
| configure_logging | `config.py` | 配置 structlog 处理管道 |
| get_logger | `logger.py` | 工厂函数，直接返回 structlog.get_logger() |
| ObservabilityLogger | `observability.py` | HTTP/DB/Redis/UI 可观测性日志 |
| logging_plugin | `plugins/logging_plugin.py` | pytest 自动配置 |

### 核心设计理念（v3.38.7）

1. **日志级别由消息性质决定**
   - 调试信息 → `logger.debug()`
   - 操作确认 → `logger.info()`
   - 警告 → `logger.warning()`
   - 错误 → `logger.error()`

2. **全局配置控制过滤显示**
   ```yaml
   # config/base.yaml
   logging:
     level: INFO   # 控制显示级别，DEBUG 日志不显示
   ```

3. **Logger Protocol 只用于类型注解**
   - 不添加额外方法（如 `log(level, event)`）
   - structlog.BoundLogger 原生满足 Protocol

---

## 使用指南

### 基础日志

```python
from df_test_framework.infrastructure.logging import get_logger

logger = get_logger(__name__)

# 各级别日志
logger.debug("调试信息", variable=value)
logger.info("操作成功", order_id=123)
logger.warning("警告", cache_miss=True)
logger.error("错误", error_type="timeout")
logger.critical("严重错误", system="database")
```

### 上下文绑定

#### 方式 1: 使用 bind()

```python
# 创建绑定上下文的 logger
request_logger = logger.bind(request_id="req_123", user_id=456)

# 所有日志自动包含 request_id 和 user_id
request_logger.info("订单创建", order_id=789)
request_logger.info("支付处理", amount=100.0)
```

#### 方式 2: 使用 ContextVar（全局上下文）

```python
from df_test_framework.infrastructure.logging import (
    bind_contextvars,
    clear_contextvars,
    get_logger,
)

# 绑定全局上下文
bind_contextvars(request_id="req_123", user_id=456)

# 任何地方的 logger 都会自动包含这些字段
logger = get_logger(__name__)
logger.info("处理请求")  # 自动包含 request_id, user_id

# 请求结束时清理
clear_contextvars()
```

### 异常处理

```python
try:
    result = risky_operation()
except Exception as e:
    logger.exception(
        "操作失败",
        operation="risky_operation",
        error_type=type(e).__name__,
    )
    raise
```

### 依赖注入

```python
from df_test_framework.infrastructure.logging import Logger

class OrderService:
    """订单服务（依赖注入 Logger）"""

    def __init__(self, logger: Logger):
        self._logger = logger

    def create_order(self, order_id: int):
        self._logger.info("订单创建", order_id=order_id)

# 生产代码
from df_test_framework.infrastructure.logging import get_logger

logger = get_logger(__name__)
service = OrderService(logger)

# 测试代码
from unittest.mock import Mock

def test_create_order():
    mock_logger = Mock(spec=Logger)
    service = OrderService(mock_logger)

    service.create_order(123)

    mock_logger.info.assert_called_once_with("订单创建", order_id=123)
```

---

## 配置管理

### configure_logging API

```python
def configure_logging(
    env: str = "dev",
    level: str = "INFO",
    json_output: bool | None = None,
    enable_sanitize: bool = True,
) -> None:
    """配置日志系统

    Args:
        env: 环境名称 (dev/test/staging/prod)
        level: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        json_output: 是否使用 JSON 输出（None=根据环境自动判断）
        enable_sanitize: 是否启用敏感信息脱敏（默认启用）
    """
```

### 环境输出对比

**开发环境** (env="dev", json_output=False):
```
2025-12-25 11:35:07.590123 [info     ] 用户登录          user_id=123 username=alice
```

**生产环境** (env="prod", json_output=True):
```json
{
  "event": "用户登录",
  "user_id": 123,
  "username": "alice",
  "timestamp": "2025-12-25 11:35:07.590123",
  "level": "info",
  "logger": "myapp.auth"
}
```

### 敏感信息脱敏

自动脱敏以下字段：
- `password`, `passwd`, `pwd`
- `token`, `secret`, `api_key`
- `authorization`, `auth`, `credential`
- `access_token`, `refresh_token`

```python
logger.info("用户创建", username="alice", password="secret123")
# 输出: {"event": "用户创建", "username": "alice", "password": "******"}
```

---

## pytest 集成

### 自动配置

v3.38.2 的 pytest 插件自动配置 structlog，无需手动配置：

```python
# conftest.py - 通过 Entry Points 自动加载，无需显式配置
# 或者手动声明：
pytest_plugins = ["df_test_framework.testing.plugins.logging_plugin"]
```

### pyproject.toml 配置

```toml
[tool.pytest]
# 日志配置
log_cli = true
log_cli_level = "INFO"
log_cli_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
log_cli_date_format = "%Y-%m-%d %H:%M:%S"

# 捕获日志（测试失败时显示）
log_level = "DEBUG"
```

### 时间格式统一

v3.38.2 统一使用 `%Y-%m-%d %H:%M:%S.%f` 格式：
- structlog TimeStamper: `fmt="%Y-%m-%d %H:%M:%S.%f"`
- pytest log_cli_date_format: `"%Y-%m-%d %H:%M:%S"`

---

## 可观测性集成

### ObservabilityLogger

框架内置的可观测性日志器，用于记录 HTTP/DB/Redis/UI 操作：

```python
from df_test_framework.infrastructure.logging import http_logger, db_logger

# HTTP 请求日志
http_logger.request_start(method="POST", url="/api/orders")
http_logger.request_end(method="POST", url="/api/orders", status=201, duration_ms=45.5)

# 数据库查询日志
db_logger.query_start(operation="SELECT", table="users")
db_logger.query_end(operation="SELECT", table="users", duration_ms=12.3, rows=5)
```

### OpenTelemetry 集成

当安装了 opentelemetry 时，日志自动包含 trace 信息：

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("process_order")
def process_order(order_id: int):
    logger.info("处理订单", order_id=order_id)
    # 日志自动包含 trace_id 和 span_id
```

输出示例：
```json
{
  "event": "处理订单",
  "order_id": 789,
  "trace_id": "0af7651916cd43dd8448eb211c80319c",
  "span_id": "b7ad6b7169203331"
}
```

---

## 最佳实践

### 1. 使用结构化字段

```python
# ❌ 不推荐
logger.info(f"User {user_id} logged in from {ip}")

# ✅ 推荐
logger.info("用户登录", user_id=user_id, ip=ip)
```

### 2. 使用有意义的事件名称

```python
# ❌ 不推荐
logger.info("Something happened")

# ✅ 推荐
logger.info("订单创建成功", order_id=123, user_id=456)
```

### 3. 日志级别使用（由消息性质决定）

| 级别 | 使用场景 | 示例 |
|------|----------|------|
| DEBUG | 详细诊断信息 | SQL 查询、变量值、缓存命中 |
| INFO | 关键操作确认 | 登录成功、订单创建、环境初始化 |
| WARNING | 警告但不影响运行 | 缓存未命中、配置缺失使用默认值 |
| ERROR | 错误但可恢复 | API 超时重试、文件不存在 |
| CRITICAL | 严重错误 | 数据库连接失败、系统不可用 |

**重要**: 日志级别由消息性质决定，通过 YAML `logging.level` 配置控制显示过滤：

```yaml
# config/base.yaml
logging:
  level: DEBUG  # 显示所有日志
  level: INFO   # 隐藏 DEBUG 日志
  level: ERROR  # 只显示错误
```

### 4. 请求级上下文

```python
from df_test_framework.infrastructure.logging import (
    bind_contextvars,
    clear_contextvars,
)

def handle_request(request):
    # 请求开始时绑定上下文
    bind_contextvars(
        request_id=str(uuid.uuid4()),
        user_id=request.user.id,
        path=request.path,
    )

    try:
        # 处理请求...
        logger.info("请求处理完成")
    finally:
        # 请求结束时清理
        clear_contextvars()
```

---

## 常见问题

### Q1: 从 loguru 迁移需要修改什么？

**修改导入**：
```python
# 旧代码
from loguru import logger

# 新代码
from df_test_framework.infrastructure.logging import get_logger

logger = get_logger(__name__)
```

API 保持兼容：
- `logger.info("message", key=value)` ✅ 无需修改
- `logger.bind(key=value)` ✅ 无需修改
- `logger.exception("error")` ✅ 无需修改

### Q2: 如何在测试中验证日志？

```python
from unittest.mock import Mock
from df_test_framework.infrastructure.logging import Logger

def test_with_mock():
    mock_logger = Mock(spec=Logger)
    service = MyService(mock_logger)

    service.do_something()

    mock_logger.info.assert_called_once_with("操作完成", result="success")
```

### Q3: 如何关闭敏感信息脱敏？

```python
configure_logging(env="dev", enable_sanitize=False)
```

### Q4: 如何强制使用 JSON 输出？

```python
configure_logging(env="dev", json_output=True)
```

---

## 参考资源

### 框架文档
- [日志配置指南](logging_configuration.md)
- [分布式追踪指南](distributed_tracing.md)

### 官方文档
- [structlog 文档](https://www.structlog.org/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/)

---

## 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v3.38.7 | 2025-12-26 | 简化架构：日志级别由消息性质决定，全局配置控制过滤 |
| v3.38.6 | 2025-12-26 | 两阶段初始化，确保日志格式统一 |
| v3.38.5 | 2025-12-25 | structlog 25.5.0 最佳实践升级，修复 pytest 集成 |
| v3.38.4 | 2025-12-25 | ProcessorFormatter、orjson、CallsiteParameterAdder |
| v3.38.2 | 2025-12-25 | 从 loguru 迁移到 structlog，完全重写 |

---

**需要帮助？** 提交 Issue 到 [GitHub Issues](https://github.com/your-org/df-test-framework/issues)
