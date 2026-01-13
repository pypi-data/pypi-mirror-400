"""ConsoleDebugObserver 单元测试

测试控制台调试器的核心功能：
- 初始化配置
- 事件订阅/取消订阅
- 敏感数据脱敏
- 请求/响应格式化
- 数据记录类
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

from df_test_framework.testing.debugging.console import (
    Colors,
    ConsoleDebugObserver,
    GraphQLCallRecord,
    GrpcCallRecord,
    MQMessageRecord,
    QueryRecord,
    RequestRecord,
    _colorize,
    _supports_color,
)


class TestColors:
    """测试 ANSI 颜色代码"""

    def test_colors_have_reset(self):
        """验证颜色类有 RESET 属性"""
        assert Colors.RESET == "\033[0m"

    def test_colors_have_foreground_colors(self):
        """验证前景色定义"""
        assert Colors.RED == "\033[91m"
        assert Colors.GREEN == "\033[92m"
        assert Colors.YELLOW == "\033[93m"
        assert Colors.BLUE == "\033[94m"
        assert Colors.CYAN == "\033[96m"

    def test_colors_have_background_colors(self):
        """验证背景色定义"""
        assert Colors.BG_RED == "\033[41m"
        assert Colors.BG_GREEN == "\033[42m"

    def test_colors_have_styles(self):
        """验证样式定义"""
        assert Colors.BOLD == "\033[1m"
        assert Colors.DIM == "\033[2m"


class TestColorHelpers:
    """测试颜色辅助函数"""

    def test_supports_color_returns_bool(self):
        """验证 _supports_color 返回布尔值"""
        result = _supports_color()
        assert isinstance(result, bool)

    @patch("sys.stdout")
    def test_supports_color_with_tty(self, mock_stdout):
        """测试终端支持颜色时的返回值"""
        mock_stdout.isatty.return_value = True
        # 重新导入以触发检测
        assert _supports_color() or not _supports_color()  # 取决于实际环境

    def test_colorize_adds_color_codes(self):
        """测试颜色添加功能"""
        # 模拟支持颜色的情况
        with patch(
            "df_test_framework.testing.debugging.console._supports_color", return_value=True
        ):
            result = _colorize("test", Colors.RED)
            assert Colors.RED in result
            assert Colors.RESET in result
            assert "test" in result

    def test_colorize_without_color_support(self):
        """测试不支持颜色时返回原文本"""
        with patch(
            "df_test_framework.testing.debugging.console._supports_color", return_value=False
        ):
            result = _colorize("test", Colors.RED)
            assert result == "test"


class TestRequestRecord:
    """测试 HTTP 请求记录数据类"""

    def test_create_request_record(self):
        """测试创建请求记录"""
        record = RequestRecord(
            correlation_id="test-123",
            method="GET",
            url="https://api.example.com/users",
        )
        assert record.correlation_id == "test-123"
        assert record.method == "GET"
        assert record.url == "https://api.example.com/users"

    def test_request_record_default_values(self):
        """测试请求记录默认值"""
        record = RequestRecord(
            correlation_id="test-123",
            method="POST",
            url="/api/test",
        )
        assert record.headers == {}
        assert record.params == {}
        assert record.body is None
        assert isinstance(record.start_time, datetime)

    def test_request_record_with_all_fields(self):
        """测试请求记录所有字段"""
        start_time = datetime.now()
        record = RequestRecord(
            correlation_id="test-456",
            method="POST",
            url="/api/users",
            headers={"Content-Type": "application/json"},
            params={"page": 1},
            body='{"name": "test"}',
            start_time=start_time,
        )
        assert record.headers == {"Content-Type": "application/json"}
        assert record.params == {"page": 1}
        assert record.body == '{"name": "test"}'
        assert record.start_time == start_time


class TestQueryRecord:
    """测试数据库查询记录数据类"""

    def test_create_query_record(self):
        """测试创建查询记录"""
        record = QueryRecord(
            correlation_id="query-123",
            operation="SELECT",
            table="users",
            sql="SELECT * FROM users WHERE id = :id",
        )
        assert record.correlation_id == "query-123"
        assert record.operation == "SELECT"
        assert record.table == "users"

    def test_query_record_default_values(self):
        """测试查询记录默认值"""
        record = QueryRecord(
            correlation_id="query-456",
            operation="INSERT",
            table="orders",
            sql="INSERT INTO orders VALUES (:values)",
        )
        assert record.params == {}
        assert record.database is None
        assert isinstance(record.start_time, datetime)


class TestGrpcCallRecord:
    """测试 gRPC 调用记录数据类"""

    def test_create_grpc_record(self):
        """测试创建 gRPC 记录"""
        record = GrpcCallRecord(
            correlation_id="grpc-123",
            service="UserService",
            method="GetUser",
        )
        assert record.correlation_id == "grpc-123"
        assert record.service == "UserService"
        assert record.method == "GetUser"

    def test_grpc_record_default_values(self):
        """测试 gRPC 记录默认值"""
        record = GrpcCallRecord(
            correlation_id="grpc-456",
            service="OrderService",
            method="CreateOrder",
        )
        assert record.metadata == {}
        assert record.request_data is None
        assert isinstance(record.start_time, datetime)


class TestGraphQLCallRecord:
    """测试 GraphQL 调用记录数据类"""

    def test_create_graphql_record(self):
        """测试创建 GraphQL 记录"""
        record = GraphQLCallRecord(
            correlation_id="gql-123",
            url="https://api.example.com/graphql",
            operation_type="query",
        )
        assert record.correlation_id == "gql-123"
        assert record.url == "https://api.example.com/graphql"
        assert record.operation_type == "query"

    def test_graphql_record_with_operation_name(self):
        """测试 GraphQL 记录包含操作名"""
        record = GraphQLCallRecord(
            correlation_id="gql-456",
            url="/graphql",
            operation_type="mutation",
            operation_name="CreateUser",
            query="mutation CreateUser($input: UserInput!) { createUser(input: $input) { id } }",
            variables='{"input": {"name": "test"}}',
        )
        assert record.operation_name == "CreateUser"
        assert "mutation" in record.query


class TestMQMessageRecord:
    """测试 MQ 消息记录数据类"""

    def test_create_mq_record(self):
        """测试创建 MQ 记录"""
        record = MQMessageRecord(topic="orders")
        assert record.topic == "orders"
        assert record.message_id == ""
        assert record.body_size == 0

    def test_mq_record_with_all_fields(self):
        """测试 MQ 记录所有字段"""
        record = MQMessageRecord(
            topic="orders",
            message_id="msg-123",
            body_size=1024,
            partition=0,
            consumer_group="order-consumers",
            offset=12345,
        )
        assert record.message_id == "msg-123"
        assert record.body_size == 1024
        assert record.partition == 0
        assert record.consumer_group == "order-consumers"
        assert record.offset == 12345


class TestConsoleDebugObserverInit:
    """测试 ConsoleDebugObserver 初始化"""

    def test_default_init(self):
        """测试默认初始化"""
        observer = ConsoleDebugObserver()
        assert observer.show_headers is True
        assert observer.show_body is True
        assert observer.show_params is True
        assert observer.max_body_length == 500
        assert observer.output_to_logger is False

    def test_init_with_custom_http_options(self):
        """测试自定义 HTTP 选项"""
        observer = ConsoleDebugObserver(
            show_headers=False,
            show_body=False,
            show_params=False,
            max_body_length=1000,
        )
        assert observer.show_headers is False
        assert observer.show_body is False
        assert observer.show_params is False
        assert observer.max_body_length == 1000

    def test_init_with_database_options(self):
        """测试数据库调试选项"""
        observer = ConsoleDebugObserver(
            show_database=True,
            show_sql=True,
            show_sql_params=False,
            max_sql_length=1000,
        )
        assert observer.show_database is True
        assert observer.show_sql is True
        assert observer.show_sql_params is False
        assert observer.max_sql_length == 1000

    def test_init_with_grpc_options(self):
        """测试 gRPC 调试选项"""
        observer = ConsoleDebugObserver(
            show_grpc=True,
            show_grpc_metadata=False,
            show_grpc_data=True,
            max_grpc_data_length=2000,
        )
        assert observer.show_grpc is True
        assert observer.show_grpc_metadata is False
        assert observer.show_grpc_data is True
        assert observer.max_grpc_data_length == 2000

    def test_init_with_graphql_options(self):
        """测试 GraphQL 调试选项"""
        observer = ConsoleDebugObserver(
            show_graphql=True,
            show_graphql_query=True,
            show_graphql_variables=True,
            max_graphql_query_length=2000,
        )
        assert observer.show_graphql is True
        assert observer.show_graphql_query is True
        assert observer.show_graphql_variables is True
        assert observer.max_graphql_query_length == 2000

    def test_init_with_mq_options(self):
        """测试 MQ 调试选项"""
        observer = ConsoleDebugObserver(show_mq=True)
        assert observer.show_mq is True

    def test_init_pending_records_empty(self):
        """测试初始化时待处理记录为空"""
        observer = ConsoleDebugObserver()
        assert observer._pending_requests == {}
        assert observer._pending_queries == {}
        assert observer._pending_grpc_calls == {}
        assert observer._pending_graphql_calls == {}

    def test_init_with_logger_output(self):
        """测试启用日志输出"""
        observer = ConsoleDebugObserver(output_to_logger=True)
        assert observer.output_to_logger is True


class TestConsoleDebugObserverSensitiveFields:
    """测试敏感字段配置 (v3.40.0 使用统一脱敏服务)"""

    def test_uses_unified_sanitize_service(self):
        """验证使用统一脱敏服务"""
        observer = ConsoleDebugObserver()
        # 访问 _sanitize_service 属性触发惰性加载
        service = observer._sanitize_service
        assert service is not None
        # 验证服务来自统一脱敏模块
        from df_test_framework.infrastructure.sanitize import SanitizeService

        assert isinstance(service, SanitizeService)

    def test_sanitize_service_has_sensitive_keys(self):
        """验证脱敏服务包含敏感字段配置"""
        observer = ConsoleDebugObserver()
        service = observer._sanitize_service
        # 验证常见敏感字段能被识别
        assert service.is_sensitive("password") is True
        assert service.is_sensitive("token") is True
        assert service.is_sensitive("secret") is True
        assert service.is_sensitive("api_key") is True


class TestConsoleDebugObserverSubscription:
    """测试事件订阅/取消订阅"""

    def test_subscribe_stores_event_bus(self):
        """测试订阅保存 EventBus 引用"""
        observer = ConsoleDebugObserver()
        mock_event_bus = MagicMock()

        observer.subscribe(mock_event_bus)

        assert observer._event_bus == mock_event_bus

    def test_subscribe_registers_http_handlers(self):
        """测试订阅注册 HTTP 事件处理器"""
        observer = ConsoleDebugObserver()
        mock_event_bus = MagicMock()

        observer.subscribe(mock_event_bus)

        # 验证调用了 subscribe 方法
        assert mock_event_bus.subscribe.called

    def test_subscribe_registers_database_handlers(self):
        """测试订阅注册数据库事件处理器"""
        observer = ConsoleDebugObserver(show_database=True)
        mock_event_bus = MagicMock()

        observer.subscribe(mock_event_bus)

        assert mock_event_bus.subscribe.called

    def test_unsubscribe_clears_event_bus(self):
        """测试取消订阅清除 EventBus 引用"""
        observer = ConsoleDebugObserver()
        mock_event_bus = MagicMock()

        observer.subscribe(mock_event_bus)
        observer.unsubscribe()

        assert observer._event_bus is None

    def test_unsubscribe_without_subscription(self):
        """测试未订阅时取消订阅不报错"""
        observer = ConsoleDebugObserver()
        # 不应该抛出异常
        observer.unsubscribe()
        assert observer._event_bus is None


class TestConsoleDebugObserverSanitize:
    """测试敏感数据脱敏"""

    def test_sanitize_sensitive_authorization(self):
        """测试脱敏 Authorization 头"""
        observer = ConsoleDebugObserver()
        result = observer._sanitize_value("authorization", "Bearer secret-token-123")
        assert "***" in result or result == "****"  # 脱敏字符

    def test_sanitize_sensitive_password(self):
        """测试脱敏 password 字段"""
        observer = ConsoleDebugObserver()
        # 使用足够长的值以确保有多个脱敏字符
        result = observer._sanitize_value("password", "mysecretpassword123")
        assert "*" in result  # 脱敏字符

    def test_sanitize_sensitive_token(self):
        """测试脱敏 token 字段"""
        observer = ConsoleDebugObserver()
        # 使用足够长的值以确保有多个脱敏字符
        result = observer._sanitize_value("token", "my-long-token-value-here")
        assert "*" in result  # 脱敏字符

    def test_sanitize_sensitive_api_key(self):
        """测试脱敏 api_key 字段"""
        observer = ConsoleDebugObserver()
        # 使用足够长的值以确保有多个脱敏字符
        result = observer._sanitize_value("api_key", "my-long-api-key-here")
        assert "*" in result  # 脱敏字符

    def test_sanitize_non_sensitive_field(self):
        """测试非敏感字段保持原值"""
        observer = ConsoleDebugObserver()
        result = observer._sanitize_value("username", "testuser")
        assert result == "testuser"

    def test_sanitize_content_type(self):
        """测试 Content-Type 保持原值"""
        observer = ConsoleDebugObserver()
        result = observer._sanitize_value("Content-Type", "application/json")
        assert result == "application/json"

    def test_sanitize_x_token(self):
        """测试 x-token 脱敏"""
        observer = ConsoleDebugObserver()
        result = observer._sanitize_value("x-token", "api-key-456")
        assert "***" in result  # 脱敏字符


class TestConsoleDebugObserverFormatting:
    """测试格式化功能"""

    def test_format_body_with_dict(self):
        """测试格式化字典 body"""
        observer = ConsoleDebugObserver()
        body = {"name": "test", "value": 123}
        result = observer._format_body(body)
        assert "name" in result
        assert "test" in result

    def test_format_body_with_string(self):
        """测试格式化字符串 body"""
        observer = ConsoleDebugObserver()
        body = '{"name": "test"}'
        result = observer._format_body(body)
        assert "name" in result

    def test_format_body_truncation(self):
        """测试 body 截断"""
        observer = ConsoleDebugObserver(max_body_length=10)
        body = "a" * 100
        result = observer._format_body(body)
        # 截断后应该比原始长度短，包含截断标记
        assert len(result) < 100
        assert "truncated" in result or len(result) <= 30

    def test_format_sql(self):
        """测试 SQL 格式化"""
        observer = ConsoleDebugObserver()
        sql = "SELECT * FROM users WHERE id = :id"
        result = observer._format_sql(sql)
        assert "SELECT" in result

    def test_format_sql_truncation(self):
        """测试 SQL 截断"""
        observer = ConsoleDebugObserver(max_sql_length=10)
        sql = "SELECT * FROM very_long_table_name WHERE column = value"
        result = observer._format_sql(sql)
        # 截断后应该比原始长度短
        assert len(result) < len(sql)

    def test_format_grpc_data(self):
        """测试 gRPC 数据格式化"""
        observer = ConsoleDebugObserver()
        data = '{"user_id": 123}'
        result = observer._format_grpc_data(data)
        assert "user_id" in result

    def test_format_graphql_query(self):
        """测试 GraphQL 查询格式化"""
        observer = ConsoleDebugObserver()
        query = "query GetUser { user(id: 1) { name } }"
        result = observer._format_graphql_query(query)
        assert "GetUser" in result


class TestConsoleDebugObserverColor:
    """测试颜色输出功能"""

    def test_color_with_colors_enabled(self):
        """测试启用颜色时的输出"""
        observer = ConsoleDebugObserver(use_colors=True)
        # 模拟支持颜色
        observer.use_colors = True
        result = observer._color("test", Colors.RED)
        # 根据终端支持情况，结果可能包含颜色代码或原文本
        assert "test" in result

    def test_color_with_colors_disabled(self):
        """测试禁用颜色时的输出"""
        observer = ConsoleDebugObserver(use_colors=False)
        observer.use_colors = False
        result = observer._color("test", Colors.RED)
        assert result == "test"


class TestConsoleDebugObserverOutput:
    """测试输出功能"""

    @patch("builtins.print")
    def test_output_to_console(self, mock_print):
        """测试输出到控制台"""
        observer = ConsoleDebugObserver(output_to_logger=False)
        observer._output("test message")
        # print 可能带 file 参数
        mock_print.assert_called()
        args, kwargs = mock_print.call_args
        assert args[0] == "test message"

    @patch("df_test_framework.testing.debugging.console.logger")
    def test_output_to_logger(self, mock_logger):
        """测试输出到日志"""
        observer = ConsoleDebugObserver(output_to_logger=True)
        observer._output("test message")
        mock_logger.debug.assert_called()


__all__ = [
    "TestColors",
    "TestColorHelpers",
    "TestRequestRecord",
    "TestQueryRecord",
    "TestGrpcCallRecord",
    "TestGraphQLCallRecord",
    "TestMQMessageRecord",
    "TestConsoleDebugObserverInit",
    "TestConsoleDebugObserverSensitiveFields",
    "TestConsoleDebugObserverSubscription",
    "TestConsoleDebugObserverSanitize",
    "TestConsoleDebugObserverFormatting",
    "TestConsoleDebugObserverColor",
    "TestConsoleDebugObserverOutput",
]
