"""配置子系统（v3.36.0 现代化重构）

使用方式：

    # 1. 获取配置（推荐）
    >>> from df_test_framework import get_settings
    >>> settings = get_settings()
    >>> print(settings.http.timeout)

    # 2. 点号路径访问
    >>> from df_test_framework import get_config
    >>> timeout = get_config("http.timeout")

    # 3. 自定义配置类
    >>> from df_test_framework import FrameworkSettings, get_settings_for_class
    >>> class MySettings(FrameworkSettings):
    ...     api_key: str = "default"
    >>> settings = get_settings_for_class(MySettings)

    # 4. pytest fixture（通过 env_plugin 提供）
    >>> def test_example(settings):
    ...     print(settings.http.timeout)

v3.36.0 变更：
- 新增 get_settings() - 惰性加载 + 单例缓存
- 新增 get_config() - 点号路径访问
- 新增 get_settings_for_class() - 自定义配置类
- 删除 manager.py - 废弃的 configure_settings/clear_settings API
- 删除 registry.py - ConfigRegistry 已移除，使用 settings.py API
"""

# ==================== 核心 API（v3.36.0 推荐）====================

# 配置获取
# 配置加载（高级用法）
from .loader import ConfigLoader, LayeredYamlSettingsSource, load_config

# 中间件配置
from .middleware_schema import (
    BearerTokenMiddlewareConfig,
    LoggingMiddlewareConfig,
    MiddlewareConfig,
    MiddlewareConfigUnion,  # v3.39.0
    MiddlewareType,
    RetryMiddlewareConfig,
    RetryStrategy,
    SignatureAlgorithm,
    SignatureMiddlewareConfig,
    TokenSource,
)
from .pipeline import ConfigPipeline

# 配置模型
from .schema import (
    CleanupConfig,
    CleanupMapping,
    DatabaseConfig,
    FrameworkSettings,
    HTTPConfig,
    LoggingConfig,
    ObservabilityConfig,
    PathPattern,
    RedisConfig,
    SanitizeConfig,
    SanitizeContextConfig,
    SanitizeStrategy,
    SignatureConfig,
    StorageConfig,
    TestExecutionConfig,
)
from .settings import (
    clear_settings_cache,
    get_config,
    get_settings,
    get_settings_for_class,
)
from .sources import ConfigSource, DictSource, DotenvSource, EnvVarSource

__all__ = [
    # ==================== 核心 API（推荐）====================
    # 配置获取
    "get_settings",
    "get_settings_for_class",
    "get_config",
    "clear_settings_cache",
    # 配置模型
    "FrameworkSettings",
    "HTTPConfig",
    "DatabaseConfig",
    "RedisConfig",
    "StorageConfig",
    "TestExecutionConfig",
    "LoggingConfig",
    "SanitizeConfig",
    "SanitizeContextConfig",
    "SanitizeStrategy",
    "SignatureConfig",
    "ObservabilityConfig",
    "CleanupConfig",
    "CleanupMapping",
    "PathPattern",
    # 中间件配置
    "MiddlewareConfig",
    "MiddlewareConfigUnion",  # v3.39.0
    "MiddlewareType",
    "SignatureMiddlewareConfig",
    "SignatureAlgorithm",
    "BearerTokenMiddlewareConfig",
    "TokenSource",
    "RetryMiddlewareConfig",
    "RetryStrategy",
    "LoggingMiddlewareConfig",
    # 配置加载（高级）
    "ConfigLoader",
    "LayeredYamlSettingsSource",
    "load_config",
    "ConfigPipeline",
    "ConfigSource",
    "DictSource",
    "EnvVarSource",
    "DotenvSource",
]

# 修复 Pydantic 前向引用问题
FrameworkSettings.model_rebuild()
