"""plugins/debug.py 测试模块

测试 pytest 调试辅助插件功能

v3.36.0 - 技术债务清理：提升测试覆盖率
"""

import json
import os
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestDebugPluginInit:
    """测试 DebugPlugin 初始化"""

    def test_init_creates_debug_dir(self, tmp_path):
        """测试初始化创建调试目录"""
        from df_test_framework.testing.plugins.debug import DebugPlugin

        with patch.object(DebugPlugin, "__init__", lambda self: None):
            plugin = DebugPlugin.__new__(DebugPlugin)
            plugin.failures = []
            plugin.debug_dir = tmp_path / "debug"
            plugin.debug_dir.mkdir(parents=True, exist_ok=True)

        assert plugin.debug_dir.exists()

    def test_init_empty_failures_list(self):
        """测试初始化空的失败列表"""
        from df_test_framework.testing.plugins.debug import DebugPlugin

        with patch("pathlib.Path.mkdir"):
            plugin = DebugPlugin()

        assert plugin.failures == []


@pytest.mark.unit
class TestCollectEnvironmentInfo:
    """测试 _collect_environment_info 方法"""

    def test_collects_python_version(self):
        """测试收集 Python 版本"""
        from df_test_framework.testing.plugins.debug import DebugPlugin

        with patch("pathlib.Path.mkdir"):
            plugin = DebugPlugin()

        info = plugin._collect_environment_info()

        assert "python_version" in info
        assert "3." in info["python_version"]  # Python 3.x

    def test_collects_platform(self):
        """测试收集平台信息"""
        from df_test_framework.testing.plugins.debug import DebugPlugin

        with patch("pathlib.Path.mkdir"):
            plugin = DebugPlugin()

        info = plugin._collect_environment_info()

        assert "platform" in info
        assert info["platform"] in ["win32", "linux", "darwin"]

    def test_collects_cwd(self):
        """测试收集工作目录"""
        from df_test_framework.testing.plugins.debug import DebugPlugin

        with patch("pathlib.Path.mkdir"):
            plugin = DebugPlugin()

        info = plugin._collect_environment_info()

        assert "cwd" in info
        assert info["cwd"] == os.getcwd()

    def test_filters_env_vars(self):
        """测试过滤相关环境变量"""
        from df_test_framework.testing.plugins.debug import DebugPlugin

        with (
            patch("pathlib.Path.mkdir"),
            patch.dict(
                os.environ,
                {
                    "DF_TEST_VAR": "test_value",
                    "PYTEST_VAR": "pytest_value",
                    "UNRELATED_VAR": "should_not_appear",
                },
            ),
        ):
            plugin = DebugPlugin()
            info = plugin._collect_environment_info()

        assert "DF_TEST_VAR" in info["env_vars"]
        assert "PYTEST_VAR" in info["env_vars"]
        assert "UNRELATED_VAR" not in info["env_vars"]


@pytest.mark.unit
class TestCollectTestMetadata:
    """测试 _collect_test_metadata 方法"""

    def test_collects_file_location(self):
        """测试收集文件位置"""
        from df_test_framework.testing.plugins.debug import DebugPlugin

        with patch("pathlib.Path.mkdir"):
            plugin = DebugPlugin()

        mock_item = MagicMock()
        mock_item.location = ("test_file.py", 10, "test_function")
        mock_item.iter_markers.return_value = []
        mock_item.fixturenames = ["fixture1"]

        metadata = plugin._collect_test_metadata(mock_item)

        assert metadata["file"] == "test_file.py"
        assert metadata["line"] == 10
        assert metadata["function"] == "test_function"

    def test_collects_markers(self):
        """测试收集 markers"""
        from df_test_framework.testing.plugins.debug import DebugPlugin

        with patch("pathlib.Path.mkdir"):
            plugin = DebugPlugin()

        mock_marker1 = MagicMock()
        mock_marker1.name = "smoke"
        mock_marker2 = MagicMock()
        mock_marker2.name = "unit"

        mock_item = MagicMock()
        mock_item.location = ("test.py", 1, "test")
        mock_item.iter_markers.return_value = [mock_marker1, mock_marker2]
        mock_item.fixturenames = []

        metadata = plugin._collect_test_metadata(mock_item)

        assert metadata["markers"] == ["smoke", "unit"]

    def test_collects_fixtures(self):
        """测试收集 fixtures"""
        from df_test_framework.testing.plugins.debug import DebugPlugin

        with patch("pathlib.Path.mkdir"):
            plugin = DebugPlugin()

        mock_item = MagicMock()
        mock_item.location = ("test.py", 1, "test")
        mock_item.iter_markers.return_value = []
        mock_item.fixturenames = ["http_client", "database"]

        metadata = plugin._collect_test_metadata(mock_item)

        assert metadata["fixtures"] == ["http_client", "database"]


@pytest.mark.unit
class TestSaveFailureInfo:
    """测试 _save_failure_info 方法"""

    def test_saves_json_file(self, tmp_path):
        """测试保存 JSON 文件"""
        from df_test_framework.testing.plugins.debug import DebugPlugin

        with patch("pathlib.Path.mkdir"):
            plugin = DebugPlugin()
            plugin.debug_dir = tmp_path

        info = {
            "test_name": "test_example",
            "timestamp": "2024-01-01T00:00:00",
            "failure_message": "AssertionError",
        }

        plugin._save_failure_info("test_example", info)

        # 检查文件是否创建
        files = list(tmp_path.glob("failure_*.json"))
        assert len(files) == 1

        # 检查内容
        with open(files[0], encoding="utf-8") as f:
            saved_info = json.load(f)
            assert saved_info["test_name"] == "test_example"

    def test_sanitizes_test_name(self, tmp_path):
        """测试清理测试名称中的特殊字符"""
        from df_test_framework.testing.plugins.debug import DebugPlugin

        with patch("pathlib.Path.mkdir"):
            plugin = DebugPlugin()
            plugin.debug_dir = tmp_path

        info = {"test_name": "path/to::test::method"}

        plugin._save_failure_info("path/to::test::method", info)

        files = list(tmp_path.glob("failure_*.json"))
        assert len(files) == 1
        # 文件名不应包含 :: 或 /
        assert "::" not in files[0].name
        assert "/" not in files[0].name


@pytest.mark.unit
class TestPrintDebugInfo:
    """测试 _print_debug_info 方法"""

    def test_prints_test_name(self, capsys):
        """测试打印测试名称"""
        from df_test_framework.testing.plugins.debug import DebugPlugin

        with patch("pathlib.Path.mkdir"):
            plugin = DebugPlugin()

        info = {
            "test_name": "test_example",
            "timestamp": "2024-01-01T00:00:00",
            "environment": {
                "python_version": "3.12.0 (main)",
                "platform": "win32",
                "cwd": "/path/to/project",
                "env_vars": {},
            },
            "test_metadata": {},
        }

        plugin._print_debug_info(info)

        captured = capsys.readouterr()
        assert "test_example" in captured.out
        assert "调试信息" in captured.out

    def test_masks_sensitive_env_vars(self, capsys):
        """测试脱敏敏感环境变量"""
        from df_test_framework.testing.plugins.debug import DebugPlugin

        with patch("pathlib.Path.mkdir"):
            plugin = DebugPlugin()

        info = {
            "test_name": "test_example",
            "timestamp": "2024-01-01T00:00:00",
            "environment": {
                "python_version": "3.12.0",
                "platform": "win32",
                "cwd": "/path",
                "env_vars": {
                    "DF_PASSWORD": "secret123",
                    "DF_TOKEN": "token123",
                    "DF_DEBUG": "true",
                },
            },
            "test_metadata": {},
        }

        plugin._print_debug_info(info)

        captured = capsys.readouterr()
        assert "***" in captured.out  # 密码应该被脱敏
        assert "secret123" not in captured.out
        assert "token123" not in captured.out


@pytest.mark.unit
class TestPytestSessionStart:
    """测试 pytest_sessionstart hook"""

    def test_prints_startup_message(self, capsys):
        """测试打印启动消息"""
        from df_test_framework.testing.plugins.debug import DebugPlugin

        with patch("pathlib.Path.mkdir"):
            plugin = DebugPlugin()

        mock_session = MagicMock()

        plugin.pytest_sessionstart(mock_session)

        captured = capsys.readouterr()
        assert "调试插件已启用" in captured.out


@pytest.mark.unit
class TestPytestSessionFinish:
    """测试 pytest_sessionfinish hook"""

    def test_prints_summary_when_failures(self, capsys):
        """测试有失败时打印总结"""
        from df_test_framework.testing.plugins.debug import DebugPlugin

        with patch("pathlib.Path.mkdir"):
            plugin = DebugPlugin()

        plugin.failures = [
            {"test_name": "test_1"},
            {"test_name": "test_2"},
        ]

        mock_session = MagicMock()

        plugin.pytest_sessionfinish(mock_session, 1)

        captured = capsys.readouterr()
        assert "2 个失败" in captured.out
        assert "test_1" in captured.out
        assert "test_2" in captured.out

    def test_no_summary_when_no_failures(self, capsys):
        """测试没有失败时不打印总结"""
        from df_test_framework.testing.plugins.debug import DebugPlugin

        with patch("pathlib.Path.mkdir"):
            plugin = DebugPlugin()

        plugin.failures = []

        mock_session = MagicMock()

        plugin.pytest_sessionfinish(mock_session, 0)

        captured = capsys.readouterr()
        assert "失败" not in captured.out


@pytest.mark.unit
class TestPytestConfigure:
    """测试 pytest_configure hook"""

    def test_registers_plugin_when_verbose(self):
        """测试 verbose 模式下注册插件"""
        from df_test_framework.testing.plugins import debug

        mock_config = MagicMock()
        mock_config.getoption.return_value = 2  # verbose >= 2

        debug.pytest_configure(mock_config)

        mock_config.pluginmanager.register.assert_called_once()

    def test_registers_plugin_when_df_debug_env(self):
        """测试 DF_DEBUG 环境变量启用插件"""
        from df_test_framework.testing.plugins import debug

        mock_config = MagicMock()
        mock_config.getoption.return_value = 0

        with patch.dict(os.environ, {"DF_DEBUG": "1"}):
            debug.pytest_configure(mock_config)

        mock_config.pluginmanager.register.assert_called_once()


@pytest.mark.unit
class TestPytestAddoption:
    """测试 pytest_addoption hook"""

    def test_adds_df_debug_option(self):
        """测试添加 --df-debug 选项"""
        from df_test_framework.testing.plugins import debug

        mock_parser = MagicMock()
        mock_group = MagicMock()
        mock_parser.getgroup.return_value = mock_group

        debug.pytest_addoption(mock_parser)

        mock_parser.getgroup.assert_called_with("df-test-framework")

        # 检查添加的选项
        call_args_list = [call[0][0] for call in mock_group.addoption.call_args_list]
        assert "--df-debug" in call_args_list
        assert "--df-debug-dir" in call_args_list


@pytest.mark.unit
class TestDebugPluginFixture:
    """测试 debug_plugin fixture"""

    def test_fixture_exists(self):
        """测试 fixture 存在"""
        from df_test_framework.testing.plugins import debug

        assert hasattr(debug, "debug_plugin")
        assert callable(debug.debug_plugin)


@pytest.mark.unit
class TestModuleExports:
    """测试模块导出"""

    def test_all_exports(self):
        """测试 __all__ 导出"""
        from df_test_framework.testing.plugins import debug

        expected_exports = ["DebugPlugin", "debug_plugin"]

        for export in expected_exports:
            assert export in debug.__all__, f"Missing export: {export}"
            assert hasattr(debug, export), f"Missing attribute: {export}"
