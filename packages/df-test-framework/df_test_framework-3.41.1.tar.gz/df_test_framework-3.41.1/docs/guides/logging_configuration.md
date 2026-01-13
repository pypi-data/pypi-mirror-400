# 日志配置指南

> **版本要求**: df-test-framework >= 3.38.7
> **更新日期**: 2025-12-26
> **structlog 版本**: 25.5.0

---

## 📋 目录

1. [概述](#概述)
2. [日志系统架构](#日志系统架构)
3. [配置方法](#配置方法)
4. [pytest 日志配置](#pytest-日志配置)
5. [时间格式配置](#时间格式配置)
6. [环境配置](#环境配置)
7. [常见问题排查](#常见问题排查)
8. [最佳实践](#最佳实践)

---

## 概述

### v3.38.2 重大变更

v3.38.2 版本将日志系统从 **loguru** 迁移到 **structlog**：

| 特性 | v3.38.1 (loguru) | v3.38.2 (structlog) |
|------|-----------------|---------------------|
| 日志库 | loguru | structlog |
| pytest 集成 | 需要桥接 | 原生支持（stdlib logging） |
| 时间格式 | `{time:YYYY-MM-DD HH:mm:ss}` | `%Y-%m-%d %H:%M:%S.%f` |
| 配置方式 | `setup_logger()` | `configure_logging()` |
| 导入方式 | `from loguru import logger` | `get_logger(__name__)` |

### 核心优势

- ✅ **日志级别由消息性质决定** - debug/info/error 调用对应方法（v3.38.7）
- ✅ **全局配置控制过滤** - YAML `logging.level` 统一控制显示级别（v3.38.7）
- ✅ **pytest 无缝集成** - ProcessorFormatter 统一格式，无重复输出（v3.38.5）
- ✅ **时间格式统一** - structlog 和 pytest 使用相同的 strftime 格式
- ✅ **结构化日志** - JSON/logfmt 输出，便于日志聚合
- ✅ **上下文传播** - 自动传播 request_id、user_id 等
- ✅ **第三方库支持** - PositionalArgumentsFormatter + ExtraAdder（v3.38.5）
- ✅ **多种输出格式** - text、json、logfmt（v3.38.5）
- ✅ **高性能** - orjson 可选支持（v3.38.4）

---

## 日志系统架构

### v3.38.7 架构

```
┌─────────────────────────────────────────────────────────────┐
│  日志系统架构 (v3.38.7 - structlog 25.5.0)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  logger.debug/info/error("msg", k=v)  ← 日志级别由消息决定  │
│  logging.info("msg %s", arg)          ← 第三方库           │
│          │                                                  │
│          ▼                                                  │
│  structlog Processors 管道:                                │
│     ├─ merge_contextvars (合并上下文)                       │
│     ├─ add_logger_name (logger 名称)                       │
│     ├─ add_log_level (添加级别)                            │
│     ├─ PositionalArgumentsFormatter (% 格式化) ← v3.38.5  │
│     ├─ ExtraAdder (extra 参数) ← v3.38.5                  │
│     ├─ sanitize_sensitive_data (脱敏)                      │
│     ├─ TimeStamper (时间戳)                                │
│     ├─ CallsiteParameterAdder (调用位置，可选)            │
│     ├─ _add_trace_info (OpenTelemetry)                    │
│     └─ wrap_for_formatter                                  │
│          │                                                  │
│          ▼                                                  │
│  ProcessorFormatter 渲染:                                  │
│     ├─ text: ConsoleRenderer (彩色)                        │
│     ├─ json: JSONRenderer (orjson 可选)                    │
│     └─ logfmt: LogfmtRenderer ← v3.38.5                   │
│          │                                                  │
│          ▼                                                  │
│  pytest logging-plugin handlers                            │
│     ├─ log_cli_handler (实时显示)                          │
│     └─ log_file_handler (文件日志)                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**关键点**：
- structlog 使用 stdlib logging 后端，pytest 可直接捕获
- v3.38.6 两阶段初始化，模块加载时即完成 structlog 配置
- 禁用 structlog 控制台输出，由 pytest 统一控制
- ProcessorFormatter 替换 pytest handler formatter，统一格式

---

## 配置方法

### configure_logging() API

```python
from df_test_framework.infrastructure.logging import configure_logging

configure_logging(
    env="dev",           # 环境: dev/test/staging/prod
    level="INFO",        # 级别: DEBUG/INFO/WARNING/ERROR/CRITICAL
    json_output=None,    # JSON 输出: None=自动, True=强制, False=禁用
    enable_sanitize=True # 敏感信息脱敏
)
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `env` | str | "dev" | 环境名称，影响输出格式 |
| `level` | str | "INFO" | 日志级别 |
| `json_output` | bool \| None | None | JSON 输出模式 |
| `enable_sanitize` | bool | True | 敏感信息脱敏 |

### 环境与输出格式

| 环境 | json_output | 输出格式 |
|------|-------------|----------|
| dev | None/False | 彩色控制台 |
| test | None/False | 彩色控制台 |
| staging | None | JSON |
| prod/production | None | JSON |
| 任意 | True | JSON |
| 任意 | False | 彩色控制台 |

---

## pytest 日志配置

### pyproject.toml 配置

```toml
[tool.pytest]
# Live logging: 实时显示日志
log_cli = true
log_cli_level = "INFO"
log_cli_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
log_cli_date_format = "%Y-%m-%d %H:%M:%S"

# 捕获日志（测试失败时显示）
log_level = "DEBUG"
log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
log_date_format = "%Y-%m-%d %H:%M:%S"
```

### 配置项说明

| 配置项 | 作用 | 默认值 | 推荐值 |
|--------|------|--------|--------|
| `log_cli` | 启用实时日志 | false | true |
| `log_cli_level` | 实时显示级别 | NOTSET | INFO |
| `log_cli_format` | 实时日志格式 | pytest 默认 | 见上方示例 |
| `log_cli_date_format` | 时间格式 | %H:%M:%S | %Y-%m-%d %H:%M:%S |
| `log_level` | 捕获级别 | NOTSET | DEBUG |

### 格式化语法

pytest 使用 Python logging 的格式化语法：

```
%(asctime)s       - 时间（由 log_cli_date_format 控制）
%(levelname)s     - 日志级别
%(levelname)-8s   - 左对齐，占 8 个字符
%(name)s          - logger 名称
%(funcName)s      - 函数名
%(lineno)d        - 行号
%(message)s       - 日志消息
```

---

## 时间格式配置

### v3.38.2 时间格式

v3.38.2 使用统一的 strftime 格式：

| 组件 | 格式 | 示例输出 |
|------|------|----------|
| structlog TimeStamper | `%Y-%m-%d %H:%M:%S.%f` | 2025-12-25 09:21:37.590123 |
| pytest log_cli_date_format | `%Y-%m-%d %H:%M:%S` | 2025-12-25 09:21:37 |

### 格式选项

| 格式字符串 | 精度 | 示例 |
|-----------|------|------|
| `%Y-%m-%d %H:%M:%S` | 秒 | 2025-12-25 09:21:37 |
| `%Y-%m-%d %H:%M:%S.%f` | 微秒 | 2025-12-25 09:21:37.590123 |

**注意**：Python strftime 的 `%f` 是微秒（6位），无法配置为 3 位毫秒。

### 统一配置

如需完全统一时间格式，可在 `pyproject.toml` 中使用微秒：

```toml
[tool.pytest]
log_cli_date_format = "%Y-%m-%d %H:%M:%S.%f"  # 微秒精度
```

---

## 环境配置

### 开发环境

```python
from df_test_framework.infrastructure.logging import configure_logging

configure_logging(
    env="dev",
    level="DEBUG",
    json_output=False,
)
```

输出示例：
```
2025-12-25 11:35:07.590123 [info     ] 用户登录          user_id=123 username=alice
```

### 生产环境

```python
configure_logging(
    env="prod",
    level="INFO",
    json_output=True,
)
```

输出示例：
```json
{"event": "用户登录", "user_id": 123, "username": "alice", "timestamp": "2025-12-25 11:35:07.590123", "level": "info"}
```

### 测试环境 (pytest)

pytest 插件自动配置，无需手动调用：

```python
# conftest.py - 通过 Entry Points 自动加载
# 或手动声明：
pytest_plugins = ["df_test_framework.testing.plugins.logging_plugin"]
```

---

## 常见问题排查

### Q1: 日志与测试名称混在同一行

**症状**：
```
tests/test_example.py::test_foo 2025-12-25 09:21:37 | INFO | ... - 日志内容
```

**原因**：v3.38.2 之前版本的桥接问题

**解决**：升级到 v3.38.2，使用 structlog 原生 stdlib 支持

---

### Q2: 测试失败时看不到 DEBUG 日志

**症状**：测试失败时的 "Captured log" 区域没有 DEBUG 级别日志

**原因**：`log_level` 配置过高

**解决**：
```toml
[tool.pytest]
log_level = "DEBUG"  # 捕获所有级别
```

注意区分：
- `log_cli_level` - 控制**实时显示**
- `log_level` - 控制**捕获级别**

---

### Q3: 敏感信息（密码、token）泄露到日志

**症状**：日志中出现明文密码或 token

**原因**：脱敏功能未启用

**解决**：确保 `enable_sanitize=True`（默认启用）

```python
configure_logging(env="dev", enable_sanitize=True)
```

自动脱敏的字段：
- password, passwd, pwd
- token, secret, api_key, apikey
- authorization, auth, credential
- access_token, refresh_token

---

### Q4: 从 loguru 迁移后日志格式变化

**症状**：日志格式与之前不同

**原因**：v3.38.2 使用 structlog，格式有变化

**适应**：
- 开发环境：彩色输出，格式类似
- 生产环境：JSON 输出，更规范
- 时间格式：使用 strftime 格式，与 pytest 统一

---

### Q5: 如何自定义日志格式？

**方法**：修改 `config.py` 中的 processors：

```python
# 自定义时间格式
structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")

# 自定义渲染器
structlog.dev.ConsoleRenderer(
    colors=True,
    exception_formatter=structlog.dev.rich_traceback
)
```

---

## 最佳实践

### 1. 推荐配置

**开发环境**：
```toml
[tool.pytest]
log_cli = true
log_cli_level = "DEBUG"
log_cli_date_format = "%Y-%m-%d %H:%M:%S"
```

**生产环境**：
```python
configure_logging(env="prod", level="INFO")
```

### 2. 日志级别使用

| 级别 | 使用场景 | 示例 |
|------|----------|------|
| DEBUG | 详细诊断信息 | SQL 查询、变量值 |
| INFO | 关键操作确认 | 用户登录、订单创建 |
| WARNING | 警告但不影响运行 | 缓存未命中 |
| ERROR | 错误但可恢复 | API 超时重试 |
| CRITICAL | 严重错误 | 数据库连接失败 |

### 3. 结构化日志

```python
# ✅ 推荐：结构化字段
logger.info("用户登录", user_id=123, ip="192.168.1.1")

# ❌ 不推荐：格式化字符串
logger.info(f"用户 {user_id} 从 {ip} 登录")
```

### 4. 上下文传播

```python
from df_test_framework.infrastructure.logging import (
    bind_contextvars,
    clear_contextvars,
)

# 请求开始时
bind_contextvars(request_id="req_123", user_id=456)

# 请求结束时
clear_contextvars()
```

---

## 参考资源

### 框架文档
- [现代化日志系统使用指南](modern_logging_best_practices.md)
- [分布式追踪指南](distributed_tracing.md)

### 官方文档
- [structlog 文档](https://www.structlog.org/)
- [pytest logging 文档](https://docs.pytest.org/en/stable/how-to/logging.html)
- [Python logging 文档](https://docs.python.org/3/library/logging.html)

### 版本历史
- [v3.38.2](../releases/v3.38.2.md) - 从 loguru 迁移到 structlog
- [v3.26.0](../releases/v3.26.0.md) - loguru → logging 桥接（已废弃）

---

## 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v3.38.7 | 2025-12-26 | 简化架构：日志级别由消息性质决定，全局配置控制过滤 |
| v3.38.6 | 2025-12-26 | 两阶段初始化，确保日志格式统一 |
| v3.38.5 | 2025-12-25 | structlog 25.5.0 最佳实践，修复 pytest 集成 |
| v3.38.4 | 2025-12-25 | ProcessorFormatter、orjson、CallsiteParameterAdder |
| v3.38.2 | 2025-12-25 | 从 loguru 迁移到 structlog，重写文档 |

---

**需要帮助？** 提交 Issue 到 [GitHub Issues](https://github.com/your-org/df-test-framework/issues)
