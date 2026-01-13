"""配置加载器（v3.35.5）

使用 pydantic-settings 原生配置源体系，实现分层 YAML 配置加载。

v3.35.5 恢复深度合并和 _extends 支持：
- LayeredYamlSettingsSource 继承 PydanticBaseSettingsSource
- 完全融入 pydantic-settings 配置源体系
- 支持 base.yaml + environments/{env}.yaml 分层
- 支持 _extends 继承语法（环境间继承、多级继承链）
- 支持 secrets/.env.local 敏感配置
- 使用 nested_model_default_partial_update 深度合并

配置优先级（从高到低）:
1. 环境变量
2. config/secrets/.env.local
3. config/environments/{env}.yaml（支持 _extends 继承）
4. config/base.yaml
5. 代码默认值

Example:
    >>> settings = load_config("staging")
    >>> print(settings.http.base_url)
    "https://staging-api.example.com"
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from df_test_framework.infrastructure.logging import get_logger

if TYPE_CHECKING:
    from .schema import FrameworkSettings

logger = get_logger(__name__)


class LayeredYamlSettingsSource(PydanticBaseSettingsSource):
    """分层 YAML 配置源

    继承 PydanticBaseSettingsSource，实现分层 YAML 配置加载：
    - base.yaml（基础配置）
    - environments/{env}.yaml（环境配置）
    - 支持 _extends 继承语法（多级继承）
    - 深度合并配置

    Example:
        >>> source = LayeredYamlSettingsSource(
        ...     settings_cls=MySettings,
        ...     config_dir="config",
        ...     env="staging"
        ... )
        >>> config = source()
        >>> print(config["http"]["base_url"])

    _extends 用法:
        # environments/staging.yaml
        _extends: environments/dev.yaml  # 继承 dev 配置
        http:
          base_url: "https://staging-api.example.com"
    """

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        config_dir: Path,
        env: str,
    ) -> None:
        """初始化分层 YAML 配置源

        Args:
            settings_cls: 配置类
            config_dir: 配置目录
            env: 环境名称
        """
        super().__init__(settings_cls)
        self.config_dir = config_dir
        self.env = env
        self._cache: dict[str, dict[str, Any]] = {}

    def get_field_value(
        self,
        field: FieldInfo,
        field_name: str,
    ) -> tuple[Any, str, bool]:
        """获取字段值（PydanticBaseSettingsSource 接口）

        此方法用于按字段获取值，但我们在 __call__ 中返回完整配置，
        所以这里返回 None。
        """
        return None, field_name, False

    def __call__(self) -> dict[str, Any]:
        """加载并返回分层 YAML 配置

        加载顺序：
        1. base.yaml
        2. environments/{env}.yaml（支持 _extends 多级继承）
        3. 设置 env 字段

        Returns:
            合并后的配置字典
        """
        # 加载基础配置
        config = self._load_yaml(self.config_dir / "base.yaml")

        # 加载环境配置（处理继承）
        env_config = self._load_env_yaml()
        config = self._deep_merge(config, env_config)

        # 设置环境名称
        config["env"] = self.env

        return config

    def _load_env_yaml(self) -> dict[str, Any]:
        """加载环境 YAML 配置（处理 _extends 继承）

        支持多级继承链，如：
        prod.yaml -> staging.yaml -> dev.yaml -> base.yaml
        """
        env_file = self.config_dir / "environments" / f"{self.env}.yaml"
        if not env_file.exists():
            env_file = self.config_dir / "environments" / f"{self.env}.yml"
            if not env_file.exists():
                return {}

        return self._load_with_extends(env_file)

    def _load_with_extends(self, path: Path, visited: set[str] | None = None) -> dict[str, Any]:
        """递归加载配置文件（处理 _extends 继承链）

        Args:
            path: 配置文件路径
            visited: 已访问的文件集合（检测循环继承）

        Returns:
            合并后的配置字典
        """
        if visited is None:
            visited = set()

        # 检测循环继承
        path_str = str(path.resolve())
        if path_str in visited:
            logger.warning(f"检测到循环继承: {path}")
            return {}
        visited.add(path_str)

        config = self._load_yaml(path)

        # 处理 _extends 继承
        if "_extends" in config:
            parent_name = config.pop("_extends")
            parent_file = self.config_dir / parent_name
            if parent_file.exists():
                parent_config = self._load_with_extends(parent_file, visited)
                config = self._deep_merge(parent_config, config)
            else:
                logger.warning(f"继承的配置文件不存在: {parent_file}")

        return config

    def _load_yaml(self, path: Path) -> dict[str, Any]:
        """加载 YAML 文件（带缓存）"""
        if not path.exists():
            return {}

        cache_key = str(path.resolve())
        if cache_key in self._cache:
            return self._cache[cache_key].copy()

        try:
            import yaml

            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            self._cache[cache_key] = data
            return data.copy()
        except Exception as e:
            logger.warning(f"加载配置文件失败: {path}, 错误: {e}")
            return {}

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """深度合并配置

        递归合并嵌套字典，override 中的值覆盖 base 中的值。

        Args:
            base: 基础配置
            override: 覆盖配置

        Returns:
            合并后的配置
        """
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result


def _create_settings_class(
    base_class: type[FrameworkSettings],
    config_dir: Path,
    secrets_dir: Path,
    env: str,
) -> type[BaseSettings]:
    """创建动态配置类

    使用 pydantic-settings 的配置源体系，将分层 YAML 配置源
    与环境变量、.env 文件配置源组合。

    Args:
        base_class: 基础配置类
        config_dir: 配置目录
        secrets_dir: secrets 目录
        env: 环境名称

    Returns:
        动态配置类
    """
    secrets_file = secrets_dir / ".env.local"
    env_file_path = str(secrets_file) if secrets_file.exists() else None

    class _DynamicSettings(base_class):  # type: ignore[valid-type,misc]
        model_config = SettingsConfigDict(
            env_prefix="",
            case_sensitive=False,
            env_nested_delimiter="__",
            env_ignore_empty=True,
            extra="allow",
            env_file=env_file_path,
            env_file_encoding="utf-8",
            # 关键：启用嵌套模型的部分更新（深度合并）
            nested_model_default_partial_update=True,
        )

        @classmethod
        def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
        ) -> tuple[PydanticBaseSettingsSource, ...]:
            """自定义配置源优先级

            优先级（从高到低）：
            1. init_settings - 构造函数传入参数（用于 with_overrides）
            2. 环境变量
            3. dotenv 文件（secrets/.env.local）
            4. LayeredYamlSettingsSource - 分层 YAML 配置
            """
            yaml_source = LayeredYamlSettingsSource(
                settings_cls=settings_cls,
                config_dir=config_dir,
                env=env,
            )
            return (
                init_settings,
                env_settings,
                dotenv_settings,
                yaml_source,
            )

    return _DynamicSettings


class ConfigLoader:
    """配置加载器

    使用 pydantic-settings 原生配置源体系，支持:
    - 分层 YAML 配置（LayeredYamlSettingsSource）
    - 配置继承（_extends 字段）
    - 环境变量深度合并（nested_model_default_partial_update）
    - secrets 管理

    Example:
        >>> loader = ConfigLoader(config_dir="config")
        >>> settings = loader.load("staging")
        >>> print(settings.env)
        "staging"

        >>> # 使用自定义配置类
        >>> loader = ConfigLoader(settings_class=MySettings)
        >>> settings = loader.load("staging")
    """

    def __init__(
        self,
        config_dir: str | Path = "config",
        secrets_dir: str | Path | None = None,
        settings_class: type[FrameworkSettings] | None = None,
    ) -> None:
        """初始化配置加载器

        Args:
            config_dir: 配置目录路径
            secrets_dir: 敏感配置目录（默认 config/secrets）
            settings_class: 配置类（默认 FrameworkSettings）
        """
        self.config_dir = Path(config_dir)
        self.secrets_dir = Path(secrets_dir) if secrets_dir else self.config_dir / "secrets"
        self.settings_class = settings_class

    def load(self, env: str | None = None) -> FrameworkSettings:
        """加载指定环境的配置

        Args:
            env: 环境名称。None 时从 ENV 环境变量读取，默认 "test"

        Returns:
            配置对象
        """
        from .schema import FrameworkSettings

        env = env or os.getenv("ENV", "test")
        base_class = self.settings_class or FrameworkSettings

        # 创建动态配置类并实例化
        settings_class = _create_settings_class(
            base_class=base_class,
            config_dir=self.config_dir,
            secrets_dir=self.secrets_dir,
            env=env,
        )

        return settings_class()


def load_config(
    env: str | None = None,
    config_dir: str | Path = "config",
    settings_class: type[FrameworkSettings] | None = None,
) -> FrameworkSettings:
    """加载配置的便捷函数

    Args:
        env: 环境名称（None 时从 ENV 环境变量读取）
        config_dir: 配置目录路径
        settings_class: 自定义配置类（可选）

    Returns:
        配置对象

    Example:
        >>> settings = load_config("staging")
        >>> settings = load_config()  # 使用 ENV 环境变量
    """
    return ConfigLoader(config_dir, settings_class=settings_class).load(env)


__all__ = [
    "ConfigLoader",
    "LayeredYamlSettingsSource",
    "load_config",
]
