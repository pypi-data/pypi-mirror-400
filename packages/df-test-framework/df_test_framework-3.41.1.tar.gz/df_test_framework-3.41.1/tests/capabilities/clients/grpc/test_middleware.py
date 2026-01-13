"""测试 gRPC 中间件

v3.32.0: 从拦截器模式重构为中间件模式
"""

import pytest

from df_test_framework.capabilities.clients.grpc.middleware import (
    GrpcEventPublisherMiddleware,
    GrpcLoggingMiddleware,
    GrpcMetadataMiddleware,
    GrpcMiddleware,
    GrpcRetryMiddleware,
    GrpcTimingMiddleware,
)
from df_test_framework.capabilities.clients.grpc.models import (
    GrpcRequest,
    GrpcResponse,
    GrpcStatusCode,
)
from df_test_framework.core.events import (
    GrpcRequestEndEvent,
    GrpcRequestErrorEvent,
    GrpcRequestStartEvent,
)
from df_test_framework.infrastructure.events import EventBus


class TestGrpcMiddleware:
    """测试 GrpcMiddleware 基类"""

    def test_middleware_default_priority(self) -> None:
        """测试默认优先级"""
        middleware = GrpcMiddleware()
        assert middleware.priority == 100

    def test_middleware_custom_priority(self) -> None:
        """测试自定义优先级"""
        middleware = GrpcMiddleware(priority=50)
        assert middleware.priority == 50

    def test_middleware_name(self) -> None:
        """测试中间件名称"""
        middleware = GrpcMiddleware(name="TestMiddleware")
        assert middleware.name == "TestMiddleware"


class TestGrpcLoggingMiddleware:
    """测试 GrpcLoggingMiddleware"""

    def test_default_config(self) -> None:
        """测试默认配置"""
        middleware = GrpcLoggingMiddleware()
        assert middleware.log_request is True
        assert middleware.log_response is True

    def test_custom_config(self) -> None:
        """测试自定义配置"""
        middleware = GrpcLoggingMiddleware(log_request=False, log_response=True)
        assert middleware.log_request is False
        assert middleware.log_response is True


class TestGrpcMetadataMiddleware:
    """测试 GrpcMetadataMiddleware"""

    def test_add_metadata(self) -> None:
        """测试添加元数据"""
        middleware = GrpcMetadataMiddleware()
        middleware.add_metadata("Authorization", "Bearer token123")

        assert "Authorization" in middleware.metadata
        assert middleware.metadata["Authorization"] == "Bearer token123"

    def test_remove_metadata(self) -> None:
        """测试移除元数据"""
        middleware = GrpcMetadataMiddleware({"key": "value"})
        middleware.remove_metadata("key")

        assert "key" not in middleware.metadata

    def test_clear_metadata(self) -> None:
        """测试清除元数据"""
        middleware = GrpcMetadataMiddleware({"key1": "value1", "key2": "value2"})
        middleware.clear_metadata()

        assert len(middleware.metadata) == 0

    @pytest.mark.asyncio
    async def test_middleware_adds_metadata(self) -> None:
        """测试中间件添加元数据到请求"""
        middleware = GrpcMetadataMiddleware(
            {
                "Authorization": "Bearer token",
                "X-Request-ID": "123",
            }
        )

        request = GrpcRequest(
            method="TestMethod",
            message={},
            metadata=[("Content-Type", "application/grpc")],
        )

        # Mock call_next
        async def mock_call_next(req: GrpcRequest) -> GrpcResponse:
            # 验证元数据已合并
            assert len(req.metadata) == 3
            assert ("Content-Type", "application/grpc") in req.metadata
            assert ("Authorization", "Bearer token") in req.metadata
            assert ("X-Request-ID", "123") in req.metadata
            return GrpcResponse(data=None, status_code=GrpcStatusCode.OK)

        await middleware(request, mock_call_next)


class TestGrpcRetryMiddleware:
    """测试 GrpcRetryMiddleware"""

    def test_default_retry_configuration(self) -> None:
        """测试默认重试配置"""
        middleware = GrpcRetryMiddleware()

        assert middleware.max_retries == 3
        assert middleware.retry_on_codes == [14]  # UNAVAILABLE
        assert middleware.backoff_multiplier == 2.0
        assert middleware.initial_backoff == 0.1

    def test_custom_retry_configuration(self) -> None:
        """测试自定义重试配置"""
        middleware = GrpcRetryMiddleware(
            max_retries=5,
            retry_on_codes=[14, 13],  # UNAVAILABLE, INTERNAL
            backoff_multiplier=1.5,
            initial_backoff=0.5,
        )

        assert middleware.max_retries == 5
        assert middleware.retry_on_codes == [14, 13]
        assert middleware.backoff_multiplier == 1.5
        assert middleware.initial_backoff == 0.5

    def test_should_retry(self) -> None:
        """测试是否应该重试"""
        middleware = GrpcRetryMiddleware(retry_on_codes=[14, 13])

        assert middleware.should_retry(14) is True
        assert middleware.should_retry(13) is True
        assert middleware.should_retry(5) is False  # NOT_FOUND

    def test_calculate_backoff(self) -> None:
        """测试计算退避时间"""
        middleware = GrpcRetryMiddleware(
            initial_backoff=1.0,
            backoff_multiplier=2.0,
        )

        assert middleware.calculate_backoff(0) == 1.0  # 1.0 * 2^0
        assert middleware.calculate_backoff(1) == 2.0  # 1.0 * 2^1
        assert middleware.calculate_backoff(2) == 4.0  # 1.0 * 2^2
        assert middleware.calculate_backoff(3) == 8.0  # 1.0 * 2^3


class TestGrpcTimingMiddleware:
    """测试 GrpcTimingMiddleware"""

    def test_get_average_timing_nonexistent_method(self) -> None:
        """测试获取不存在方法的耗时"""
        middleware = GrpcTimingMiddleware()

        average = middleware.get_average_timing("NonExistentMethod")
        assert average is None

    def test_get_average_timing(self) -> None:
        """测试获取平均耗时"""
        middleware = GrpcTimingMiddleware()

        # 手动添加一些耗时记录
        middleware.timings["TestMethod"] = [0.1, 0.2, 0.3]

        average = middleware.get_average_timing("TestMethod")
        assert average == pytest.approx(0.2)

    def test_get_all_timings(self) -> None:
        """测试获取所有耗时统计"""
        middleware = GrpcTimingMiddleware()

        # 手动添加耗时记录
        middleware.timings["Method1"] = [0.1, 0.2, 0.3]
        middleware.timings["Method2"] = [0.5, 0.6]

        all_timings = middleware.get_all_timings()

        assert "Method1" in all_timings
        assert "Method2" in all_timings

        assert all_timings["Method1"]["count"] == 3
        assert all_timings["Method1"]["average"] == pytest.approx(0.2)
        assert all_timings["Method1"]["min"] == pytest.approx(0.1)
        assert all_timings["Method1"]["max"] == pytest.approx(0.3)
        assert all_timings["Method1"]["total"] == pytest.approx(0.6)

        assert all_timings["Method2"]["count"] == 2
        assert all_timings["Method2"]["average"] == pytest.approx(0.55)

    def test_clear_timings(self) -> None:
        """测试清除耗时记录"""
        middleware = GrpcTimingMiddleware()
        middleware.timings["Method1"] = [0.1, 0.2]

        middleware.clear_timings()

        assert len(middleware.timings) == 0


class TestGrpcEventPublisherMiddleware:
    """测试 GrpcEventPublisherMiddleware (v3.32.0 新增)"""

    @pytest.mark.asyncio
    async def test_publishes_start_event(self) -> None:
        """测试发布开始事件"""
        event_bus = EventBus()
        middleware = GrpcEventPublisherMiddleware(
            event_bus=event_bus,
            service_name="TestService",
        )

        events: list = []
        event_bus.subscribe(GrpcRequestStartEvent, lambda e: events.append(e))

        request = GrpcRequest(
            method="TestMethod",
            message={"name": "test"},
            metadata=[("key", "value")],
        )

        async def mock_call_next(req: GrpcRequest) -> GrpcResponse:
            return GrpcResponse(data={"result": "ok"}, status_code=GrpcStatusCode.OK)

        await middleware(request, mock_call_next)

        assert len(events) == 1
        assert events[0].service == "TestService"
        assert events[0].method == "TestMethod"

    @pytest.mark.asyncio
    async def test_publishes_end_event(self) -> None:
        """测试发布结束事件"""
        event_bus = EventBus()
        middleware = GrpcEventPublisherMiddleware(
            event_bus=event_bus,
            service_name="TestService",
        )

        start_events: list = []
        end_events: list = []
        event_bus.subscribe(GrpcRequestStartEvent, lambda e: start_events.append(e))
        event_bus.subscribe(GrpcRequestEndEvent, lambda e: end_events.append(e))

        request = GrpcRequest(
            method="TestMethod",
            message={"name": "test"},
        )

        async def mock_call_next(req: GrpcRequest) -> GrpcResponse:
            return GrpcResponse(data={"result": "success"}, status_code=GrpcStatusCode.OK)

        await middleware(request, mock_call_next)

        assert len(start_events) == 1
        assert len(end_events) == 1
        assert end_events[0].service == "TestService"
        assert end_events[0].method == "TestMethod"
        assert end_events[0].status_code == 0
        # 验证 correlation_id 一致
        assert end_events[0].correlation_id == start_events[0].correlation_id

    @pytest.mark.asyncio
    async def test_publishes_error_event(self) -> None:
        """测试发布错误事件"""
        event_bus = EventBus()
        middleware = GrpcEventPublisherMiddleware(
            event_bus=event_bus,
            service_name="TestService",
        )

        start_events: list = []
        error_events: list = []
        event_bus.subscribe(GrpcRequestStartEvent, lambda e: start_events.append(e))
        event_bus.subscribe(GrpcRequestErrorEvent, lambda e: error_events.append(e))

        request = GrpcRequest(
            method="TestMethod",
            message={"name": "test"},
        )

        async def mock_call_next(req: GrpcRequest) -> GrpcResponse:
            raise RuntimeError("Connection failed")

        with pytest.raises(RuntimeError, match="Connection failed"):
            await middleware(request, mock_call_next)

        assert len(start_events) == 1
        assert len(error_events) == 1
        assert error_events[0].service == "TestService"
        assert error_events[0].method == "TestMethod"
        assert error_events[0].error_type == "RuntimeError"
        assert "Connection failed" in error_events[0].error_message
        # 验证 correlation_id 一致
        assert error_events[0].correlation_id == start_events[0].correlation_id

    @pytest.mark.asyncio
    async def test_disabled_middleware_does_not_publish(self) -> None:
        """测试禁用的中间件不发布事件"""
        event_bus = EventBus()
        middleware = GrpcEventPublisherMiddleware(
            event_bus=event_bus,
            service_name="TestService",
            enabled=False,
        )

        events: list = []
        event_bus.subscribe(GrpcRequestStartEvent, lambda e: events.append(e))

        request = GrpcRequest(
            method="TestMethod",
            message={"name": "test"},
        )

        async def mock_call_next(req: GrpcRequest) -> GrpcResponse:
            return GrpcResponse(data=None, status_code=GrpcStatusCode.OK)

        await middleware(request, mock_call_next)

        assert len(events) == 0

    def test_serialize_data_with_string(self) -> None:
        """测试数据序列化 - 字符串"""
        event_bus = EventBus()
        middleware = GrpcEventPublisherMiddleware(
            event_bus=event_bus,
            service_name="TestService",
            log_request_data=True,
        )

        result = middleware._serialize_data("test string")
        assert result == "test string"

    def test_serialize_data_truncation(self) -> None:
        """测试数据序列化 - 截断"""
        event_bus = EventBus()
        middleware = GrpcEventPublisherMiddleware(
            event_bus=event_bus,
            service_name="TestService",
            max_data_length=10,
        )

        result = middleware._serialize_data("this is a very long string")
        assert "truncated" in result
        assert len(result.replace("... (truncated)", "")) <= 10

    def test_serialize_data_none(self) -> None:
        """测试数据序列化 - None"""
        event_bus = EventBus()
        middleware = GrpcEventPublisherMiddleware(event_bus=event_bus)

        result = middleware._serialize_data(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_adds_correlation_id_to_metadata(self) -> None:
        """测试中间件添加 correlation_id 到元数据"""
        event_bus = EventBus()
        middleware = GrpcEventPublisherMiddleware(
            event_bus=event_bus,
            service_name="TestService",
        )

        request = GrpcRequest(
            method="TestMethod",
            message={},
        )

        captured_request: GrpcRequest | None = None

        async def mock_call_next(req: GrpcRequest) -> GrpcResponse:
            nonlocal captured_request
            captured_request = req
            return GrpcResponse(data=None, status_code=GrpcStatusCode.OK)

        await middleware(request, mock_call_next)

        # 验证添加了 correlation_id
        assert captured_request is not None
        correlation_id = captured_request.get_metadata("x-correlation-id")
        assert correlation_id is not None
        assert correlation_id.startswith("cor-")
