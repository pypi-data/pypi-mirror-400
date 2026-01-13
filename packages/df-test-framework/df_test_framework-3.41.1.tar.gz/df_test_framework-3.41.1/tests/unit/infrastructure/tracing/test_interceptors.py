"""追踪拦截器/中间件测试

测试 HTTP 和 gRPC 追踪拦截器/中间件的功能

v3.32.0: GrpcTracingInterceptor 重构为 GrpcTracingMiddleware
"""

import pytest

from df_test_framework.infrastructure.tracing.interceptors import (
    GrpcTracingInterceptor,
    GrpcTracingMiddleware,
    SpanContextCarrier,
    TracingInterceptor,
)


class TestTracingInterceptorBasic:
    """HTTP 追踪拦截器基础测试"""

    def test_create_interceptor(self):
        """测试创建拦截器"""
        interceptor = TracingInterceptor()

        assert interceptor.name == "TracingInterceptor"
        assert interceptor.priority == 10
        assert interceptor.propagate_context is True
        assert interceptor.record_headers is False
        assert interceptor.record_body is False

    def test_create_interceptor_with_custom_config(self):
        """测试自定义配置"""
        interceptor = TracingInterceptor(
            name="CustomTracing",
            priority=5,
            record_headers=True,
            record_body=True,
            propagate_context=False,
            sensitive_headers=["x-custom-secret"],
        )

        assert interceptor.name == "CustomTracing"
        assert interceptor.priority == 5
        assert interceptor.record_headers is True
        assert interceptor.record_body is True
        assert interceptor.propagate_context is False
        assert "x-custom-secret" in interceptor.sensitive_headers

    def test_default_sensitive_headers(self):
        """测试默认敏感头列表"""
        interceptor = TracingInterceptor()

        assert "authorization" in interceptor.sensitive_headers
        assert "x-api-key" in interceptor.sensitive_headers
        assert "cookie" in interceptor.sensitive_headers


class TestSpanContextCarrier:
    """SpanContextCarrier 测试"""

    def test_set_and_get(self):
        """测试设置和获取"""
        SpanContextCarrier.clear()

        span_mock = object()
        start_time = 1234567890.123

        SpanContextCarrier.set(span_mock, start_time)

        retrieved_span, retrieved_time = SpanContextCarrier.get()
        assert retrieved_span is span_mock
        assert retrieved_time == start_time

    def test_clear(self):
        """测试清除"""
        span_mock = object()
        SpanContextCarrier.set(span_mock, 123.0)

        SpanContextCarrier.clear()

        span, start_time = SpanContextCarrier.get()
        assert span is None
        assert start_time is None


class TestGrpcTracingMiddlewareBasic:
    """gRPC 追踪中间件基础测试（v3.32.0 重构）"""

    def test_create_middleware(self):
        """测试创建中间件"""
        middleware = GrpcTracingMiddleware()

        assert middleware.name == "GrpcTracingMiddleware"
        assert middleware.priority == 10
        assert middleware.propagate_context is True
        assert middleware.record_metadata is False

    def test_create_middleware_with_custom_config(self):
        """测试自定义配置"""
        middleware = GrpcTracingMiddleware(
            record_metadata=True,
            propagate_context=False,
            sensitive_keys=["x-custom-key"],
            priority=5,
        )

        assert middleware.name == "GrpcTracingMiddleware"
        assert middleware.priority == 5
        assert middleware.record_metadata is True
        assert middleware.propagate_context is False
        assert "x-custom-key" in middleware.sensitive_keys

    def test_default_sensitive_keys(self):
        """测试默认敏感键列表"""
        middleware = GrpcTracingMiddleware()

        assert "authorization" in middleware.sensitive_keys
        assert "x-api-key" in middleware.sensitive_keys
        assert "cookie" in middleware.sensitive_keys

    def test_parse_method(self):
        """测试解析 gRPC 方法名"""
        middleware = GrpcTracingMiddleware()

        # 标准格式
        service, method = middleware._parse_method("/package.UserService/GetUser")
        assert service == "package.UserService"
        assert method == "GetUser"

        # 简单格式
        service, method = middleware._parse_method("/MyService/DoSomething")
        assert service == "MyService"
        assert method == "DoSomething"

        # 无效格式
        service, method = middleware._parse_method("invalid")
        assert service == "invalid"
        assert method == "unknown"

    def test_sanitize_value(self):
        """测试脱敏功能"""
        middleware = GrpcTracingMiddleware(sensitive_keys=["secret-key"])

        # 敏感键
        result = middleware._sanitize_value("secret-key", "my-secret-value")
        assert result == "***"

        # 非敏感键
        result = middleware._sanitize_value("normal-key", "normal-value")
        assert result == "normal-value"

    def test_build_request_attributes(self):
        """测试构建请求属性"""
        middleware = GrpcTracingMiddleware(record_metadata=True)

        attrs = middleware._build_request_attributes(
            full_method="/package.UserService/GetUser",
            service_name="package.UserService",
            method_name="GetUser",
            metadata=[("x-request-id", "abc-123"), ("authorization", "Bearer token")],
        )

        assert attrs["rpc.system"] == "grpc"
        assert attrs["rpc.service"] == "package.UserService"
        assert attrs["rpc.method"] == "GetUser"
        assert attrs["rpc.grpc.full_method"] == "/package.UserService/GetUser"

        # 验证元数据记录（非敏感键）
        assert attrs.get("rpc.request.metadata.x-request-id") == "abc-123"
        # 验证敏感键脱敏
        assert attrs.get("rpc.request.metadata.authorization") == "***"

    def test_build_request_attributes_without_metadata(self):
        """测试不记录元数据"""
        middleware = GrpcTracingMiddleware(record_metadata=False)

        attrs = middleware._build_request_attributes(
            full_method="/UserService/GetUser",
            service_name="UserService",
            method_name="GetUser",
            metadata=[("x-request-id", "abc-123")],
        )

        # 不应该包含元数据属性
        assert "rpc.request.metadata.x-request-id" not in attrs


class TestGrpcTracingMiddlewareAsync:
    """gRPC 追踪中间件异步测试"""

    @pytest.mark.asyncio
    async def test_middleware_call_without_otel(self):
        """测试无 OpenTelemetry 时的行为"""
        from df_test_framework.capabilities.clients.grpc.models import (
            GrpcRequest,
            GrpcResponse,
            GrpcStatusCode,
        )

        middleware = GrpcTracingMiddleware()

        request = GrpcRequest(
            method="/UserService/GetUser",
            message={"user_id": 123},
            metadata=[("x-request-id", "abc-123")],
        )

        async def mock_call_next(req: GrpcRequest) -> GrpcResponse:
            return GrpcResponse(data={"name": "Alice"}, status_code=GrpcStatusCode.OK)

        # 即使没有 OTEL，也应该正常执行
        response = await middleware(request, mock_call_next)

        assert response.status_code == GrpcStatusCode.OK
        assert response.data == {"name": "Alice"}


class TestBackwardCompatibility:
    """向后兼容性测试"""

    def test_grpc_tracing_interceptor_alias(self):
        """测试 GrpcTracingInterceptor 是 GrpcTracingMiddleware 的别名"""
        assert GrpcTracingInterceptor is GrpcTracingMiddleware

    def test_create_using_old_name(self):
        """测试使用旧名称创建"""
        interceptor = GrpcTracingInterceptor()

        # 应该是 GrpcTracingMiddleware 实例
        assert isinstance(interceptor, GrpcTracingMiddleware)
        assert interceptor.name == "GrpcTracingMiddleware"


class TestInterceptorImports:
    """测试拦截器/中间件导入"""

    def test_import_from_interceptors_package(self):
        """测试从 interceptors 包导入"""
        from df_test_framework.infrastructure.tracing.interceptors import (
            GrpcTracingInterceptor,
            GrpcTracingMiddleware,
            SpanContextCarrier,
            TracingInterceptor,
        )

        assert TracingInterceptor is not None
        assert SpanContextCarrier is not None
        assert GrpcTracingMiddleware is not None
        assert GrpcTracingInterceptor is not None

    def test_import_directly(self):
        """测试直接导入"""
        from df_test_framework.infrastructure.tracing.interceptors.grpc import (
            GrpcTracingInterceptor,
            GrpcTracingMiddleware,
        )
        from df_test_framework.infrastructure.tracing.interceptors.http import (
            TracingInterceptor,
        )

        assert TracingInterceptor is not None
        assert GrpcTracingMiddleware is not None
        assert GrpcTracingInterceptor is not None

    def test_import_from_tracing_module(self):
        """测试从 tracing 模块导入"""
        from df_test_framework.infrastructure.tracing import (
            GrpcTracingInterceptor,
            GrpcTracingMiddleware,
        )

        assert GrpcTracingMiddleware is not None
        assert GrpcTracingInterceptor is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
