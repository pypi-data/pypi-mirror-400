"""环境管理 pytest 插件

v3.37.0: 现代化重构
- 使用 pytest11 Entry Points 自动发现
- 使用 config 对象属性管理状态
- 简化配置加载流程

提供环境配置管理，支持:
- --env 参数指定运行环境
- --config-dir 参数指定配置目录
- YAML 分层配置（优先）或 .env 文件（回退）

使用方式:
    # 方式1: pip install df-test-framework 后自动加载（推荐）

    # 方式2: 手动声明（向后兼容）
    pytest_plugins = ["df_test_framework.testing.plugins.env_plugin"]

    # 命令行使用
    pytest tests/ --env=staging
    pytest tests/ --env=prod --config-dir=my_config

配置加载优先级（从高到低）:
    1. 环境变量
    2. config/secrets/.env.local
    3. config/environments/{env}.yaml
    4. config/base.yaml
    5. .env + .env.{env}（回退模式）
    6. 代码默认值
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pytest import hookimpl

if TYPE_CHECKING:
    from df_test_framework.infrastructure.config import FrameworkSettings


def _resolve_settings_class(path: str) -> type:
    """解析配置类路径"""
    import importlib

    from df_test_framework.infrastructure.config import FrameworkSettings

    module_name, _, class_name = path.rpartition(".")
    if not module_name:
        raise RuntimeError(f"无效的配置类路径: {path!r}")
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    if not issubclass(cls, FrameworkSettings):
        raise TypeError(f"{path!r} 不是 FrameworkSettings 的子类")
    return cls


def _get_settings_class(config: pytest.Config) -> type | None:
    """获取项目配置类"""
    ini_value = config.getini("df_settings_class") if "df_settings_class" in config.inicfg else None
    cli_value = config.getoption("--df-settings-class", default=None)
    env_value = os.getenv("DF_SETTINGS_CLASS")

    settings_path = cli_value or ini_value or env_value

    if settings_path:
        return _resolve_settings_class(settings_path)
    return None


def pytest_addoption(parser: pytest.Parser) -> None:
    """添加环境管理命令行参数"""
    parser.addoption(
        "--env",
        action="store",
        default=None,
        help="指定运行环境（如: --env=staging）",
    )
    parser.addoption(
        "--config-dir",
        action="store",
        default="config",
        help="配置目录路径（默认: config）",
    )


@hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    """配置环境

    使用 @hookimpl(tryfirst=True) 确保在 core.pytest_configure 之前执行。
    """
    from df_test_framework.infrastructure.config import (
        FrameworkSettings,
        clear_settings_cache,
        get_settings_for_class,
    )

    env = config.getoption("--env")
    config_dir = config.getoption("--config-dir")

    # 清除配置缓存（每个 session 只清除一次）
    if not hasattr(config, "_df_cache_cleared"):
        clear_settings_cache()
        config._df_cache_cleared = True  # type: ignore[attr-defined]

    if env:
        # 设置环境变量，供 pydantic-settings 使用
        os.environ["ENV"] = env

    # 记录到配置中
    config._df_env_name = env  # type: ignore[attr-defined]
    config._df_config_dir = config_dir  # type: ignore[attr-defined]

    # 获取项目配置类
    settings_class = _get_settings_class(config)
    actual_class = settings_class or FrameworkSettings
    settings = get_settings_for_class(actual_class, env=env, config_dir=config_dir)

    # 存储到 pytest 配置中（供 core.py 使用）
    config._df_settings = settings  # type: ignore[attr-defined]
    config._df_current_env = env or settings.env  # type: ignore[attr-defined]


def pytest_report_header(config: pytest.Config) -> list[str]:
    """在测试报告头部显示环境信息"""
    headers = []

    env = config.getoption("--env")
    config_dir = config.getoption("--config-dir")

    if env:
        headers.append(f"环境: {env}")

    config_path = Path(config_dir)
    if config_path.exists() and (config_path / "base.yaml").exists():
        headers.append(f"配置: {config_dir}/ (YAML)")
    else:
        headers.append("配置: .env (dotenv)")

    return headers


@pytest.fixture(scope="session")
def settings(request: pytest.FixtureRequest) -> FrameworkSettings:
    """框架配置 fixture

    Example:
        >>> def test_example(settings):
        ...     assert settings.env in ["dev", "test", "staging", "prod"]
    """
    return request.config._df_settings  # type: ignore[attr-defined]


@pytest.fixture(scope="session")
def current_env(request: pytest.FixtureRequest) -> str:
    """当前环境名称 fixture

    Example:
        >>> def test_example(current_env):
        ...     if current_env == "prod":
        ...         pytest.skip("跳过生产环境")
    """
    return request.config._df_current_env  # type: ignore[attr-defined]


__all__ = [
    "pytest_addoption",
    "pytest_configure",
    "pytest_report_header",
    "settings",
    "current_env",
]
