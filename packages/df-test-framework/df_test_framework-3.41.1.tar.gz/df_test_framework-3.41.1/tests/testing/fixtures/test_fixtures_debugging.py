"""fixtures/debugging.py 测试模块

测试调试相关 pytest fixtures 功能

v3.36.0 - 技术债务清理：提升测试覆盖率
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestIsGlobalDebugEnabled:
    """测试 _is_global_debug_enabled 函数"""

    def test_returns_false_when_settings_none(self):
        """测试 settings 为 None 时返回 False"""
        from df_test_framework.testing.fixtures import debugging

        # Mock 在实际导入的位置
        with patch(
            "df_test_framework.infrastructure.config.get_settings",
            return_value=None,
        ):
            result = debugging._is_global_debug_enabled()
            assert result is False

    def test_returns_false_when_no_observability(self):
        """测试没有 observability 配置时返回 False"""
        from df_test_framework.testing.fixtures import debugging

        mock_settings = MagicMock()
        mock_settings.observability = None

        with patch(
            "df_test_framework.infrastructure.config.get_settings",
            return_value=mock_settings,
        ):
            result = debugging._is_global_debug_enabled()
            assert result is False

    def test_returns_false_when_observability_disabled(self):
        """测试 observability 总开关关闭时返回 False"""
        from df_test_framework.testing.fixtures import debugging

        mock_settings = MagicMock()
        mock_settings.observability.enabled = False

        with patch(
            "df_test_framework.infrastructure.config.get_settings",
            return_value=mock_settings,
        ):
            result = debugging._is_global_debug_enabled()
            assert result is False

    def test_returns_debug_output_value_when_enabled(self):
        """测试 observability 启用时返回 debug_output 值"""
        from df_test_framework.testing.fixtures import debugging

        mock_settings = MagicMock()
        mock_settings.observability.enabled = True
        mock_settings.observability.debug_output = True

        with patch(
            "df_test_framework.infrastructure.config.get_settings",
            return_value=mock_settings,
        ):
            result = debugging._is_global_debug_enabled()
            assert result is True

    def test_returns_false_on_exception(self):
        """测试发生异常时返回 False"""
        from df_test_framework.testing.fixtures import debugging

        with patch(
            "df_test_framework.infrastructure.config.get_settings",
            side_effect=Exception("Config error"),
        ):
            result = debugging._is_global_debug_enabled()
            assert result is False


@pytest.mark.unit
class TestShowSFlagHint:
    """测试 _show_s_flag_hint 函数"""

    def test_hint_shown_only_once(self):
        """测试提示只显示一次"""
        from df_test_framework.testing.fixtures import debugging

        # 重置状态
        debugging._s_flag_hint_shown = False

        with (
            patch("sys.stderr") as mock_stderr,
            patch.object(debugging, "logger") as mock_logger,
        ):
            mock_stderr.isatty.return_value = False

            # 第一次调用
            debugging._show_s_flag_hint()
            assert mock_logger.warning.call_count == 1

            # 第二次调用 - 不应再次提示
            debugging._show_s_flag_hint()
            assert mock_logger.warning.call_count == 1

        # 恢复状态
        debugging._s_flag_hint_shown = False

    def test_no_hint_when_tty(self):
        """测试 TTY 时不显示提示"""
        from df_test_framework.testing.fixtures import debugging

        debugging._s_flag_hint_shown = False

        with (
            patch("sys.stderr") as mock_stderr,
            patch.object(debugging, "logger") as mock_logger,
        ):
            mock_stderr.isatty.return_value = True

            debugging._show_s_flag_hint()

            mock_logger.warning.assert_not_called()

        debugging._s_flag_hint_shown = False


@pytest.mark.unit
class TestCreateConsoleDebugger:
    """测试 _create_console_debugger 函数"""

    def test_creates_debugger_with_default_options(self):
        """测试使用默认选项创建调试器"""
        from df_test_framework.testing.fixtures import debugging

        with (
            patch.object(debugging, "_show_s_flag_hint"),
            patch(
                "df_test_framework.infrastructure.events.get_event_bus",
                return_value=MagicMock(),
            ),
            patch("df_test_framework.testing.debugging.ConsoleDebugObserver") as mock_cls,
        ):
            mock_debugger = MagicMock()
            mock_cls.return_value = mock_debugger

            result = debugging._create_console_debugger()

            assert result is mock_debugger
            mock_cls.assert_called_once()
            call_kwargs = mock_cls.call_args[1]
            assert call_kwargs["show_headers"] is True
            assert call_kwargs["show_body"] is True
            assert call_kwargs["show_database"] is True
            assert call_kwargs["show_sql"] is True

    def test_subscribes_to_event_bus(self):
        """测试订阅 EventBus"""
        from df_test_framework.testing.fixtures import debugging

        mock_event_bus = MagicMock()
        mock_debugger = MagicMock()

        with (
            patch.object(debugging, "_show_s_flag_hint"),
            patch(
                "df_test_framework.infrastructure.events.get_event_bus",
                return_value=mock_event_bus,
            ),
            patch(
                "df_test_framework.testing.debugging.ConsoleDebugObserver",
                return_value=mock_debugger,
            ),
        ):
            debugging._create_console_debugger()

            mock_debugger.subscribe.assert_called_once_with(mock_event_bus)

    def test_no_subscribe_when_no_event_bus(self):
        """测试没有 EventBus 时不订阅"""
        from df_test_framework.testing.fixtures import debugging

        mock_debugger = MagicMock()

        with (
            patch.object(debugging, "_show_s_flag_hint"),
            patch(
                "df_test_framework.infrastructure.events.get_event_bus",
                return_value=None,
            ),
            patch(
                "df_test_framework.testing.debugging.ConsoleDebugObserver",
                return_value=mock_debugger,
            ),
        ):
            debugging._create_console_debugger()

            mock_debugger.subscribe.assert_not_called()


@pytest.mark.unit
class TestConsoleDebuggerFixture:
    """测试 console_debugger fixture"""

    def test_fixture_exists(self):
        """测试 fixture 存在"""
        from df_test_framework.testing.fixtures import debugging

        assert hasattr(debugging, "console_debugger")
        assert callable(debugging.console_debugger)

    def test_fixture_is_pytest_fixture(self):
        """测试是 pytest fixture"""
        from df_test_framework.testing.fixtures import debugging

        func_repr = repr(debugging.console_debugger)
        assert "pytest_fixture" in func_repr or "fixture" in func_repr.lower()


@pytest.mark.unit
class TestAutoDebugByMarkerFixture:
    """测试 _auto_debug_by_marker fixture"""

    def test_fixture_exists(self):
        """测试 fixture 存在"""
        from df_test_framework.testing.fixtures import debugging

        assert hasattr(debugging, "_auto_debug_by_marker")

    def test_fixture_is_autouse(self):
        """测试是 autouse fixture"""
        from pathlib import Path

        import df_test_framework.testing.fixtures

        fixtures_path = Path(df_test_framework.testing.fixtures.__file__).parent
        debugging_path = fixtures_path / "debugging.py"

        content = debugging_path.read_text(encoding="utf-8")

        # 检查 autouse=True
        assert "autouse=True" in content


@pytest.mark.unit
class TestDebugModeFixture:
    """测试 debug_mode fixture"""

    def test_fixture_exists(self):
        """测试 fixture 存在"""
        from df_test_framework.testing.fixtures import debugging

        assert hasattr(debugging, "debug_mode")
        assert callable(debugging.debug_mode)


@pytest.mark.unit
class TestModuleExports:
    """测试模块导出"""

    def test_all_exports(self):
        """测试 __all__ 导出"""
        from df_test_framework.testing.fixtures import debugging

        expected_exports = ["console_debugger", "debug_mode"]

        for export in expected_exports:
            assert export in debugging.__all__, f"Missing export: {export}"
            assert hasattr(debugging, export), f"Missing attribute: {export}"
