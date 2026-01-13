"""
测试 Bootstrap 启动流程

验证 Bootstrap 配置构建、BootstrapApp 运行和 RuntimeContext 创建的完整流程。

v3.16.0: Bootstrap、Providers、Runtime 已迁移到 bootstrap/ (Layer 4)
v3.36.0: 使用新的配置 API，移除 namespace/sources 参数
v3.38.2: 移除日志策略模式，使用 configure_logging
"""

from df_test_framework.bootstrap import (
    Bootstrap,
    BootstrapApp,
    ProviderRegistry,
    RuntimeContext,
)
from df_test_framework.infrastructure import (
    FrameworkSettings,
    clear_settings_cache,
)
from df_test_framework.infrastructure.logging import reset_logging
from df_test_framework.infrastructure.plugins import PluggyPluginManager


class CustomSettings(FrameworkSettings):
    """自定义配置类用于测试"""

    custom_field: str = "default_value"


class TestBootstrap:
    """测试 Bootstrap 构建器"""

    def test_default_bootstrap_creation(self):
        """测试创建默认 Bootstrap 实例"""
        bootstrap = Bootstrap()

        assert bootstrap.settings_cls == FrameworkSettings
        assert bootstrap.profile is None
        assert bootstrap.config_dir == "config"
        assert bootstrap.log_level == "INFO"
        assert bootstrap.json_output is None
        assert bootstrap.provider_factory is None
        assert bootstrap.plugins == []

    def test_with_settings(self):
        """测试 with_settings 流式配置"""
        bootstrap = Bootstrap().with_settings(
            CustomSettings,
            profile="dev",
            config_dir="custom_config",
        )

        assert bootstrap.settings_cls == CustomSettings
        assert bootstrap.profile == "dev"
        assert bootstrap.config_dir == "custom_config"

    def test_with_logging(self):
        """测试 with_logging 流式配置"""
        bootstrap = Bootstrap().with_logging(level="DEBUG", json_output=True)

        assert bootstrap.log_level == "DEBUG"
        assert bootstrap.json_output is True

    def test_with_provider_factory(self):
        """测试 with_provider_factory 流式配置"""

        def custom_factory():
            return ProviderRegistry(providers={})

        bootstrap = Bootstrap().with_provider_factory(custom_factory)

        assert bootstrap.provider_factory is custom_factory

    def test_with_plugin(self):
        """测试 with_plugin 流式配置"""
        plugin1 = "path.to.plugin1"
        plugin2 = object()

        bootstrap = Bootstrap().with_plugin(plugin1).with_plugin(plugin2)

        assert len(bootstrap.plugins) == 2
        assert bootstrap.plugins[0] == plugin1
        assert bootstrap.plugins[1] is plugin2

    def test_fluent_chaining(self):
        """测试流式链式调用"""
        bootstrap = (
            Bootstrap()
            .with_settings(CustomSettings, profile="test")
            .with_logging(level="WARNING", json_output=False)
            .with_plugin("plugin1")
            .with_plugin("plugin2")
        )

        assert bootstrap.settings_cls == CustomSettings
        assert bootstrap.profile == "test"
        assert bootstrap.log_level == "WARNING"
        assert bootstrap.json_output is False
        assert len(bootstrap.plugins) == 2

    def test_build_returns_bootstrap_app(self):
        """测试 build 方法返回 BootstrapApp"""
        bootstrap = Bootstrap().with_settings(CustomSettings, profile="test")
        app = bootstrap.build()

        assert isinstance(app, BootstrapApp)
        assert app.settings_cls == CustomSettings
        assert app.profile == "test"


class TestBootstrapApp:
    """测试 BootstrapApp 运行"""

    def setup_method(self):
        """每个测试前清理配置缓存"""
        clear_settings_cache()
        reset_logging()

    def teardown_method(self):
        """每个测试后清理配置缓存"""
        clear_settings_cache()
        reset_logging()

    def test_run_creates_runtime_context(self):
        """测试 run 方法创建 RuntimeContext"""
        app = Bootstrap().with_logging(level="WARNING").build()
        runtime = app.run()

        try:
            assert isinstance(runtime, RuntimeContext)
            assert runtime.settings is not None
            assert runtime.logger is not None
            assert runtime.providers is not None
        finally:
            runtime.close()

    def test_run_with_custom_settings(self, tmp_path):
        """测试使用自定义配置运行"""
        # 创建临时配置目录
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # 创建 base.yaml
        base_yaml = config_dir / "base.yaml"
        base_yaml.write_text(
            "custom_field: test_value\n",
            encoding="utf-8",
        )

        app = (
            Bootstrap()
            .with_settings(CustomSettings, config_dir=config_dir)
            .with_logging(level="WARNING")
            .build()
        )

        runtime = app.run()

        try:
            assert isinstance(runtime.settings, CustomSettings)
            assert runtime.settings.custom_field == "test_value"
        finally:
            runtime.close()

    def test_run_with_force_reload(self):
        """测试 force_reload 强制重新加载配置"""
        app = Bootstrap().with_logging(level="WARNING").build()

        runtime1 = app.run()
        try:
            # 确保第一次运行成功
            assert runtime1.settings is not None
        finally:
            runtime1.close()

        # 第二次运行，使用 force_reload
        runtime2 = app.run(force_reload=True)
        try:
            # force_reload 会清理缓存并重新加载
            assert runtime2.settings is not None
        finally:
            runtime2.close()

    def test_run_initializes_providers(self):
        """测试运行初始化 Providers"""
        app = Bootstrap().with_logging(level="WARNING").build()
        runtime = app.run()

        try:
            assert runtime.providers is not None
            assert isinstance(runtime.providers, ProviderRegistry)
        finally:
            runtime.close()

    def test_run_with_custom_provider_factory(self):
        """测试使用自定义 Provider 工厂"""
        custom_providers_called = []

        def custom_provider_factory():
            custom_providers_called.append(True)
            return ProviderRegistry(providers={})

        app = (
            Bootstrap()
            .with_logging(level="WARNING")
            .with_provider_factory(custom_provider_factory)
            .build()
        )

        runtime = app.run()

        try:
            assert len(custom_providers_called) == 1
            assert runtime.providers is not None
        finally:
            runtime.close()

    def test_run_initializes_extensions(self):
        """测试运行初始化扩展系统"""
        app = Bootstrap().with_logging(level="WARNING").build()
        runtime = app.run()

        try:
            assert runtime.extensions is not None
            assert isinstance(runtime.extensions, PluggyPluginManager)
        finally:
            runtime.close()

    def test_run_with_multiple_plugins(self):
        """测试使用多个插件运行"""

        class MockPlugin:
            def __init__(self, name):
                self.name = name

        plugin1 = MockPlugin("plugin1")
        plugin2 = MockPlugin("plugin2")

        app = (
            Bootstrap()
            .with_logging(level="WARNING")
            .with_plugin(plugin1)
            .with_plugin(plugin2)
            .build()
        )

        runtime = app.run()

        try:
            assert runtime.extensions is not None
        finally:
            runtime.close()


class TestBootstrapIntegration:
    """集成测试：完整的 Bootstrap 流程"""

    def setup_method(self):
        """每个测试前清理"""
        clear_settings_cache()
        reset_logging()

    def teardown_method(self):
        """每个测试后清理"""
        clear_settings_cache()
        reset_logging()

    def test_complete_bootstrap_flow(self, tmp_path):
        """测试完整的 Bootstrap 流程"""
        # 创建临时配置目录
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # 创建 base.yaml
        base_yaml = config_dir / "base.yaml"
        base_yaml.write_text(
            """
app_name: IntegrationTest
app_env: test
custom_field: integration_value
""",
            encoding="utf-8",
        )

        # 构建并运行
        runtime = (
            Bootstrap()
            .with_settings(CustomSettings, config_dir=config_dir)
            .with_logging(level="WARNING")
            .build()
            .run()
        )

        try:
            # 验证 RuntimeContext
            assert isinstance(runtime, RuntimeContext)

            # 验证 Settings
            assert isinstance(runtime.settings, CustomSettings)
            assert runtime.settings.app_name == "IntegrationTest"
            assert runtime.settings.app_env == "test"
            assert runtime.settings.custom_field == "integration_value"

            # 验证 Logger
            assert runtime.logger is not None

            # 验证 Providers
            assert runtime.providers is not None

            # 验证 Extensions
            assert runtime.extensions is not None

        finally:
            runtime.close()

    def test_bootstrap_with_minimal_config(self):
        """测试最小配置的 Bootstrap"""
        runtime = Bootstrap().with_logging(level="WARNING").build().run()

        try:
            assert runtime.settings is not None
            assert runtime.logger is not None
            assert runtime.providers is not None
        finally:
            runtime.close()

    def test_bootstrap_with_profile(self, tmp_path, monkeypatch):
        """测试 Bootstrap 使用 profile 参数"""
        # 切换到临时目录
        monkeypatch.chdir(tmp_path)

        # 创建 .env.dev 文件
        env_dev_path = tmp_path / ".env.dev"
        env_dev_path.write_text("APP_NAME=DevApp\nAPP_ENV=dev", encoding="utf-8")

        # 使用 profile="dev" 启动
        runtime = (
            Bootstrap()
            .with_settings(FrameworkSettings, profile="dev")
            .with_logging(level="WARNING")
            .build()
            .run()
        )

        try:
            # 验证加载了 .env.dev 的配置
            assert runtime.settings.app_name == "DevApp"
            assert runtime.settings.app_env == "dev"
        finally:
            runtime.close()
