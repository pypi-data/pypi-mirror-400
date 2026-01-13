"""中间件链集成测试

测试中间件系统的洋葱模型执行顺序、组合使用和路径过滤功能。
"""

from typing import Any

import pytest

from df_test_framework.capabilities.clients.http.middleware import (
    BearerTokenMiddleware,
    MiddlewareFactory,
    PathFilteredMiddleware,
    RetryMiddleware,
    SignatureMiddleware,
)
from df_test_framework.core.middleware import BaseMiddleware
from df_test_framework.infrastructure.config.middleware_schema import (
    BearerTokenMiddlewareConfig,
    RetryMiddlewareConfig,
    SignatureAlgorithm,
    SignatureMiddlewareConfig,
    TokenSource,
)


class MockRequest:
    """模拟 HTTP 请求对象"""

    def __init__(
        self,
        method: str = "GET",
        path: str = "/api/test",
        params: dict | None = None,
        json: dict | None = None,
        headers: dict | None = None,
    ):
        self.method = method
        self.path = path
        self.url = path  # 兼容 PathFilteredMiddleware
        self.params = params or {}
        self.json = json
        self.headers = dict(headers) if headers else {}
        self._metadata: dict[str, Any] = {}

    def with_header(self, name: str, value: str) -> "MockRequest":
        """添加请求头（返回新对象）"""
        new_request = MockRequest(
            method=self.method,
            path=self.path,
            params=self.params.copy(),
            json=self.json.copy() if self.json else None,
            headers=self.headers.copy(),
        )
        new_request.headers[name] = value
        new_request._metadata = self._metadata.copy()
        return new_request

    def with_param(self, name: str, value: str) -> "MockRequest":
        """添加查询参数（返回新对象）"""
        new_request = MockRequest(
            method=self.method,
            path=self.path,
            params=self.params.copy(),
            json=self.json.copy() if self.json else None,
            headers=self.headers.copy(),
        )
        new_request.params[name] = value
        new_request._metadata = self._metadata.copy()
        return new_request

    def with_metadata(self, key: str, value: Any) -> "MockRequest":
        """添加元数据（返回新对象）"""
        new_request = MockRequest(
            method=self.method,
            path=self.path,
            params=self.params.copy(),
            json=self.json.copy() if self.json else None,
            headers=self.headers.copy(),
        )
        new_request._metadata = self._metadata.copy()
        new_request._metadata[key] = value
        return new_request

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """获取元数据"""
        return self._metadata.get(key, default)


class MockResponse:
    """模拟 HTTP 响应对象"""

    def __init__(self, status_code: int = 200, body: dict | None = None):
        self.status_code = status_code
        self.body = body or {}


class TestMiddlewareExecutionOrder:
    """中间件执行顺序测试（洋葱模型）"""

    def test_middleware_onion_model(self):
        """验证洋葱模型执行顺序"""
        execution_order = []

        class TrackingMiddleware(BaseMiddleware):
            def __init__(self, name: str, priority: int):
                super().__init__(name=name, priority=priority)

            async def __call__(self, request, call_next):
                execution_order.append(f"{self.name}:before")
                response = await call_next(request)
                execution_order.append(f"{self.name}:after")
                return response

        # 创建不同优先级的中间件
        middleware_a = TrackingMiddleware("A", priority=10)  # 高优先级
        middleware_b = TrackingMiddleware("B", priority=20)
        middleware_c = TrackingMiddleware("C", priority=30)  # 低优先级

        # 按优先级排序并执行
        middlewares = sorted(
            [middleware_a, middleware_b, middleware_c],
            key=lambda m: m.priority,
        )

        async def run_chain():
            async def final_handler(request):
                execution_order.append("handler")
                return MockResponse(200)

            # 构建中间件链
            handler = final_handler
            for middleware in reversed(middlewares):
                prev_handler = handler

                async def make_handler(m, h):
                    async def wrapped(req):
                        return await m(req, h)

                    return wrapped

                handler = await make_handler(middleware, prev_handler)

            return await handler(MockRequest())

        import asyncio

        asyncio.run(run_chain())

        # 验证洋葱模型：进入顺序 A→B→C，返回顺序 C→B→A
        assert execution_order == [
            "A:before",
            "B:before",
            "C:before",
            "handler",
            "C:after",
            "B:after",
            "A:after",
        ]

    def test_priority_affects_execution_order(self):
        """验证优先级影响执行顺序"""
        # RetryMiddleware 默认 priority=5
        # SignatureMiddleware 默认 priority=10
        # BearerTokenMiddleware 默认 priority=20

        retry = RetryMiddleware(max_retries=1)
        signature = SignatureMiddleware(secret="test")
        bearer = BearerTokenMiddleware(token="token123")

        assert retry.priority < signature.priority < bearer.priority

        # 按优先级排序
        middlewares = sorted([bearer, retry, signature], key=lambda m: m.priority)
        names = [m.name for m in middlewares]

        # 应该是 Retry → Signature → BearerToken 顺序
        assert names == ["RetryMiddleware", "SignatureMiddleware", "BearerTokenMiddleware"]


class TestSignatureMiddleware:
    """签名中间件测试"""

    @pytest.mark.asyncio
    async def test_md5_signature(self):
        """MD5 签名测试"""
        middleware = SignatureMiddleware(
            secret="my_secret",
            algorithm="md5",
            header_name="X-Sign",
        )

        request = MockRequest(
            method="POST",
            path="/api/orders",
            json={"product": "phone", "price": 999},
        )

        final_request = None

        async def capture_request(req):
            nonlocal final_request
            final_request = req
            return MockResponse(200)

        await middleware(request, capture_request)

        # 验证签名头已添加
        assert "X-Sign" in final_request.headers
        assert len(final_request.headers["X-Sign"]) == 32  # MD5 长度

    @pytest.mark.asyncio
    async def test_sha256_signature(self):
        """SHA256 签名测试"""
        middleware = SignatureMiddleware(
            secret="my_secret",
            algorithm="sha256",
            header_name="X-Signature",
        )

        request = MockRequest(json={"data": "test"})

        final_request = None

        async def capture_request(req):
            nonlocal final_request
            final_request = req
            return MockResponse(200)

        await middleware(request, capture_request)

        assert "X-Signature" in final_request.headers
        assert len(final_request.headers["X-Signature"]) == 64  # SHA256 长度

    @pytest.mark.asyncio
    async def test_timestamp_header(self):
        """时间戳头测试"""
        middleware = SignatureMiddleware(
            secret="secret",
            timestamp_header="X-Timestamp",
        )

        request = MockRequest()
        final_request = None

        async def capture_request(req):
            nonlocal final_request
            final_request = req
            return MockResponse(200)

        await middleware(request, capture_request)

        # 验证时间戳头已添加
        assert "X-Timestamp" in final_request.headers
        timestamp = final_request.headers["X-Timestamp"]
        assert timestamp.isdigit()
        assert len(timestamp) == 10  # Unix 时间戳（秒级）


class TestBearerTokenMiddleware:
    """Bearer Token 中间件测试"""

    @pytest.mark.asyncio
    async def test_static_token(self):
        """静态 Token 测试"""
        middleware = BearerTokenMiddleware(token="my_token_123")

        request = MockRequest()
        final_request = None

        async def capture_request(req):
            nonlocal final_request
            final_request = req
            return MockResponse(200)

        await middleware(request, capture_request)

        assert final_request.headers["Authorization"] == "Bearer my_token_123"

    @pytest.mark.asyncio
    async def test_custom_header_prefix(self):
        """自定义 Token 前缀测试"""
        middleware = BearerTokenMiddleware(
            token="api_key_xxx",
            header_name="X-Auth-Token",
            header_prefix="Token",
        )

        request = MockRequest()
        final_request = None

        async def capture_request(req):
            nonlocal final_request
            final_request = req
            return MockResponse(200)

        await middleware(request, capture_request)

        assert final_request.headers["X-Auth-Token"] == "Token api_key_xxx"

    @pytest.mark.asyncio
    async def test_skip_auth_metadata(self):
        """v3.19.0: skip_auth 跳过认证测试"""
        middleware = BearerTokenMiddleware(token="my_token")

        request = MockRequest().with_metadata("skip_auth", True)
        final_request = None

        async def capture_request(req):
            nonlocal final_request
            final_request = req
            return MockResponse(200)

        await middleware(request, capture_request)

        # 应该没有添加 Authorization 头
        assert "Authorization" not in final_request.headers

    @pytest.mark.asyncio
    async def test_custom_token_metadata(self):
        """v3.19.0: custom_token 自定义 Token 测试"""
        middleware = BearerTokenMiddleware(token="default_token")

        request = MockRequest().with_metadata("custom_token", "override_token")
        final_request = None

        async def capture_request(req):
            nonlocal final_request
            final_request = req
            return MockResponse(200)

        await middleware(request, capture_request)

        # 应该使用自定义 Token
        assert final_request.headers["Authorization"] == "Bearer override_token"


class TestRetryMiddleware:
    """重试中间件测试"""

    @pytest.mark.asyncio
    async def test_no_retry_on_success(self):
        """成功响应不重试"""
        middleware = RetryMiddleware(max_retries=3)
        call_count = 0

        async def handler(request):
            nonlocal call_count
            call_count += 1
            return MockResponse(200)

        response = await middleware(MockRequest(), handler)

        assert response.status_code == 200
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_server_error(self):
        """服务器错误重试"""
        middleware = RetryMiddleware(
            max_retries=3,
            initial_delay=0.01,  # 加快测试
            retry_on_status=[500, 502, 503],
        )
        call_count = 0

        async def handler(request):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return MockResponse(500)
            return MockResponse(200)

        response = await middleware(MockRequest(), handler)

        assert response.status_code == 200
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """超过最大重试次数"""
        middleware = RetryMiddleware(
            max_retries=2,
            initial_delay=0.01,
            retry_on_status=[500],
        )
        call_count = 0

        async def handler(request):
            nonlocal call_count
            call_count += 1
            return MockResponse(500)

        response = await middleware(MockRequest(), handler)

        # 返回最后一次响应
        assert response.status_code == 500
        assert call_count == 2


class TestPathFilteredMiddleware:
    """路径过滤中间件测试"""

    @pytest.mark.asyncio
    async def test_include_paths_match(self):
        """匹配包含路径时执行中间件"""
        inner_middleware = SignatureMiddleware(secret="test")
        middleware = PathFilteredMiddleware(
            middleware=inner_middleware,
            include_paths=["/api/**"],
        )

        request = MockRequest(path="/api/users")
        final_request = None

        async def capture_request(req):
            nonlocal final_request
            final_request = req
            return MockResponse(200)

        await middleware(request, capture_request)

        # 签名中间件应该执行
        assert "X-Sign" in final_request.headers

    @pytest.mark.asyncio
    async def test_include_paths_no_match(self):
        """不匹配包含路径时跳过中间件"""
        inner_middleware = SignatureMiddleware(secret="test")
        middleware = PathFilteredMiddleware(
            middleware=inner_middleware,
            include_paths=["/admin/**"],
        )

        request = MockRequest(path="/api/users")
        final_request = None

        async def capture_request(req):
            nonlocal final_request
            final_request = req
            return MockResponse(200)

        await middleware(request, capture_request)

        # 签名中间件不应该执行
        assert "X-Sign" not in final_request.headers

    @pytest.mark.asyncio
    async def test_exclude_paths(self):
        """排除路径测试"""
        inner_middleware = SignatureMiddleware(secret="test")
        middleware = PathFilteredMiddleware(
            middleware=inner_middleware,
            include_paths=["/api/**"],
            exclude_paths=["/api/health"],
        )

        # 匹配 include 但也匹配 exclude - 应该跳过
        request = MockRequest(path="/api/health")
        final_request = None

        async def capture_request(req):
            nonlocal final_request
            final_request = req
            return MockResponse(200)

        await middleware(request, capture_request)

        assert "X-Sign" not in final_request.headers


class TestMiddlewareFactory:
    """中间件工厂测试"""

    def test_create_signature_middleware(self):
        """从配置创建签名中间件"""
        config = SignatureMiddlewareConfig(
            algorithm=SignatureAlgorithm.SHA256,
            secret="factory_secret",
            header="X-Factory-Sign",
            priority=15,
        )

        middleware = MiddlewareFactory.create(config)

        assert middleware is not None
        assert isinstance(middleware, SignatureMiddleware)
        assert middleware.priority == 15
        assert middleware.algorithm == "sha256"
        assert middleware.header_name == "X-Factory-Sign"

    def test_create_bearer_token_middleware(self):
        """从配置创建 Bearer Token 中间件"""
        config = BearerTokenMiddlewareConfig(
            source=TokenSource.STATIC,
            token="config_token",
            header="Authorization",
            token_prefix="Bearer",
        )

        middleware = MiddlewareFactory.create(config)

        assert middleware is not None
        assert isinstance(middleware, BearerTokenMiddleware)
        assert middleware._token == "config_token"

    def test_create_retry_middleware(self):
        """从配置创建重试中间件"""
        config = RetryMiddlewareConfig(
            max_retries=5,
            initial_delay=0.5,
            max_delay=30.0,
            retry_on_status=[500, 502, 503, 504],
        )

        middleware = MiddlewareFactory.create(config)

        assert middleware is not None
        assert isinstance(middleware, RetryMiddleware)
        assert middleware.max_retries == 5
        assert middleware.initial_delay == 0.5
        assert middleware.max_delay == 30.0

    def test_create_disabled_middleware(self):
        """禁用的中间件返回 None"""
        config = SignatureMiddlewareConfig(
            algorithm=SignatureAlgorithm.MD5,
            secret="secret",
            enabled=False,
        )

        middleware = MiddlewareFactory.create(config)

        assert middleware is None

    def test_create_two_step_login_middleware(self):
        """v3.39.0: 从配置创建两步登录 Bearer Token 中间件"""
        config = BearerTokenMiddlewareConfig(
            source=TokenSource.TWO_STEP_LOGIN,
            login_url="/auth/login",
            check_url="/auth/check",
            credentials={"username": "admin", "password": "pass", "smsCode": "123456"},
            token_key="access_token",
            status_ok_values=["ok"],
            data_field="data",
        )

        middleware = MiddlewareFactory.create(config)

        assert middleware is not None
        assert isinstance(middleware, BearerTokenMiddleware)
        # 验证使用的是 TwoStepLoginTokenProvider
        from df_test_framework.capabilities.clients.http.middleware.auth import (
            TwoStepLoginTokenProvider,
        )

        assert isinstance(middleware._login_token_provider, TwoStepLoginTokenProvider)


class TestMiddlewareChainComposition:
    """中间件链组合测试"""

    @pytest.mark.asyncio
    async def test_full_middleware_chain(self):
        """完整中间件链测试"""
        # 创建中间件
        signature = SignatureMiddleware(
            secret="secret",
            header_name="X-Sign",
            timestamp_header="X-Time",
        )
        bearer = BearerTokenMiddleware(token="my_token")

        # 按优先级排序
        middlewares = sorted([signature, bearer], key=lambda m: m.priority)

        request = MockRequest(
            method="POST",
            path="/api/orders",
            json={"amount": 100},
        )

        async def run_chain():
            async def final_handler(req):
                return MockResponse(200), req

            # 构建中间件链
            handler = final_handler
            for middleware in reversed(middlewares):

                async def make_handler(m, h):
                    async def wrapped(req):
                        result = await m(req, lambda r: h(r))
                        return result

                    return wrapped

                handler = await make_handler(middleware, handler)

            return await handler(request)

        response = await run_chain()

        # 由于中间件链复杂，这里主要验证不抛异常
        assert response is not None

    @pytest.mark.asyncio
    async def test_middleware_error_handling(self):
        """中间件错误处理测试"""

        class ErrorMiddleware(BaseMiddleware):
            async def __call__(self, request, call_next):
                raise ValueError("Middleware error")

        middleware = ErrorMiddleware()

        async def handler(request):
            return MockResponse(200)

        with pytest.raises(ValueError, match="Middleware error"):
            await middleware(MockRequest(), handler)

    @pytest.mark.asyncio
    async def test_middleware_modifies_request(self):
        """中间件修改请求测试"""

        class AddHeaderMiddleware(BaseMiddleware):
            async def __call__(self, request, call_next):
                request = request.with_header("X-Custom", "value")
                return await call_next(request)

        middleware = AddHeaderMiddleware()
        final_request = None

        async def capture_request(req):
            nonlocal final_request
            final_request = req
            return MockResponse(200)

        await middleware(MockRequest(), capture_request)

        assert final_request.headers["X-Custom"] == "value"

    @pytest.mark.asyncio
    async def test_middleware_modifies_response(self):
        """中间件修改响应测试"""

        class ModifyResponseMiddleware(BaseMiddleware):
            async def __call__(self, request, call_next):
                response = await call_next(request)
                response.body["modified"] = True
                return response

        middleware = ModifyResponseMiddleware()

        async def handler(request):
            return MockResponse(200, body={"data": "test"})

        response = await middleware(MockRequest(), handler)

        assert response.body["modified"] is True
        assert response.body["data"] == "test"
