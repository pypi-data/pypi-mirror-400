"""API 自动发现 pytest 插件测试

测试 api_autodiscovery.py 模块功能

v3.36.0 - 技术债务清理：提升测试覆盖率
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestPytestConfigure:
    """测试 pytest_configure 函数"""

    def test_configure_registers_plugin(self):
        """测试配置函数注册插件"""
        from df_test_framework.testing.plugins.api_autodiscovery import pytest_configure

        mock_config = MagicMock()
        mock_pluginmanager = MagicMock()
        mock_config.pluginmanager = mock_pluginmanager

        pytest_configure(mock_config)

        # 验证插件被注册
        mock_pluginmanager.register.assert_called_once()
        call_args = mock_pluginmanager.register.call_args
        assert (
            call_args[1] == {"name": "api_autodiscovery"} or call_args[0][1] == "api_autodiscovery"
        )


@pytest.mark.unit
class TestAPIAutoDiscoveryPlugin:
    """测试 APIAutoDiscoveryPlugin 类"""

    def test_plugin_class_exists(self):
        """测试插件类存在"""
        from df_test_framework.testing.plugins.api_autodiscovery import (
            APIAutoDiscoveryPlugin,
        )

        plugin = APIAutoDiscoveryPlugin()

        # 验证类可实例化
        assert plugin is not None

    def test_plugin_has_registry_fixture_method(self):
        """测试插件有 _api_registry_loaded 方法"""
        from df_test_framework.testing.plugins.api_autodiscovery import (
            APIAutoDiscoveryPlugin,
        )

        plugin = APIAutoDiscoveryPlugin()

        # 验证 fixture 方法存在（是个方法，不能直接调用因为是 fixture）
        assert hasattr(plugin, "_api_registry_loaded")
        assert callable(getattr(plugin, "_api_registry_loaded"))


@pytest.mark.unit
class TestPytestGenerateTests:
    """测试 pytest_generate_tests 函数"""

    def test_generate_tests_with_empty_registry(self):
        """测试空注册表时的行为"""
        from df_test_framework.testing.plugins.api_autodiscovery import (
            pytest_generate_tests,
        )

        mock_metafunc = MagicMock()
        mock_metafunc.fixturenames = ["some_fixture", "another_fixture"]

        # 模拟 _api_registry 从 decorators 模块导入
        with patch("df_test_framework.testing.decorators.api_class._api_registry", {}):
            # 应该不抛出异常
            pytest_generate_tests(mock_metafunc)

    def test_generate_tests_with_registered_api(self):
        """测试有注册 API 时的行为"""
        from df_test_framework.testing.plugins.api_autodiscovery import (
            pytest_generate_tests,
        )

        mock_metafunc = MagicMock()
        mock_metafunc.fixturenames = ["user_api", "other_fixture"]

        # 模拟注册的 API
        mock_registry = {"user_api": MagicMock()}

        with patch(
            "df_test_framework.testing.decorators.api_class._api_registry",
            mock_registry,
        ):
            # 应该不抛出异常
            pytest_generate_tests(mock_metafunc)


@pytest.mark.unit
class TestRegisterApiFixtures:
    """测试 register_api_fixtures 函数"""

    def test_register_api_fixtures_function_exists(self):
        """测试 register_api_fixtures 函数存在"""
        from df_test_framework.testing.plugins.api_autodiscovery import (
            register_api_fixtures,
        )

        assert callable(register_api_fixtures)

    def test_register_api_fixtures_raises_when_create_api_fixtures_missing(self):
        """测试当 create_api_fixtures 不存在时会抛出异常

        注意: create_api_fixtures 目前未实现，调用 register_api_fixtures 会失败
        """
        from df_test_framework.testing.plugins.api_autodiscovery import (
            register_api_fixtures,
        )

        mock_config = MagicMock()

        # 应该抛出 ImportError 因为 create_api_fixtures 不存在
        with pytest.raises(ImportError):
            register_api_fixtures(mock_config)


@pytest.mark.unit
class TestExports:
    """测试模块导出"""

    def test_all_exports(self):
        """测试 __all__ 导出"""
        from df_test_framework.testing.plugins import api_autodiscovery

        expected_exports = [
            "pytest_configure",
            "pytest_generate_tests",
            "register_api_fixtures",
        ]

        for export in expected_exports:
            assert hasattr(api_autodiscovery, export), f"Missing export: {export}"

    def test_api_autodiscovery_plugin_class(self):
        """测试 APIAutoDiscoveryPlugin 类可导入"""
        from df_test_framework.testing.plugins.api_autodiscovery import (
            APIAutoDiscoveryPlugin,
        )

        assert APIAutoDiscoveryPlugin is not None
