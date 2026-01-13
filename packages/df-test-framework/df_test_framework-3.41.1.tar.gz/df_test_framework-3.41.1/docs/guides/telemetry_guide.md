# Telemetry 可观测性指南

> **版本**: v3.38.0 | **更新**: 2025-12-24
> **引入版本**: v3.14.0

---

## 概述

Telemetry 是 v3.14.0 引入的**可观测性融合**系统，将 Tracing、Metrics、Logging 三大支柱统一管理。

**核心理念**: **一次埋点，三种输出**

```python
# 一行代码
async with telemetry.span("api.call") as span:
    response = await call_api()

# 自动产生：
# ✅ Trace Span (链路追踪)
# ✅ Metrics (指标统计: duration histogram, count counter)
# ✅ Logs (结构化日志: Starting/Completed api.call)
```

---

## 快速开始

### 1. 基本用法

```python
from df_test_framework import Telemetry
import logging

logger = logging.getLogger(__name__)
telemetry = Telemetry(logger=logger)

# 使用 span 记录操作
async with telemetry.span("http.request", {"method": "POST"}) as span:
    response = await send_request()
    span.set_attribute("status_code", response.status_code)

# 自动输出：
# - [Log] Starting http.request
# - [Log] Completed http.request (duration=0.234s)
# - [Metric] http.request.duration = 0.234s (histogram)
# - [Metric] http.request.count += 1 (counter)
# - [Trace] Span{ name="http.request", attributes={...}, duration=0.234s }
```

### 2. 集成到 HttpClient

```python
from df_test_framework import (
    HttpClient,
    HttpTelemetryMiddleware,
    Telemetry
)
import logging

logger = logging.getLogger(__name__)
telemetry = Telemetry(logger=logger)

client = HttpClient(base_url="https://api.example.com")
client.use(HttpTelemetryMiddleware(telemetry=telemetry))

# 每个请求自动记录 Trace/Metrics/Logs
response = client.get("/users")
```

---

## Telemetry 三大支柱

### 1. Tracing (链路追踪)

**用途**: 追踪请求在系统中的完整路径

```python
async with telemetry.span("order.create") as root_span:
    # 子 Span
    async with telemetry.span("validate.user") as span1:
        validate_user()
        span1.set_attribute("user_id", 123)

    async with telemetry.span("check.inventory") as span2:
        check_inventory()
        span2.set_attribute("product_id", "P001")

    async with telemetry.span("payment.process") as span3:
        process_payment()
        span3.set_attribute("amount", 100.0)

# 产生层级 Trace:
# order.create [0.8s]
#   ├─ validate.user [0.1s]
#   ├─ check.inventory [0.2s]
#   └─ payment.process [0.5s]
```

### 2. Metrics (指标统计)

**用途**: 量化系统性能和行为

**自动指标**（使用 span 时自动记录）:
- `{span_name}.duration` - Histogram（持续时间分布）
- `{span_name}.success` - Counter（成功计数，无异常）
- `{span_name}.error` - Counter（错误计数，有异常）

```python
# 使用 span 自动记录指标
async with telemetry.span("api.request") as span:
    response = await call_api()
    span.set_attribute("endpoint", "/users")

# 自动产生指标:
# - api.request.duration (histogram)
# - api.request.success (counter, 成功时+1)
# - api.request.error (counter, 异常时+1)
```

> **注意**: `record_histogram()`, `increment_counter()`, `record_gauge()` 是内部实现,不推荐直接调用。请使用 `span()` 上下文管理器自动记录指标。

### 3. Logging (日志)

**用途**: 记录事件详情

```python
async with telemetry.span("operation") as span:
    # 自动记录:
    # [INFO] Starting operation
    # [INFO] Completed operation (duration=0.123s)

    # 手动记录
    span.log("Custom log message")
```

---

## 实用场景

### 场景 1: API 性能监控

```python
from df_test_framework import Telemetry, HttpTelemetryMiddleware

telemetry = Telemetry(logger=logger)
client = HttpClient(base_url="...")
client.use(HttpTelemetryMiddleware(telemetry=telemetry))

# 自动收集每个 API 的:
# - 响应时间分布 (histogram)
# - 请求总数 (counter)
# - 成功/失败计数 (counter)
```

### 场景 2: 慢操作定位

```python
async def complex_operation():
    async with telemetry.span("complex.operation") as root:

        async with telemetry.span("step1.load_data"):
            data = load_data()  # 0.5s

        async with telemetry.span("step2.process"):
            result = process(data)  # 3.0s  ← 慢！

        async with telemetry.span("step3.save"):
            save(result)  # 0.2s

# 通过 Trace 可视化快速定位: step2.process 最慢
```

### 场景 3: 错误监控

```python
async with telemetry.span("risky.operation") as span:
    try:
        result = risky_call()
        span.set_attribute("success", True)
    except Exception as e:
        span.set_attribute("success", False)
        span.set_attribute("error", str(e))
        span.set_attribute("error.type", type(e).__name__)
        # span 会自动记录异常，并增加 risky.operation.error 计数
        raise
```

---

## 属性标记

### 设置 Span 属性

```python
async with telemetry.span("http.request") as span:
    span.set_attribute("http.method", "POST")
    span.set_attribute("http.url", "/api/users")
    span.set_attribute("http.status_code", 201)
    span.set_attribute("user.id", 123)
```

### 批量设置

```python
async with telemetry.span("operation", {
    "env": "production",
    "version": "1.0.0",
    "region": "us-west-1"
}) as span:
    # ...
    pass
```

---

## NoopTelemetry (禁用模式)

```python
from df_test_framework import NoopTelemetry

# 用于测试或禁用可观测性
telemetry = NoopTelemetry()

# 所有操作变为空操作，无性能开销
async with telemetry.span("operation"):
    # 不会记录任何 Trace/Metrics/Logs
    pass
```

---

## 最佳实践

### 1. 合理命名 Span

```python
# ✅ 好：清晰、有层级
async with telemetry.span("http.request.post.users"):
    pass

# ❌ 差：模糊
async with telemetry.span("operation"):
    pass
```

### 2. 添加关键属性

```python
# ✅ 好：足够的上下文
async with telemetry.span("payment.process") as span:
    span.set_attribute("order_id", order_id)
    span.set_attribute("amount", amount)
    span.set_attribute("currency", "USD")

# ❌ 差：缺少上下文
async with telemetry.span("payment"):
    pass
```

### 3. 不要过度埋点

```python
# ✅ 好：关键操作
async with telemetry.span("database.query"):
    results = db.query(sql)

# ❌ 差：过度埋点
async with telemetry.span("loop.iteration.1"):
    async with telemetry.span("variable.assignment"):
        x = 1  # 没必要
```

---

## 集成 OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

# 设置 OpenTelemetry
provider = TracerProvider()
trace.set_tracer_provider(provider)

# 使用框架 Telemetry
telemetry = Telemetry(logger=logger)

# Span 会自动集成到 OpenTelemetry
```

---

## 参考资料

- [快速开始](../user-guide/QUICK_START_V3.14.md)
- [中间件使用指南](middleware_guide.md)
- [EventBus 使用指南](event_bus_guide.md)
- [OpenTelemetry 文档](https://opentelemetry.io/)
