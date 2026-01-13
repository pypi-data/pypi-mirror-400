"""
事件类型定义

定义框架中使用的各种事件类型。
所有事件都是不可变的 dataclass。

v3.17.0 重构:
- 添加 event_id 唯一标识
- 添加 CorrelatedEvent 支持 Start/End 事件关联
- 添加工厂方法创建事件
- 整合 OpenTelemetry 追踪上下文（trace_id/span_id）
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from df_test_framework.core.context.execution import ExecutionContext


def _get_current_trace_context() -> tuple[str | None, str | None]:
    """获取当前 OpenTelemetry 追踪上下文

    Returns:
        (trace_id, span_id) 元组，如果没有活动追踪则返回 (None, None)
    """
    try:
        from df_test_framework.infrastructure.tracing import OTEL_AVAILABLE

        if not OTEL_AVAILABLE:
            return None, None

        from opentelemetry import trace

        span = trace.get_current_span()
        if span and span.is_recording():
            ctx = span.get_span_context()
            # 格式化为十六进制字符串（标准格式）
            trace_id = format(ctx.trace_id, "032x")
            span_id = format(ctx.span_id, "016x")
            return trace_id, span_id
    except Exception:
        pass

    return None, None


def generate_event_id() -> str:
    """生成事件唯一 ID

    格式: evt-{12位十六进制}
    示例: evt-a1b2c3d4e5f6
    """
    return f"evt-{uuid.uuid4().hex[:12]}"


def generate_correlation_id() -> str:
    """生成关联 ID

    用于关联 Start/End 事件对。
    格式: cor-{12位十六进制}
    示例: cor-x7y8z9a1b2c3
    """
    return f"cor-{uuid.uuid4().hex[:12]}"


@dataclass(frozen=True)
class Event:
    """事件基类

    所有事件都应继承此类。

    属性:
        event_id: 事件唯一标识（自动生成）
        timestamp: 事件发生时间（自动生成）
        context: 执行上下文（可选，用于追踪关联）
        trace_id: OpenTelemetry 追踪 ID（自动从当前 Span 获取）
        span_id: OpenTelemetry Span ID（自动从当前 Span 获取）

    v3.17.0: 新增 event_id 字段
    v3.17.0: 整合 OpenTelemetry，新增 trace_id/span_id 字段
    """

    event_id: str = field(default_factory=generate_event_id)
    timestamp: datetime = field(default_factory=datetime.now)
    context: ExecutionContext | None = None
    # OpenTelemetry 追踪上下文（可选，自动从当前 Span 获取）
    trace_id: str | None = field(default=None)
    span_id: str | None = field(default=None)


@dataclass(frozen=True)
class CorrelatedEvent(Event):
    """可关联事件基类

    用于 Start/End 事件对的关联。
    同一对 Start/End 事件共享相同的 correlation_id。

    属性:
        correlation_id: 关联 ID（同一对 Start/End 共享）

    v3.17.0: 新增
    """

    correlation_id: str = ""


# =============================================================================
# HTTP 事件
# =============================================================================


@dataclass(frozen=True)
class HttpRequestStartEvent(CorrelatedEvent):
    """HTTP 请求开始事件

    在发送 HTTP 请求前触发。
    correlation_id 由发布者生成，End 事件复用同一 ID。

    v3.17.0: 继承 CorrelatedEvent，添加工厂方法
    v3.22.0: 添加 params 字段，支持记录 GET 请求参数
    """

    method: str = ""
    url: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)  # v3.22.0: GET 请求参数
    body: str | None = None

    @classmethod
    def create(
        cls,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        body: str | None = None,
        context: ExecutionContext | None = None,
    ) -> tuple["HttpRequestStartEvent", str]:
        """工厂方法：创建事件并返回 correlation_id

        自动注入当前 OpenTelemetry 追踪上下文（trace_id/span_id）。

        Args:
            method: HTTP 方法
            url: 请求 URL
            headers: 请求头
            params: GET 请求参数（v3.22.0 新增）
            body: 请求体
            context: 执行上下文

        Returns:
            (event, correlation_id) 元组
        """
        correlation_id = generate_correlation_id()
        # 自动获取当前追踪上下文
        trace_id, span_id = _get_current_trace_context()
        event = cls(
            method=method,
            url=url,
            headers=headers or {},
            params=params or {},
            body=body,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )
        return event, correlation_id


@dataclass(frozen=True)
class HttpRequestEndEvent(CorrelatedEvent):
    """HTTP 请求结束事件

    在收到 HTTP 响应后触发。
    correlation_id 必须与对应的 StartEvent 相同。

    v3.17.0: 继承 CorrelatedEvent，添加工厂方法
    """

    method: str = ""
    url: str = ""
    status_code: int = 0
    duration: float = 0.0
    headers: dict[str, str] = field(default_factory=dict)
    body: str | None = None

    @classmethod
    def create(
        cls,
        correlation_id: str,
        method: str,
        url: str,
        status_code: int,
        duration: float,
        headers: dict[str, str] | None = None,
        body: str | None = None,
        context: ExecutionContext | None = None,
    ) -> "HttpRequestEndEvent":
        """工厂方法：创建事件（复用 correlation_id）

        自动注入当前 OpenTelemetry 追踪上下文（trace_id/span_id）。

        Args:
            correlation_id: 关联 ID（必须与 StartEvent 相同）
            method: HTTP 方法
            url: 请求 URL
            status_code: 响应状态码
            duration: 请求耗时（秒）
            headers: 响应头
            body: 响应体
            context: 执行上下文

        Returns:
            HttpRequestEndEvent 实例
        """
        # 自动获取当前追踪上下文
        trace_id, span_id = _get_current_trace_context()
        return cls(
            method=method,
            url=url,
            status_code=status_code,
            duration=duration,
            headers=headers or {},
            body=body,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


@dataclass(frozen=True)
class HttpRequestErrorEvent(CorrelatedEvent):
    """HTTP 请求错误事件

    在 HTTP 请求发生异常时触发。

    v3.17.0: 继承 CorrelatedEvent，添加工厂方法
    """

    method: str = ""
    url: str = ""
    error_type: str = ""
    error_message: str = ""
    duration: float = 0.0

    @classmethod
    def create(
        cls,
        correlation_id: str,
        method: str,
        url: str,
        error: Exception,
        duration: float,
        context: ExecutionContext | None = None,
    ) -> "HttpRequestErrorEvent":
        """工厂方法：创建错误事件

        自动注入当前 OpenTelemetry 追踪上下文（trace_id/span_id）。

        Args:
            correlation_id: 关联 ID
            method: HTTP 方法
            url: 请求 URL
            error: 异常对象
            duration: 请求耗时（秒）
            context: 执行上下文

        Returns:
            HttpRequestErrorEvent 实例
        """
        # 自动获取当前追踪上下文
        trace_id, span_id = _get_current_trace_context()
        return cls(
            method=method,
            url=url,
            error_type=type(error).__name__,
            error_message=str(error),
            duration=duration,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


# =============================================================================
# 中间件事件
# =============================================================================


@dataclass(frozen=True)
class MiddlewareExecuteEvent(CorrelatedEvent):
    """中间件执行事件

    记录中间件对请求/响应的修改。

    v3.17.0 新增
    """

    middleware_name: str = ""
    phase: str = ""  # "before" 或 "after"
    changes: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        correlation_id: str,
        middleware_name: str,
        phase: str,
        changes: dict[str, Any],
        context: ExecutionContext | None = None,
    ) -> "MiddlewareExecuteEvent":
        """工厂方法：创建中间件执行事件

        自动注入当前 OpenTelemetry 追踪上下文（trace_id/span_id）。

        Args:
            correlation_id: 关联 ID（与请求事件相同）
            middleware_name: 中间件名称
            phase: 执行阶段 ("before" 或 "after")
            changes: 中间件做的修改

        Returns:
            MiddlewareExecuteEvent 实例
        """
        # 自动获取当前追踪上下文
        trace_id, span_id = _get_current_trace_context()
        return cls(
            middleware_name=middleware_name,
            phase=phase,
            changes=changes,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


# =============================================================================
# Database 事件
# =============================================================================


@dataclass(frozen=True)
class DatabaseQueryStartEvent(CorrelatedEvent):
    """数据库查询开始事件

    v3.18.0: 升级为 CorrelatedEvent，支持 Start/End 事件关联
    """

    operation: str = ""  # SELECT, INSERT, UPDATE, DELETE
    table: str = ""
    sql: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    database: str | None = None

    @classmethod
    def create(
        cls,
        operation: str,
        table: str,
        sql: str,
        params: dict[str, Any] | None = None,
        database: str | None = None,
        context: ExecutionContext | None = None,
    ) -> tuple["DatabaseQueryStartEvent", str]:
        """工厂方法：创建事件并返回 correlation_id

        Args:
            operation: 操作类型（SELECT/INSERT/UPDATE/DELETE）
            table: 表名
            sql: SQL 语句
            params: SQL 参数
            database: 数据库名
            context: 执行上下文

        Returns:
            (event, correlation_id) 元组
        """
        correlation_id = generate_correlation_id()
        trace_id, span_id = _get_current_trace_context()
        event = cls(
            operation=operation,
            table=table,
            sql=sql,
            params=params or {},
            database=database,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )
        return event, correlation_id


@dataclass(frozen=True)
class DatabaseQueryEndEvent(CorrelatedEvent):
    """数据库查询结束事件

    v3.18.0: 升级为 CorrelatedEvent，支持 Start/End 事件关联
    """

    operation: str = ""
    table: str = ""
    sql: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    row_count: int = 0
    database: str | None = None

    @classmethod
    def create(
        cls,
        correlation_id: str,
        operation: str,
        table: str,
        sql: str,
        params: dict[str, Any] | None = None,
        duration_ms: float = 0.0,
        row_count: int = 0,
        database: str | None = None,
        context: ExecutionContext | None = None,
    ) -> "DatabaseQueryEndEvent":
        """工厂方法：创建事件（复用 correlation_id）"""
        trace_id, span_id = _get_current_trace_context()
        return cls(
            operation=operation,
            table=table,
            sql=sql,
            params=params or {},
            duration_ms=duration_ms,
            row_count=row_count,
            database=database,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


@dataclass(frozen=True)
class DatabaseQueryErrorEvent(CorrelatedEvent):
    """数据库查询错误事件

    v3.18.0: 升级为 CorrelatedEvent，支持 Start/End 事件关联
    """

    operation: str = ""
    table: str = ""
    sql: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    error_type: str = ""
    error_message: str = ""
    duration_ms: float = 0.0
    database: str | None = None

    @classmethod
    def create(
        cls,
        correlation_id: str,
        operation: str,
        table: str,
        sql: str,
        params: dict[str, Any] | None = None,
        error: Exception | None = None,
        duration_ms: float = 0.0,
        database: str | None = None,
        context: ExecutionContext | None = None,
    ) -> "DatabaseQueryErrorEvent":
        """工厂方法：创建事件（复用 correlation_id）"""
        trace_id, span_id = _get_current_trace_context()
        return cls(
            operation=operation,
            table=table,
            sql=sql,
            params=params or {},
            error_type=type(error).__name__ if error else "UnknownError",
            error_message=str(error) if error else "",
            duration_ms=duration_ms,
            database=database,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


# =============================================================================
# Cache 事件 (Redis)
# =============================================================================


@dataclass(frozen=True)
class CacheOperationStartEvent(CorrelatedEvent):
    """缓存操作开始事件

    在执行缓存操作前触发。
    correlation_id 由发布者生成，End 事件复用同一 ID。

    v3.18.0: 新增
    """

    operation: str = ""  # SET, GET, DELETE, HSET, HGET, LPUSH, SADD, ZADD 等
    key: str = ""
    field: str | None = None  # Hash 操作的 field

    @classmethod
    def create(
        cls,
        operation: str,
        key: str,
        field: str | None = None,
        context: ExecutionContext | None = None,
    ) -> tuple["CacheOperationStartEvent", str]:
        """工厂方法：创建事件并返回 correlation_id

        Args:
            operation: 缓存操作类型（SET, GET, DELETE 等）
            key: 缓存键
            field: Hash 操作的字段名（可选）
            context: 执行上下文

        Returns:
            (event, correlation_id) 元组
        """
        correlation_id = generate_correlation_id()
        trace_id, span_id = _get_current_trace_context()
        event = cls(
            operation=operation,
            key=key,
            field=field,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )
        return event, correlation_id


@dataclass(frozen=True)
class CacheOperationEndEvent(CorrelatedEvent):
    """缓存操作结束事件

    在缓存操作完成后触发。
    correlation_id 必须与对应的 StartEvent 相同。

    v3.18.0: 新增
    """

    operation: str = ""
    key: str = ""
    hit: bool | None = None  # GET 操作是否命中（None 表示非 GET 操作）
    duration_ms: float = 0.0
    success: bool = True

    @classmethod
    def create(
        cls,
        correlation_id: str,
        operation: str,
        key: str,
        duration_ms: float,
        hit: bool | None = None,
        context: ExecutionContext | None = None,
    ) -> "CacheOperationEndEvent":
        """工厂方法：创建事件（复用 correlation_id）

        Args:
            correlation_id: 关联 ID（必须与 StartEvent 相同）
            operation: 缓存操作类型
            key: 缓存键
            duration_ms: 操作耗时（毫秒）
            hit: GET 操作是否命中
            context: 执行上下文

        Returns:
            CacheOperationEndEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()
        return cls(
            operation=operation,
            key=key,
            hit=hit,
            duration_ms=duration_ms,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


@dataclass(frozen=True)
class CacheOperationErrorEvent(CorrelatedEvent):
    """缓存操作错误事件

    在缓存操作发生异常时触发。

    v3.18.0: 新增
    """

    operation: str = ""
    key: str = ""
    error_type: str = ""
    error_message: str = ""
    duration_ms: float = 0.0

    @classmethod
    def create(
        cls,
        correlation_id: str,
        operation: str,
        key: str,
        error: Exception,
        duration_ms: float,
        context: ExecutionContext | None = None,
    ) -> "CacheOperationErrorEvent":
        """工厂方法：创建错误事件

        Args:
            correlation_id: 关联 ID
            operation: 缓存操作类型
            key: 缓存键
            error: 异常对象
            duration_ms: 操作耗时（毫秒）
            context: 执行上下文

        Returns:
            CacheOperationErrorEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()
        return cls(
            operation=operation,
            key=key,
            error_type=type(error).__name__,
            error_message=str(error),
            duration_ms=duration_ms,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


# =============================================================================
# MQ 发布事件 (v3.34.1 重构)
# =============================================================================


@dataclass(frozen=True)
class MessagePublishStartEvent(CorrelatedEvent):
    """消息发布开始事件

    在发送消息前触发。
    correlation_id 由发布者生成，End/Error 事件复用同一 ID。

    v3.34.1: 重构，继承 CorrelatedEvent，添加工厂方法
    """

    messenger_type: str = ""  # kafka, rabbitmq, rocketmq
    topic: str = ""
    message_id: str = ""
    key: str | None = None
    partition: int | None = None
    body_size: int = 0
    headers: dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        messenger_type: str,
        topic: str,
        body_size: int = 0,
        message_id: str = "",
        key: str | None = None,
        partition: int | None = None,
        headers: dict[str, str] | None = None,
        context: ExecutionContext | None = None,
    ) -> tuple["MessagePublishStartEvent", str]:
        """工厂方法：创建事件并返回 correlation_id

        自动注入当前 OpenTelemetry 追踪上下文（trace_id/span_id）。

        Args:
            messenger_type: 消息队列类型（kafka/rabbitmq/rocketmq）
            topic: 主题/队列名
            body_size: 消息体大小（字节）
            message_id: 消息 ID
            key: 消息键（Kafka）
            partition: 分区号
            headers: 消息头
            context: 执行上下文

        Returns:
            (event, correlation_id) 元组
        """
        correlation_id = str(uuid.uuid4())
        trace_id, span_id = _get_current_trace_context()

        event = cls(
            messenger_type=messenger_type,
            topic=topic,
            message_id=message_id,
            key=key,
            partition=partition,
            body_size=body_size,
            headers=headers or {},
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )
        return event, correlation_id


@dataclass(frozen=True)
class MessagePublishEndEvent(CorrelatedEvent):
    """消息发布成功事件

    在消息发布成功后触发。
    correlation_id 必须与对应的 StartEvent 相同。

    v3.34.1: 新增
    """

    messenger_type: str = ""
    topic: str = ""
    message_id: str = ""
    partition: int | None = None
    offset: int | None = None  # Kafka 返回的 offset
    duration: float = 0.0  # 发布耗时（秒）

    @classmethod
    def create(
        cls,
        correlation_id: str,
        messenger_type: str,
        topic: str,
        duration: float,
        message_id: str = "",
        partition: int | None = None,
        offset: int | None = None,
        context: ExecutionContext | None = None,
    ) -> "MessagePublishEndEvent":
        """工厂方法：创建事件（复用 correlation_id）

        Args:
            correlation_id: 关联 ID（必须与 StartEvent 相同）
            messenger_type: 消息队列类型
            topic: 主题/队列名
            duration: 发布耗时（秒）
            message_id: 消息 ID
            partition: 分区号
            offset: 消息偏移量
            context: 执行上下文

        Returns:
            MessagePublishEndEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()

        return cls(
            messenger_type=messenger_type,
            topic=topic,
            message_id=message_id,
            partition=partition,
            offset=offset,
            duration=duration,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


@dataclass(frozen=True)
class MessagePublishErrorEvent(CorrelatedEvent):
    """消息发布错误事件

    在消息发布失败时触发。

    v3.34.1: 新增
    """

    messenger_type: str = ""
    topic: str = ""
    error_type: str = ""
    error_message: str = ""
    duration: float = 0.0

    @classmethod
    def create(
        cls,
        correlation_id: str,
        messenger_type: str,
        topic: str,
        error: Exception,
        duration: float,
        context: ExecutionContext | None = None,
    ) -> "MessagePublishErrorEvent":
        """工厂方法：创建错误事件

        Args:
            correlation_id: 关联 ID
            messenger_type: 消息队列类型
            topic: 主题/队列名
            error: 异常对象
            duration: 耗时（秒）
            context: 执行上下文

        Returns:
            MessagePublishErrorEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()

        return cls(
            messenger_type=messenger_type,
            topic=topic,
            error_type=type(error).__name__,
            error_message=str(error),
            duration=duration,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


# =============================================================================
# MQ 消费事件 (v3.34.1 重构)
# =============================================================================


@dataclass(frozen=True)
class MessageConsumeStartEvent(CorrelatedEvent):
    """消息消费开始事件

    在开始处理消息时触发。
    correlation_id 由发布者生成，End/Error 事件复用同一 ID。

    v3.34.1: 新增
    """

    messenger_type: str = ""
    topic: str = ""
    message_id: str = ""
    consumer_group: str = ""
    partition: int | None = None
    offset: int | None = None
    body_size: int = 0

    @classmethod
    def create(
        cls,
        messenger_type: str,
        topic: str,
        consumer_group: str,
        message_id: str = "",
        partition: int | None = None,
        offset: int | None = None,
        body_size: int = 0,
        context: ExecutionContext | None = None,
    ) -> tuple["MessageConsumeStartEvent", str]:
        """工厂方法：创建事件并返回 correlation_id

        Args:
            messenger_type: 消息队列类型
            topic: 主题/队列名
            consumer_group: 消费者组
            message_id: 消息 ID
            partition: 分区号
            offset: 消息偏移量
            body_size: 消息体大小
            context: 执行上下文

        Returns:
            (event, correlation_id) 元组
        """
        correlation_id = str(uuid.uuid4())
        trace_id, span_id = _get_current_trace_context()

        event = cls(
            messenger_type=messenger_type,
            topic=topic,
            message_id=message_id,
            consumer_group=consumer_group,
            partition=partition,
            offset=offset,
            body_size=body_size,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )
        return event, correlation_id


@dataclass(frozen=True)
class MessageConsumeEndEvent(CorrelatedEvent):
    """消息消费成功事件

    在消息处理成功后触发。
    correlation_id 必须与对应的 StartEvent 相同。

    v3.34.1: 重构（原 MessageConsumeEvent）
    """

    messenger_type: str = ""
    topic: str = ""
    message_id: str = ""
    consumer_group: str = ""
    partition: int | None = None
    offset: int | None = None
    processing_time: float = 0.0  # 处理耗时（秒）

    @classmethod
    def create(
        cls,
        correlation_id: str,
        messenger_type: str,
        topic: str,
        consumer_group: str,
        processing_time: float,
        message_id: str = "",
        partition: int | None = None,
        offset: int | None = None,
        context: ExecutionContext | None = None,
    ) -> "MessageConsumeEndEvent":
        """工厂方法：创建事件（复用 correlation_id）

        Args:
            correlation_id: 关联 ID
            messenger_type: 消息队列类型
            topic: 主题/队列名
            consumer_group: 消费者组
            processing_time: 处理耗时（秒）
            message_id: 消息 ID
            partition: 分区号
            offset: 消息偏移量
            context: 执行上下文

        Returns:
            MessageConsumeEndEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()

        return cls(
            messenger_type=messenger_type,
            topic=topic,
            message_id=message_id,
            consumer_group=consumer_group,
            partition=partition,
            offset=offset,
            processing_time=processing_time,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


@dataclass(frozen=True)
class MessageConsumeErrorEvent(CorrelatedEvent):
    """消息消费错误事件

    在消息处理失败时触发。

    v3.34.1: 新增
    """

    messenger_type: str = ""
    topic: str = ""
    message_id: str = ""
    consumer_group: str = ""
    error_type: str = ""
    error_message: str = ""
    processing_time: float = 0.0

    @classmethod
    def create(
        cls,
        correlation_id: str,
        messenger_type: str,
        topic: str,
        consumer_group: str,
        error: Exception,
        processing_time: float,
        message_id: str = "",
        context: ExecutionContext | None = None,
    ) -> "MessageConsumeErrorEvent":
        """工厂方法：创建错误事件

        Args:
            correlation_id: 关联 ID
            messenger_type: 消息队列类型
            topic: 主题/队列名
            consumer_group: 消费者组
            error: 异常对象
            processing_time: 处理耗时（秒）
            message_id: 消息 ID
            context: 执行上下文

        Returns:
            MessageConsumeErrorEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()

        return cls(
            messenger_type=messenger_type,
            topic=topic,
            message_id=message_id,
            consumer_group=consumer_group,
            error_type=type(error).__name__,
            error_message=str(error),
            processing_time=processing_time,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


# =============================================================================
# Storage 事件 (v3.18.0)
# =============================================================================


@dataclass(frozen=True)
class StorageOperationStartEvent(CorrelatedEvent):
    """存储操作开始事件

    在执行存储操作前触发。
    correlation_id 由发布者生成，End 事件复用同一 ID。

    v3.18.0: 新增
    """

    storage_type: str = ""  # local, s3, oss
    operation: str = ""  # upload, download, delete, copy, move, list
    path: str = ""
    size: int | None = None  # 上传时的文件大小

    @classmethod
    def create(
        cls,
        storage_type: str,
        operation: str,
        path: str,
        size: int | None = None,
        context: ExecutionContext | None = None,
    ) -> tuple["StorageOperationStartEvent", str]:
        """工厂方法：创建事件并返回 correlation_id

        Args:
            storage_type: 存储类型（local, s3, oss）
            operation: 操作类型（upload, download, delete 等）
            path: 文件路径或对象键
            size: 文件大小（字节，上传时可用）
            context: 执行上下文

        Returns:
            (event, correlation_id) 元组
        """
        correlation_id = generate_correlation_id()
        trace_id, span_id = _get_current_trace_context()
        event = cls(
            storage_type=storage_type,
            operation=operation,
            path=path,
            size=size,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )
        return event, correlation_id


@dataclass(frozen=True)
class StorageOperationEndEvent(CorrelatedEvent):
    """存储操作结束事件

    在存储操作完成后触发。
    correlation_id 必须与对应的 StartEvent 相同。

    v3.18.0: 新增
    """

    storage_type: str = ""
    operation: str = ""
    path: str = ""
    size: int | None = None  # 下载时的文件大小
    duration_ms: float = 0.0
    success: bool = True

    @classmethod
    def create(
        cls,
        correlation_id: str,
        storage_type: str,
        operation: str,
        path: str,
        duration_ms: float,
        size: int | None = None,
        context: ExecutionContext | None = None,
    ) -> "StorageOperationEndEvent":
        """工厂方法：创建事件（复用 correlation_id）

        Args:
            correlation_id: 关联 ID（必须与 StartEvent 相同）
            storage_type: 存储类型
            operation: 操作类型
            path: 文件路径或对象键
            duration_ms: 操作耗时（毫秒）
            size: 文件大小（字节）
            context: 执行上下文

        Returns:
            StorageOperationEndEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()
        return cls(
            storage_type=storage_type,
            operation=operation,
            path=path,
            size=size,
            duration_ms=duration_ms,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


@dataclass(frozen=True)
class StorageOperationErrorEvent(CorrelatedEvent):
    """存储操作错误事件

    在存储操作发生异常时触发。

    v3.18.0: 新增
    """

    storage_type: str = ""
    operation: str = ""
    path: str = ""
    error_type: str = ""
    error_message: str = ""
    duration_ms: float = 0.0

    @classmethod
    def create(
        cls,
        correlation_id: str,
        storage_type: str,
        operation: str,
        path: str,
        error: Exception,
        duration_ms: float,
        context: ExecutionContext | None = None,
    ) -> "StorageOperationErrorEvent":
        """工厂方法：创建错误事件

        Args:
            correlation_id: 关联 ID
            storage_type: 存储类型
            operation: 操作类型
            path: 文件路径或对象键
            error: 异常对象
            duration_ms: 操作耗时（毫秒）
            context: 执行上下文

        Returns:
            StorageOperationErrorEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()
        return cls(
            storage_type=storage_type,
            operation=operation,
            path=path,
            error_type=type(error).__name__,
            error_message=str(error),
            duration_ms=duration_ms,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


# =============================================================================
# gRPC 事件 (v3.32.0)
# =============================================================================


@dataclass(frozen=True)
class GrpcRequestStartEvent(CorrelatedEvent):
    """gRPC 请求开始事件

    在发送 gRPC 请求前触发。
    correlation_id 由发布者生成，End 事件复用同一 ID。

    v3.32.0: 新增
    """

    service: str = ""  # 服务名称（如 "greeter.Greeter"）
    method: str = ""  # 方法名（如 "SayHello"）
    metadata: dict[str, str] = field(default_factory=dict)  # gRPC 元数据
    request_data: str | None = None  # 请求数据（序列化后的字符串）

    @classmethod
    def create(
        cls,
        service: str,
        method: str,
        metadata: dict[str, str] | None = None,
        request_data: str | None = None,
        context: ExecutionContext | None = None,
    ) -> tuple["GrpcRequestStartEvent", str]:
        """工厂方法：创建事件并返回 correlation_id

        自动注入当前 OpenTelemetry 追踪上下文（trace_id/span_id）。

        Args:
            service: gRPC 服务名称
            method: RPC 方法名
            metadata: gRPC 元数据
            request_data: 请求数据
            context: 执行上下文

        Returns:
            (event, correlation_id) 元组
        """
        correlation_id = generate_correlation_id()
        trace_id, span_id = _get_current_trace_context()
        event = cls(
            service=service,
            method=method,
            metadata=metadata or {},
            request_data=request_data,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )
        return event, correlation_id


@dataclass(frozen=True)
class GrpcRequestEndEvent(CorrelatedEvent):
    """gRPC 请求结束事件

    在收到 gRPC 响应后触发。
    correlation_id 必须与对应的 StartEvent 相同。

    v3.32.0: 新增
    """

    service: str = ""
    method: str = ""
    status_code: int = 0  # gRPC 状态码（0=OK, 1=CANCELLED, ...）
    status_message: str = ""  # 状态消息
    duration: float = 0.0  # 请求耗时（秒）
    response_data: str | None = None  # 响应数据（序列化后的字符串）

    @classmethod
    def create(
        cls,
        correlation_id: str,
        service: str,
        method: str,
        status_code: int,
        duration: float,
        status_message: str = "",
        response_data: str | None = None,
        context: ExecutionContext | None = None,
    ) -> "GrpcRequestEndEvent":
        """工厂方法：创建事件（复用 correlation_id）

        自动注入当前 OpenTelemetry 追踪上下文（trace_id/span_id）。

        Args:
            correlation_id: 关联 ID（必须与 StartEvent 相同）
            service: gRPC 服务名称
            method: RPC 方法名
            status_code: gRPC 状态码
            duration: 请求耗时（秒）
            status_message: 状态消息
            response_data: 响应数据
            context: 执行上下文

        Returns:
            GrpcRequestEndEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()
        return cls(
            service=service,
            method=method,
            status_code=status_code,
            status_message=status_message,
            duration=duration,
            response_data=response_data,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


@dataclass(frozen=True)
class GrpcRequestErrorEvent(CorrelatedEvent):
    """gRPC 请求错误事件

    在 gRPC 请求发生异常时触发。

    v3.32.0: 新增
    """

    service: str = ""
    method: str = ""
    error_code: int = 0  # gRPC 错误码
    error_type: str = ""  # 异常类型名
    error_message: str = ""  # 错误消息
    duration: float = 0.0  # 请求耗时（秒）

    @classmethod
    def create(
        cls,
        correlation_id: str,
        service: str,
        method: str,
        error: Exception,
        duration: float,
        error_code: int = 2,  # UNKNOWN
        context: ExecutionContext | None = None,
    ) -> "GrpcRequestErrorEvent":
        """工厂方法：创建错误事件

        自动注入当前 OpenTelemetry 追踪上下文（trace_id/span_id）。

        Args:
            correlation_id: 关联 ID
            service: gRPC 服务名称
            method: RPC 方法名
            error: 异常对象
            duration: 请求耗时（秒）
            error_code: gRPC 错误码
            context: 执行上下文

        Returns:
            GrpcRequestErrorEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()
        return cls(
            service=service,
            method=method,
            error_code=error_code,
            error_type=type(error).__name__,
            error_message=str(error),
            duration=duration,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


# =============================================================================
# GraphQL 事件 (v3.33.0)
# =============================================================================


@dataclass(frozen=True)
class GraphQLRequestStartEvent(CorrelatedEvent):
    """GraphQL 请求开始事件

    在发送 GraphQL 请求前触发。
    correlation_id 由发布者生成，End 事件复用同一 ID。

    v3.33.0: 新增
    """

    url: str = ""  # GraphQL 端点 URL
    operation_type: str = ""  # query, mutation, subscription
    operation_name: str | None = None  # 操作名称
    query: str | None = None  # 查询语句（可选，可能过长）
    variables: str | None = None  # 变量 JSON 字符串

    @classmethod
    def create(
        cls,
        url: str,
        operation_type: str,
        operation_name: str | None = None,
        query: str | None = None,
        variables: str | None = None,
        context: ExecutionContext | None = None,
    ) -> tuple["GraphQLRequestStartEvent", str]:
        """工厂方法：创建事件并返回 correlation_id

        自动注入当前 OpenTelemetry 追踪上下文（trace_id/span_id）。

        Args:
            url: GraphQL 端点 URL
            operation_type: 操作类型（query/mutation/subscription）
            operation_name: 操作名称
            query: 查询语句
            variables: 变量 JSON 字符串
            context: 执行上下文

        Returns:
            (event, correlation_id) 元组
        """
        correlation_id = generate_correlation_id()
        trace_id, span_id = _get_current_trace_context()
        event = cls(
            url=url,
            operation_type=operation_type,
            operation_name=operation_name,
            query=query,
            variables=variables,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )
        return event, correlation_id


@dataclass(frozen=True)
class GraphQLRequestEndEvent(CorrelatedEvent):
    """GraphQL 请求结束事件

    在收到 GraphQL 响应后触发。
    correlation_id 必须与对应的 StartEvent 相同。

    v3.33.0: 新增
    """

    url: str = ""
    operation_type: str = ""
    operation_name: str | None = None
    duration: float = 0.0  # 请求耗时（秒）
    has_errors: bool = False  # 是否有 GraphQL 错误
    error_count: int = 0  # 错误数量
    data: str | None = None  # 响应数据 JSON 字符串

    @classmethod
    def create(
        cls,
        correlation_id: str,
        url: str,
        operation_type: str,
        duration: float,
        operation_name: str | None = None,
        has_errors: bool = False,
        error_count: int = 0,
        data: str | None = None,
        context: ExecutionContext | None = None,
    ) -> "GraphQLRequestEndEvent":
        """工厂方法：创建事件（复用 correlation_id）

        自动注入当前 OpenTelemetry 追踪上下文（trace_id/span_id）。

        Args:
            correlation_id: 关联 ID（必须与 StartEvent 相同）
            url: GraphQL 端点 URL
            operation_type: 操作类型
            duration: 请求耗时（秒）
            operation_name: 操作名称
            has_errors: 是否有 GraphQL 错误
            error_count: 错误数量
            data: 响应数据 JSON 字符串
            context: 执行上下文

        Returns:
            GraphQLRequestEndEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()
        return cls(
            url=url,
            operation_type=operation_type,
            operation_name=operation_name,
            duration=duration,
            has_errors=has_errors,
            error_count=error_count,
            data=data,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


@dataclass(frozen=True)
class GraphQLRequestErrorEvent(CorrelatedEvent):
    """GraphQL 请求错误事件

    在 GraphQL 请求发生 HTTP 传输层异常时触发。

    注意：GraphQL 业务错误（response.errors）通过 EndEvent.has_errors 标识，
    此事件仅用于 HTTP 传输层错误（网络超时、连接失败等）。

    v3.33.0: 新增
    """

    url: str = ""
    operation_type: str = ""
    operation_name: str | None = None
    error_type: str = ""  # 异常类型名
    error_message: str = ""  # 错误消息
    duration: float = 0.0  # 请求耗时（秒）

    @classmethod
    def create(
        cls,
        correlation_id: str,
        url: str,
        operation_type: str,
        error: Exception,
        duration: float,
        operation_name: str | None = None,
        context: ExecutionContext | None = None,
    ) -> "GraphQLRequestErrorEvent":
        """工厂方法：创建错误事件

        自动注入当前 OpenTelemetry 追踪上下文（trace_id/span_id）。

        Args:
            correlation_id: 关联 ID
            url: GraphQL 端点 URL
            operation_type: 操作类型
            error: 异常对象
            duration: 请求耗时（秒）
            operation_name: 操作名称
            context: 执行上下文

        Returns:
            GraphQLRequestErrorEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()
        return cls(
            url=url,
            operation_type=operation_type,
            operation_name=operation_name,
            error_type=type(error).__name__,
            error_message=str(error),
            duration=duration,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


# =============================================================================
# 测试事件
# =============================================================================


@dataclass(frozen=True)
class TestStartEvent(Event):
    """测试开始事件"""

    test_name: str = ""
    test_file: str = ""
    markers: list[str] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TestEndEvent(Event):
    """测试结束事件"""

    test_name: str = ""
    test_file: str = ""
    status: str = ""  # passed, failed, skipped, error
    duration: float = 0.0
    failure_message: str | None = None
    markers: list[str] = field(default_factory=list)


# =============================================================================
# 事务事件 (v3.18.0)
# =============================================================================


@dataclass(frozen=True)
class TransactionCommitEvent(Event):
    """事务提交事件

    在 UnitOfWork.commit() 时触发。

    v3.18.0: 新增
    """

    repository_count: int = 0  # 涉及的 Repository 数量
    session_id: str | None = None  # Session 标识（可选）

    @classmethod
    def create(
        cls,
        repository_count: int = 0,
        session_id: str | None = None,
        context: ExecutionContext | None = None,
    ) -> "TransactionCommitEvent":
        """工厂方法：创建事件

        Args:
            repository_count: 涉及的 Repository 数量
            session_id: Session 标识
            context: 执行上下文

        Returns:
            TransactionCommitEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()
        return cls(
            repository_count=repository_count,
            session_id=session_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


@dataclass(frozen=True)
class TransactionRollbackEvent(Event):
    """事务回滚事件

    在 UnitOfWork.rollback() 时触发。

    v3.18.0: 新增
    """

    repository_count: int = 0  # 涉及的 Repository 数量
    reason: str = "auto"  # auto: 自动回滚, exception: 异常回滚, manual: 手动回滚
    session_id: str | None = None  # Session 标识（可选）

    @classmethod
    def create(
        cls,
        repository_count: int = 0,
        reason: str = "auto",
        session_id: str | None = None,
        context: ExecutionContext | None = None,
    ) -> "TransactionRollbackEvent":
        """工厂方法：创建事件

        Args:
            repository_count: 涉及的 Repository 数量
            reason: 回滚原因（auto/exception/manual）
            session_id: Session 标识
            context: 执行上下文

        Returns:
            TransactionRollbackEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()
        return cls(
            repository_count=repository_count,
            reason=reason,
            session_id=session_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


# =============================================================================
# UI 事件 (v3.35.7)
# =============================================================================


@dataclass(frozen=True)
class UINavigationStartEvent(CorrelatedEvent):
    """UI 页面导航开始事件

    在 BasePage.goto() 或页面跳转时触发。
    correlation_id 由发布者生成，End 事件复用同一 ID。

    v3.35.7: 新增
    """

    page_name: str = ""  # 页面对象名称（如 "HomePage"）
    url: str = ""  # 目标 URL
    base_url: str = ""  # 基础 URL

    @classmethod
    def create(
        cls,
        page_name: str,
        url: str,
        base_url: str = "",
        context: ExecutionContext | None = None,
    ) -> tuple["UINavigationStartEvent", str]:
        """工厂方法：创建事件并返回 correlation_id

        自动注入当前 OpenTelemetry 追踪上下文（trace_id/span_id）。

        Args:
            page_name: 页面对象名称
            url: 目标 URL
            base_url: 基础 URL
            context: 执行上下文

        Returns:
            (event, correlation_id) 元组
        """
        correlation_id = generate_correlation_id()
        trace_id, span_id = _get_current_trace_context()
        event = cls(
            page_name=page_name,
            url=url,
            base_url=base_url,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )
        return event, correlation_id


@dataclass(frozen=True)
class UINavigationEndEvent(CorrelatedEvent):
    """UI 页面导航结束事件

    在页面加载完成后触发。
    correlation_id 必须与对应的 StartEvent 相同。

    v3.35.7: 新增
    """

    page_name: str = ""
    url: str = ""
    title: str = ""  # 页面标题
    duration: float = 0.0  # 导航耗时（秒）
    success: bool = True

    @classmethod
    def create(
        cls,
        correlation_id: str,
        page_name: str,
        url: str,
        title: str,
        duration: float,
        success: bool = True,
        context: ExecutionContext | None = None,
    ) -> "UINavigationEndEvent":
        """工厂方法：创建事件（复用 correlation_id）

        自动注入当前 OpenTelemetry 追踪上下文（trace_id/span_id）。

        Args:
            correlation_id: 关联 ID（必须与 StartEvent 相同）
            page_name: 页面对象名称
            url: 目标 URL
            title: 页面标题
            duration: 导航耗时（秒）
            success: 是否成功
            context: 执行上下文

        Returns:
            UINavigationEndEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()
        return cls(
            page_name=page_name,
            url=url,
            title=title,
            duration=duration,
            success=success,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


@dataclass(frozen=True)
class UIClickEvent(Event):
    """UI 点击事件

    在 BasePage.click() 时触发。
    单一事件（非 Start/End 对）。

    v3.35.7: 新增
    """

    page_name: str = ""
    selector: str = ""  # 选择器
    element_text: str = ""  # 元素文本（如果有）
    duration: float = 0.0  # 点击耗时（秒）

    @classmethod
    def create(
        cls,
        page_name: str,
        selector: str,
        element_text: str = "",
        duration: float = 0.0,
        context: ExecutionContext | None = None,
    ) -> "UIClickEvent":
        """工厂方法

        自动注入当前 OpenTelemetry 追踪上下文（trace_id/span_id）。

        Args:
            page_name: 页面对象名称
            selector: 元素选择器
            element_text: 元素文本
            duration: 点击耗时（秒）
            context: 执行上下文

        Returns:
            UIClickEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()
        return cls(
            page_name=page_name,
            selector=selector,
            element_text=element_text,
            duration=duration,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


@dataclass(frozen=True)
class UIInputEvent(Event):
    """UI 输入事件

    在 BasePage.fill() 或 type() 时触发。

    v3.35.7: 新增
    """

    page_name: str = ""
    selector: str = ""
    value: str = ""  # 输入值（可能脱敏）
    masked: bool = False  # 是否已脱敏
    duration: float = 0.0

    @classmethod
    def create(
        cls,
        page_name: str,
        selector: str,
        value: str,
        masked: bool = False,
        duration: float = 0.0,
        context: ExecutionContext | None = None,
    ) -> "UIInputEvent":
        """工厂方法

        自动注入当前 OpenTelemetry 追踪上下文（trace_id/span_id）。

        Args:
            page_name: 页面对象名称
            selector: 元素选择器
            value: 输入值（可能已脱敏）
            masked: 是否已脱敏
            duration: 输入耗时（秒）
            context: 执行上下文

        Returns:
            UIInputEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()
        return cls(
            page_name=page_name,
            selector=selector,
            value=value,
            masked=masked,
            duration=duration,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


@dataclass(frozen=True)
class UIScreenshotEvent(Event):
    """UI 截图事件

    在 BasePage.screenshot() 时触发。

    v3.35.7: 新增
    """

    page_name: str = ""
    path: str = ""  # 截图保存路径
    full_page: bool = False  # 是否全页截图
    element_selector: str = ""  # 元素截图的选择器
    size_bytes: int = 0  # 图片大小

    @classmethod
    def create(
        cls,
        page_name: str,
        path: str = "",
        full_page: bool = False,
        element_selector: str = "",
        size_bytes: int = 0,
        context: ExecutionContext | None = None,
    ) -> "UIScreenshotEvent":
        """工厂方法

        自动注入当前 OpenTelemetry 追踪上下文（trace_id/span_id）。

        Args:
            page_name: 页面对象名称
            path: 截图保存路径
            full_page: 是否全页截图
            element_selector: 元素截图的选择器
            size_bytes: 图片大小（字节）
            context: 执行上下文

        Returns:
            UIScreenshotEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()
        return cls(
            page_name=page_name,
            path=path,
            full_page=full_page,
            element_selector=element_selector,
            size_bytes=size_bytes,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


@dataclass(frozen=True)
class UIWaitEvent(Event):
    """UI 等待事件

    在 BasePage.wait_for_*() 时触发。

    v3.35.7: 新增
    """

    page_name: str = ""
    wait_type: str = ""  # selector, url, load_state, timeout
    condition: str = ""  # 等待条件描述
    timeout: float = 0.0  # 超时时间（秒）
    duration: float = 0.0  # 实际等待时间（秒）
    success: bool = True

    @classmethod
    def create(
        cls,
        page_name: str,
        wait_type: str,
        condition: str,
        timeout: float = 0.0,
        duration: float = 0.0,
        success: bool = True,
        context: ExecutionContext | None = None,
    ) -> "UIWaitEvent":
        """工厂方法

        自动注入当前 OpenTelemetry 追踪上下文（trace_id/span_id）。

        Args:
            page_name: 页面对象名称
            wait_type: 等待类型（selector/url/load_state/timeout）
            condition: 等待条件描述
            timeout: 超时时间（秒）
            duration: 实际等待时间（秒）
            success: 是否成功
            context: 执行上下文

        Returns:
            UIWaitEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()
        return cls(
            page_name=page_name,
            wait_type=wait_type,
            condition=condition,
            timeout=timeout,
            duration=duration,
            success=success,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


@dataclass(frozen=True)
class UIErrorEvent(Event):
    """UI 操作错误事件

    在 UI 操作发生异常时触发。

    v3.35.7: 新增
    """

    page_name: str = ""
    operation: str = ""  # click, fill, wait_for_selector 等
    selector: str = ""
    error_type: str = ""
    error_message: str = ""
    screenshot_path: str = ""  # 错误截图路径（如果有）

    @classmethod
    def create(
        cls,
        page_name: str,
        operation: str,
        selector: str,
        error: Exception,
        screenshot_path: str = "",
        context: ExecutionContext | None = None,
    ) -> "UIErrorEvent":
        """工厂方法

        自动注入当前 OpenTelemetry 追踪上下文（trace_id/span_id）。

        Args:
            page_name: 页面对象名称
            operation: 操作类型（click/fill/wait_for_selector 等）
            selector: 元素选择器或操作目标
            error: 异常对象
            screenshot_path: 错误截图路径
            context: 执行上下文

        Returns:
            UIErrorEvent 实例
        """
        trace_id, span_id = _get_current_trace_context()
        return cls(
            page_name=page_name,
            operation=operation,
            selector=selector,
            error_type=type(error).__name__,
            error_message=str(error),
            screenshot_path=screenshot_path,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )
