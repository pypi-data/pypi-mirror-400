"""配置管理入口（v3.36.0）

现代化配置管理，遵循以下原则：
- 惰性加载：首次访问时自动初始化
- 单例缓存：使用 lru_cache 确保全局唯一
- 依赖注入友好：可直接用于 pytest fixture
- 类型安全：完整的 Pydantic 验证

使用方式：

    # 1. 最简使用（自动从环境变量/配置文件加载）
    >>> from df_test_framework import get_settings
    >>> settings = get_settings()
    >>> print(settings.http.timeout)
    30

    # 2. 指定环境
    >>> settings = get_settings(env="staging")

    # 3. 点号路径访问
    >>> from df_test_framework import get_config
    >>> timeout = get_config("http.timeout")

    # 4. pytest fixture（推荐）
    >>> @pytest.fixture
    ... def settings():
    ...     return get_settings()

    # 5. 测试中使用自定义配置
    >>> from df_test_framework import FrameworkSettings
    >>> custom = FrameworkSettings(env="test", debug=True)
    >>> # 直接传入函数使用
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, overload

if TYPE_CHECKING:
    from .schema import FrameworkSettings

# 环境变量名
ENV_VAR_NAMES = ("ENV", "APP_ENV", "ENVIRONMENT")
DEFAULT_ENV = "test"
DEFAULT_CONFIG_DIR = "config"


def _detect_env() -> str:
    """从环境变量检测当前环境"""
    for var in ENV_VAR_NAMES:
        if value := os.getenv(var):
            return value.lower()
    return DEFAULT_ENV


def _load_settings[T: "FrameworkSettings"](
    env: str | None = None,
    config_dir: str | Path = DEFAULT_CONFIG_DIR,
    settings_class: type[T] | None = None,
) -> T:
    """加载配置

    优先使用 YAML 配置（如果 config_dir 存在），否则使用 .env 文件。

    Args:
        env: 环境名称（None 时从环境变量检测）
        config_dir: 配置目录
        settings_class: 配置类（默认 FrameworkSettings）

    Returns:
        配置对象
    """
    from .schema import FrameworkSettings as DefaultSettings

    actual_class = settings_class or DefaultSettings
    actual_env = env or _detect_env()
    config_path = Path(config_dir)

    if config_path.exists():
        # YAML 配置模式
        from .loader import load_config

        return load_config(actual_env, config_dir, actual_class)  # type: ignore
    else:
        # .env 文件模式
        return actual_class.for_environment(actual_env)  # type: ignore


@lru_cache(maxsize=1)
def get_settings(
    env: str | None = None,
    config_dir: str | Path = DEFAULT_CONFIG_DIR,
) -> FrameworkSettings:
    """获取配置（惰性加载 + 单例缓存）

    首次调用时加载配置，后续调用返回缓存的实例。

    Args:
        env: 环境名称（None 时从环境变量检测）
        config_dir: 配置目录

    Returns:
        配置对象

    Example:
        >>> settings = get_settings()
        >>> print(settings.http.timeout)
        30
        >>> print(settings.env)
        'test'
    """
    return _load_settings(env, config_dir)


def get_settings_for_class[T: "FrameworkSettings"](
    settings_class: type[T],
    env: str | None = None,
    config_dir: str | Path = DEFAULT_CONFIG_DIR,
) -> T:
    """获取指定类型的配置

    用于项目自定义 Settings 类。

    Args:
        settings_class: 配置类
        env: 环境名称
        config_dir: 配置目录

    Returns:
        配置对象

    Example:
        >>> class MySettings(FrameworkSettings):
        ...     api_key: str = "default"
        >>>
        >>> settings = get_settings_for_class(MySettings)
    """
    return _load_settings(env, config_dir, settings_class)


def clear_settings_cache() -> None:
    """清除配置缓存

    主要用于测试，强制下次调用 get_settings() 重新加载。

    v3.40.1: 脱敏服务缓存在 settings 对象上，随 settings 一起清除，无需额外处理。
    """
    get_settings.cache_clear()


@overload
def get_config(path: str, default: Any = None) -> Any: ...


@overload
def get_config() -> FrameworkSettings: ...


def get_config(path: str = "", default: Any = None) -> Any:
    """便捷函数：按路径获取配置值

    Args:
        path: 配置路径（如 "http.timeout"），空字符串返回完整配置对象
        default: 默认值

    Returns:
        配置值或完整配置对象

    Example:
        >>> # 获取单个值
        >>> timeout = get_config("http.timeout")
        >>> base_url = get_config("http.base_url", "http://localhost")
        >>>
        >>> # 获取完整配置
        >>> settings = get_config()
    """
    settings = get_settings()

    if not path:
        return settings

    # 按点号路径访问
    obj: Any = settings
    for key in path.split("."):
        if hasattr(obj, key):
            obj = getattr(obj, key)
        elif isinstance(obj, dict) and key in obj:
            obj = obj[key]
        else:
            return default
    return obj


# ==================== pytest fixture 支持 ====================


def settings_fixture():
    """用于 pytest 的 settings fixture 工厂

    在 conftest.py 中使用：

        from df_test_framework.infrastructure.config import settings_fixture
        settings = settings_fixture()

    或者直接定义：

        @pytest.fixture
        def settings():
            from df_test_framework import get_settings
            return get_settings()
    """
    import pytest

    @pytest.fixture(scope="session")
    def settings() -> FrameworkSettings:
        return get_settings()

    return settings


__all__ = [
    "get_settings",
    "get_settings_for_class",
    "get_config",
    "clear_settings_cache",
    "settings_fixture",
]
