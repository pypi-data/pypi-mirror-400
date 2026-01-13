"""
测试 structlog 日志系统

v3.38.2: 重写，测试新的 structlog 日志系统
v3.38.3: 使用 LoggingConfig 对象
v3.38.5: 新增 structlog 25.5.0 功能测试
    - PositionalArgumentsFormatter
    - ExtraAdder
    - LogfmtRenderer
    - QUAL_NAME (Python 3.11+)
    - orjson 支持
"""

import logging

from df_test_framework.infrastructure.config import LoggingConfig
from df_test_framework.infrastructure.logging import (
    bind_contextvars,
    clear_contextvars,
    configure_logging,
    get_logger,
    is_logger_configured,
    is_orjson_available,
    reset_logging,
)


class TestConfigureLogging:
    """测试 configure_logging 函数"""

    def teardown_method(self):
        """每个测试后重置日志配置"""
        reset_logging()
        clear_contextvars()

    def test_configure_logging_dev_env(self):
        """测试开发环境配置"""
        config = LoggingConfig(level="DEBUG", format="text")
        configure_logging(config)
        assert is_logger_configured()

    def test_configure_logging_prod_env(self):
        """测试生产环境配置"""
        config = LoggingConfig(level="INFO", format="json")
        configure_logging(config)
        assert is_logger_configured()

    def test_configure_logging_with_json_output(self):
        """测试 JSON 输出配置"""
        config = LoggingConfig(level="INFO", format="json")
        configure_logging(config)
        assert is_logger_configured()

    def test_configure_logging_without_sanitize(self):
        """测试禁用脱敏"""
        config = LoggingConfig(level="INFO", sanitize=False)
        configure_logging(config)
        assert is_logger_configured()

    def test_configure_logging_different_levels(self):
        """测试不同的日志级别"""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in levels:
            reset_logging()
            config = LoggingConfig(level=level)
            configure_logging(config)
            assert is_logger_configured()

    # v3.38.5 新增测试
    def test_configure_logging_with_logfmt(self):
        """测试 logfmt 输出格式（v3.38.5 新增）"""
        config = LoggingConfig(level="INFO", format="logfmt")
        configure_logging(config)
        assert is_logger_configured()

        logger = get_logger(__name__)
        # 不应抛出异常
        logger.info("test logfmt output", key="value")

    def test_configure_logging_with_utc(self):
        """测试 UTC 时间戳配置"""
        config = LoggingConfig(level="INFO", use_utc=True)
        configure_logging(config)
        assert is_logger_configured()

    def test_configure_logging_with_callsite(self):
        """测试调用位置信息配置"""
        config = LoggingConfig(level="DEBUG", add_callsite=True)
        configure_logging(config)
        assert is_logger_configured()

        logger = get_logger(__name__)
        # 不应抛出异常
        logger.info("test callsite info")


class TestGetLogger:
    """测试 get_logger 函数"""

    def setup_method(self):
        """每个测试前配置日志"""
        config = LoggingConfig(level="DEBUG")
        configure_logging(config)

    def teardown_method(self):
        """每个测试后重置日志配置"""
        reset_logging()
        clear_contextvars()

    def test_get_logger_with_name(self):
        """测试使用名称获取 logger"""
        logger = get_logger("test_module")
        assert logger is not None

    def test_get_logger_without_name(self):
        """测试不使用名称获取 logger"""
        logger = get_logger()
        assert logger is not None

    def test_logger_methods(self):
        """测试 logger 的各种方法"""
        logger = get_logger(__name__)

        # 这些方法不应抛出异常
        logger.debug("debug message", key="value")
        logger.info("info message", key="value")
        logger.warning("warning message", key="value")
        logger.error("error message", key="value")

    def test_logger_critical(self):
        """测试 critical 级别日志"""
        logger = get_logger(__name__)
        # 不应抛出异常
        logger.critical("critical message", system="database")

    def test_logger_exception(self):
        """测试 exception 方法"""
        logger = get_logger(__name__)
        try:
            raise ValueError("test error")
        except ValueError:
            # 不应抛出异常
            logger.exception("caught exception")

    def test_logger_bind(self):
        """测试 logger.bind()"""
        logger = get_logger(__name__)

        # bind 应返回新的 logger
        bound_logger = logger.bind(request_id="test_123")
        assert bound_logger is not None

        # 绑定的 logger 应能正常使用
        bound_logger.info("bound message")

    def test_logger_implements_protocol(self):
        """测试 logger 实现 Logger Protocol"""
        logger = get_logger(__name__)

        # 检查是否实现了 Logger Protocol 的方法
        assert hasattr(logger, "debug")
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
        assert hasattr(logger, "critical")
        assert hasattr(logger, "exception")
        assert hasattr(logger, "bind")
        assert callable(logger.debug)
        assert callable(logger.info)
        assert callable(logger.warning)
        assert callable(logger.error)
        assert callable(logger.critical)
        assert callable(logger.exception)
        assert callable(logger.bind)


class TestContextVars:
    """测试上下文变量管理"""

    def setup_method(self):
        """每个测试前配置日志"""
        config = LoggingConfig(level="DEBUG")
        configure_logging(config)

    def teardown_method(self):
        """每个测试后重置"""
        reset_logging()
        clear_contextvars()

    def test_bind_contextvars(self):
        """测试绑定上下文变量"""
        bind_contextvars(request_id="req_123", user_id=456)

        # 验证可以正常记录日志（不抛异常）
        logger = get_logger(__name__)
        logger.info("test message")

    def test_clear_contextvars(self):
        """测试清除上下文变量"""
        bind_contextvars(request_id="req_123")
        clear_contextvars()

        # 验证可以正常记录日志（不抛异常）
        logger = get_logger(__name__)
        logger.info("test message after clear")


class TestLoggingIntegration:
    """集成测试：完整的日志配置流程"""

    def teardown_method(self):
        """每个测试后重置"""
        reset_logging()
        clear_contextvars()

    def test_complete_logging_flow(self):
        """测试完整的日志流程"""
        # 1. 配置日志
        config = LoggingConfig(level="DEBUG", sanitize=True)
        configure_logging(config)

        # 2. 获取 logger
        logger = get_logger(__name__)

        # 3. 绑定上下文
        bind_contextvars(request_id="req_abc123")

        # 4. 记录日志
        logger.debug("Debug message", extra_key="value")
        logger.info("Info message", user_id=123)
        logger.warning("Warning message")
        logger.error("Error message", error_code=500)

        # 5. 使用 bind
        request_logger = logger.bind(session_id="sess_456")
        request_logger.info("Bound logger message")

        # 6. 清除上下文
        clear_contextvars()

        # 7. 验证配置状态
        assert is_logger_configured()

    def test_multiple_configure_calls(self):
        """测试多次调用 configure_logging"""
        config1 = LoggingConfig(level="DEBUG")
        configure_logging(config1)
        logger1 = get_logger("test1")

        config2 = LoggingConfig(level="INFO", format="json")
        configure_logging(config2)
        logger2 = get_logger("test2")

        # 两个 logger 都应该可用
        logger1.info("message 1")
        logger2.info("message 2")

    def test_reset_and_reconfigure(self):
        """测试重置后重新配置"""
        # 第一次配置
        config1 = LoggingConfig(level="DEBUG")
        configure_logging(config1)
        assert is_logger_configured()

        # 重置
        reset_logging()
        assert not is_logger_configured()

        # 重新配置
        config2 = LoggingConfig(level="INFO", format="json")
        configure_logging(config2)
        assert is_logger_configured()


class TestSanitization:
    """测试敏感信息脱敏"""

    def setup_method(self):
        """每个测试前配置日志（启用脱敏）"""
        config = LoggingConfig(level="DEBUG", sanitize=True)
        configure_logging(config)

    def teardown_method(self):
        """每个测试后重置"""
        reset_logging()

    def test_sanitize_password_field(self):
        """测试密码字段脱敏"""
        logger = get_logger(__name__)
        # 不应抛出异常
        logger.info("user created", username="alice", password="secret123")

    def test_sanitize_token_field(self):
        """测试 token 字段脱敏"""
        logger = get_logger(__name__)
        # 不应抛出异常
        logger.info("auth success", token="abc123token")

    def test_sanitize_api_key_field(self):
        """测试 api_key 字段脱敏"""
        logger = get_logger(__name__)
        # 不应抛出异常
        logger.info("api call", api_key="key_12345")


class TestFileLogging:
    """测试文件日志功能"""

    def teardown_method(self):
        """每个测试后重置"""
        reset_logging()

    def test_configure_with_file(self, tmp_path):
        """测试配置文件日志"""
        log_file = tmp_path / "test.log"
        config = LoggingConfig(
            level="DEBUG",
            file=str(log_file),
            rotation="1 MB",
            retention="3 days",
        )
        configure_logging(config)

        logger = get_logger(__name__)
        logger.info("test message to file")

        assert is_logger_configured()
        # 注意：由于 structlog 的缓冲，文件可能不会立即写入

    def test_configure_without_console(self, tmp_path):
        """测试禁用控制台输出"""
        log_file = tmp_path / "test.log"
        config = LoggingConfig(
            level="DEBUG",
            file=str(log_file),
            enable_console=False,
        )
        configure_logging(config)

        logger = get_logger(__name__)
        logger.info("test message")

        assert is_logger_configured()


class TestThirdPartyLogIntegration:
    """测试第三方库日志集成（v3.38.5 新增）"""

    def setup_method(self):
        """每个测试前配置日志"""
        config = LoggingConfig(level="DEBUG", format="text")
        configure_logging(config)

    def teardown_method(self):
        """每个测试后重置"""
        reset_logging()

    def test_positional_arguments_formatter(self):
        """测试 PositionalArgumentsFormatter 处理 % 格式化"""
        # 使用标准库 logging 模拟第三方库
        stdlib_logger = logging.getLogger("third_party_lib")

        # 不应抛出异常，% 格式化应该正常工作
        stdlib_logger.info("User %s logged in from %s", "alice", "192.168.1.1")
        stdlib_logger.debug("Processing %d items", 42)

    def test_extra_adder(self):
        """测试 ExtraAdder 处理 extra 参数"""
        stdlib_logger = logging.getLogger("third_party_lib")

        # 不应抛出异常，extra 参数应该被正确处理
        stdlib_logger.info("Request completed", extra={"request_id": "abc123", "duration_ms": 45.5})

    def test_mixed_structlog_and_stdlib(self):
        """测试 structlog 和 stdlib 日志混合使用"""
        # structlog logger
        sl_logger = get_logger("my_app")
        sl_logger.info("Application started", version="1.0.0")

        # stdlib logger（模拟第三方库）
        stdlib_logger = logging.getLogger("httpx")
        stdlib_logger.info("HTTP request: %s %s", "GET", "/api/users")

        # 两者都不应抛出异常


class TestOrjsonSupport:
    """测试 orjson 高性能 JSON 序列化（v3.38.5 新增）"""

    def teardown_method(self):
        """每个测试后重置"""
        reset_logging()

    def test_is_orjson_available(self):
        """测试 is_orjson_available 函数"""
        # 函数应该返回布尔值
        result = is_orjson_available()
        assert isinstance(result, bool)

    def test_json_output_with_orjson(self):
        """测试使用 orjson 的 JSON 输出"""
        config = LoggingConfig(level="DEBUG", format="json", use_orjson=True)
        configure_logging(config)

        logger = get_logger(__name__)
        # 不应抛出异常
        logger.info("test orjson", data={"key": "value", "number": 123})

    def test_json_output_without_orjson(self):
        """测试禁用 orjson 的 JSON 输出"""
        config = LoggingConfig(level="DEBUG", format="json", use_orjson=False)
        configure_logging(config)

        logger = get_logger(__name__)
        # 不应抛出异常
        logger.info("test stdlib json", data={"key": "value", "number": 123})


class TestCallsiteInfo:
    """测试调用位置信息（v3.38.5 新增）"""

    def teardown_method(self):
        """每个测试后重置"""
        reset_logging()

    def test_callsite_with_qual_name(self):
        """测试 QUAL_NAME 调用位置信息"""
        config = LoggingConfig(level="DEBUG", add_callsite=True)
        configure_logging(config)

        logger = get_logger(__name__)
        # 不应抛出异常
        logger.info("test callsite")
        # QUAL_NAME 会包含类名（如果在类方法中）

    def test_callsite_in_class_method(self):
        """测试类方法中的调用位置信息"""
        config = LoggingConfig(level="DEBUG", add_callsite=True)
        configure_logging(config)

        class TestService:
            def __init__(self):
                self.logger = get_logger(__name__)

            def do_something(self):
                # Python 3.11+ 应该显示 TestService.do_something
                self.logger.info("doing something")

        service = TestService()
        service.do_something()  # 不应抛出异常


class TestLogfmtFormat:
    """测试 Logfmt 输出格式（v3.38.5 新增）"""

    def teardown_method(self):
        """每个测试后重置"""
        reset_logging()

    def test_logfmt_basic(self):
        """测试基础 logfmt 输出"""
        config = LoggingConfig(level="DEBUG", format="logfmt")
        configure_logging(config)

        logger = get_logger(__name__)
        # 不应抛出异常
        logger.info("test event", key="value", number=123)

    def test_logfmt_with_special_characters(self):
        """测试 logfmt 处理特殊字符"""
        config = LoggingConfig(level="DEBUG", format="logfmt")
        configure_logging(config)

        logger = get_logger(__name__)
        # 不应抛出异常，特殊字符应该被正确转义
        logger.info("test with spaces", message="hello world", path="/api/users?id=123")

    def test_logfmt_with_context(self):
        """测试 logfmt 与上下文变量"""
        config = LoggingConfig(level="DEBUG", format="logfmt")
        configure_logging(config)

        bind_contextvars(request_id="req_123")

        logger = get_logger(__name__)
        logger.info("test with context", user_id=456)

        clear_contextvars()
