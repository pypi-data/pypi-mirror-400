"""
测试 logging_plugin - pytest 日志集成插件

v3.38.9: 新增 captured log handler 替换测试
    - caplog_handler - caplog fixture 使用的 handler
    - report_handler - "Captured log setup/call/teardown" 区域
"""

import logging
from unittest.mock import MagicMock

from df_test_framework.infrastructure.config import LoggingConfig
from df_test_framework.infrastructure.logging import create_processor_formatter


class TestLoggingPluginHandlerReplacement:
    """测试 logging_plugin 的 handler formatter 替换功能"""

    def test_create_processor_formatter_returns_formatter(self):
        """测试 create_processor_formatter 返回有效的 Formatter"""
        config = LoggingConfig(level="DEBUG", format="text")
        formatter = create_processor_formatter(config)

        assert formatter is not None
        assert isinstance(formatter, logging.Formatter)

    def test_processor_formatter_formats_log_record(self):
        """测试 ProcessorFormatter 正确格式化日志记录"""
        config = LoggingConfig(level="DEBUG", format="text")
        formatter = create_processor_formatter(config)

        # 创建一个日志记录
        record = logging.LogRecord(
            name="test.logger",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=10,
            msg="测试消息",
            args=(),
            exc_info=None,
        )

        # 格式化日志记录
        formatted = formatter.format(record)

        # 验证格式化结果包含关键信息
        assert "测试消息" in formatted
        assert "test.logger" in formatted or "test" in formatted

    def test_processor_formatter_handles_extra_fields(self):
        """测试 ProcessorFormatter 处理额外字段"""
        config = LoggingConfig(level="DEBUG", format="text")
        formatter = create_processor_formatter(config)

        # 创建带有额外字段的日志记录
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=20,
            msg="带额外字段的消息",
            args=(),
            exc_info=None,
        )
        record.user_id = "12345"

        # 格式化日志记录
        formatted = formatter.format(record)

        # 验证基本信息存在
        assert "带额外字段的消息" in formatted


class TestLoggingPluginCapturedLogHandlers:
    """测试 v3.38.9 captured log handler 替换功能

    验证 pytest_sessionstart 中对以下 handler 的 formatter 替换：
    - caplog_handler: caplog fixture 使用的 handler
    - report_handler: "Captured log setup/call/teardown" 区域
    """

    def test_caplog_handler_formatter_replacement(self):
        """测试 caplog_handler 的 formatter 被替换为 ProcessorFormatter"""
        from df_test_framework.testing.plugins import logging_plugin

        # 模拟 logging plugin 和 caplog_handler
        mock_logging_plugin = MagicMock()
        mock_caplog_handler = MagicMock(spec=logging.Handler)
        mock_logging_plugin.caplog_handler = mock_caplog_handler

        # 模拟 session 和 config
        mock_session = MagicMock()
        mock_config = MagicMock()
        mock_plugin_manager = MagicMock()
        mock_plugin_manager.get_plugin.return_value = mock_logging_plugin
        mock_session.config = mock_config
        mock_config.pluginmanager = mock_plugin_manager

        # 设置 _logging_config
        config = LoggingConfig(level="DEBUG", format="text")
        logging_plugin._logging_config = config

        # 调用 pytest_sessionstart
        logging_plugin.pytest_sessionstart(mock_session)

        # 验证 caplog_handler 的 setFormatter 被调用
        mock_caplog_handler.setFormatter.assert_called_once()

        # 清理
        logging_plugin._logging_config = None

    def test_report_handler_formatter_replacement(self):
        """测试 report_handler 的 formatter 被替换为 ProcessorFormatter"""
        from df_test_framework.testing.plugins import logging_plugin

        # 模拟 logging plugin 和 report_handler
        mock_logging_plugin = MagicMock()
        mock_report_handler = MagicMock(spec=logging.Handler)
        mock_logging_plugin.report_handler = mock_report_handler
        # 确保其他 handler 为 None
        mock_logging_plugin.caplog_handler = None
        mock_logging_plugin.log_cli_handler = None
        mock_logging_plugin.log_file_handler = None

        # 模拟 session 和 config
        mock_session = MagicMock()
        mock_config = MagicMock()
        mock_plugin_manager = MagicMock()
        mock_plugin_manager.get_plugin.return_value = mock_logging_plugin
        mock_session.config = mock_config
        mock_config.pluginmanager = mock_plugin_manager

        # 设置 _logging_config
        config = LoggingConfig(level="DEBUG", format="text")
        logging_plugin._logging_config = config

        # 调用 pytest_sessionstart
        logging_plugin.pytest_sessionstart(mock_session)

        # 验证 report_handler 的 setFormatter 被调用
        mock_report_handler.setFormatter.assert_called_once()

        # 清理
        logging_plugin._logging_config = None

    def test_all_four_handlers_formatter_replacement(self):
        """测试所有四个 handler 的 formatter 都被替换

        pytest logging plugin 有四个 handler:
        1. log_cli_handler - 实时日志（--log-cli-level）
        2. log_file_handler - 文件日志（--log-file）
        3. caplog_handler - caplog fixture（v3.38.9）
        4. report_handler - Captured log 区域（v3.38.9）
        """
        from df_test_framework.testing.plugins import logging_plugin

        # 模拟所有四个 handler
        mock_logging_plugin = MagicMock()
        mock_log_cli_handler = MagicMock(spec=logging.Handler)
        mock_log_file_handler = MagicMock(spec=logging.Handler)
        mock_caplog_handler = MagicMock(spec=logging.Handler)
        mock_report_handler = MagicMock(spec=logging.Handler)

        mock_logging_plugin.log_cli_handler = mock_log_cli_handler
        mock_logging_plugin.log_file_handler = mock_log_file_handler
        mock_logging_plugin.caplog_handler = mock_caplog_handler
        mock_logging_plugin.report_handler = mock_report_handler

        # 模拟 session 和 config
        mock_session = MagicMock()
        mock_config = MagicMock()
        mock_plugin_manager = MagicMock()
        mock_plugin_manager.get_plugin.return_value = mock_logging_plugin
        mock_session.config = mock_config
        mock_config.pluginmanager = mock_plugin_manager

        # 设置 _logging_config
        config = LoggingConfig(level="DEBUG", format="text")
        logging_plugin._logging_config = config

        # 调用 pytest_sessionstart
        logging_plugin.pytest_sessionstart(mock_session)

        # 验证所有四个 handler 的 setFormatter 都被调用
        mock_log_cli_handler.setFormatter.assert_called_once()
        mock_log_file_handler.setFormatter.assert_called_once()
        mock_caplog_handler.setFormatter.assert_called_once()
        mock_report_handler.setFormatter.assert_called_once()

        # 清理
        logging_plugin._logging_config = None

    def test_missing_handlers_gracefully_handled(self):
        """测试缺少 handler 时不会报错"""
        from df_test_framework.testing.plugins import logging_plugin

        # 模拟没有任何 handler 的 logging plugin
        mock_logging_plugin = MagicMock(spec=[])  # 空规范，没有任何属性

        # 模拟 session 和 config
        mock_session = MagicMock()
        mock_config = MagicMock()
        mock_plugin_manager = MagicMock()
        mock_plugin_manager.get_plugin.return_value = mock_logging_plugin
        mock_session.config = mock_config
        mock_config.pluginmanager = mock_plugin_manager

        # 设置 _logging_config
        config = LoggingConfig(level="DEBUG", format="text")
        logging_plugin._logging_config = config

        # 调用 pytest_sessionstart - 不应抛出异常
        logging_plugin.pytest_sessionstart(mock_session)

        # 清理
        logging_plugin._logging_config = None

    def test_none_handlers_gracefully_handled(self):
        """测试 handler 为 None 时不会报错"""
        from df_test_framework.testing.plugins import logging_plugin

        # 模拟所有 handler 为 None
        mock_logging_plugin = MagicMock()
        mock_logging_plugin.log_cli_handler = None
        mock_logging_plugin.log_file_handler = None
        mock_logging_plugin.caplog_handler = None
        mock_logging_plugin.report_handler = None

        # 模拟 session 和 config
        mock_session = MagicMock()
        mock_config = MagicMock()
        mock_plugin_manager = MagicMock()
        mock_plugin_manager.get_plugin.return_value = mock_logging_plugin
        mock_session.config = mock_config
        mock_config.pluginmanager = mock_plugin_manager

        # 设置 _logging_config
        config = LoggingConfig(level="DEBUG", format="text")
        logging_plugin._logging_config = config

        # 调用 pytest_sessionstart - 不应抛出异常
        logging_plugin.pytest_sessionstart(mock_session)

        # 清理
        logging_plugin._logging_config = None

    def test_no_logging_plugin_gracefully_handled(self):
        """测试没有 logging plugin 时不会报错"""
        from df_test_framework.testing.plugins import logging_plugin

        # 模拟 session 和 config，get_plugin 返回 None
        mock_session = MagicMock()
        mock_config = MagicMock()
        mock_plugin_manager = MagicMock()
        mock_plugin_manager.get_plugin.return_value = None
        mock_session.config = mock_config
        mock_config.pluginmanager = mock_plugin_manager

        # 设置 _logging_config
        config = LoggingConfig(level="DEBUG", format="text")
        logging_plugin._logging_config = config

        # 调用 pytest_sessionstart - 不应抛出异常
        logging_plugin.pytest_sessionstart(mock_session)

        # 清理
        logging_plugin._logging_config = None


class TestLoggingPluginIntegration:
    """集成测试 - 验证 captured log 实际使用 ProcessorFormatter"""

    def test_caplog_uses_processor_formatter(self, caplog):
        """测试 caplog 使用 ProcessorFormatter 格式

        注意: 此测试需要框架 logging_plugin 已加载
        """
        logger = logging.getLogger("test.integration")
        logger.setLevel(logging.DEBUG)

        with caplog.at_level(logging.DEBUG):
            logger.debug("集成测试日志", extra={"user_id": "123"})

        # 验证日志被捕获
        assert len(caplog.records) >= 1

        # 查找我们的测试日志（LogRecord 使用 msg 属性，不是 message）
        test_record = None
        for record in caplog.records:
            # msg 可能是格式化前的消息模板
            if hasattr(record, "msg") and "集成测试日志" in str(record.msg):
                test_record = record
                break

        assert test_record is not None, "未找到测试日志记录"
        assert test_record.levelno == logging.DEBUG

        # 验证 caplog.text 中包含 ProcessorFormatter 格式的输出
        # ProcessorFormatter 格式: 时间戳 [level] 消息 [logger_name] key=value
        assert "集成测试日志" in caplog.text
        assert "test.integration" in caplog.text
