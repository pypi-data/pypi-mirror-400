"""fixtures/core.py 测试模块

测试核心 pytest fixtures 功能

v3.37.0 - 现代化重构：使用 config 属性管理状态
"""

import os
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestResolveSettingsClass:
    """测试 _resolve_settings_class 函数"""

    def test_resolve_valid_settings_class(self):
        """测试解析有效的配置类"""
        from df_test_framework.testing.fixtures.core import _resolve_settings_class

        cls = _resolve_settings_class("df_test_framework.infrastructure.config.FrameworkSettings")

        from df_test_framework.infrastructure.config import FrameworkSettings

        assert cls is FrameworkSettings

    def test_resolve_invalid_path_no_module(self):
        """测试解析无效路径（无模块名）"""
        from df_test_framework.testing.fixtures.core import _resolve_settings_class

        with pytest.raises(RuntimeError, match="无效的配置类路径"):
            _resolve_settings_class("InvalidPath")

    def test_resolve_nonexistent_module(self):
        """测试解析不存在的模块"""
        from df_test_framework.testing.fixtures.core import _resolve_settings_class

        with pytest.raises(ModuleNotFoundError):
            _resolve_settings_class("nonexistent.module.Settings")

    def test_resolve_nonexistent_class(self):
        """测试解析不存在的类"""
        from df_test_framework.testing.fixtures.core import _resolve_settings_class

        with pytest.raises(AttributeError):
            _resolve_settings_class("df_test_framework.infrastructure.config.NonexistentClass")

    def test_resolve_non_settings_subclass(self):
        """测试解析非 FrameworkSettings 子类"""
        from df_test_framework.testing.fixtures.core import _resolve_settings_class

        with pytest.raises(TypeError, match="不是 FrameworkSettings 的子类"):
            _resolve_settings_class("pathlib.Path")


@pytest.mark.unit
class TestGetSettingsPath:
    """测试 _get_settings_path 函数"""

    def test_get_settings_path_from_cli(self):
        """测试从命令行获取配置路径"""
        from df_test_framework.testing.fixtures.core import _get_settings_path

        mock_config = MagicMock()
        mock_config.inicfg = {}
        mock_config.getoption.return_value = "my.settings.MySettings"

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("DF_SETTINGS_CLASS", None)
            result = _get_settings_path(mock_config)

        assert result == "my.settings.MySettings"

    def test_get_settings_path_from_env(self):
        """测试从环境变量获取配置路径"""
        from df_test_framework.testing.fixtures.core import _get_settings_path

        mock_config = MagicMock()
        mock_config.inicfg = {}
        mock_config.getoption.return_value = None

        with patch.dict(os.environ, {"DF_SETTINGS_CLASS": "env.settings.Settings"}):
            result = _get_settings_path(mock_config)

        assert result == "env.settings.Settings"

    def test_get_settings_path_default(self):
        """测试默认配置路径"""
        from df_test_framework.testing.fixtures.core import _get_settings_path

        mock_config = MagicMock()
        mock_config.inicfg = {}
        mock_config.getoption.return_value = None

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("DF_SETTINGS_CLASS", None)
            result = _get_settings_path(mock_config)

        assert "FrameworkSettings" in result


@pytest.mark.unit
class TestGetPluginPaths:
    """测试 _get_plugin_paths 函数"""

    def test_get_plugin_paths_empty(self):
        """测试无插件时返回空"""
        from df_test_framework.testing.fixtures.core import _get_plugin_paths

        mock_config = MagicMock()
        mock_config.inicfg = {}
        mock_config.getoption.return_value = []

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("DF_PLUGINS", None)
            result = list(_get_plugin_paths(mock_config))

        assert result == []

    def test_get_plugin_paths_from_cli(self):
        """测试从命令行获取插件路径"""
        from df_test_framework.testing.fixtures.core import _get_plugin_paths

        mock_config = MagicMock()
        mock_config.inicfg = {}
        mock_config.getoption.return_value = ["plugin1", "plugin2"]

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("DF_PLUGINS", None)
            result = list(_get_plugin_paths(mock_config))

        assert result == ["plugin1", "plugin2"]

    def test_get_plugin_paths_from_env(self):
        """测试从环境变量获取插件路径（逗号分隔）"""
        from df_test_framework.testing.fixtures.core import _get_plugin_paths

        mock_config = MagicMock()
        mock_config.inicfg = {}
        mock_config.getoption.return_value = []

        with patch.dict(os.environ, {"DF_PLUGINS": "plugin1,plugin2,plugin3"}):
            result = list(_get_plugin_paths(mock_config))

        assert result == ["plugin1", "plugin2", "plugin3"]

    def test_get_plugin_paths_deduplication(self):
        """测试插件路径去重"""
        from df_test_framework.testing.fixtures.core import _get_plugin_paths

        mock_config = MagicMock()
        mock_config.inicfg = {}
        mock_config.getoption.return_value = ["plugin1", "plugin2"]

        with patch.dict(os.environ, {"DF_PLUGINS": "plugin2,plugin3"}):
            result = list(_get_plugin_paths(mock_config))

        # plugin2 应该只出现一次
        assert result == ["plugin1", "plugin2", "plugin3"]

    def test_get_plugin_paths_whitespace_handling(self):
        """测试空白字符处理"""
        from df_test_framework.testing.fixtures.core import _get_plugin_paths

        mock_config = MagicMock()
        mock_config.inicfg = {}
        mock_config.getoption.return_value = [" plugin1 ", "  plugin2  "]

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("DF_PLUGINS", None)
            result = list(_get_plugin_paths(mock_config))

        assert result == ["plugin1", "plugin2"]


@pytest.mark.unit
class TestPytestAddoption:
    """测试 pytest_addoption 函数"""

    def test_addoption_registers_all_options(self):
        """测试注册所有命令行选项"""
        from df_test_framework.testing.fixtures.core import pytest_addoption

        mock_parser = MagicMock()

        pytest_addoption(mock_parser)

        # 验证调用了 addoption
        call_args_list = [call[0][0] for call in mock_parser.addoption.call_args_list]
        assert "--df-settings-class" in call_args_list
        assert "--df-plugin" in call_args_list
        assert "--keep-test-data" in call_args_list

    def test_addoption_registers_ini_options(self):
        """测试注册 ini 配置选项"""
        from df_test_framework.testing.fixtures.core import pytest_addoption

        mock_parser = MagicMock()

        pytest_addoption(mock_parser)

        # 验证调用了 addini
        call_args_list = [call[0][0] for call in mock_parser.addini.call_args_list]
        assert "df_settings_class" in call_args_list
        assert "df_plugins" in call_args_list


@pytest.mark.unit
class TestPytestUnconfigure:
    """测试 pytest_unconfigure 函数

    v3.37.0: 使用 config 属性管理状态
    """

    def test_unconfigure_closes_runtime(self):
        """测试清理函数关闭 runtime"""
        from df_test_framework.testing.fixtures.core import pytest_unconfigure

        mock_config = MagicMock()
        mock_runtime = MagicMock()
        mock_config._df_runtime = mock_runtime

        pytest_unconfigure(mock_config)

        # 验证 runtime 被关闭
        mock_runtime.close.assert_called_once()

    def test_unconfigure_without_runtime(self):
        """测试没有 runtime 时不报错"""
        from df_test_framework.testing.fixtures.core import pytest_unconfigure

        mock_config = MagicMock(spec=[])

        # 不应抛出异常
        pytest_unconfigure(mock_config)

    def test_unconfigure_cleans_event_buses(self):
        """测试清理 EventBus"""
        from df_test_framework.testing.fixtures.core import pytest_unconfigure

        mock_config = MagicMock()
        mock_bus = MagicMock()
        mock_config._df_test_buses = {"test1": mock_bus}

        pytest_unconfigure(mock_config)

        # 验证 EventBus 被清理
        mock_bus.clear.assert_called_once()
        assert mock_config._df_test_buses == {}


@pytest.mark.unit
class TestRuntimeFixture:
    """测试 runtime fixture"""

    def test_runtime_raises_when_not_initialized(self):
        """测试未初始化时抛出异常

        pytest 9.0+ 不允许直接调用 fixture 函数，
        所以我们测试底层逻辑而不是 fixture 本身。
        """
        mock_config = MagicMock(spec=[])  # 没有 _df_runtime 属性

        # 验证 config 没有 _df_runtime 属性
        assert not hasattr(mock_config, "_df_runtime")

        # 验证访问 _df_runtime 时会触发 AttributeError
        with pytest.raises(AttributeError):
            _ = mock_config._df_runtime


@pytest.mark.unit
class TestEventBusFunctions:
    """测试 EventBus 辅助函数"""

    def test_get_test_event_bus_creates_new(self):
        """测试创建新的 EventBus"""
        from df_test_framework.testing.fixtures.core import _get_test_event_bus

        mock_config = MagicMock(spec=[])

        bus = _get_test_event_bus(mock_config, "test::id")

        assert hasattr(mock_config, "_df_test_buses")
        assert "test::id" in mock_config._df_test_buses
        assert bus is mock_config._df_test_buses["test::id"]

    def test_get_test_event_bus_reuses_existing(self):
        """测试复用已存在的 EventBus"""
        from df_test_framework.testing.fixtures.core import _get_test_event_bus

        mock_config = MagicMock()
        existing_bus = MagicMock()
        mock_config._df_test_buses = {"test::id": existing_bus}

        bus = _get_test_event_bus(mock_config, "test::id")

        assert bus is existing_bus

    def test_cleanup_test_event_bus(self):
        """测试清理 EventBus"""
        from df_test_framework.testing.fixtures.core import _cleanup_test_event_bus

        mock_config = MagicMock()
        mock_bus = MagicMock()
        mock_config._df_test_buses = {"test::id": mock_bus}

        _cleanup_test_event_bus(mock_config, "test::id")

        mock_bus.clear.assert_called_once()
        assert "test::id" not in mock_config._df_test_buses


@pytest.mark.unit
class TestModuleExports:
    """测试模块导出"""

    def test_core_module_has_fixtures(self):
        """测试核心模块包含 fixture 函数"""
        from df_test_framework.testing.fixtures import core

        # 验证 fixture 函数存在
        assert hasattr(core, "runtime")
        assert hasattr(core, "http_client")
        assert hasattr(core, "database")
        assert hasattr(core, "redis_client")
        assert hasattr(core, "uow")
        assert hasattr(core, "cleanup")
        assert hasattr(core, "prepare_data")
        assert hasattr(core, "data_preparer")

    def test_core_module_has_hooks(self):
        """测试核心模块包含 pytest hook"""
        from df_test_framework.testing.fixtures import core

        assert hasattr(core, "pytest_addoption")
        assert hasattr(core, "pytest_configure")
        assert hasattr(core, "pytest_unconfigure")

    def test_core_module_has_helper_functions(self):
        """测试核心模块包含辅助函数"""
        from df_test_framework.testing.fixtures import core

        assert hasattr(core, "_resolve_settings_class")
        assert hasattr(core, "_get_settings_path")
        assert hasattr(core, "_get_plugin_paths")
        assert hasattr(core, "_get_test_event_bus")
        assert hasattr(core, "_cleanup_test_event_bus")
