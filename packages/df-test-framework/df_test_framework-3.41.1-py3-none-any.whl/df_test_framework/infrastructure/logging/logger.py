"""Logger 工厂模块

提供统一的日志获取接口。

v3.38.2: 重写，基于 structlog 替代 loguru
v3.38.7: 简化架构，直接使用 structlog.get_logger()
"""

from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from .interface import Logger


def get_logger(name: str | None = None) -> "Logger":
    """获取 logger 实例

    直接返回 structlog.BoundLogger，它已实现 Logger Protocol 的所有方法。

    Args:
        name: logger 名称，通常传入 __name__ 获取模块级 logger

    Returns:
        structlog.BoundLogger 实例

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("用户登录", user_id=123, username="alice")

        >>> # 绑定上下文
        >>> request_logger = logger.bind(request_id="abc123")
        >>> request_logger.info("订单创建", order_id=456)

    Note:
        返回的 structlog.BoundLogger 原生支持：
        - debug/info/warning/error/critical/exception 方法
        - bind/unbind/try_unbind 上下文绑定
        - 结构化日志字段
    """
    return structlog.get_logger(name)


def bind_contextvars(**kwargs) -> None:
    """绑定上下文变量（全局）

    绑定的变量会自动添加到所有日志中，直到调用 clear_contextvars()。

    Args:
        **kwargs: 要绑定的上下文字段

    Example:
        >>> # 在请求开始时
        >>> bind_contextvars(request_id="req_123", user_id=456)

        >>> # 任何地方的日志都会包含这些字段
        >>> logger = get_logger(__name__)
        >>> logger.info("处理订单")
        # 输出包含 request_id="req_123", user_id=456
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_contextvars() -> None:
    """清除所有上下文变量

    通常在请求结束时调用。

    Example:
        >>> # 请求结束时
        >>> clear_contextvars()
    """
    structlog.contextvars.clear_contextvars()


def unbind_contextvars(*keys: str) -> None:
    """解除指定的上下文变量绑定

    Args:
        *keys: 要解除绑定的字段名

    Example:
        >>> unbind_contextvars("request_id", "user_id")
    """
    structlog.contextvars.unbind_contextvars(*keys)


__all__ = [
    "get_logger",
    "bind_contextvars",
    "clear_contextvars",
    "unbind_contextvars",
]
