"""统一脱敏服务

v3.40.0 新增：将日志系统、ConsoleDebugObserver、AllureObserver 的脱敏逻辑统一。
v3.40.1 重构：移除独立单例，与 settings 生命周期绑定，配置变更自动生效。

特性：
- 共享敏感字段定义（支持正则匹配）
- 多种脱敏策略（完全隐藏、部分保留、哈希）
- 深度递归脱敏（支持嵌套 dict/list）
- 消息内容正则脱敏
- 各组件独立开关控制
- 与 settings 生命周期绑定（clear_settings_cache 自动清除）

使用方式：
    >>> from df_test_framework.infrastructure.sanitize import get_sanitize_service
    >>> service = get_sanitize_service()
    >>> service.sanitize_value("password", "secret123")
    'secr****t123'
    >>> service.sanitize_dict({"password": "secret", "name": "test"})
    {'password': 'secr****', 'name': 'test'}
"""

from __future__ import annotations

import hashlib
import re
from contextvars import ContextVar
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from df_test_framework.infrastructure.config import SanitizeConfig, SanitizeStrategy

# 测试上下文（用于测试隔离）
_sanitize_service: ContextVar[SanitizeService | None] = ContextVar("sanitize_service", default=None)

# settings 对象上缓存 service 的属性名
_SETTINGS_ATTR = "_sanitize_service_instance"


class SanitizeService:
    """统一脱敏服务

    提供统一的敏感数据脱敏功能，支持：
    - 字段名匹配（精确匹配 + 正则表达式）
    - 多种脱敏策略（FULL/PARTIAL/HASH）
    - 深度递归脱敏
    - 消息内容正则脱敏

    Example:
        >>> from df_test_framework.infrastructure.config import SanitizeConfig
        >>> config = SanitizeConfig()
        >>> service = SanitizeService(config)
        >>> service.sanitize_value("password", "mysecretpassword")
        'myse****word'
        >>> service.is_sensitive("api_key")
        True
        >>> service.is_sensitive("username")
        False
    """

    def __init__(self, config: SanitizeConfig):
        """初始化脱敏服务

        Args:
            config: 脱敏配置
        """
        self.config = config
        self._key_patterns: list[re.Pattern] = []
        self._message_patterns: list[re.Pattern] = []
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """编译正则表达式模式（缓存提升性能）"""
        # 编译字段名匹配模式
        for key in self.config.sensitive_keys:
            try:
                # 检查是否是正则表达式（包含正则特殊字符）
                if any(c in key for c in r".*+?^${}[]|\()"):
                    self._key_patterns.append(re.compile(key, re.IGNORECASE))
                else:
                    # 精确匹配，转换为正则
                    self._key_patterns.append(re.compile(f"^{re.escape(key)}$", re.IGNORECASE))
            except re.error:
                # 无效正则，当作精确匹配
                self._key_patterns.append(re.compile(f"^{re.escape(key)}$", re.IGNORECASE))

        # 编译消息内容匹配模式
        for pattern in self.config.sensitive_patterns:
            try:
                self._message_patterns.append(re.compile(pattern, re.IGNORECASE))
            except re.error:
                # 跳过无效正则
                pass

    def is_sensitive(self, key: str) -> bool:
        """判断字段名是否敏感

        Args:
            key: 字段名

        Returns:
            是否为敏感字段
        """
        if not self.config.enabled:
            return False

        for pattern in self._key_patterns:
            if pattern.search(key):
                return True
        return False

    def sanitize_value(
        self,
        key: str,
        value: str,
        strategy: SanitizeStrategy | None = None,
    ) -> str:
        """脱敏单个值

        Args:
            key: 字段名
            value: 字段值
            strategy: 脱敏策略（可选，默认使用配置中的策略）

        Returns:
            脱敏后的值
        """
        if not self.config.enabled:
            return value

        if not self.is_sensitive(key):
            return value

        if not isinstance(value, str) or not value:
            return value

        # 延迟导入避免循环依赖
        from df_test_framework.infrastructure.config import SanitizeStrategy

        strategy = strategy or self.config.default_strategy

        if strategy == SanitizeStrategy.FULL:
            return self.config.mask_value

        elif strategy == SanitizeStrategy.PARTIAL:
            return self._partial_mask(value)

        elif strategy == SanitizeStrategy.HASH:
            hash_value = hashlib.sha256(value.encode()).hexdigest()[:16]
            return f"sha256:{hash_value}"

        return value

    def _partial_mask(self, value: str) -> str:
        """部分脱敏（保留首尾字符）

        Args:
            value: 原始值

        Returns:
            脱敏后的值（如 "myse****word"）
        """
        if not value:
            return value

        prefix_len = self.config.keep_prefix
        suffix_len = self.config.keep_suffix
        mask_char = self.config.mask_char

        # 如果值太短，完全脱敏
        if len(value) <= prefix_len + suffix_len:
            return mask_char * 4

        # 保留首尾，中间用脱敏字符替代
        prefix = value[:prefix_len] if prefix_len > 0 else ""
        suffix = value[-suffix_len:] if suffix_len > 0 else ""
        mask_len = min(4, len(value) - prefix_len - suffix_len)  # 最多4个脱敏字符
        mask = mask_char * mask_len

        return f"{prefix}{mask}{suffix}"

    def sanitize_dict(
        self,
        data: dict[str, Any] | None,
        context: str = "default",
    ) -> dict[str, Any] | None:
        """脱敏字典（深度递归）

        Args:
            data: 要脱敏的字典
            context: 上下文（logging/console/allure），用于检查独立开关

        Returns:
            脱敏后的字典
        """
        if data is None:
            return None

        if not self.config.enabled:
            return data

        # 检查该 context 是否启用
        ctx_config = getattr(self.config, context, None)
        if ctx_config and not ctx_config.enabled:
            return data

        return self._sanitize_recursive(data)

    def _sanitize_recursive(self, data: Any) -> Any:
        """递归脱敏

        Args:
            data: 要脱敏的数据（支持 dict/list/基本类型）

        Returns:
            脱敏后的数据
        """
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if isinstance(value, str) and self.is_sensitive(key):
                    result[key] = self.sanitize_value(key, value)
                elif isinstance(value, dict):
                    result[key] = self._sanitize_recursive(value)
                elif isinstance(value, list):
                    result[key] = self._sanitize_recursive(value)
                else:
                    result[key] = value
            return result

        elif isinstance(data, list):
            return [self._sanitize_recursive(item) for item in data]

        return data

    def sanitize_message(self, message: str) -> str:
        """脱敏消息内容（正则匹配）

        用于脱敏日志消息中的敏感内容，如 "password=xxx"

        Args:
            message: 原始消息

        Returns:
            脱敏后的消息
        """
        if not self.config.enabled:
            return message

        if not isinstance(message, str):
            return message

        # 检查 logging 上下文是否启用
        if not self.config.logging.enabled:
            return message

        result = message
        for pattern in self._message_patterns:
            # 保留第一个分组（键名部分），替换第二个分组（值部分）
            result = pattern.sub(rf"\1{self.config.mask_value}", result)

        return result

    def is_context_enabled(self, context: str) -> bool:
        """检查指定上下文是否启用脱敏

        Args:
            context: 上下文名称（logging/console/allure）

        Returns:
            是否启用脱敏
        """
        if not self.config.enabled:
            return False

        ctx_config = getattr(self.config, context, None)
        if ctx_config is None:
            return True  # 未配置时默认启用

        return ctx_config.enabled


def get_sanitize_service() -> SanitizeService:
    """获取脱敏服务实例

    v3.40.1 重构：与 settings 生命周期绑定。
    当 clear_settings_cache() 被调用时，service 自动随 settings 一起清除。

    优先级：
    1. 测试上下文中的服务（通过 ContextVar，用于测试隔离）
    2. settings 对象上缓存的服务（与配置生命周期绑定）

    Returns:
        脱敏服务实例
    """
    # 优先使用测试上下文（用于测试隔离）
    test_service = _sanitize_service.get()
    if test_service is not None:
        return test_service

    # 从 settings 获取，与配置生命周期绑定
    from df_test_framework.infrastructure.config import SanitizeConfig

    try:
        from df_test_framework import get_settings

        settings = get_settings()

        # 在 settings 对象上缓存 service
        # 当 clear_settings_cache() 清除 settings 时，service 也随之清除
        if not hasattr(settings, _SETTINGS_ATTR):
            config = settings.sanitize or SanitizeConfig()
            setattr(settings, _SETTINGS_ATTR, SanitizeService(config))

        return getattr(settings, _SETTINGS_ATTR)

    except Exception:
        # 配置加载失败时使用默认配置（不缓存）
        return SanitizeService(SanitizeConfig())


def set_sanitize_service(service: SanitizeService | None) -> None:
    """设置测试上下文中的脱敏服务

    用于测试隔离，每个测试可以使用独立的脱敏配置。

    Args:
        service: 脱敏服务实例，None 表示清除
    """
    _sanitize_service.set(service)


def clear_sanitize_service() -> None:
    """清除测试上下文中的脱敏服务

    v3.40.1: 仅清除测试上下文。
    settings 上的缓存会随 clear_settings_cache() 自动清除，无需单独处理。
    """
    _sanitize_service.set(None)


__all__ = [
    "SanitizeService",
    "get_sanitize_service",
    "set_sanitize_service",
    "clear_sanitize_service",
]
