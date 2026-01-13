"""现代化控制台调试器

v3.22.0 新增
v3.22.1 扩展：支持数据库调试

基于 EventBus 的事件驱动调试器，提供彩色、结构化的控制台输出。

特性：
- 事件驱动：自动订阅 EventBus，无需手动调用
- 彩色输出：使用 ANSI 颜色代码
- 结构化：清晰的请求/响应分隔
- 脱敏：自动隐藏敏感信息（Token、密码等）
- 多类型支持：HTTP 请求、数据库查询
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from df_test_framework.core.events.types import (
    DatabaseQueryEndEvent,
    DatabaseQueryErrorEvent,
    DatabaseQueryStartEvent,
    # GraphQL 事件 (v3.33.0)
    GraphQLRequestEndEvent,
    GraphQLRequestErrorEvent,
    GraphQLRequestStartEvent,
    # gRPC 事件 (v3.32.0)
    GrpcRequestEndEvent,
    GrpcRequestErrorEvent,
    GrpcRequestStartEvent,
    HttpRequestEndEvent,
    HttpRequestErrorEvent,
    HttpRequestStartEvent,
    # MQ 事件 (v3.34.1 重构)
    MessageConsumeEndEvent,
    MessageConsumeErrorEvent,
    MessagePublishEndEvent,
    MessagePublishErrorEvent,
)
from df_test_framework.infrastructure.logging import get_logger

logger = get_logger(__name__)


# ANSI 颜色代码
class Colors:
    """ANSI 颜色代码"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # 前景色
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

    # 背景色
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


def _supports_color() -> bool:
    """检查终端是否支持颜色"""
    # Windows 终端、VS Code、大多数现代终端都支持
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _colorize(text: str, color: str) -> str:
    """添加颜色（如果支持）"""
    if _supports_color():
        return f"{color}{text}{Colors.RESET}"
    return text


@dataclass
class RequestRecord:
    """HTTP 请求记录"""

    correlation_id: str
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    body: str | None = None
    start_time: datetime = field(default_factory=datetime.now)


@dataclass
class QueryRecord:
    """数据库查询记录（v3.22.1 新增）"""

    correlation_id: str
    operation: str  # SELECT, INSERT, UPDATE, DELETE
    table: str
    sql: str
    params: dict[str, Any] = field(default_factory=dict)
    database: str | None = None
    start_time: datetime = field(default_factory=datetime.now)


@dataclass
class GrpcCallRecord:
    """gRPC 调用记录（v3.32.0 新增）"""

    correlation_id: str
    service: str
    method: str
    metadata: dict[str, str] = field(default_factory=dict)
    request_data: str | None = None
    start_time: datetime = field(default_factory=datetime.now)


@dataclass
class GraphQLCallRecord:
    """GraphQL 调用记录（v3.33.0 新增）"""

    correlation_id: str
    url: str
    operation_type: str  # query, mutation, subscription
    operation_name: str | None = None
    query: str | None = None
    variables: str | None = None
    start_time: datetime = field(default_factory=datetime.now)


@dataclass
class MQMessageRecord:
    """MQ 消息记录（v3.34.0 新增）"""

    topic: str
    message_id: str = ""
    body_size: int = 0
    partition: int | None = None
    consumer_group: str | None = None  # 仅消费事件
    offset: int | None = None  # 仅消费事件
    timestamp: datetime = field(default_factory=datetime.now)


class ConsoleDebugObserver:
    """现代化控制台调试器

    v3.22.0 新增
    v3.22.1 扩展：支持数据库调试
    v3.32.0 扩展：支持 gRPC 调试
    v3.33.0 扩展：支持 GraphQL 调试
    v3.34.0 扩展：支持消息队列调试

    基于 EventBus 的事件驱动调试器，自动订阅事件并输出调试信息。

    特性：
    - 事件驱动：自动订阅 EventBus
    - 彩色输出：请求/响应使用不同颜色
    - 结构化：清晰的分隔线和缩进
    - 脱敏：自动隐藏 Token、密码等敏感信息
    - 可配置：控制是否显示 headers、body、SQL 等
    - 多类型支持：HTTP、数据库（v3.22.1）、gRPC（v3.32.0）、GraphQL（v3.33.0）、MQ（v3.34.0）

    使用方式：
        # 方式1：通过 fixture（推荐）
        def test_api(http_client, console_debugger):
            response = http_client.get("/users")
            # 控制台自动输出调试信息

        # 方式2：手动创建
        from df_test_framework.infrastructure.events import get_event_bus

        observer = ConsoleDebugObserver()
        observer.subscribe(get_event_bus())

        # 执行请求...

        observer.unsubscribe()

        # v3.22.1: 启用数据库调试
        observer = ConsoleDebugObserver(show_database=True)
        observer.subscribe(get_event_bus())

        # v3.32.0: 启用 gRPC 调试
        observer = ConsoleDebugObserver(show_grpc=True)
        observer.subscribe(get_event_bus())

        # v3.33.0: 启用 GraphQL 调试
        observer = ConsoleDebugObserver(show_graphql=True)
        observer.subscribe(get_event_bus())

        # v3.34.0: 启用消息队列调试
        observer = ConsoleDebugObserver(show_mq=True)
        observer.subscribe(get_event_bus())
    """

    def __init__(
        self,
        show_headers: bool = True,
        show_body: bool = True,
        show_params: bool = True,
        max_body_length: int = 500,
        use_colors: bool = True,
        output_to_logger: bool = False,
        # v3.22.1: 数据库调试选项
        show_database: bool = True,
        show_sql: bool = True,
        show_sql_params: bool = True,
        max_sql_length: int = 500,
        # v3.32.0: gRPC 调试选项
        show_grpc: bool = True,
        show_grpc_metadata: bool = True,
        show_grpc_data: bool = True,
        max_grpc_data_length: int = 500,
        # v3.33.0: GraphQL 调试选项
        show_graphql: bool = True,
        show_graphql_query: bool = True,
        show_graphql_variables: bool = False,
        max_graphql_query_length: int = 500,
        # v3.34.0: MQ 调试选项
        show_mq: bool = True,
    ):
        """初始化控制台调试器

        Args:
            show_headers: 是否显示请求/响应头
            show_body: 是否显示请求/响应体
            show_params: 是否显示 GET 参数
            max_body_length: 最大 body 显示长度
            use_colors: 是否使用颜色（自动检测终端支持）
            output_to_logger: 是否同时输出到 logger
            show_database: 是否显示数据库查询（v3.22.1 新增）
            show_sql: 是否显示 SQL 语句（v3.22.1 新增）
            show_sql_params: 是否显示 SQL 参数（v3.22.1 新增）
            max_sql_length: 最大 SQL 显示长度（v3.22.1 新增）
            show_grpc: 是否显示 gRPC 调用（v3.32.0 新增）
            show_grpc_metadata: 是否显示 gRPC 元数据（v3.32.0 新增）
            show_grpc_data: 是否显示 gRPC 请求/响应数据（v3.32.0 新增）
            max_grpc_data_length: 最大 gRPC 数据显示长度（v3.32.0 新增）
            show_graphql: 是否显示 GraphQL 调用（v3.33.0 新增）
            show_graphql_query: 是否显示 GraphQL 查询语句（v3.33.0 新增）
            show_graphql_variables: 是否显示 GraphQL 变量（v3.33.0 新增）
            max_graphql_query_length: 最大 GraphQL 查询显示长度（v3.33.0 新增）
            show_mq: 是否显示消息队列事件（v3.34.0 新增）
        """
        # HTTP 选项
        self.show_headers = show_headers
        self.show_body = show_body
        self.show_params = show_params
        self.max_body_length = max_body_length
        self.use_colors = use_colors and _supports_color()
        self.output_to_logger = output_to_logger

        # 数据库选项（v3.22.1）
        self.show_database = show_database
        self.show_sql = show_sql
        self.show_sql_params = show_sql_params
        self.max_sql_length = max_sql_length

        # gRPC 选项（v3.32.0）
        self.show_grpc = show_grpc
        self.show_grpc_metadata = show_grpc_metadata
        self.show_grpc_data = show_grpc_data
        self.max_grpc_data_length = max_grpc_data_length

        # GraphQL 选项（v3.33.0）
        self.show_graphql = show_graphql
        self.show_graphql_query = show_graphql_query
        self.show_graphql_variables = show_graphql_variables
        self.max_graphql_query_length = max_graphql_query_length

        # MQ 选项（v3.34.0）
        self.show_mq = show_mq

        # 存储进行中的请求/查询（用于关联 Start/End 事件）
        self._pending_requests: dict[str, RequestRecord] = {}
        self._pending_queries: dict[str, QueryRecord] = {}  # v3.22.1
        self._pending_grpc_calls: dict[str, GrpcCallRecord] = {}  # v3.32.0
        self._pending_graphql_calls: dict[str, GraphQLCallRecord] = {}  # v3.33.0
        self._event_bus = None

    def subscribe(self, event_bus) -> None:
        """订阅 EventBus 事件

        Args:
            event_bus: EventBus 实例
        """
        self._event_bus = event_bus

        # 订阅 HTTP 事件（使用事件类型类，保持类型安全）
        event_bus.subscribe(HttpRequestStartEvent, self._handle_request_start)
        event_bus.subscribe(HttpRequestEndEvent, self._handle_request_end)
        event_bus.subscribe(HttpRequestErrorEvent, self._handle_request_error)

        # v3.22.1: 订阅数据库事件
        if self.show_database:
            event_bus.subscribe(DatabaseQueryStartEvent, self._handle_query_start)
            event_bus.subscribe(DatabaseQueryEndEvent, self._handle_query_end)
            event_bus.subscribe(DatabaseQueryErrorEvent, self._handle_query_error)

        # v3.32.0: 订阅 gRPC 事件
        if self.show_grpc:
            event_bus.subscribe(GrpcRequestStartEvent, self._handle_grpc_start)
            event_bus.subscribe(GrpcRequestEndEvent, self._handle_grpc_end)
            event_bus.subscribe(GrpcRequestErrorEvent, self._handle_grpc_error)

        # v3.33.0: 订阅 GraphQL 事件
        if self.show_graphql:
            event_bus.subscribe(GraphQLRequestStartEvent, self._handle_graphql_start)
            event_bus.subscribe(GraphQLRequestEndEvent, self._handle_graphql_end)
            event_bus.subscribe(GraphQLRequestErrorEvent, self._handle_graphql_error)

        # v3.34.1: 订阅 MQ 事件（重构为 End/Error 事件）
        if self.show_mq:
            event_bus.subscribe(MessagePublishEndEvent, self._handle_mq_publish_end)
            event_bus.subscribe(MessagePublishErrorEvent, self._handle_mq_publish_error)
            event_bus.subscribe(MessageConsumeEndEvent, self._handle_mq_consume_end)
            event_bus.subscribe(MessageConsumeErrorEvent, self._handle_mq_consume_error)

    def unsubscribe(self) -> None:
        """取消订阅"""
        if self._event_bus:
            # 取消 HTTP 事件订阅
            self._event_bus.unsubscribe(HttpRequestStartEvent, self._handle_request_start)
            self._event_bus.unsubscribe(HttpRequestEndEvent, self._handle_request_end)
            self._event_bus.unsubscribe(HttpRequestErrorEvent, self._handle_request_error)

            # 取消数据库事件订阅
            if self.show_database:
                self._event_bus.unsubscribe(DatabaseQueryStartEvent, self._handle_query_start)
                self._event_bus.unsubscribe(DatabaseQueryEndEvent, self._handle_query_end)
                self._event_bus.unsubscribe(DatabaseQueryErrorEvent, self._handle_query_error)

            # v3.32.0: 取消 gRPC 事件订阅
            if self.show_grpc:
                self._event_bus.unsubscribe(GrpcRequestStartEvent, self._handle_grpc_start)
                self._event_bus.unsubscribe(GrpcRequestEndEvent, self._handle_grpc_end)
                self._event_bus.unsubscribe(GrpcRequestErrorEvent, self._handle_grpc_error)

            # v3.33.0: 取消 GraphQL 事件订阅
            if self.show_graphql:
                self._event_bus.unsubscribe(GraphQLRequestStartEvent, self._handle_graphql_start)
                self._event_bus.unsubscribe(GraphQLRequestEndEvent, self._handle_graphql_end)
                self._event_bus.unsubscribe(GraphQLRequestErrorEvent, self._handle_graphql_error)

            # v3.34.1: 取消 MQ 事件订阅（重构为 End/Error 事件）
            if self.show_mq:
                self._event_bus.unsubscribe(MessagePublishEndEvent, self._handle_mq_publish_end)
                self._event_bus.unsubscribe(MessagePublishErrorEvent, self._handle_mq_publish_error)
                self._event_bus.unsubscribe(MessageConsumeEndEvent, self._handle_mq_consume_end)
                self._event_bus.unsubscribe(MessageConsumeErrorEvent, self._handle_mq_consume_error)

            self._event_bus = None

    def _handle_request_start(self, event) -> None:
        """处理请求开始事件"""
        correlation_id = getattr(event, "correlation_id", "")

        # 记录请求信息
        record = RequestRecord(
            correlation_id=correlation_id,
            method=getattr(event, "method", ""),
            url=getattr(event, "url", ""),
            headers=dict(event.headers) if getattr(event, "headers", None) else {},
            params=dict(event.params) if getattr(event, "params", None) else {},
            body=getattr(event, "body", None),
        )
        self._pending_requests[correlation_id] = record

        # 输出请求信息
        self._print_request(record)

    def _handle_request_end(self, event) -> None:
        """处理请求结束事件"""
        correlation_id = getattr(event, "correlation_id", "")
        request = self._pending_requests.pop(correlation_id, None)

        status_code = getattr(event, "status_code", 0)
        duration = getattr(event, "duration", 0)
        headers = dict(event.headers) if getattr(event, "headers", None) else {}
        body = getattr(event, "body", None)

        # 输出响应信息
        self._print_response(
            method=request.method if request else "???",
            url=request.url if request else "???",
            status_code=status_code,
            duration_ms=duration * 1000,
            headers=headers,
            body=body,
        )

    def _handle_request_error(self, event) -> None:
        """处理请求错误事件"""
        correlation_id = getattr(event, "correlation_id", "")
        request = self._pending_requests.pop(correlation_id, None)

        error_type = getattr(event, "error_type", "UnknownError")
        error_message = getattr(event, "error_message", "")
        duration = getattr(event, "duration", 0)

        # 输出错误信息
        self._print_error(
            method=request.method if request else "???",
            url=request.url if request else "???",
            error_type=error_type,
            error_message=error_message,
            duration_ms=duration * 1000,
        )

    def _print_request(self, record: RequestRecord) -> None:
        """打印请求信息"""
        lines = []

        # 分隔线和标题
        separator = "─" * 60
        lines.append("")
        lines.append(self._color(separator, Colors.DIM))
        lines.append(
            self._color(f"🌐 {record.method} ", Colors.BOLD + Colors.CYAN)
            + self._color(record.url, Colors.CYAN)
        )

        # Headers
        if self.show_headers and record.headers:
            lines.append(self._color("  Headers:", Colors.GRAY))
            for key, value in record.headers.items():
                safe_value = self._sanitize_value(key, value)
                lines.append(f"    {self._color(key, Colors.BLUE)}: {safe_value}")

        # Params
        if self.show_params and record.params:
            lines.append(self._color("  Params:", Colors.GRAY))
            for key, value in record.params.items():
                lines.append(f"    {self._color(key, Colors.MAGENTA)}: {value}")

        # Body
        if self.show_body and record.body:
            lines.append(self._color("  Body:", Colors.GRAY))
            body_str = self._format_body(record.body)
            for line in body_str.split("\n"):
                lines.append(f"    {line}")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _print_response(
        self,
        method: str,
        url: str,
        status_code: int,
        duration_ms: float,
        headers: dict[str, str],
        body: str | None,
    ) -> None:
        """打印响应信息"""
        lines = []

        # 状态颜色
        if 200 <= status_code < 300:
            status_color = Colors.GREEN
            status_icon = "✅"
        elif 300 <= status_code < 400:
            status_color = Colors.YELLOW
            status_icon = "↩️"
        elif 400 <= status_code < 500:
            status_color = Colors.YELLOW
            status_icon = "⚠️"
        else:
            status_color = Colors.RED
            status_icon = "❌"

        # 响应行
        lines.append(
            f"  {status_icon} "
            + self._color(f"{status_code}", Colors.BOLD + status_color)
            + self._color(f" ({duration_ms:.2f}ms)", Colors.DIM)
        )

        # Headers
        if self.show_headers and headers:
            # 只显示关键响应头
            key_headers = ["content-type", "content-length", "x-request-id"]
            for key in key_headers:
                for h_key, h_value in headers.items():
                    if h_key.lower() == key:
                        lines.append(f"    {self._color(h_key, Colors.BLUE)}: {h_value}")

        # Body
        if self.show_body and body:
            lines.append(self._color("  Response:", Colors.GRAY))
            body_str = self._format_body(body)
            for line in body_str.split("\n")[:10]:  # 最多显示10行
                lines.append(f"    {line}")
            if body_str.count("\n") > 10:
                lines.append(self._color("    ... (truncated)", Colors.DIM))

        # 分隔线
        separator = "─" * 60
        lines.append(self._color(separator, Colors.DIM))
        lines.append("")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _print_error(
        self,
        method: str,
        url: str,
        error_type: str,
        error_message: str,
        duration_ms: float,
    ) -> None:
        """打印错误信息"""
        lines = []

        # 错误行
        lines.append(
            "  💥 "
            + self._color(f"{error_type}", Colors.BOLD + Colors.RED)
            + self._color(f" ({duration_ms:.2f}ms)", Colors.DIM)
        )
        lines.append(f"    {self._color(error_message, Colors.RED)}")

        # 分隔线
        separator = "─" * 60
        lines.append(self._color(separator, Colors.DIM))
        lines.append("")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    # =========================================================================
    # 数据库事件处理（v3.22.1 新增）
    # =========================================================================

    def _handle_query_start(self, event) -> None:
        """处理数据库查询开始事件"""
        if not self.show_database:
            return

        correlation_id = getattr(event, "correlation_id", "")

        # 记录查询信息
        record = QueryRecord(
            correlation_id=correlation_id,
            operation=getattr(event, "operation", ""),
            table=getattr(event, "table", ""),
            sql=getattr(event, "sql", ""),
            params=dict(event.params) if getattr(event, "params", None) else {},
            database=getattr(event, "database", None),
        )
        self._pending_queries[correlation_id] = record

        # 输出查询信息
        self._print_query(record)

    def _handle_query_end(self, event) -> None:
        """处理数据库查询结束事件"""
        if not self.show_database:
            return

        correlation_id = getattr(event, "correlation_id", "")
        query = self._pending_queries.pop(correlation_id, None)

        duration_ms = getattr(event, "duration_ms", 0)
        row_count = getattr(event, "row_count", 0)

        # 输出查询结果
        self._print_query_result(
            operation=query.operation if query else "???",
            table=query.table if query else "???",
            duration_ms=duration_ms,
            row_count=row_count,
        )

    def _handle_query_error(self, event) -> None:
        """处理数据库查询错误事件"""
        if not self.show_database:
            return

        correlation_id = getattr(event, "correlation_id", "")
        query = self._pending_queries.pop(correlation_id, None)

        error_type = getattr(event, "error_type", "UnknownError")
        error_message = getattr(event, "error_message", "")
        duration_ms = getattr(event, "duration_ms", 0)

        # 输出错误信息
        self._print_query_error(
            operation=query.operation if query else "???",
            table=query.table if query else "???",
            error_type=error_type,
            error_message=error_message,
            duration_ms=duration_ms,
        )

    def _print_query(self, record: QueryRecord) -> None:
        """打印数据库查询信息"""
        lines = []

        # 分隔线和标题
        separator = "─" * 60
        lines.append("")
        lines.append(self._color(separator, Colors.DIM))

        # 操作类型图标
        op_icons = {
            "SELECT": "🔍",
            "INSERT": "➕",
            "UPDATE": "✏️",
            "DELETE": "🗑️",
        }
        icon = op_icons.get(record.operation.upper(), "📊")

        # 数据库名（如果有）
        db_info = f" [{record.database}]" if record.database else ""

        lines.append(
            self._color(f"{icon} {record.operation} ", Colors.BOLD + Colors.YELLOW)
            + self._color(record.table, Colors.YELLOW)
            + self._color(db_info, Colors.DIM)
        )

        # SQL
        if self.show_sql and record.sql:
            lines.append(self._color("  SQL:", Colors.GRAY))
            sql_str = self._format_sql(record.sql)
            for line in sql_str.split("\n"):
                lines.append(f"    {self._color(line, Colors.WHITE)}")

        # Params
        if self.show_sql_params and record.params:
            lines.append(self._color("  Params:", Colors.GRAY))
            for key, value in record.params.items():
                lines.append(f"    {self._color(str(key), Colors.MAGENTA)}: {value}")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _print_query_result(
        self,
        operation: str,
        table: str,
        duration_ms: float,
        row_count: int,
    ) -> None:
        """打印数据库查询结果"""
        lines = []

        # 结果行
        lines.append(
            "  ✅ "
            + self._color(f"{row_count} rows", Colors.BOLD + Colors.GREEN)
            + self._color(f" ({duration_ms:.2f}ms)", Colors.DIM)
        )

        # 分隔线
        separator = "─" * 60
        lines.append(self._color(separator, Colors.DIM))
        lines.append("")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _print_query_error(
        self,
        operation: str,
        table: str,
        error_type: str,
        error_message: str,
        duration_ms: float,
    ) -> None:
        """打印数据库查询错误"""
        lines = []

        # 错误行
        lines.append(
            "  💥 "
            + self._color(f"{error_type}", Colors.BOLD + Colors.RED)
            + self._color(f" ({duration_ms:.2f}ms)", Colors.DIM)
        )
        lines.append(f"    {self._color(error_message, Colors.RED)}")

        # 分隔线
        separator = "─" * 60
        lines.append(self._color(separator, Colors.DIM))
        lines.append("")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _format_sql(self, sql: str) -> str:
        """格式化 SQL 语句"""
        # 简单格式化：去除多余空白
        sql_str = " ".join(sql.split())

        # 截断
        if len(sql_str) > self.max_sql_length:
            sql_str = sql_str[: self.max_sql_length] + " ... (truncated)"

        return sql_str

    # =========================================================================
    # gRPC 事件处理（v3.32.0 新增）
    # =========================================================================

    def _handle_grpc_start(self, event) -> None:
        """处理 gRPC 请求开始事件"""
        if not self.show_grpc:
            return

        correlation_id = getattr(event, "correlation_id", "")

        # 记录请求信息
        record = GrpcCallRecord(
            correlation_id=correlation_id,
            service=getattr(event, "service", ""),
            method=getattr(event, "method", ""),
            metadata=dict(event.metadata) if getattr(event, "metadata", None) else {},
            request_data=getattr(event, "request_data", None),
        )
        self._pending_grpc_calls[correlation_id] = record

        # 输出请求信息
        self._print_grpc_request(record)

    def _handle_grpc_end(self, event) -> None:
        """处理 gRPC 请求结束事件"""
        if not self.show_grpc:
            return

        correlation_id = getattr(event, "correlation_id", "")
        grpc_call = self._pending_grpc_calls.pop(correlation_id, None)

        status_code = getattr(event, "status_code", 0)
        duration = getattr(event, "duration", 0)
        response_data = getattr(event, "response_data", None)

        # 输出响应信息
        self._print_grpc_response(
            service=grpc_call.service if grpc_call else "???",
            method=grpc_call.method if grpc_call else "???",
            status_code=status_code,
            duration_ms=duration * 1000,
            response_data=response_data,
        )

    def _handle_grpc_error(self, event) -> None:
        """处理 gRPC 请求错误事件"""
        if not self.show_grpc:
            return

        correlation_id = getattr(event, "correlation_id", "")
        grpc_call = self._pending_grpc_calls.pop(correlation_id, None)

        error_code = getattr(event, "error_code", 2)
        error_type = getattr(event, "error_type", "UnknownError")
        error_message = getattr(event, "error_message", "")
        duration = getattr(event, "duration", 0)

        # 输出错误信息
        self._print_grpc_error(
            service=grpc_call.service if grpc_call else "???",
            method=grpc_call.method if grpc_call else "???",
            error_code=error_code,
            error_type=error_type,
            error_message=error_message,
            duration_ms=duration * 1000,
        )

    def _print_grpc_request(self, record: GrpcCallRecord) -> None:
        """打印 gRPC 请求信息"""
        lines = []

        # 分隔线和标题
        separator = "─" * 60
        lines.append("")
        lines.append(self._color(separator, Colors.DIM))
        lines.append(
            self._color("🔗 gRPC ", Colors.BOLD + Colors.MAGENTA)
            + self._color(f"{record.service}.{record.method}", Colors.MAGENTA)
        )

        # Metadata
        if self.show_grpc_metadata and record.metadata:
            lines.append(self._color("  Metadata:", Colors.GRAY))
            for key, value in record.metadata.items():
                safe_value = self._sanitize_value(key, value)
                lines.append(f"    {self._color(key, Colors.BLUE)}: {safe_value}")

        # Request Data
        if self.show_grpc_data and record.request_data:
            lines.append(self._color("  Request:", Colors.GRAY))
            data_str = self._format_grpc_data(record.request_data)
            for line in data_str.split("\n")[:10]:  # 最多显示10行
                lines.append(f"    {line}")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _print_grpc_response(
        self,
        service: str,
        method: str,
        status_code: int,
        duration_ms: float,
        response_data: str | None,
    ) -> None:
        """打印 gRPC 响应信息"""
        lines = []

        # 状态颜色和图标
        if status_code == 0:  # OK
            status_color = Colors.GREEN
            status_icon = "✅"
            status_name = "OK"
        else:
            status_color = Colors.RED
            status_icon = "❌"
            # gRPC 状态码名称映射
            status_names = {
                1: "CANCELLED",
                2: "UNKNOWN",
                3: "INVALID_ARGUMENT",
                4: "DEADLINE_EXCEEDED",
                5: "NOT_FOUND",
                6: "ALREADY_EXISTS",
                7: "PERMISSION_DENIED",
                8: "RESOURCE_EXHAUSTED",
                9: "FAILED_PRECONDITION",
                10: "ABORTED",
                11: "OUT_OF_RANGE",
                12: "UNIMPLEMENTED",
                13: "INTERNAL",
                14: "UNAVAILABLE",
                15: "DATA_LOSS",
                16: "UNAUTHENTICATED",
            }
            status_name = status_names.get(status_code, f"CODE_{status_code}")

        # 响应行
        lines.append(
            f"  {status_icon} "
            + self._color(f"{status_name}", Colors.BOLD + status_color)
            + self._color(f" ({duration_ms:.2f}ms)", Colors.DIM)
        )

        # Response Data
        if self.show_grpc_data and response_data:
            lines.append(self._color("  Response:", Colors.GRAY))
            data_str = self._format_grpc_data(response_data)
            for line in data_str.split("\n")[:10]:  # 最多显示10行
                lines.append(f"    {line}")

        # 分隔线
        separator = "─" * 60
        lines.append(self._color(separator, Colors.DIM))
        lines.append("")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _print_grpc_error(
        self,
        service: str,
        method: str,
        error_code: int,
        error_type: str,
        error_message: str,
        duration_ms: float,
    ) -> None:
        """打印 gRPC 错误信息"""
        lines = []

        # 错误行
        lines.append(
            "  💥 "
            + self._color(f"{error_type} (code={error_code})", Colors.BOLD + Colors.RED)
            + self._color(f" ({duration_ms:.2f}ms)", Colors.DIM)
        )
        lines.append(f"    {self._color(error_message, Colors.RED)}")

        # 分隔线
        separator = "─" * 60
        lines.append(self._color(separator, Colors.DIM))
        lines.append("")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _format_grpc_data(self, data: str) -> str:
        """格式化 gRPC 数据"""
        if not data:
            return ""

        # 尝试格式化 JSON
        try:
            parsed = json.loads(data)
            data_str = json.dumps(parsed, indent=2, ensure_ascii=False, default=str)
        except (json.JSONDecodeError, TypeError):
            data_str = data

        # 截断
        if len(data_str) > self.max_grpc_data_length:
            data_str = data_str[: self.max_grpc_data_length] + "\n... (truncated)"

        return data_str

    # =========================================================================
    # GraphQL 事件处理（v3.33.0 新增）
    # =========================================================================

    def _handle_graphql_start(self, event) -> None:
        """处理 GraphQL 请求开始事件"""
        if not self.show_graphql:
            return

        correlation_id = getattr(event, "correlation_id", "")

        # 记录请求信息
        record = GraphQLCallRecord(
            correlation_id=correlation_id,
            url=getattr(event, "url", ""),
            operation_type=getattr(event, "operation_type", ""),
            operation_name=getattr(event, "operation_name", None),
            query=getattr(event, "query", None),
            variables=getattr(event, "variables", None),
        )
        self._pending_graphql_calls[correlation_id] = record

        # 输出请求信息
        self._print_graphql_request(record)

    def _handle_graphql_end(self, event) -> None:
        """处理 GraphQL 请求结束事件"""
        if not self.show_graphql:
            return

        correlation_id = getattr(event, "correlation_id", "")
        graphql_call = self._pending_graphql_calls.pop(correlation_id, None)

        has_errors = getattr(event, "has_errors", False)
        error_count = getattr(event, "error_count", 0)
        duration = getattr(event, "duration", 0)
        data = getattr(event, "data", None)

        # 输出响应信息
        self._print_graphql_response(
            operation_type=graphql_call.operation_type if graphql_call else "???",
            operation_name=graphql_call.operation_name if graphql_call else None,
            has_errors=has_errors,
            error_count=error_count,
            duration_ms=duration * 1000,
            data=data,
        )

    def _handle_graphql_error(self, event) -> None:
        """处理 GraphQL 请求错误事件"""
        if not self.show_graphql:
            return

        correlation_id = getattr(event, "correlation_id", "")
        graphql_call = self._pending_graphql_calls.pop(correlation_id, None)

        error_type = getattr(event, "error_type", "UnknownError")
        error_message = getattr(event, "error_message", "")
        duration = getattr(event, "duration", 0)

        # 输出错误信息
        self._print_graphql_error(
            operation_type=graphql_call.operation_type if graphql_call else "???",
            operation_name=graphql_call.operation_name if graphql_call else None,
            error_type=error_type,
            error_message=error_message,
            duration_ms=duration * 1000,
        )

    def _print_graphql_request(self, record: GraphQLCallRecord) -> None:
        """打印 GraphQL 请求信息"""
        lines = []

        # 分隔线和标题
        separator = "─" * 60
        lines.append("")
        lines.append(self._color(separator, Colors.DIM))

        # 操作类型图标
        op_icons = {
            "query": "🔍",
            "mutation": "✏️",
            "subscription": "📡",
        }
        icon = op_icons.get(record.operation_type.lower(), "📊")
        op_name = record.operation_name or "anonymous"

        lines.append(
            self._color(f"{icon} GraphQL {record.operation_type}: ", Colors.BOLD + Colors.GREEN)
            + self._color(op_name, Colors.GREEN)
        )

        # URL
        if record.url:
            lines.append(self._color(f"  URL: {record.url}", Colors.DIM))

        # Query
        if self.show_graphql_query and record.query:
            lines.append(self._color("  Query:", Colors.GRAY))
            query_str = self._format_graphql_query(record.query)
            for line in query_str.split("\n")[:10]:  # 最多显示10行
                lines.append(f"    {self._color(line, Colors.WHITE)}")
            if query_str.count("\n") > 10:
                lines.append(self._color("    ... (truncated)", Colors.DIM))

        # Variables
        if self.show_graphql_variables and record.variables:
            lines.append(self._color("  Variables:", Colors.GRAY))
            try:
                vars_parsed = json.loads(record.variables)
                vars_str = json.dumps(vars_parsed, indent=2, ensure_ascii=False)
                for line in vars_str.split("\n")[:5]:  # 最多显示5行
                    lines.append(f"    {self._color(line, Colors.MAGENTA)}")
            except (json.JSONDecodeError, TypeError):
                lines.append(f"    {self._color(record.variables[:100], Colors.MAGENTA)}")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _print_graphql_response(
        self,
        operation_type: str,
        operation_name: str | None,
        has_errors: bool,
        error_count: int,
        duration_ms: float,
        data: str | None,
    ) -> None:
        """打印 GraphQL 响应信息"""
        lines = []

        # 状态颜色和图标
        if has_errors:
            status_color = Colors.RED
            status_icon = "❌"
            status_text = f"{error_count} error(s)"
        else:
            status_color = Colors.GREEN
            status_icon = "✅"
            status_text = "success"

        # 响应行
        lines.append(
            f"  {status_icon} "
            + self._color(status_text, Colors.BOLD + status_color)
            + self._color(f" ({duration_ms:.2f}ms)", Colors.DIM)
        )

        # 分隔线
        separator = "─" * 60
        lines.append(self._color(separator, Colors.DIM))
        lines.append("")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _print_graphql_error(
        self,
        operation_type: str,
        operation_name: str | None,
        error_type: str,
        error_message: str,
        duration_ms: float,
    ) -> None:
        """打印 GraphQL 错误信息"""
        lines = []

        # 错误行
        lines.append(
            "  💥 "
            + self._color(f"{error_type}", Colors.BOLD + Colors.RED)
            + self._color(f" ({duration_ms:.2f}ms)", Colors.DIM)
        )
        lines.append(f"    {self._color(error_message, Colors.RED)}")

        # 分隔线
        separator = "─" * 60
        lines.append(self._color(separator, Colors.DIM))
        lines.append("")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _format_graphql_query(self, query: str) -> str:
        """格式化 GraphQL 查询语句"""
        # 简单格式化：去除多余空白
        query_str = " ".join(query.split())

        # 截断
        if len(query_str) > self.max_graphql_query_length:
            query_str = query_str[: self.max_graphql_query_length] + " ... (truncated)"

        return query_str

    # =========================================================================
    # MQ 事件处理（v3.34.0 新增，v3.34.1 重构为 End/Error 模式）
    # =========================================================================

    def _handle_mq_publish_end(self, event: MessagePublishEndEvent) -> None:
        """处理消息发布完成事件（v3.34.1 重构）"""
        if not self.show_mq:
            return

        messenger_type = getattr(event, "messenger_type", "mq")
        topic = getattr(event, "topic", "")
        message_id = getattr(event, "message_id", "")
        duration = getattr(event, "duration", 0)
        partition = getattr(event, "partition", None)
        offset = getattr(event, "offset", None)

        self._print_mq_publish(
            messenger_type=messenger_type,
            topic=topic,
            message_id=message_id,
            duration=duration,
            partition=partition,
            offset=offset,
        )

    def _handle_mq_publish_error(self, event: MessagePublishErrorEvent) -> None:
        """处理消息发布错误事件（v3.34.1 新增）"""
        if not self.show_mq:
            return

        messenger_type = getattr(event, "messenger_type", "mq")
        topic = getattr(event, "topic", "")
        error_type = getattr(event, "error_type", "UnknownError")
        error_message = getattr(event, "error_message", "")
        duration = getattr(event, "duration", 0)

        self._print_mq_publish_error(
            messenger_type=messenger_type,
            topic=topic,
            error_type=error_type,
            error_message=error_message,
            duration=duration,
        )

    def _handle_mq_consume_end(self, event: MessageConsumeEndEvent) -> None:
        """处理消息消费完成事件（v3.34.1 重构）"""
        if not self.show_mq:
            return

        messenger_type = getattr(event, "messenger_type", "mq")
        topic = getattr(event, "topic", "")
        message_id = getattr(event, "message_id", "")
        consumer_group = getattr(event, "consumer_group", "")
        processing_time = getattr(event, "processing_time", 0)
        partition = getattr(event, "partition", None)
        offset = getattr(event, "offset", None)

        self._print_mq_consume(
            messenger_type=messenger_type,
            topic=topic,
            message_id=message_id,
            consumer_group=consumer_group,
            processing_time=processing_time,
            partition=partition,
            offset=offset,
        )

    def _handle_mq_consume_error(self, event: MessageConsumeErrorEvent) -> None:
        """处理消息消费错误事件（v3.34.1 新增）"""
        if not self.show_mq:
            return

        messenger_type = getattr(event, "messenger_type", "mq")
        topic = getattr(event, "topic", "")
        consumer_group = getattr(event, "consumer_group", "")
        error_type = getattr(event, "error_type", "UnknownError")
        error_message = getattr(event, "error_message", "")
        processing_time = getattr(event, "processing_time", 0)

        self._print_mq_consume_error(
            messenger_type=messenger_type,
            topic=topic,
            consumer_group=consumer_group,
            error_type=error_type,
            error_message=error_message,
            processing_time=processing_time,
        )

    def _print_mq_publish(
        self,
        messenger_type: str,
        topic: str,
        message_id: str,
        duration: float,
        partition: int | None,
        offset: int | None,
    ) -> None:
        """打印消息发布信息（v3.34.1 重构）"""
        lines = []

        # 分隔线和标题
        separator = "─" * 60
        lines.append("")
        lines.append(self._color(separator, Colors.DIM))

        # 发布图标和标题（显示 messenger_type）
        type_label = messenger_type.upper() if messenger_type else "MQ"
        lines.append(
            self._color(f"📤 {type_label} Publish: ", Colors.BOLD + Colors.CYAN)
            + self._color(topic, Colors.CYAN)
        )

        # 详情
        details = []
        if message_id:
            details.append(
                f"id={message_id[:16]}..." if len(message_id) > 16 else f"id={message_id}"
            )
        if partition is not None:
            details.append(f"partition={partition}")
        if offset is not None:
            details.append(f"offset={offset}")

        if details:
            lines.append(self._color(f"  {', '.join(details)}", Colors.DIM))

        # 状态和耗时
        duration_ms = duration * 1000 if duration else 0
        lines.append(
            "  ✅ "
            + self._color("published", Colors.BOLD + Colors.GREEN)
            + self._color(f" ({duration_ms:.2f}ms)", Colors.DIM)
        )

        # 分隔线
        lines.append(self._color(separator, Colors.DIM))
        lines.append("")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _print_mq_publish_error(
        self,
        messenger_type: str,
        topic: str,
        error_type: str,
        error_message: str,
        duration: float,
    ) -> None:
        """打印消息发布错误信息（v3.34.1 新增）"""
        lines = []

        # 分隔线和标题
        separator = "─" * 60
        lines.append("")
        lines.append(self._color(separator, Colors.DIM))

        # 发布图标和标题（显示 messenger_type）
        type_label = messenger_type.upper() if messenger_type else "MQ"
        lines.append(
            self._color(f"📤 {type_label} Publish: ", Colors.BOLD + Colors.CYAN)
            + self._color(topic, Colors.CYAN)
        )

        # 错误行
        duration_ms = duration * 1000 if duration else 0
        lines.append(
            "  💥 "
            + self._color(f"{error_type}", Colors.BOLD + Colors.RED)
            + self._color(f" ({duration_ms:.2f}ms)", Colors.DIM)
        )
        lines.append(f"    {self._color(error_message, Colors.RED)}")

        # 分隔线
        lines.append(self._color(separator, Colors.DIM))
        lines.append("")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _print_mq_consume(
        self,
        messenger_type: str,
        topic: str,
        message_id: str,
        consumer_group: str,
        processing_time: float,
        partition: int | None,
        offset: int | None,
    ) -> None:
        """打印消息消费信息（v3.34.1 重构）"""
        lines = []

        # 分隔线和标题
        separator = "─" * 60
        lines.append("")
        lines.append(self._color(separator, Colors.DIM))

        # 消费图标和标题（显示 messenger_type）
        type_label = messenger_type.upper() if messenger_type else "MQ"
        lines.append(
            self._color(f"📥 {type_label} Consume: ", Colors.BOLD + Colors.YELLOW)
            + self._color(topic, Colors.YELLOW)
        )

        # 详情
        details = []
        if consumer_group:
            details.append(f"group={consumer_group}")
        if message_id:
            details.append(
                f"id={message_id[:16]}..." if len(message_id) > 16 else f"id={message_id}"
            )
        if partition is not None:
            details.append(f"partition={partition}")
        if offset is not None:
            details.append(f"offset={offset}")

        if details:
            lines.append(self._color(f"  {', '.join(details)}", Colors.DIM))

        # 状态和耗时
        processing_ms = processing_time * 1000 if processing_time else 0
        lines.append(
            "  ✅ "
            + self._color("consumed", Colors.BOLD + Colors.GREEN)
            + self._color(f" ({processing_ms:.2f}ms)", Colors.DIM)
        )

        # 分隔线
        lines.append(self._color(separator, Colors.DIM))
        lines.append("")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    def _print_mq_consume_error(
        self,
        messenger_type: str,
        topic: str,
        consumer_group: str,
        error_type: str,
        error_message: str,
        processing_time: float,
    ) -> None:
        """打印消息消费错误信息（v3.34.1 新增）"""
        lines = []

        # 分隔线和标题
        separator = "─" * 60
        lines.append("")
        lines.append(self._color(separator, Colors.DIM))

        # 消费图标和标题（显示 messenger_type）
        type_label = messenger_type.upper() if messenger_type else "MQ"
        lines.append(
            self._color(f"📥 {type_label} Consume: ", Colors.BOLD + Colors.YELLOW)
            + self._color(topic, Colors.YELLOW)
        )

        # 消费者组信息
        if consumer_group:
            lines.append(self._color(f"  group={consumer_group}", Colors.DIM))

        # 错误行
        processing_ms = processing_time * 1000 if processing_time else 0
        lines.append(
            "  💥 "
            + self._color(f"{error_type}", Colors.BOLD + Colors.RED)
            + self._color(f" ({processing_ms:.2f}ms)", Colors.DIM)
        )
        lines.append(f"    {self._color(error_message, Colors.RED)}")

        # 分隔线
        lines.append(self._color(separator, Colors.DIM))
        lines.append("")

        # 输出
        output = "\n".join(lines)
        self._output(output)

    # =========================================================================
    # 通用辅助方法
    # =========================================================================

    def _color(self, text: str, color: str) -> str:
        """添加颜色"""
        if self.use_colors:
            return f"{color}{text}{Colors.RESET}"
        return text

    @property
    def _sanitize_service(self):
        """获取脱敏服务

        v3.40.0 新增：使用统一脱敏服务
        v3.40.1 修复：移除类级别缓存，确保配置变更后能正确生效
        """
        from df_test_framework.infrastructure.sanitize import get_sanitize_service

        return get_sanitize_service()

    def _sanitize_value(self, key: str, value: str) -> str:
        """脱敏敏感值

        v3.40.0 重构：使用统一脱敏服务 SanitizeService
        - 敏感字段通过 SanitizeConfig.sensitive_keys 配置
        - 脱敏策略通过 SanitizeConfig.default_strategy 配置
        - 通过 SanitizeConfig.console.enabled 独立控制
        """
        service = self._sanitize_service
        if not service.is_context_enabled("console"):
            return value
        return service.sanitize_value(key, value)

    def _format_body(self, body: str | dict | Any) -> str:
        """格式化 body"""
        if isinstance(body, dict):
            body_str = json.dumps(body, indent=2, ensure_ascii=False, default=str)
        elif isinstance(body, str):
            # 尝试格式化 JSON
            try:
                parsed = json.loads(body)
                body_str = json.dumps(parsed, indent=2, ensure_ascii=False, default=str)
            except (json.JSONDecodeError, TypeError):
                body_str = body
        else:
            body_str = str(body)

        # 截断
        if len(body_str) > self.max_body_length:
            body_str = body_str[: self.max_body_length] + "\n... (truncated)"

        return body_str

    def _output(self, text: str) -> None:
        """输出到控制台

        v3.28.0: 调试输出始终直接输出到 stderr，不走 pytest 桥接。
        原因：调试输出有自己的格式化（彩色、分隔线），不应被 pytest log_cli_format 破坏。
        """
        # 直接输出到 stderr，保持调试输出的完整格式
        print(text, file=sys.stderr)
        if self.output_to_logger:
            logger.debug(text)


# 创建默认实例的便捷函数
def create_console_debugger(
    show_headers: bool = True,
    show_body: bool = True,
    show_params: bool = True,
    max_body_length: int = 500,
    # v3.22.1: 数据库调试选项
    show_database: bool = True,
    show_sql: bool = True,
    show_sql_params: bool = True,
    max_sql_length: int = 500,
    # v3.32.0: gRPC 调试选项
    show_grpc: bool = True,
    show_grpc_metadata: bool = True,
    show_grpc_data: bool = True,
    max_grpc_data_length: int = 500,
    # v3.33.0: GraphQL 调试选项
    show_graphql: bool = True,
    show_graphql_query: bool = True,
    show_graphql_variables: bool = False,
    max_graphql_query_length: int = 500,
    # v3.34.0: MQ 调试选项
    show_mq: bool = True,
) -> ConsoleDebugObserver:
    """创建控制台调试器

    Args:
        show_headers: 是否显示请求/响应头
        show_body: 是否显示请求/响应体
        show_params: 是否显示 GET 参数
        max_body_length: 最大 body 显示长度
        show_database: 是否显示数据库查询（v3.22.1 新增）
        show_sql: 是否显示 SQL 语句（v3.22.1 新增）
        show_sql_params: 是否显示 SQL 参数（v3.22.1 新增）
        max_sql_length: 最大 SQL 显示长度（v3.22.1 新增）
        show_grpc: 是否显示 gRPC 调用（v3.32.0 新增）
        show_grpc_metadata: 是否显示 gRPC 元数据（v3.32.0 新增）
        show_grpc_data: 是否显示 gRPC 请求/响应数据（v3.32.0 新增）
        max_grpc_data_length: 最大 gRPC 数据显示长度（v3.32.0 新增）
        show_graphql: 是否显示 GraphQL 调用（v3.33.0 新增）
        show_graphql_query: 是否显示 GraphQL 查询语句（v3.33.0 新增）
        show_graphql_variables: 是否显示 GraphQL 变量（v3.33.0 新增）
        max_graphql_query_length: 最大 GraphQL 查询显示长度（v3.33.0 新增）
        show_mq: 是否显示消息队列事件（v3.34.0 新增）

    Returns:
        ConsoleDebugObserver 实例
    """
    return ConsoleDebugObserver(
        show_headers=show_headers,
        show_body=show_body,
        show_params=show_params,
        max_body_length=max_body_length,
        show_database=show_database,
        show_sql=show_sql,
        show_sql_params=show_sql_params,
        max_sql_length=max_sql_length,
        show_grpc=show_grpc,
        show_grpc_metadata=show_grpc_metadata,
        show_grpc_data=show_grpc_data,
        max_grpc_data_length=max_grpc_data_length,
        show_graphql=show_graphql,
        show_graphql_query=show_graphql_query,
        show_graphql_variables=show_graphql_variables,
        max_graphql_query_length=max_graphql_query_length,
        show_mq=show_mq,
    )


__all__ = [
    "ConsoleDebugObserver",
    "create_console_debugger",
    "Colors",
    "QueryRecord",
    "GrpcCallRecord",
    "GraphQLCallRecord",
    "MQMessageRecord",
]
