"""环境管理 pytest 插件测试

测试 env_plugin.py 模块功能

v3.36.0 - 技术债务清理：提升测试覆盖率
v3.36.0 - 移除 ConfigRegistry，使用现代化 API
"""

import os
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestResolveSettingsClass:
    """测试 _resolve_settings_class 函数"""

    def test_resolve_valid_settings_class(self):
        """测试解析有效的配置类"""
        from df_test_framework.testing.plugins.env_plugin import _resolve_settings_class

        # 使用框架内置的类进行测试
        cls = _resolve_settings_class("df_test_framework.infrastructure.config.FrameworkSettings")

        from df_test_framework.infrastructure.config import FrameworkSettings

        assert cls is FrameworkSettings

    def test_resolve_invalid_path_no_module(self):
        """测试解析无效路径（无模块名）"""
        from df_test_framework.testing.plugins.env_plugin import _resolve_settings_class

        with pytest.raises(RuntimeError, match="无效的配置类路径"):
            _resolve_settings_class("InvalidPath")

    def test_resolve_nonexistent_module(self):
        """测试解析不存在的模块"""
        from df_test_framework.testing.plugins.env_plugin import _resolve_settings_class

        with pytest.raises(ModuleNotFoundError):
            _resolve_settings_class("nonexistent.module.Settings")

    def test_resolve_nonexistent_class(self):
        """测试解析不存在的类"""
        from df_test_framework.testing.plugins.env_plugin import _resolve_settings_class

        with pytest.raises(AttributeError):
            _resolve_settings_class("df_test_framework.infrastructure.config.NonexistentClass")

    def test_resolve_non_settings_subclass(self):
        """测试解析非 FrameworkSettings 子类"""
        from df_test_framework.testing.plugins.env_plugin import _resolve_settings_class

        # Path 不是 FrameworkSettings 的子类
        with pytest.raises(TypeError, match="不是 FrameworkSettings 的子类"):
            _resolve_settings_class("pathlib.Path")


@pytest.mark.unit
class TestGetSettingsClass:
    """测试 _get_settings_class 函数"""

    def test_get_settings_class_from_env(self):
        """测试从环境变量获取配置类"""
        from df_test_framework.testing.plugins.env_plugin import _get_settings_class

        mock_config = MagicMock()
        mock_config.inicfg = {}
        mock_config.getoption.return_value = None

        with patch.dict(
            os.environ,
            {"DF_SETTINGS_CLASS": "df_test_framework.infrastructure.config.FrameworkSettings"},
        ):
            cls = _get_settings_class(mock_config)

        from df_test_framework.infrastructure.config import FrameworkSettings

        assert cls is FrameworkSettings

    def test_get_settings_class_from_cli(self):
        """测试从命令行获取配置类"""
        from df_test_framework.testing.plugins.env_plugin import _get_settings_class

        mock_config = MagicMock()
        mock_config.inicfg = {}
        mock_config.getoption.return_value = (
            "df_test_framework.infrastructure.config.FrameworkSettings"
        )

        with patch.dict(os.environ, {}, clear=True):
            # 移除环境变量
            os.environ.pop("DF_SETTINGS_CLASS", None)
            cls = _get_settings_class(mock_config)

        from df_test_framework.infrastructure.config import FrameworkSettings

        assert cls is FrameworkSettings

    def test_get_settings_class_none(self):
        """测试没有配置时返回 None"""
        from df_test_framework.testing.plugins.env_plugin import _get_settings_class

        mock_config = MagicMock()
        mock_config.inicfg = {}
        mock_config.getoption.return_value = None

        # 确保环境变量不存在
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("DF_SETTINGS_CLASS", None)
            cls = _get_settings_class(mock_config)

        assert cls is None


@pytest.mark.unit
class TestPytestAddoption:
    """测试 pytest_addoption 函数"""

    def test_addoption_env(self):
        """测试添加 --env 选项"""
        from df_test_framework.testing.plugins.env_plugin import pytest_addoption

        mock_parser = MagicMock()

        pytest_addoption(mock_parser)

        # 验证调用了 addoption
        assert mock_parser.addoption.call_count == 2

        # 验证 --env 参数
        calls = mock_parser.addoption.call_args_list
        env_call = calls[0]
        assert env_call[0][0] == "--env"
        assert env_call[1]["default"] is None

    def test_addoption_config_dir(self):
        """测试添加 --config-dir 选项"""
        from df_test_framework.testing.plugins.env_plugin import pytest_addoption

        mock_parser = MagicMock()

        pytest_addoption(mock_parser)

        # 验证 --config-dir 参数
        calls = mock_parser.addoption.call_args_list
        config_dir_call = calls[1]
        assert config_dir_call[0][0] == "--config-dir"
        assert config_dir_call[1]["default"] == "config"


@pytest.mark.unit
class TestPytestReportHeader:
    """测试 pytest_report_header 函数"""

    def test_report_header_with_env(self):
        """测试有环境时的报告头"""
        from df_test_framework.testing.plugins.env_plugin import pytest_report_header

        mock_config = MagicMock()
        mock_config.getoption.side_effect = lambda opt: {
            "--env": "staging",
            "--config-dir": "config",
        }.get(opt)

        headers = pytest_report_header(mock_config)

        assert "环境: staging" in headers

    def test_report_header_without_env(self):
        """测试无环境时的报告头"""
        from df_test_framework.testing.plugins.env_plugin import pytest_report_header

        mock_config = MagicMock()
        mock_config.getoption.side_effect = lambda opt: {
            "--env": None,
            "--config-dir": "config",
        }.get(opt)

        headers = pytest_report_header(mock_config)

        # 不应包含环境信息
        env_headers = [h for h in headers if h.startswith("环境:")]
        assert len(env_headers) == 0

    def test_report_header_dotenv_mode(self):
        """测试 dotenv 模式的报告头"""
        from df_test_framework.testing.plugins.env_plugin import pytest_report_header

        mock_config = MagicMock()
        mock_config.getoption.side_effect = lambda opt: {
            "--env": None,
            "--config-dir": "nonexistent_config",
        }.get(opt)

        headers = pytest_report_header(mock_config)

        assert "配置: .env (dotenv)" in headers


@pytest.mark.unit
class TestPytestConfigure:
    """测试 pytest_configure 函数"""

    def test_configure_sets_env_variable(self):
        """测试配置函数设置环境变量"""
        from df_test_framework.testing.plugins.env_plugin import pytest_configure

        mock_config = MagicMock()
        mock_config.getoption.side_effect = lambda opt, **kw: {
            "--env": "staging",
            "--config-dir": "nonexistent",
            "--df-settings-class": None,
        }.get(opt)
        mock_config.inicfg = {}

        # 确保测试后清理环境变量
        original_env = os.environ.get("ENV")
        try:
            pytest_configure(mock_config)

            # 验证环境变量被设置
            assert os.environ.get("ENV") == "staging"
            # 验证配置对象属性（v3.37.0: 使用 _df_ 前缀）
            assert mock_config._df_env_name == "staging"
            assert mock_config._df_config_dir == "nonexistent"
        finally:
            if original_env is None:
                os.environ.pop("ENV", None)
            else:
                os.environ["ENV"] = original_env

    def test_configure_without_env(self):
        """测试不指定环境时的配置"""
        from df_test_framework.testing.plugins.env_plugin import pytest_configure

        mock_config = MagicMock()
        mock_config.getoption.side_effect = lambda opt, **kw: {
            "--env": None,
            "--config-dir": "nonexistent",
            "--df-settings-class": None,
        }.get(opt)
        mock_config.inicfg = {}

        pytest_configure(mock_config)

        # v3.37.0: 使用 _df_ 前缀
        assert mock_config._df_env_name is None


@pytest.mark.unit
class TestExports:
    """测试模块导出"""

    def test_all_exports(self):
        """测试 __all__ 导出

        v3.36.0: 移除 config_registry，使用现代化 API
        """
        from df_test_framework.testing.plugins import env_plugin

        expected_exports = [
            "pytest_addoption",
            "pytest_configure",
            "pytest_report_header",
            "settings",
            "current_env",
        ]

        for export in expected_exports:
            assert hasattr(env_plugin, export), f"Missing export: {export}"
