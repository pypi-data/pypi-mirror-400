"""
测试 v3.16.0 中间件配置系统

验证:
1. MiddlewareConfig 基类功能
2. 各种具体中间件配置类
3. 路径匹配规则
4. 配置验证
5. v3.39.0: MiddlewareConfigUnion Discriminated Union 解析
6. v3.39.0: TWO_STEP_LOGIN 两步登录配置
"""

import pytest
from pydantic import TypeAdapter

from df_test_framework.infrastructure.config import (
    BearerTokenMiddlewareConfig,
    LoggingMiddlewareConfig,
    MiddlewareConfig,
    MiddlewareConfigUnion,
    MiddlewareType,
    RetryMiddlewareConfig,
    RetryStrategy,
    SignatureAlgorithm,
    SignatureMiddlewareConfig,
    TokenSource,
)


class TestMiddlewareConfig:
    """测试 MiddlewareConfig 基类"""

    def test_middleware_config_defaults(self):
        """测试默认值"""

        class TestMiddleware(MiddlewareConfig):
            type: MiddlewareType = MiddlewareType.LOGGING

        config = TestMiddleware()
        assert config.enabled is True
        assert config.priority == 50
        assert config.include_paths == []
        assert config.exclude_paths == []

    def test_middleware_config_with_paths(self):
        """测试路径配置"""

        class TestMiddleware(MiddlewareConfig):
            type: MiddlewareType = MiddlewareType.LOGGING

        config = TestMiddleware(
            include_paths=["/api/**", "/admin/**"],
            exclude_paths=["/api/health"],
        )
        assert config.include_paths == ["/api/**", "/admin/**"]
        assert config.exclude_paths == ["/api/health"]

    def test_normalize_paths_from_string(self):
        """测试路径标准化 - 从字符串"""

        class TestMiddleware(MiddlewareConfig):
            type: MiddlewareType = MiddlewareType.LOGGING

        config = TestMiddleware(include_paths="/api/**")
        assert config.include_paths == ["/api/**"]


class TestSignatureMiddlewareConfig:
    """测试签名中间件配置"""

    def test_signature_config_basic(self):
        """测试基础配置"""
        config = SignatureMiddlewareConfig(
            algorithm=SignatureAlgorithm.MD5,
            secret="my_secret",
        )
        assert config.type == MiddlewareType.SIGNATURE
        assert config.algorithm == SignatureAlgorithm.MD5
        assert config.secret == "my_secret"
        assert config.header == "X-Sign"
        assert config.enabled is True

    def test_signature_config_with_custom_header(self):
        """测试自定义 Header"""
        config = SignatureMiddlewareConfig(
            algorithm=SignatureAlgorithm.SHA256,
            secret="secret",
            header="Custom-Sign",
        )
        assert config.header == "Custom-Sign"

    def test_signature_config_with_paths(self):
        """测试路径过滤"""
        config = SignatureMiddlewareConfig(
            algorithm=SignatureAlgorithm.HMAC_SHA256,
            secret="secret",
            include_paths=["/master/**", "/h5/**"],
            exclude_paths=["/master/health"],
        )
        assert config.include_paths == ["/master/**", "/h5/**"]
        assert config.exclude_paths == ["/master/health"]


class TestBearerTokenMiddlewareConfig:
    """测试 Bearer Token 中间件配置"""

    def test_static_token_config(self):
        """测试静态 Token 配置"""
        config = BearerTokenMiddlewareConfig(
            source=TokenSource.STATIC,
            token="my_static_token",
        )
        assert config.source == TokenSource.STATIC
        assert config.token == "my_static_token"
        assert config.header == "Authorization"
        assert config.token_prefix == "Bearer"

    def test_login_token_config(self):
        """测试登录获取 Token 配置"""
        config = BearerTokenMiddlewareConfig(
            source=TokenSource.LOGIN,
            login_url="/auth/login",
            credentials={"username": "admin", "password": "pass"},
        )
        assert config.source == TokenSource.LOGIN
        assert config.login_url == "/auth/login"
        assert config.credentials == {"username": "admin", "password": "pass"}

    def test_custom_header_and_prefix(self):
        """测试自定义 Header 和前缀"""
        config = BearerTokenMiddlewareConfig(
            source=TokenSource.STATIC,
            token="token",
            header="X-Auth-Token",
            token_prefix="Token",
        )
        assert config.header == "X-Auth-Token"
        assert config.token_prefix == "Token"


class TestRetryMiddlewareConfig:
    """测试重试中间件配置"""

    def test_retry_config_defaults(self):
        """测试默认配置"""
        config = RetryMiddlewareConfig()
        assert config.type == MiddlewareType.RETRY
        assert config.max_retries == 3
        assert config.strategy == RetryStrategy.EXPONENTIAL
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.retry_on_status == [500, 502, 503, 504]

    def test_retry_config_custom(self):
        """测试自定义配置"""
        config = RetryMiddlewareConfig(
            max_retries=5,
            strategy=RetryStrategy.LINEAR,
            initial_delay=2.0,
            retry_on_status=[500, 502],
        )
        assert config.max_retries == 5
        assert config.strategy == RetryStrategy.LINEAR
        assert config.initial_delay == 2.0
        assert config.retry_on_status == [500, 502]


class TestLoggingMiddlewareConfig:
    """测试日志中间件配置"""

    def test_logging_config_defaults(self):
        """测试默认配置"""
        config = LoggingMiddlewareConfig()
        assert config.type == MiddlewareType.LOGGING
        assert config.log_request is True
        assert config.log_response is True
        assert config.log_headers is False
        assert config.log_body is True
        assert config.mask_fields == ["password", "token", "secret"]
        assert config.max_body_length == 1000

    def test_logging_config_custom(self):
        """测试自定义配置"""
        config = LoggingMiddlewareConfig(
            log_headers=True,
            mask_fields=["password", "api_key"],
            max_body_length=500,
        )
        assert config.log_headers is True
        assert config.mask_fields == ["password", "api_key"]
        assert config.max_body_length == 500


class TestMiddlewarePriority:
    """测试中间件优先级"""

    def test_priority_ordering(self):
        """测试优先级排序"""
        configs = [
            SignatureMiddlewareConfig(
                algorithm=SignatureAlgorithm.MD5,
                secret="s1",
                priority=50,
            ),
            BearerTokenMiddlewareConfig(
                source=TokenSource.STATIC,
                token="t1",
                priority=10,
            ),
            LoggingMiddlewareConfig(priority=100),
        ]

        # 按优先级排序（数字越小越先执行）
        sorted_configs = sorted(configs, key=lambda c: c.priority)
        assert sorted_configs[0].priority == 10
        assert sorted_configs[1].priority == 50
        assert sorted_configs[2].priority == 100


class TestTwoStepLoginConfig:
    """测试 v3.39.0 两步登录配置"""

    def test_two_step_login_basic(self):
        """测试两步登录基本配置"""
        config = BearerTokenMiddlewareConfig(
            source=TokenSource.TWO_STEP_LOGIN,
            login_url="/auth/login",
            check_url="/auth/check",
            credentials={"username": "admin", "password": "pass", "smsCode": "123456"},
        )
        assert config.source == TokenSource.TWO_STEP_LOGIN
        assert config.login_url == "/auth/login"
        assert config.check_url == "/auth/check"
        assert config.credentials == {"username": "admin", "password": "pass", "smsCode": "123456"}
        assert config.token_key == "access_token"  # 默认值
        assert config.status_ok_values == ["ok", "success"]  # 默认值
        assert config.data_field == "data"  # 默认值

    def test_two_step_login_custom_fields(self):
        """测试两步登录自定义字段"""
        config = BearerTokenMiddlewareConfig(
            source=TokenSource.TWO_STEP_LOGIN,
            login_url="/admin/login/token",
            check_url="/admin/login/check",
            credentials={"username": "admin", "password": "pass"},
            check_credentials={"username": "admin"},
            token_key="token",
            status_field="code",
            status_ok_values=["ok"],
            data_field="result",
        )
        assert config.token_key == "token"
        assert config.status_field == "code"
        assert config.status_ok_values == ["ok"]
        assert config.data_field == "result"
        assert config.check_credentials == {"username": "admin"}

    def test_credentials_from_json_string(self):
        """测试 credentials 从 JSON 字符串解析"""
        config = BearerTokenMiddlewareConfig(
            source=TokenSource.TWO_STEP_LOGIN,
            login_url="/auth/login",
            credentials='{"username": "admin", "password": "secret"}',
        )
        assert config.credentials == {"username": "admin", "password": "secret"}


class TestPathsNormalization:
    """测试路径规范化"""

    def test_paths_from_json_string(self):
        """测试 paths 从 JSON 字符串解析"""
        config = LoggingMiddlewareConfig(
            include_paths='["/api/**", "/admin/**"]',
            exclude_paths='["/health"]',
        )
        assert config.include_paths == ["/api/**", "/admin/**"]
        assert config.exclude_paths == ["/health"]

    def test_paths_from_none(self):
        """测试 paths 为 None"""
        config = LoggingMiddlewareConfig(
            include_paths=None,
            exclude_paths=None,
        )
        assert config.include_paths == []
        assert config.exclude_paths == []


class TestMiddlewareConfigUnion:
    """测试 v3.39.0 Discriminated Union 解析"""

    def test_parse_bearer_token_config(self):
        """测试解析 Bearer Token 配置"""
        adapter = TypeAdapter(MiddlewareConfigUnion)
        config = adapter.validate_python(
            {
                "type": "bearer_token",
                "source": "static",
                "token": "my_token",
            }
        )
        assert isinstance(config, BearerTokenMiddlewareConfig)
        assert config.source == TokenSource.STATIC
        assert config.token == "my_token"

    def test_parse_signature_config(self):
        """测试解析签名配置"""
        adapter = TypeAdapter(MiddlewareConfigUnion)
        config = adapter.validate_python(
            {
                "type": "signature",
                "algorithm": "md5",
                "secret": "my_secret",
            }
        )
        assert isinstance(config, SignatureMiddlewareConfig)
        assert config.algorithm == SignatureAlgorithm.MD5
        assert config.secret == "my_secret"

    def test_parse_retry_config(self):
        """测试解析重试配置"""
        adapter = TypeAdapter(MiddlewareConfigUnion)
        config = adapter.validate_python(
            {
                "type": "retry",
                "max_retries": 5,
            }
        )
        assert isinstance(config, RetryMiddlewareConfig)
        assert config.max_retries == 5

    def test_parse_logging_config(self):
        """测试解析日志配置"""
        adapter = TypeAdapter(MiddlewareConfigUnion)
        config = adapter.validate_python(
            {
                "type": "logging",
                "log_headers": True,
            }
        )
        assert isinstance(config, LoggingMiddlewareConfig)
        assert config.log_headers is True

    def test_parse_two_step_login_config(self):
        """测试解析两步登录配置"""
        adapter = TypeAdapter(MiddlewareConfigUnion)
        config = adapter.validate_python(
            {
                "type": "bearer_token",
                "source": "two_step_login",
                "login_url": "/auth/login",
                "check_url": "/auth/check",
                "credentials": {"username": "admin", "password": "pass"},
                "token_key": "access_token",
                "status_ok_values": ["ok"],
            }
        )
        assert isinstance(config, BearerTokenMiddlewareConfig)
        assert config.source == TokenSource.TWO_STEP_LOGIN
        assert config.check_url == "/auth/check"
        assert config.token_key == "access_token"
        assert config.status_ok_values == ["ok"]

    def test_parse_middleware_list(self):
        """测试解析中间件配置列表"""
        adapter = TypeAdapter(list[MiddlewareConfigUnion])
        configs = adapter.validate_python(
            [
                {"type": "bearer_token", "source": "static", "token": "t1"},
                {"type": "signature", "algorithm": "md5", "secret": "s1"},
                {"type": "logging"},
            ]
        )
        assert len(configs) == 3
        assert isinstance(configs[0], BearerTokenMiddlewareConfig)
        assert isinstance(configs[1], SignatureMiddlewareConfig)
        assert isinstance(configs[2], LoggingMiddlewareConfig)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
