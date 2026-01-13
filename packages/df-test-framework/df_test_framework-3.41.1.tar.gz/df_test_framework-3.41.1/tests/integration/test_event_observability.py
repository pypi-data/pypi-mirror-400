"""事件系统 + 可观测性集成测试

测试 EventBus、事件类型与观察者的协同工作。
"""

import pytest

from df_test_framework.core.events import (
    Event,
    HttpRequestEndEvent,
    HttpRequestErrorEvent,
    HttpRequestStartEvent,
)
from df_test_framework.infrastructure.events import EventBus


class TestEventBusIntegration:
    """EventBus 集成测试"""

    @pytest.fixture
    def event_bus(self):
        """创建独立的 EventBus 实例"""
        return EventBus()

    @pytest.mark.asyncio
    async def test_publish_subscribe_basic(self, event_bus):
        """基本发布订阅"""
        received_events = []

        async def handler(event):
            received_events.append(event)

        # 订阅特定事件类型
        event_bus.subscribe(Event, handler)

        # 发布事件
        event = Event()
        await event_bus.publish(event)

        assert len(received_events) == 1
        assert received_events[0].event_id == event.event_id

    @pytest.mark.asyncio
    async def test_subscribe_all_events(self, event_bus):
        """订阅所有事件"""
        received_events = []

        async def handler(event):
            received_events.append(event)

        # 订阅所有事件
        event_bus.subscribe_all(handler)

        # 发布多种事件
        event1 = Event()
        await event_bus.publish(event1)

        # 验证接收到事件
        assert len(received_events) == 1

    @pytest.mark.asyncio
    async def test_event_correlation(self, event_bus):
        """事件关联测试"""
        start_events = []
        end_events = []

        async def start_handler(event):
            start_events.append(event)

        async def end_handler(event):
            end_events.append(event)

        event_bus.subscribe(HttpRequestStartEvent, start_handler)
        event_bus.subscribe(HttpRequestEndEvent, end_handler)

        # 创建关联事件
        start_event, correlation_id = HttpRequestStartEvent.create(
            method="GET",
            url="https://api.example.com/users",
        )
        await event_bus.publish(start_event)

        end_event = HttpRequestEndEvent.create(
            correlation_id=correlation_id,
            method="GET",
            url="https://api.example.com/users",
            status_code=200,
            duration=0.5,
        )
        await event_bus.publish(end_event)

        # 验证关联
        assert len(start_events) == 1
        assert len(end_events) == 1
        assert start_events[0].correlation_id == end_events[0].correlation_id

    @pytest.mark.asyncio
    async def test_multiple_handlers(self, event_bus):
        """多处理器订阅同一事件"""
        handler1_calls = []
        handler2_calls = []

        async def handler1(event):
            handler1_calls.append(event)

        async def handler2(event):
            handler2_calls.append(event)

        event_bus.subscribe(Event, handler1)
        event_bus.subscribe(Event, handler2)

        event = Event()
        await event_bus.publish(event)

        assert len(handler1_calls) == 1
        assert len(handler2_calls) == 1

    @pytest.mark.asyncio
    async def test_unsubscribe(self, event_bus):
        """取消订阅"""
        received_events = []

        async def handler(event):
            received_events.append(event)

        event_bus.subscribe(Event, handler)
        await event_bus.publish(Event())
        assert len(received_events) == 1

        event_bus.unsubscribe(Event, handler)
        await event_bus.publish(Event())
        assert len(received_events) == 1  # 不再接收


class TestHttpEventIntegration:
    """HTTP 事件集成测试"""

    @pytest.fixture
    def event_bus(self):
        return EventBus()

    @pytest.mark.asyncio
    async def test_http_request_lifecycle(self, event_bus):
        """HTTP 请求生命周期事件"""
        events = []

        async def handler(event):
            events.append(event)

        event_bus.subscribe(HttpRequestStartEvent, handler)
        event_bus.subscribe(HttpRequestEndEvent, handler)

        # 模拟请求开始
        start_event, correlation_id = HttpRequestStartEvent.create(
            method="POST",
            url="https://api.example.com/orders",
            headers={"Content-Type": "application/json"},
            body='{"product": "phone"}',
        )
        await event_bus.publish(start_event)

        # 模拟请求成功
        end_event = HttpRequestEndEvent.create(
            correlation_id=correlation_id,
            method="POST",
            url="https://api.example.com/orders",
            status_code=201,
            duration=0.3,
            body='{"id": 123}',
        )
        await event_bus.publish(end_event)

        assert len(events) == 2

        # 验证开始事件
        start = events[0]
        assert start.method == "POST"
        assert start.body == '{"product": "phone"}'

        # 验证结束事件
        end = events[1]
        assert end.status_code == 201
        assert end.duration == 0.3

    @pytest.mark.asyncio
    async def test_http_request_error(self, event_bus):
        """HTTP 请求错误事件"""
        events = []

        async def handler(event):
            events.append(event)

        event_bus.subscribe(HttpRequestStartEvent, handler)
        event_bus.subscribe(HttpRequestErrorEvent, handler)

        # 模拟请求开始
        start_event, correlation_id = HttpRequestStartEvent.create(
            method="GET",
            url="https://api.example.com/fail",
        )
        await event_bus.publish(start_event)

        # 模拟请求失败
        error_event = HttpRequestErrorEvent.create(
            correlation_id=correlation_id,
            method="GET",
            url="https://api.example.com/fail",
            error=ConnectionError("Connection refused"),
            duration=5.0,
        )
        await event_bus.publish(error_event)

        assert len(events) == 2

        error = events[1]
        assert error.error_type == "ConnectionError"
        assert error.correlation_id == start_event.correlation_id


class TestEventObserverPattern:
    """观察者模式集成测试"""

    @pytest.fixture
    def event_bus(self):
        return EventBus()

    @pytest.mark.asyncio
    async def test_custom_observer(self, event_bus):
        """自定义观察者"""

        class MetricsObserver:
            def __init__(self):
                self.request_count = 0
                self.error_count = 0
                self.total_duration = 0.0

            async def on_request_end(self, event):
                self.request_count += 1
                self.total_duration += event.duration

            async def on_request_error(self, event):
                self.error_count += 1

        observer = MetricsObserver()

        # 订阅事件
        event_bus.subscribe(HttpRequestEndEvent, observer.on_request_end)
        event_bus.subscribe(HttpRequestErrorEvent, observer.on_request_error)

        # 发布成功请求事件
        for i in range(5):
            _, cid = HttpRequestStartEvent.create(method="GET", url="/test")
            await event_bus.publish(
                HttpRequestEndEvent.create(
                    correlation_id=cid,
                    method="GET",
                    url="/test",
                    status_code=200,
                    duration=0.1 * (i + 1),
                )
            )

        # 发布错误事件
        _, cid = HttpRequestStartEvent.create(method="GET", url="/error")
        await event_bus.publish(
            HttpRequestErrorEvent.create(
                correlation_id=cid,
                method="GET",
                url="/error",
                error=TimeoutError("Request timeout"),
                duration=30.0,
            )
        )

        # 验证统计
        assert observer.request_count == 5
        assert observer.error_count == 1
        assert observer.total_duration == pytest.approx(1.5, rel=0.01)

    @pytest.mark.asyncio
    async def test_logging_observer(self, event_bus):
        """日志观察者"""
        logs = []

        class LoggingObserver:
            async def handle_event(self, event):
                logs.append(f"[{type(event).__name__}] {event.event_id}")

        observer = LoggingObserver()
        event_bus.subscribe_all(observer.handle_event)

        # 发布多种事件
        await event_bus.publish(Event())
        await event_bus.publish(Event())
        await event_bus.publish(Event())

        assert len(logs) == 3
        assert all("[Event]" in log for log in logs)


class TestEventPersistence:
    """事件持久化集成测试"""

    @pytest.fixture
    def event_bus(self):
        return EventBus()

    @pytest.mark.asyncio
    async def test_event_store_pattern(self, event_bus):
        """事件存储模式"""
        event_store = []

        class EventStoreObserver:
            async def store(self, event):
                event_store.append(
                    {
                        "event_id": event.event_id,
                        "event_type": type(event).__name__,
                        "timestamp": event.timestamp,
                        "data": self._serialize(event),
                    }
                )

            def _serialize(self, event):
                """序列化事件数据"""
                data = {}
                for field in ["method", "url", "status_code", "duration"]:
                    if hasattr(event, field):
                        data[field] = getattr(event, field)
                return data

        observer = EventStoreObserver()
        event_bus.subscribe(HttpRequestStartEvent, observer.store)
        event_bus.subscribe(HttpRequestEndEvent, observer.store)

        # 发布事件
        start, cid = HttpRequestStartEvent.create(method="GET", url="/api/users")
        await event_bus.publish(start)

        end = HttpRequestEndEvent.create(
            correlation_id=cid,
            method="GET",
            url="/api/users",
            status_code=200,
            duration=0.5,
        )
        await event_bus.publish(end)

        # 验证存储
        assert len(event_store) == 2
        assert event_store[0]["event_type"] == "HttpRequestStartEvent"
        assert event_store[1]["event_type"] == "HttpRequestEndEvent"
        assert event_store[1]["data"]["status_code"] == 200


class TestEventFiltering:
    """事件过滤集成测试"""

    @pytest.fixture
    def event_bus(self):
        return EventBus()

    @pytest.mark.asyncio
    async def test_conditional_handler(self, event_bus):
        """条件过滤处理器"""
        slow_requests = []

        async def slow_request_handler(event):
            if hasattr(event, "duration") and event.duration > 1.0:
                slow_requests.append(event)

        event_bus.subscribe(HttpRequestEndEvent, slow_request_handler)

        # 发布快速请求
        _, cid1 = HttpRequestStartEvent.create(method="GET", url="/fast")
        await event_bus.publish(
            HttpRequestEndEvent.create(
                correlation_id=cid1,
                method="GET",
                url="/fast",
                status_code=200,
                duration=0.1,
            )
        )

        # 发布慢请求
        _, cid2 = HttpRequestStartEvent.create(method="GET", url="/slow")
        await event_bus.publish(
            HttpRequestEndEvent.create(
                correlation_id=cid2,
                method="GET",
                url="/slow",
                status_code=200,
                duration=2.5,
            )
        )

        assert len(slow_requests) == 1
        assert slow_requests[0].duration == 2.5

    @pytest.mark.asyncio
    async def test_status_code_filter(self, event_bus):
        """状态码过滤"""
        errors = []

        async def error_handler(event):
            if hasattr(event, "status_code") and event.status_code >= 400:
                errors.append(event)

        event_bus.subscribe(HttpRequestEndEvent, error_handler)

        # 发布不同状态码的响应
        for status_code in [200, 201, 400, 404, 500]:
            _, cid = HttpRequestStartEvent.create(method="GET", url="/test")
            await event_bus.publish(
                HttpRequestEndEvent.create(
                    correlation_id=cid,
                    method="GET",
                    url="/test",
                    status_code=status_code,
                    duration=0.1,
                )
            )

        assert len(errors) == 3
        assert all(e.status_code >= 400 for e in errors)


class TestSyncPublish:
    """同步发布测试"""

    def test_publish_sync_basic(self):
        """publish_sync 基本功能测试"""
        event_bus = EventBus()
        received_events = []

        async def handler(event):
            received_events.append(event)

        event_bus.subscribe(Event, handler)

        # 同步发布
        event = Event()
        event_bus.publish_sync(event)

        assert len(received_events) == 1
        assert received_events[0].event_id == event.event_id

    def test_publish_sync_http_event(self):
        """publish_sync HTTP 事件测试"""
        event_bus = EventBus()
        received_events = []

        async def handler(event):
            received_events.append(event)

        event_bus.subscribe(HttpRequestEndEvent, handler)

        # 同步发布 HTTP 事件
        _, cid = HttpRequestStartEvent.create(method="GET", url="/api")
        event = HttpRequestEndEvent.create(
            correlation_id=cid,
            method="GET",
            url="/api",
            status_code=200,
            duration=0.5,
        )
        event_bus.publish_sync(event)

        assert len(received_events) == 1
        assert received_events[0].status_code == 200


class TestDecoratorSyntax:
    """装饰器语法测试"""

    @pytest.mark.asyncio
    async def test_on_decorator(self):
        """@bus.on 装饰器测试"""
        event_bus = EventBus()
        received_events = []

        @event_bus.on(HttpRequestEndEvent)
        async def handle_http_end(event: HttpRequestEndEvent):
            received_events.append(event)

        # 发布事件
        _, cid = HttpRequestStartEvent.create(method="GET", url="/test")
        event = HttpRequestEndEvent.create(
            correlation_id=cid,
            method="GET",
            url="/test",
            status_code=200,
            duration=0.1,
        )
        await event_bus.publish(event)

        assert len(received_events) == 1
        assert received_events[0].method == "GET"
