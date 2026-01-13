"""
Bootstrap 引导程序 (Layer 4: Bootstrap)

职责:
- Bootstrap: 链式配置 settings、logging、providers、plugins
- BootstrapApp: 执行引导流程，返回 RuntimeContext

v3.16.0 架构重构:
- 从 infrastructure/bootstrap/ 迁移到 bootstrap/
- 作为 Layer 4 可以合法依赖所有层

v3.36.0 现代化重构:
- 使用新的 get_settings_for_class() API
- 移除废弃的 configure_settings/clear_settings

v3.38.2 日志系统重构:
- 移除 LoggerStrategy 模式
- 使用 configure_logging() 配置 structlog
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeVar

from df_test_framework.infrastructure.config import (
    FrameworkSettings,
    clear_settings_cache,
    get_settings_for_class,
)
from df_test_framework.infrastructure.logging import configure_logging, get_logger
from df_test_framework.infrastructure.plugins import PluggyPluginManager

from .providers import ProviderRegistry, default_providers
from .runtime import RuntimeBuilder, RuntimeContext

TSettings = TypeVar("TSettings", bound=FrameworkSettings)


ProviderFactory = Callable[[], ProviderRegistry]


@dataclass
class Bootstrap:
    """Bootstrap 引导器

    链式配置 settings、logging、providers、plugins。

    Example:
        >>> runtime = Bootstrap().with_settings(MySettings, profile="dev").build().run()
    """

    settings_cls: type[FrameworkSettings] = FrameworkSettings
    profile: str | None = None  # 环境配置（dev/test/staging/prod）
    config_dir: str | Path = "config"  # 配置目录
    log_level: str = "INFO"  # 日志级别
    json_output: bool | None = None  # JSON 输出（None=根据环境自动判断）
    provider_factory: ProviderFactory | None = None
    plugins: list[str | object] = field(default_factory=list)

    def with_settings(
        self,
        settings_cls: type[TSettings],
        *,
        profile: str | None = None,
        config_dir: str | Path = "config",
    ) -> Bootstrap:
        """配置 Settings

        Args:
            settings_cls: Settings 类
            profile: 环境配置（dev/test/staging/prod），优先级高于 ENV 环境变量
            config_dir: 配置目录

        Example:
            >>> Bootstrap().with_settings(
            ...     CustomSettings,
            ...     profile="dev",  # 明确指定使用 dev 环境配置
            ... )
        """
        self.settings_cls = settings_cls
        self.profile = profile
        self.config_dir = config_dir
        return self

    def with_logging(self, *, level: str = "INFO", json_output: bool | None = None) -> Bootstrap:
        """配置日志

        Args:
            level: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
            json_output: 是否使用 JSON 输出（None=根据环境自动判断）
        """
        self.log_level = level
        self.json_output = json_output
        return self

    def with_provider_factory(self, factory: ProviderFactory) -> Bootstrap:
        """配置 Provider 工厂"""
        self.provider_factory = factory
        return self

    def with_plugin(self, plugin: str | object) -> Bootstrap:
        """添加插件"""
        self.plugins.append(plugin)
        return self

    def build(self) -> BootstrapApp:
        """构建 BootstrapApp"""
        return BootstrapApp(
            settings_cls=self.settings_cls,
            profile=self.profile,
            config_dir=self.config_dir,
            log_level=self.log_level,
            json_output=self.json_output,
            provider_factory=self.provider_factory,
            plugins=list(self.plugins),
        )


@dataclass
class BootstrapApp:
    """Bootstrap 应用

    执行引导流程，返回 RuntimeContext。
    """

    settings_cls: type[FrameworkSettings]
    profile: str | None
    config_dir: str | Path
    log_level: str
    json_output: bool | None
    provider_factory: ProviderFactory | None
    plugins: list[str | object]

    def run(self, *, force_reload: bool = False) -> RuntimeContext:
        """执行引导流程

        Args:
            force_reload: 是否强制重新加载配置

        Returns:
            RuntimeContext 运行时上下文
        """
        if force_reload:
            clear_settings_cache()

        # 加载插件
        extensions = PluggyPluginManager()
        for plugin in self.plugins:
            if isinstance(plugin, str):
                import importlib

                module = importlib.import_module(plugin)
                extensions.register(module, name=plugin)
            else:
                extensions.register(plugin)
        pm = extensions

        # 加载配置
        settings = get_settings_for_class(
            self.settings_cls,
            env=self.profile,
            config_dir=self.config_dir,
        )

        # 配置日志（v3.38.3: 使用 LoggingConfig 对象）
        logging_config = settings.logging
        if logging_config is not None:
            # 应用 Bootstrap 参数覆盖
            overrides = {}
            if self.log_level != "INFO":
                overrides["level"] = self.log_level
            if self.json_output is not None:
                overrides["format"] = "json" if self.json_output else "text"
            if overrides:
                logging_config = logging_config.model_copy(update=overrides)
            configure_logging(logging_config)
        logger = get_logger("bootstrap")

        # 构建运行时
        builder = RuntimeBuilder().with_settings(settings).with_logger(logger)
        providers_factory = self.provider_factory or default_providers
        providers = providers_factory()

        for contributed in pm.hook.df_providers(settings=settings, logger=logger):
            if contributed:
                providers.extend(contributed)

        builder.with_providers(lambda: providers)
        builder.with_extensions(extensions)
        runtime = builder.build()

        pm.hook.df_post_bootstrap(runtime=runtime)
        return runtime


__all__ = [
    "Bootstrap",
    "BootstrapApp",
]
