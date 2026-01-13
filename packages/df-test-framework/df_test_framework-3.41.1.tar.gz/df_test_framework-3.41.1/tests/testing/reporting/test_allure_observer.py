"""AllureObserver 测试模块

测试 Allure 观察者的各种功能：
- 初始化和配置
- HTTP 请求/响应记录
- GraphQL 请求记录
- gRPC 调用记录
- 数据库事件处理
- 缓存事件处理
- 消息队列事件处理
- 存储操作事件处理
- 事务事件处理
- UI 事件处理
- 清理机制

v3.36.0 - 技术债务清理：提升测试覆盖率
"""

import json
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest

# ========== 辅助类：模拟事件 ==========


@dataclass
class MockRequest:
    """模拟 HTTP Request"""

    method: str = "GET"
    url: str = "https://api.example.com/users"
    headers: dict | None = None
    params: dict | None = None
    json: dict | None = None
    data: str | None = None


@dataclass
class MockResponse:
    """模拟 HTTP Response"""

    status_code: int = 200
    headers: dict | None = None
    body: str | None = None


@dataclass
class MockEvent:
    """模拟事件基类"""

    event_id: str = "evt-001"
    correlation_id: str = "corr-001"
    trace_id: str | None = None
    span_id: str | None = None


@dataclass
class MockHttpRequestStartEvent(MockEvent):
    """模拟 HTTP 请求开始事件"""

    method: str = "POST"
    url: str = "https://api.example.com/orders"
    headers: dict | None = None
    body: str | None = None
    params: dict | None = None


@dataclass
class MockHttpRequestEndEvent(MockEvent):
    """模拟 HTTP 请求结束事件"""

    method: str = "POST"
    url: str = "https://api.example.com/orders"
    status_code: int = 201
    headers: dict | None = None
    body: str | None = None
    duration: float = 0.5


@dataclass
class MockHttpRequestErrorEvent(MockEvent):
    """模拟 HTTP 请求错误事件"""

    method: str = "POST"
    url: str = "https://api.example.com/orders"
    error_type: str = "ConnectionError"
    error_message: str = "Connection refused"
    duration: float = 0.1


@dataclass
class MockMiddlewareExecuteEvent(MockEvent):
    """模拟中间件执行事件"""

    middleware_name: str = "SignatureMiddleware"
    phase: str = "before"
    changes: dict | None = None


@dataclass
class MockGraphQLRequestStartEvent(MockEvent):
    """模拟 GraphQL 请求开始事件"""

    url: str = "https://api.example.com/graphql"
    operation_type: str = "query"
    operation_name: str = "GetUsers"
    query: str = "query GetUsers { users { id name } }"
    variables: dict | None = None


@dataclass
class MockGraphQLRequestEndEvent(MockEvent):
    """模拟 GraphQL 请求结束事件"""

    url: str = "https://api.example.com/graphql"
    operation_type: str = "query"
    operation_name: str = "GetUsers"
    has_errors: bool = False
    error_count: int = 0
    data: str | None = None
    duration: float = 0.3


@dataclass
class MockGraphQLRequestErrorEvent(MockEvent):
    """模拟 GraphQL 请求错误事件"""

    url: str = "https://api.example.com/graphql"
    operation_type: str = "mutation"
    operation_name: str = "CreateUser"
    error_type: str = "NetworkError"
    error_message: str = "Service unavailable"
    duration: float = 0.1


@dataclass
class MockDatabaseQueryStartEvent(MockEvent):
    """模拟数据库查询开始事件"""

    operation: str = "SELECT"
    table: str = "users"
    sql: str = "SELECT * FROM users WHERE id = ?"
    params: dict | None = None


@dataclass
class MockDatabaseQueryEndEvent(MockEvent):
    """模拟数据库查询结束事件"""

    operation: str = "SELECT"
    table: str = "users"
    row_count: int = 1
    duration_ms: float = 10.5


@dataclass
class MockDatabaseQueryErrorEvent(MockEvent):
    """模拟数据库查询错误事件"""

    operation: str = "INSERT"
    table: str = "users"
    error_type: str = "IntegrityError"
    error_message: str = "Duplicate key"
    duration_ms: float = 5.0


@dataclass
class MockCacheOperationStartEvent(MockEvent):
    """模拟缓存操作开始事件"""

    operation: str = "GET"
    key: str = "user:123"
    field: str | None = None


@dataclass
class MockCacheOperationEndEvent(MockEvent):
    """模拟缓存操作结束事件"""

    operation: str = "GET"
    key: str = "user:123"
    hit: bool = True
    duration_ms: float = 1.5


@dataclass
class MockCacheOperationErrorEvent(MockEvent):
    """模拟缓存操作错误事件"""

    operation: str = "SET"
    key: str = "user:123"
    error_type: str = "ConnectionError"
    error_message: str = "Redis connection refused"
    duration_ms: float = 100.0


@dataclass
class MockMessagePublishEndEvent(MockEvent):
    """模拟消息发布成功事件"""

    topic: str = "orders"
    messenger_type: str = "kafka"
    message_id: str = "msg-001"
    duration: float = 0.05
    partition: int | None = None
    offset: int | None = None


@dataclass
class MockMessagePublishErrorEvent(MockEvent):
    """模拟消息发布错误事件"""

    topic: str = "orders"
    messenger_type: str = "kafka"
    error_type: str = "KafkaError"
    error_message: str = "Broker not available"
    duration: float = 0.1


@dataclass
class MockMessageConsumeEndEvent(MockEvent):
    """模拟消息消费成功事件"""

    topic: str = "orders"
    messenger_type: str = "kafka"
    message_id: str = "msg-001"
    consumer_group: str = "test-group"
    processing_time: float = 0.02
    partition: int | None = None
    offset: int | None = None


@dataclass
class MockMessageConsumeErrorEvent(MockEvent):
    """模拟消息消费错误事件"""

    topic: str = "orders"
    messenger_type: str = "kafka"
    message_id: str = "msg-001"
    consumer_group: str = "test-group"
    error_type: str = "DeserializationError"
    error_message: str = "Invalid JSON"
    processing_time: float = 0.01


@dataclass
class MockStorageOperationStartEvent(MockEvent):
    """模拟存储操作开始事件"""

    storage_type: str = "s3"
    operation: str = "UPLOAD"
    path: str = "files/report.pdf"
    size: int = 1024


@dataclass
class MockStorageOperationEndEvent(MockEvent):
    """模拟存储操作结束事件"""

    storage_type: str = "s3"
    operation: str = "UPLOAD"
    path: str = "files/report.pdf"
    size: int = 1024
    duration_ms: float = 500.0


@dataclass
class MockStorageOperationErrorEvent(MockEvent):
    """模拟存储操作错误事件"""

    storage_type: str = "s3"
    operation: str = "DOWNLOAD"
    path: str = "files/missing.pdf"
    error_type: str = "NotFound"
    error_message: str = "Object not found"
    duration_ms: float = 50.0


@dataclass
class MockTransactionCommitEvent(MockEvent):
    """模拟事务提交事件"""

    repository_count: int = 2
    session_id: str = "sess-001"


@dataclass
class MockTransactionRollbackEvent(MockEvent):
    """模拟事务回滚事件"""

    repository_count: int = 2
    reason: str = "exception"
    session_id: str = "sess-001"


@dataclass
class MockUINavigationStartEvent(MockEvent):
    """模拟 UI 导航开始事件"""

    page_name: str = "LoginPage"
    url: str = "https://app.example.com/login"
    base_url: str = "https://app.example.com"


@dataclass
class MockUINavigationEndEvent(MockEvent):
    """模拟 UI 导航结束事件"""

    page_name: str = "LoginPage"
    url: str = "https://app.example.com/login"
    title: str = "Login - Example App"
    duration: float = 1.5
    success: bool = True


@dataclass
class MockUIClickEvent(MockEvent):
    """模拟 UI 点击事件"""

    page_name: str = "LoginPage"
    selector: str = "#login-button"
    element_text: str = "Sign In"
    duration: float = 0.1


@dataclass
class MockUIInputEvent(MockEvent):
    """模拟 UI 输入事件"""

    page_name: str = "LoginPage"
    selector: str = "#username"
    value: str = "testuser"
    masked: bool = False
    duration: float = 0.05


@dataclass
class MockUIScreenshotEvent(MockEvent):
    """模拟 UI 截图事件"""

    page_name: str = "LoginPage"
    path: str = ""
    full_page: bool = False
    size_bytes: int = 50000


@dataclass
class MockUIWaitEvent(MockEvent):
    """模拟 UI 等待事件"""

    page_name: str = "DashboardPage"
    wait_type: str = "visibility"
    condition: str = "#dashboard-loaded"
    duration: float = 2.0
    success: bool = True


@dataclass
class MockUIErrorEvent(MockEvent):
    """模拟 UI 错误事件"""

    page_name: str = "LoginPage"
    operation: str = "click"
    selector: str = "#missing-button"
    error_type: str = "ElementNotFound"
    error_message: str = "Element not found"
    screenshot_path: str = ""


# ========== 测试 ==========


@pytest.fixture
def mock_allure():
    """Mock allure 模块"""
    with patch.dict("sys.modules", {"allure": MagicMock(), "allure_commons": MagicMock()}):
        mock = MagicMock()
        mock.step = MagicMock(return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock()))
        mock.attach = MagicMock()
        mock.attachment_type = MagicMock()
        mock.attachment_type.JSON = "application/json"
        mock.attachment_type.PNG = "image/png"

        with patch("df_test_framework.testing.reporting.allure.observer.allure", mock):
            with patch(
                "df_test_framework.testing.reporting.allure.observer.ALLURE_AVAILABLE",
                True,
            ):
                yield mock


@pytest.fixture
def mock_allure_disabled():
    """Mock allure 模块（禁用）"""
    with patch("df_test_framework.testing.reporting.allure.observer.ALLURE_AVAILABLE", False):
        yield


@pytest.fixture
def observer(mock_allure):
    """创建 AllureObserver 实例"""
    from df_test_framework.testing.reporting.allure.observer import AllureObserver

    return AllureObserver(test_name="test_example")


@pytest.fixture
def observer_with_custom_config(mock_allure):
    """创建自定义配置的 AllureObserver 实例"""
    from df_test_framework.testing.reporting.allure.observer import AllureObserver

    return AllureObserver(
        test_name="test_custom",
        max_body_length=500,
        max_value_length=200,
        max_sql_length=1000,
    )


@pytest.mark.unit
class TestIsAllureEnabled:
    """测试 is_allure_enabled 函数"""

    def test_returns_false_when_allure_not_available(self, mock_allure_disabled):
        """Allure 不可用时返回 False"""
        from df_test_framework.testing.reporting.allure.observer import is_allure_enabled

        assert is_allure_enabled() is False

    def test_returns_true_when_allure_available(self, mock_allure):
        """Allure 可用时返回 True"""
        with patch("df_test_framework.infrastructure.config.get_settings") as mock_settings:
            mock_settings.return_value.enable_allure = True
            from df_test_framework.testing.reporting.allure.observer import (
                is_allure_enabled,
            )

            assert is_allure_enabled() is True

    def test_returns_true_when_settings_raises_exception(self, mock_allure):
        """获取设置异常时默认返回 True"""
        with patch(
            "df_test_framework.infrastructure.config.get_settings",
            side_effect=Exception("Config error"),
        ):
            from df_test_framework.testing.reporting.allure.observer import (
                is_allure_enabled,
            )

            assert is_allure_enabled() is True


@pytest.mark.unit
class TestStepContext:
    """测试 StepContext 类"""

    def test_step_context_creation(self, mock_allure):
        """测试创建 StepContext"""
        from df_test_framework.testing.reporting.allure.observer import StepContext

        ctx = StepContext()

        assert ctx.exit_stack is not None
        assert ctx.start_time is not None
        assert ctx.step_context is None

    def test_step_context_as_context_manager(self, mock_allure):
        """测试 StepContext 作为上下文管理器"""
        from df_test_framework.testing.reporting.allure.observer import StepContext

        with StepContext() as ctx:
            assert ctx is not None
            assert ctx.exit_stack is not None


@pytest.mark.unit
class TestAllureObserverInit:
    """测试 AllureObserver 初始化"""

    def test_default_init(self, observer):
        """测试默认初始化"""
        assert observer.test_name == "test_example"
        assert observer.request_counter == 0
        assert observer.query_counter == 0
        assert observer.graphql_counter == 0
        assert observer.grpc_counter == 0
        assert observer.ui_counter == 0

    def test_default_truncate_lengths(self, observer):
        """测试默认截断长度"""
        assert observer.max_body_length == 1000
        assert observer.max_value_length == 500
        assert observer.max_sql_length == 2000

    def test_custom_truncate_lengths(self, observer_with_custom_config):
        """测试自定义截断长度"""
        assert observer_with_custom_config.max_body_length == 500
        assert observer_with_custom_config.max_value_length == 200
        assert observer_with_custom_config.max_sql_length == 1000

    def test_contexts_initialized_empty(self, observer):
        """测试上下文初始化为空"""
        assert len(observer._http_contexts) == 0
        assert len(observer._query_contexts) == 0
        assert len(observer._graphql_contexts) == 0
        assert len(observer._grpc_contexts) == 0
        assert len(observer._event_correlations) == 0


@pytest.mark.unit
class TestAllureObserverTruncate:
    """测试截断方法"""

    def test_truncate_none_value(self, observer):
        """测试截断 None 值"""
        result = observer._truncate(None, 100)
        assert result is None

    def test_truncate_short_string(self, observer):
        """测试截断短字符串（不需要截断）"""
        short_str = "Hello World"
        result = observer._truncate(short_str, 100)
        assert result == short_str

    def test_truncate_long_string(self, observer):
        """测试截断长字符串"""
        long_str = "A" * 200
        result = observer._truncate(long_str, 100)
        assert result.startswith("A" * 100)
        assert "truncated" in result
        assert "200 chars" in result

    def test_truncate_exact_length(self, observer):
        """测试刚好达到长度限制"""
        exact_str = "A" * 100
        result = observer._truncate(exact_str, 100)
        assert result == exact_str


@pytest.mark.unit
class TestAllureObserverHttpMethods:
    """测试 HTTP 相关方法"""

    def test_on_http_request_start(self, observer, mock_allure):
        """测试 HTTP 请求开始"""
        request = MockRequest(
            method="POST",
            url="https://api.example.com/users",
            headers={"Content-Type": "application/json"},
            json={"name": "Alice"},
        )

        request_id = observer.on_http_request_start(request)

        assert request_id == "req-001"
        assert observer.request_counter == 1
        assert request_id in observer._http_contexts
        mock_allure.attach.assert_called()

    def test_on_http_request_start_disabled(self, mock_allure_disabled):
        """测试 Allure 禁用时 HTTP 请求开始"""
        from df_test_framework.testing.reporting.allure.observer import AllureObserver

        observer = AllureObserver(test_name="test")
        request = MockRequest()

        request_id = observer.on_http_request_start(request)

        assert request_id is None

    def test_on_http_request_end(self, observer, mock_allure):
        """测试 HTTP 请求结束"""
        request = MockRequest()
        request_id = observer.on_http_request_start(request)

        response = MockResponse(status_code=200, body='{"id": 1}')
        observer.on_http_request_end(request_id, response, duration_ms=100)

        assert request_id not in observer._http_contexts

    def test_on_http_request_end_without_context(self, observer, mock_allure):
        """测试没有上下文时的请求结束"""
        response = MockResponse()
        # 不应该抛出异常
        observer.on_http_request_end("invalid-id", response)

    def test_on_interceptor_execute(self, observer, mock_allure):
        """测试拦截器执行记录"""
        observer.on_interceptor_execute(
            request_id="req-001",
            interceptor_name="SignatureMiddleware",
            changes={"headers": {"X-Signature": "abc123"}},
        )

        mock_allure.step.assert_called()

    def test_on_interceptor_execute_empty_changes(self, observer, mock_allure):
        """测试拦截器执行空变化"""
        mock_allure.step.reset_mock()
        observer.on_interceptor_execute(
            request_id="req-001", interceptor_name="SomeMiddleware", changes={}
        )

        # 空变化不应该创建 step
        mock_allure.step.assert_not_called()

    def test_on_error(self, observer, mock_allure):
        """测试错误记录"""
        # 先创建一个请求上下文
        request = MockRequest()
        request_id = observer.on_http_request_start(request)

        error = ValueError("Something went wrong")
        observer.on_error(error, {"stage": "request", "request_id": request_id})

        mock_allure.attach.assert_called()
        assert request_id not in observer._http_contexts


@pytest.mark.unit
class TestAllureObserverHttpEventHandlers:
    """测试 HTTP EventBus 事件处理器"""

    @pytest.mark.asyncio
    async def test_handle_http_request_start_event(self, observer, mock_allure):
        """测试处理 HTTP 请求开始事件"""
        event = MockHttpRequestStartEvent(
            headers={"Content-Type": "application/json"},
            params={"page": "1"},
            trace_id="trace-123",
            span_id="span-456",
        )

        await observer.handle_http_request_start_event(event)

        assert observer.request_counter == 1
        assert event.correlation_id in observer._event_correlations
        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_http_request_end_event(self, observer, mock_allure):
        """测试处理 HTTP 请求结束事件"""
        # 先模拟开始事件
        start_event = MockHttpRequestStartEvent()
        await observer.handle_http_request_start_event(start_event)

        end_event = MockHttpRequestEndEvent(
            correlation_id=start_event.correlation_id,
            trace_id="trace-123",
        )

        await observer.handle_http_request_end_event(end_event)

        assert end_event.correlation_id not in observer._event_correlations
        assert mock_allure.attach.call_count >= 2

    @pytest.mark.asyncio
    async def test_handle_http_request_error_event(self, observer, mock_allure):
        """测试处理 HTTP 请求错误事件"""
        event = MockHttpRequestErrorEvent(trace_id="trace-123", span_id="span-456")

        await observer.handle_http_request_error_event(event)

        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_middleware_execute_event(self, observer, mock_allure):
        """测试处理中间件执行事件"""
        event = MockMiddlewareExecuteEvent(changes={"headers": {"X-Signature": "sig123"}})

        await observer.handle_middleware_execute_event(event)

        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_middleware_execute_event_empty_changes(self, observer, mock_allure):
        """测试处理空变化的中间件执行事件"""
        mock_allure.attach.reset_mock()
        event = MockMiddlewareExecuteEvent(changes={})

        await observer.handle_middleware_execute_event(event)

        # 空变化不应该记录
        mock_allure.attach.assert_not_called()


@pytest.mark.unit
class TestAllureObserverGraphQLMethods:
    """测试 GraphQL 相关方法"""

    def test_on_graphql_request_start(self, observer, mock_allure):
        """测试 GraphQL 请求开始"""
        graphql_id = observer.on_graphql_request_start(
            operation_name="GetUsers",
            operation_type="query",
            query="query GetUsers { users { id name } }",
            variables={"page": 1},
        )

        assert graphql_id == "gql-001"
        assert observer.graphql_counter == 1
        assert graphql_id in observer._graphql_contexts

    def test_on_graphql_request_start_anonymous(self, observer, mock_allure):
        """测试匿名 GraphQL 请求"""
        graphql_id = observer.on_graphql_request_start(
            operation_name=None,
            operation_type="query",
            query="{ users { id } }",
        )

        assert graphql_id is not None

    def test_on_graphql_request_end_with_data(self, observer, mock_allure):
        """测试 GraphQL 请求成功结束"""
        graphql_id = observer.on_graphql_request_start(
            operation_name="GetUsers",
            operation_type="query",
            query="query GetUsers { users { id } }",
        )

        observer.on_graphql_request_end(
            graphql_id=graphql_id,
            data={"users": [{"id": 1}]},
            errors=None,
            duration_ms=50,
        )

        assert graphql_id not in observer._graphql_contexts

    def test_on_graphql_request_end_with_errors(self, observer, mock_allure):
        """测试 GraphQL 请求错误结束"""
        graphql_id = observer.on_graphql_request_start(
            operation_name="GetUsers",
            operation_type="query",
            query="query GetUsers { users { id } }",
        )

        observer.on_graphql_request_end(
            graphql_id=graphql_id,
            data=None,
            errors=[{"message": "Not found"}],
            duration_ms=30,
        )

        assert graphql_id not in observer._graphql_contexts


@pytest.mark.unit
class TestAllureObserverGraphQLEventHandlers:
    """测试 GraphQL EventBus 事件处理器"""

    @pytest.mark.asyncio
    async def test_handle_graphql_request_start_event(self, observer, mock_allure):
        """测试处理 GraphQL 请求开始事件"""
        event = MockGraphQLRequestStartEvent(trace_id="trace-123")

        await observer.handle_graphql_request_start_event(event)

        assert observer.graphql_counter == 1
        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_graphql_request_end_event(self, observer, mock_allure):
        """测试处理 GraphQL 请求结束事件"""
        event = MockGraphQLRequestEndEvent(data='{"users": []}')

        await observer.handle_graphql_request_end_event(event)

        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_graphql_request_error_event(self, observer, mock_allure):
        """测试处理 GraphQL 请求错误事件"""
        event = MockGraphQLRequestErrorEvent()

        await observer.handle_graphql_request_error_event(event)

        mock_allure.attach.assert_called()


@pytest.mark.unit
class TestAllureObserverGrpcMethods:
    """测试 gRPC 相关方法"""

    def test_on_grpc_call_start(self, observer, mock_allure):
        """测试 gRPC 调用开始"""
        grpc_id = observer.on_grpc_call_start(
            service="UserService",
            method="GetUser",
            request_type="unary",
            metadata={"authorization": "Bearer token"},
        )

        assert grpc_id == "grpc-001"
        assert observer.grpc_counter == 1
        assert grpc_id in observer._grpc_contexts

    def test_on_grpc_call_end_ok(self, observer, mock_allure):
        """测试 gRPC 调用成功结束"""
        grpc_id = observer.on_grpc_call_start(
            service="UserService", method="GetUser", request_type="unary"
        )

        observer.on_grpc_call_end(
            grpc_id=grpc_id,
            status_code="OK",
            status_message=None,
            duration_ms=20,
        )

        assert grpc_id not in observer._grpc_contexts

    def test_on_grpc_call_end_error(self, observer, mock_allure):
        """测试 gRPC 调用失败结束"""
        grpc_id = observer.on_grpc_call_start(
            service="UserService", method="GetUser", request_type="unary"
        )

        observer.on_grpc_call_end(
            grpc_id=grpc_id,
            status_code="NOT_FOUND",
            status_message="User not found",
            duration_ms=15,
        )

        assert grpc_id not in observer._grpc_contexts


@pytest.mark.unit
class TestAllureObserverDatabaseEventHandlers:
    """测试数据库 EventBus 事件处理器"""

    def test_handle_database_query_start_event(self, observer, mock_allure):
        """测试处理数据库查询开始事件"""
        event = MockDatabaseQueryStartEvent(
            params={"id": 1}, trace_id="trace-123", span_id="span-456"
        )

        observer.handle_database_query_start_event(event)

        assert event.correlation_id in observer._query_contexts
        mock_allure.attach.assert_called()

    def test_handle_database_query_end_event(self, observer, mock_allure):
        """测试处理数据库查询结束事件"""
        # 先创建开始事件
        start_event = MockDatabaseQueryStartEvent()
        observer.handle_database_query_start_event(start_event)

        end_event = MockDatabaseQueryEndEvent(correlation_id=start_event.correlation_id)
        observer.handle_database_query_end_event(end_event)

        assert end_event.correlation_id not in observer._query_contexts

    def test_handle_database_query_error_event(self, observer, mock_allure):
        """测试处理数据库查询错误事件"""
        # 先创建开始事件
        start_event = MockDatabaseQueryStartEvent()
        observer.handle_database_query_start_event(start_event)

        error_event = MockDatabaseQueryErrorEvent(correlation_id=start_event.correlation_id)
        observer.handle_database_query_error_event(error_event)

        assert error_event.correlation_id not in observer._query_contexts


@pytest.mark.unit
class TestAllureObserverCacheEventHandlers:
    """测试缓存 EventBus 事件处理器"""

    @pytest.mark.asyncio
    async def test_handle_cache_operation_start_event(self, observer, mock_allure):
        """测试处理缓存操作开始事件"""
        event = MockCacheOperationStartEvent(field="name", trace_id="trace-123", span_id="span-456")

        await observer.handle_cache_operation_start_event(event)

        assert event.correlation_id in observer._event_correlations
        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_cache_operation_end_event_hit(self, observer, mock_allure):
        """测试处理缓存命中事件"""
        event = MockCacheOperationEndEvent(hit=True)

        await observer.handle_cache_operation_end_event(event)

        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_cache_operation_end_event_miss(self, observer, mock_allure):
        """测试处理缓存未命中事件"""
        event = MockCacheOperationEndEvent(hit=False)

        await observer.handle_cache_operation_end_event(event)

        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_cache_operation_error_event(self, observer, mock_allure):
        """测试处理缓存操作错误事件"""
        event = MockCacheOperationErrorEvent()

        await observer.handle_cache_operation_error_event(event)

        mock_allure.attach.assert_called()


@pytest.mark.unit
class TestAllureObserverMessageMethods:
    """测试消息队列方法"""

    def test_on_message_publish(self, observer, mock_allure):
        """测试消息发布记录"""
        observer.on_message_publish(
            queue_type="kafka",
            topic="orders",
            message={"order_id": "ORD-001"},
            key="ORD-001",
            partition=0,
            headers={"trace_id": "trace-123"},
            message_id="msg-001",
            duration_ms=10,
        )

        mock_allure.step.assert_called()
        mock_allure.attach.assert_called()

    def test_on_message_publish_bytes(self, observer, mock_allure):
        """测试消息发布（字节类型）"""
        observer.on_message_publish(
            queue_type="kafka",
            topic="orders",
            message=b'{"order_id": "ORD-001"}',
        )

        mock_allure.step.assert_called()

    def test_on_message_publish_binary(self, observer, mock_allure):
        """测试消息发布（二进制类型）"""
        observer.on_message_publish(
            queue_type="kafka",
            topic="orders",
            message=b"\x00\x01\x02\x03",  # 非 UTF-8 二进制
        )

        mock_allure.step.assert_called()

    def test_on_message_consume(self, observer, mock_allure):
        """测试消息消费记录"""
        observer.on_message_consume(
            queue_type="kafka",
            topic="orders",
            message={"order_id": "ORD-001"},
            consumer_group="test-group",
            partition=0,
            offset=100,
            message_id="msg-001",
            processing_time_ms=5,
        )

        mock_allure.step.assert_called()
        mock_allure.attach.assert_called()


@pytest.mark.unit
class TestAllureObserverMessageEventHandlers:
    """测试消息队列 EventBus 事件处理器"""

    @pytest.mark.asyncio
    async def test_handle_message_publish_end_event(self, observer, mock_allure):
        """测试处理消息发布成功事件"""
        event = MockMessagePublishEndEvent(
            partition=0, offset=100, trace_id="trace-123", span_id="span-456"
        )

        await observer.handle_message_publish_end_event(event)

        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_message_publish_error_event(self, observer, mock_allure):
        """测试处理消息发布错误事件"""
        event = MockMessagePublishErrorEvent()

        await observer.handle_message_publish_error_event(event)

        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_message_consume_end_event(self, observer, mock_allure):
        """测试处理消息消费成功事件"""
        event = MockMessageConsumeEndEvent(
            partition=0, offset=100, trace_id="trace-123", span_id="span-456"
        )

        await observer.handle_message_consume_end_event(event)

        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_message_consume_error_event(self, observer, mock_allure):
        """测试处理消息消费错误事件"""
        event = MockMessageConsumeErrorEvent()

        await observer.handle_message_consume_error_event(event)

        mock_allure.attach.assert_called()


@pytest.mark.unit
class TestAllureObserverStorageMethods:
    """测试存储操作方法"""

    def test_on_storage_operation_upload(self, observer, mock_allure):
        """测试存储上传操作记录"""
        observer.on_storage_operation(
            storage_type="s3",
            operation="upload",
            path="files/report.pdf",
            size=1024 * 1024,  # 1MB
            duration_ms=500,
            success=True,
        )

        mock_allure.step.assert_called()
        mock_allure.attach.assert_called()

    def test_on_storage_operation_download(self, observer, mock_allure):
        """测试存储下载操作记录"""
        observer.on_storage_operation(
            storage_type="oss",
            operation="download",
            path="files/data.json",
            size=512,  # bytes
            duration_ms=100,
            success=True,
        )

        mock_allure.step.assert_called()

    def test_on_storage_operation_error(self, observer, mock_allure):
        """测试存储操作失败记录"""
        observer.on_storage_operation(
            storage_type="s3",
            operation="delete",
            path="files/missing.txt",
            success=False,
            error="Object not found",
        )

        mock_allure.step.assert_called()


@pytest.mark.unit
class TestAllureObserverStorageEventHandlers:
    """测试存储操作 EventBus 事件处理器"""

    @pytest.mark.asyncio
    async def test_handle_storage_operation_start_event(self, observer, mock_allure):
        """测试处理存储操作开始事件"""
        event = MockStorageOperationStartEvent(trace_id="trace-123", span_id="span-456")

        await observer.handle_storage_operation_start_event(event)

        assert event.correlation_id in observer._event_correlations
        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_storage_operation_end_event(self, observer, mock_allure):
        """测试处理存储操作结束事件"""
        event = MockStorageOperationEndEvent(trace_id="trace-123")

        await observer.handle_storage_operation_end_event(event)

        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_storage_operation_error_event(self, observer, mock_allure):
        """测试处理存储操作错误事件"""
        event = MockStorageOperationErrorEvent()

        await observer.handle_storage_operation_error_event(event)

        mock_allure.attach.assert_called()


@pytest.mark.unit
class TestAllureObserverTransactionEventHandlers:
    """测试事务 EventBus 事件处理器"""

    def test_handle_transaction_commit_event(self, observer, mock_allure):
        """测试处理事务提交事件"""
        event = MockTransactionCommitEvent(trace_id="trace-123", span_id="span-456")

        observer.handle_transaction_commit_event(event)

        mock_allure.attach.assert_called()

    def test_handle_transaction_rollback_event_exception(self, observer, mock_allure):
        """测试处理异常回滚事件"""
        event = MockTransactionRollbackEvent(reason="exception")

        observer.handle_transaction_rollback_event(event)

        mock_allure.attach.assert_called()

    def test_handle_transaction_rollback_event_auto(self, observer, mock_allure):
        """测试处理自动回滚事件"""
        event = MockTransactionRollbackEvent(reason="auto")

        observer.handle_transaction_rollback_event(event)

        mock_allure.attach.assert_called()

    def test_handle_transaction_rollback_event_manual(self, observer, mock_allure):
        """测试处理手动回滚事件"""
        event = MockTransactionRollbackEvent(reason="manual")

        observer.handle_transaction_rollback_event(event)

        mock_allure.attach.assert_called()


@pytest.mark.unit
class TestAllureObserverUIEventHandlers:
    """测试 UI EventBus 事件处理器"""

    @pytest.mark.asyncio
    async def test_handle_ui_navigation_start_event(self, observer, mock_allure):
        """测试处理 UI 导航开始事件"""
        event = MockUINavigationStartEvent(trace_id="trace-123", span_id="span-456")

        await observer.handle_ui_navigation_start_event(event)

        assert observer.ui_counter == 1
        assert event.correlation_id in observer._event_correlations
        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_ui_navigation_end_event(self, observer, mock_allure):
        """测试处理 UI 导航结束事件"""
        event = MockUINavigationEndEvent()

        await observer.handle_ui_navigation_end_event(event)

        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_ui_navigation_end_event_failed(self, observer, mock_allure):
        """测试处理 UI 导航失败事件"""
        event = MockUINavigationEndEvent(success=False)

        await observer.handle_ui_navigation_end_event(event)

        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_ui_click_event(self, observer, mock_allure):
        """测试处理 UI 点击事件"""
        event = MockUIClickEvent()

        await observer.handle_ui_click_event(event)

        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_ui_input_event(self, observer, mock_allure):
        """测试处理 UI 输入事件"""
        event = MockUIInputEvent()

        await observer.handle_ui_input_event(event)

        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_ui_input_event_masked(self, observer, mock_allure):
        """测试处理 UI 输入事件（密码掩码）"""
        event = MockUIInputEvent(masked=True, value="secret_password")

        await observer.handle_ui_input_event(event)

        # 检查 attach 调用参数中的值是否被掩码
        call_args = mock_allure.attach.call_args
        if call_args:
            json_str = call_args[0][0]
            data = json.loads(json_str)
            assert data["value"] == "***"

    @pytest.mark.asyncio
    async def test_handle_ui_screenshot_event(self, observer, mock_allure):
        """测试处理 UI 截图事件"""
        event = MockUIScreenshotEvent()

        await observer.handle_ui_screenshot_event(event)

        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_ui_wait_event(self, observer, mock_allure):
        """测试处理 UI 等待事件"""
        event = MockUIWaitEvent()

        await observer.handle_ui_wait_event(event)

        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_ui_wait_event_timeout(self, observer, mock_allure):
        """测试处理 UI 等待超时事件"""
        event = MockUIWaitEvent(success=False)

        await observer.handle_ui_wait_event(event)

        mock_allure.attach.assert_called()

    @pytest.mark.asyncio
    async def test_handle_ui_error_event(self, observer, mock_allure):
        """测试处理 UI 错误事件"""
        event = MockUIErrorEvent(trace_id="trace-123", span_id="span-456")

        await observer.handle_ui_error_event(event)

        mock_allure.attach.assert_called()


@pytest.mark.unit
class TestAllureObserverCleanup:
    """测试清理机制"""

    def test_cleanup_clears_http_contexts(self, observer, mock_allure):
        """测试清理 HTTP 上下文"""
        # 创建一个未关闭的请求
        request = MockRequest()
        observer.on_http_request_start(request)

        assert len(observer._http_contexts) == 1

        observer.cleanup()

        assert len(observer._http_contexts) == 0

    def test_cleanup_clears_all_contexts(self, observer, mock_allure):
        """测试清理所有上下文"""
        # 创建各种未关闭的上下文
        request = MockRequest()
        observer.on_http_request_start(request)
        observer.on_graphql_request_start("GetUsers", "query", "{ users }")
        observer.on_grpc_call_start("UserService", "GetUser", "unary")

        observer.cleanup()

        assert len(observer._http_contexts) == 0
        assert len(observer._graphql_contexts) == 0
        assert len(observer._grpc_contexts) == 0
        assert len(observer._query_contexts) == 0


@pytest.mark.unit
class TestGetSetCurrentObserver:
    """测试 get/set 当前 observer 函数"""

    def test_get_current_observer_default(self, mock_allure):
        """测试默认返回 None"""
        from df_test_framework.testing.reporting.allure.observer import (
            get_current_observer,
            set_current_observer,
        )

        # 重置为 None
        set_current_observer(None)
        result = get_current_observer()
        assert result is None

    def test_set_and_get_current_observer(self, observer, mock_allure):
        """测试设置和获取当前 observer"""
        from df_test_framework.testing.reporting.allure.observer import (
            get_current_observer,
            set_current_observer,
        )

        set_current_observer(observer)
        result = get_current_observer()

        assert result is observer

        # 清理
        set_current_observer(None)

    def test_set_current_observer_to_none(self, observer, mock_allure):
        """测试设置 observer 为 None"""
        from df_test_framework.testing.reporting.allure.observer import (
            get_current_observer,
            set_current_observer,
        )

        set_current_observer(observer)
        set_current_observer(None)
        result = get_current_observer()

        assert result is None
