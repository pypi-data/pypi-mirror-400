"""mocking/http_mock.py 测试模块

测试 HTTP Mock 功能

v3.36.0 - 技术债务清理：提升测试覆盖率
"""

import re
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.mark.unit
class TestMockResponseException:
    """测试 MockResponseException 异常"""

    def test_exception_attributes(self):
        """测试异常属性"""
        from df_test_framework.testing.mocking.http_mock import MockResponseException

        mock_response = MagicMock()
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.url = "/api/users"

        exc = MockResponseException(mock_response, mock_request)

        assert exc.response is mock_response
        assert exc.request is mock_request
        assert "GET" in str(exc)
        assert "/api/users" in str(exc)

    def test_mock_response_alias(self):
        """测试 MockResponse 别名"""
        from df_test_framework.testing.mocking.http_mock import (
            MockResponse,
            MockResponseException,
        )

        assert MockResponse is MockResponseException


@pytest.mark.unit
class TestMockRule:
    """测试 MockRule 数据类"""

    def test_mock_rule_basic(self):
        """测试基本规则创建"""
        from df_test_framework.testing.mocking.http_mock import MockRule

        rule = MockRule(
            url="/api/users",
            method="GET",
            status_code=200,
            json_data={"users": []},
        )

        assert rule.url == "/api/users"
        assert rule.method == "GET"
        assert rule.status_code == 200
        assert rule.json_data == {"users": []}
        assert rule.text_data is None
        assert rule.headers == {}
        assert rule.match_headers is None
        assert rule.match_json is None
        assert rule.times is None

    def test_mock_rule_with_regex(self):
        """测试正则表达式 URL"""
        from df_test_framework.testing.mocking.http_mock import MockRule

        pattern = re.compile(r"/api/users/\d+")
        rule = MockRule(url=pattern, status_code=200)

        assert rule.url == pattern

    def test_mock_rule_with_headers(self):
        """测试带 Headers 的规则"""
        from df_test_framework.testing.mocking.http_mock import MockRule

        rule = MockRule(
            url="/api/users",
            headers={"X-Custom": "value"},
            match_headers={"Authorization": "Bearer token"},
        )

        assert rule.headers == {"X-Custom": "value"}
        assert rule.match_headers == {"Authorization": "Bearer token"}

    def test_mock_rule_with_json_matching(self):
        """测试 JSON 匹配"""
        from df_test_framework.testing.mocking.http_mock import MockRule

        rule = MockRule(
            url="/api/users",
            method="POST",
            match_json={"name": "Alice"},
            json_data={"id": 1, "name": "Alice"},
        )

        assert rule.match_json == {"name": "Alice"}

    def test_mock_rule_with_times(self):
        """测试次数限制"""
        from df_test_framework.testing.mocking.http_mock import MockRule

        rule = MockRule(url="/api/users", times=3)

        assert rule.times == 3


@pytest.mark.unit
class TestMockMiddleware:
    """测试 MockMiddleware 类"""

    def test_middleware_init(self):
        """测试中间件初始化"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware

        middleware = MockMiddleware()

        assert middleware.name == "MockMiddleware"
        assert middleware.priority == 1
        assert middleware.rules == []
        assert middleware.matched_requests == []

    def test_middleware_init_with_priority(self):
        """测试带优先级的初始化"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware

        middleware = MockMiddleware(priority=10)

        assert middleware.priority == 10

    def test_add_rule(self):
        """测试添加规则"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware

        middleware = MockMiddleware()
        result = middleware.add_rule(
            url="/api/users",
            method="GET",
            json_data={"users": []},
        )

        assert result is middleware  # 链式调用
        assert len(middleware.rules) == 1
        assert middleware.rules[0].url == "/api/users"
        assert middleware.rules[0].method == "GET"

    def test_add_rule_chaining(self):
        """测试链式添加规则"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware

        middleware = MockMiddleware()
        middleware.add_rule("/api/users", "GET").add_rule("/api/login", "POST")

        assert len(middleware.rules) == 2

    def test_clear_rules(self):
        """测试清空规则"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware

        middleware = MockMiddleware()
        middleware.add_rule("/api/users", "GET")
        middleware.matched_requests.append(MagicMock())

        middleware.clear_rules()

        assert middleware.rules == []
        assert middleware.matched_requests == []

    def test_match_rule_string_url(self):
        """测试字符串 URL 匹配"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware, MockRule

        middleware = MockMiddleware()
        rule = MockRule(url="/api/users", method="GET")

        mock_request = MagicMock()
        mock_request.url = "/api/users"
        mock_request.method = "GET"
        mock_request.headers = {}
        mock_request.json = None

        assert middleware._match_rule(rule, mock_request) is True

    def test_match_rule_regex_url(self):
        """测试正则 URL 匹配"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware, MockRule

        middleware = MockMiddleware()
        pattern = re.compile(r"/api/users/\d+")
        rule = MockRule(url=pattern, method="GET")

        mock_request = MagicMock()
        mock_request.url = "/api/users/123"
        mock_request.method = "GET"
        mock_request.headers = {}
        mock_request.json = None

        assert middleware._match_rule(rule, mock_request) is True

    def test_match_rule_wildcard_url(self):
        """测试通配符 URL 匹配"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware, MockRule

        middleware = MockMiddleware()
        rule = MockRule(url="/api/*", method=None)

        mock_request = MagicMock()
        mock_request.url = "/api/users"
        mock_request.method = "GET"
        mock_request.headers = {}
        mock_request.json = None

        assert middleware._match_rule(rule, mock_request) is True

    def test_match_rule_method_mismatch(self):
        """测试方法不匹配"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware, MockRule

        middleware = MockMiddleware()
        rule = MockRule(url="/api/users", method="POST")

        mock_request = MagicMock()
        mock_request.url = "/api/users"
        mock_request.method = "GET"
        mock_request.headers = {}
        mock_request.json = None

        assert middleware._match_rule(rule, mock_request) is False

    def test_match_rule_headers_match(self):
        """测试 Headers 匹配"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware, MockRule

        middleware = MockMiddleware()
        rule = MockRule(url="/api/users", match_headers={"X-Token": "abc"})

        mock_request = MagicMock()
        mock_request.url = "/api/users"
        mock_request.method = "GET"
        mock_request.headers = {"X-Token": "abc"}
        mock_request.json = None

        assert middleware._match_rule(rule, mock_request) is True

    def test_match_rule_headers_mismatch(self):
        """测试 Headers 不匹配"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware, MockRule

        middleware = MockMiddleware()
        rule = MockRule(url="/api/users", match_headers={"X-Token": "abc"})

        mock_request = MagicMock()
        mock_request.url = "/api/users"
        mock_request.method = "GET"
        mock_request.headers = {"X-Token": "xyz"}
        mock_request.json = None

        assert middleware._match_rule(rule, mock_request) is False

    def test_match_rule_json_match(self):
        """测试 JSON 匹配"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware, MockRule

        middleware = MockMiddleware()
        rule = MockRule(url="/api/users", match_json={"name": "Alice"})

        mock_request = MagicMock()
        mock_request.url = "/api/users"
        mock_request.method = "POST"
        mock_request.headers = {}
        mock_request.json = {"name": "Alice"}

        assert middleware._match_rule(rule, mock_request) is True

    def test_match_rule_json_mismatch(self):
        """测试 JSON 不匹配"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware, MockRule

        middleware = MockMiddleware()
        rule = MockRule(url="/api/users", match_json={"name": "Alice"})

        mock_request = MagicMock()
        mock_request.url = "/api/users"
        mock_request.method = "POST"
        mock_request.headers = {}
        mock_request.json = {"name": "Bob"}

        assert middleware._match_rule(rule, mock_request) is False

    def test_create_mock_response_json(self):
        """测试创建 JSON 响应"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware, MockRule

        middleware = MockMiddleware()
        rule = MockRule(
            url="/api/users",
            status_code=200,
            json_data={"users": [{"id": 1}]},
        )

        mock_request = MagicMock()
        response = middleware._create_mock_response(rule, mock_request)

        assert response.status_code == 200
        assert response.json_data == {"users": [{"id": 1}]}
        assert "application/json" in response.headers.get("Content-Type", "")

    def test_create_mock_response_text(self):
        """测试创建文本响应"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware, MockRule

        middleware = MockMiddleware()
        rule = MockRule(
            url="/api/health",
            status_code=200,
            text_data="OK",
        )

        mock_request = MagicMock()
        response = middleware._create_mock_response(rule, mock_request)

        assert response.status_code == 200
        assert response.body == "OK"

    def test_create_mock_response_custom_headers(self):
        """测试自定义响应 Headers"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware, MockRule

        middleware = MockMiddleware()
        rule = MockRule(
            url="/api/users",
            headers={"X-Custom": "value"},
            json_data={"id": 1},
        )

        mock_request = MagicMock()
        response = middleware._create_mock_response(rule, mock_request)

        assert response.headers["X-Custom"] == "value"

    @pytest.mark.asyncio
    async def test_middleware_call_with_match(self):
        """测试中间件调用（匹配）"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware

        middleware = MockMiddleware()
        middleware.add_rule("/api/users", "GET", json_data={"users": []})

        mock_request = MagicMock()
        mock_request.url = "/api/users"
        mock_request.method = "GET"
        mock_request.headers = {}
        mock_request.json = None

        mock_call_next = AsyncMock()

        response = await middleware(mock_request, mock_call_next)

        assert response.status_code == 200
        assert response.json_data == {"users": []}
        mock_call_next.assert_not_called()  # 不应调用 call_next

    @pytest.mark.asyncio
    async def test_middleware_call_without_match(self):
        """测试中间件调用（不匹配）"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware

        middleware = MockMiddleware()
        middleware.add_rule("/api/users", "GET", json_data={"users": []})

        mock_request = MagicMock()
        mock_request.url = "/api/orders"
        mock_request.method = "GET"
        mock_request.headers = {}
        mock_request.json = None

        mock_response = MagicMock()
        mock_call_next = AsyncMock(return_value=mock_response)

        response = await middleware(mock_request, mock_call_next)

        assert response is mock_response
        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_middleware_call_times_limit(self):
        """测试中间件调用次数限制"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware

        middleware = MockMiddleware()
        middleware.add_rule("/api/users", "GET", json_data={"users": []}, times=2)

        mock_request = MagicMock()
        mock_request.url = "/api/users"
        mock_request.method = "GET"
        mock_request.headers = {}
        mock_request.json = None

        mock_call_next = AsyncMock()

        # 第一次调用
        await middleware(mock_request, mock_call_next)
        assert len(middleware.rules) == 1

        # 第二次调用（达到限制）
        await middleware(mock_request, mock_call_next)
        assert len(middleware.rules) == 0  # 规则被移除

    def test_assert_called_success(self):
        """测试断言调用成功"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware

        middleware = MockMiddleware()

        mock_request = MagicMock()
        mock_request.url = "/api/users"
        mock_request.method = "GET"

        middleware.matched_requests.append(mock_request)

        # 不应抛出异常
        middleware.assert_called("/api/users")
        middleware.assert_called("/api/users", "GET")
        middleware.assert_called("/api/users", "GET", times=1)

    def test_assert_called_failure(self):
        """测试断言调用失败"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware

        middleware = MockMiddleware()

        with pytest.raises(AssertionError):
            middleware.assert_called("/api/users")

    def test_assert_called_wrong_times(self):
        """测试断言调用次数错误"""
        from df_test_framework.testing.mocking.http_mock import MockMiddleware

        middleware = MockMiddleware()

        mock_request = MagicMock()
        mock_request.url = "/api/users"
        mock_request.method = "GET"

        middleware.matched_requests.append(mock_request)

        with pytest.raises(AssertionError):
            middleware.assert_called("/api/users", times=2)


@pytest.mark.unit
class TestMockInterceptorAlias:
    """测试 MockInterceptor 别名"""

    def test_mock_interceptor_alias(self):
        """测试 MockInterceptor 是 MockMiddleware 的别名"""
        from df_test_framework.testing.mocking.http_mock import (
            MockInterceptor,
            MockMiddleware,
        )

        assert MockInterceptor is MockMiddleware


@pytest.mark.unit
class TestHttpMocker:
    """测试 HttpMocker 类"""

    def test_http_mocker_init(self):
        """测试初始化"""
        from df_test_framework.testing.mocking.http_mock import HttpMocker

        mock_client = MagicMock()
        mocker = HttpMocker(mock_client)

        assert mocker.http_client is mock_client
        assert mocker.middleware is not None

    def test_http_mocker_init_with_use_method(self):
        """测试使用 use 方法的客户端"""
        from df_test_framework.testing.mocking.http_mock import HttpMocker

        mock_client = MagicMock()
        mock_client.use = MagicMock()

        mocker = HttpMocker(mock_client)

        mock_client.use.assert_called_once_with(mocker.middleware)

    def test_http_mocker_add_rule(self):
        """测试添加规则"""
        from df_test_framework.testing.mocking.http_mock import HttpMocker

        mock_client = MagicMock()
        mocker = HttpMocker(mock_client)

        result = mocker.add_rule("/api/users", "GET", json_data={"users": []})

        assert result is mocker  # 链式调用
        assert len(mocker.middleware.rules) == 1

    def test_http_mocker_get(self):
        """测试 GET 快捷方法"""
        from df_test_framework.testing.mocking.http_mock import HttpMocker

        mock_client = MagicMock()
        mocker = HttpMocker(mock_client)

        mocker.get("/api/users", json={"users": []})

        assert len(mocker.middleware.rules) == 1
        assert mocker.middleware.rules[0].method == "GET"
        assert mocker.middleware.rules[0].status_code == 200

    def test_http_mocker_post(self):
        """测试 POST 快捷方法"""
        from df_test_framework.testing.mocking.http_mock import HttpMocker

        mock_client = MagicMock()
        mocker = HttpMocker(mock_client)

        mocker.post("/api/users", json={"id": 1})

        assert len(mocker.middleware.rules) == 1
        assert mocker.middleware.rules[0].method == "POST"
        assert mocker.middleware.rules[0].status_code == 201

    def test_http_mocker_put(self):
        """测试 PUT 快捷方法"""
        from df_test_framework.testing.mocking.http_mock import HttpMocker

        mock_client = MagicMock()
        mocker = HttpMocker(mock_client)

        mocker.put("/api/users/1", json={"name": "Updated"})

        assert len(mocker.middleware.rules) == 1
        assert mocker.middleware.rules[0].method == "PUT"
        assert mocker.middleware.rules[0].status_code == 200

    def test_http_mocker_delete(self):
        """测试 DELETE 快捷方法"""
        from df_test_framework.testing.mocking.http_mock import HttpMocker

        mock_client = MagicMock()
        mocker = HttpMocker(mock_client)

        mocker.delete("/api/users/1")

        assert len(mocker.middleware.rules) == 1
        assert mocker.middleware.rules[0].method == "DELETE"
        assert mocker.middleware.rules[0].status_code == 204

    def test_http_mocker_chaining(self):
        """测试链式调用"""
        from df_test_framework.testing.mocking.http_mock import HttpMocker

        mock_client = MagicMock()
        mocker = HttpMocker(mock_client)

        mocker.get("/api/users").post("/api/users").delete("/api/users/1")

        assert len(mocker.middleware.rules) == 3

    def test_http_mocker_assert_called(self):
        """测试断言调用"""
        from df_test_framework.testing.mocking.http_mock import HttpMocker

        mock_client = MagicMock()
        mocker = HttpMocker(mock_client)

        mock_request = MagicMock()
        mock_request.url = "/api/users"
        mock_request.method = "GET"
        mocker.middleware.matched_requests.append(mock_request)

        # 不应抛出异常
        mocker.assert_called("/api/users", "GET")

    def test_http_mocker_reset(self):
        """测试重置"""
        from df_test_framework.testing.mocking.http_mock import HttpMocker

        mock_client = MagicMock()
        mocker = HttpMocker(mock_client)

        mocker.get("/api/users")
        mocker.middleware.matched_requests.append(MagicMock())

        mocker.reset()

        assert mocker.middleware.rules == []
        assert mocker.middleware.matched_requests == []


@pytest.mark.unit
class TestHttpxMockAvailability:
    """测试 HTTPX Mock 可用性"""

    def test_httpx_mock_available_constant(self):
        """测试 HTTPX_MOCK_AVAILABLE 常量"""
        from df_test_framework.testing.mocking.http_mock import HTTPX_MOCK_AVAILABLE

        assert isinstance(HTTPX_MOCK_AVAILABLE, bool)


@pytest.mark.unit
class TestModuleExports:
    """测试模块导出"""

    def test_all_exports(self):
        """测试 __all__ 导出"""
        from df_test_framework.testing.mocking import http_mock

        expected_exports = [
            "MockRule",
            "MockMiddleware",
            "MockInterceptor",
            "MockResponse",
            "MockResponseException",
            "HttpMocker",
            "HTTPX_MOCK_AVAILABLE",
        ]

        for export in expected_exports:
            assert export in http_mock.__all__, f"Missing export: {export}"
            assert hasattr(http_mock, export), f"Missing attribute: {export}"
