"""现代化日志系统

基于 structlog 的结构化日志系统，支持 OpenTelemetry 集成。

v3.38.2: 重写，使用 structlog 替代 loguru
v3.38.4: 最佳实践改进
    - ProcessorFormatter 统一第三方日志格式
    - ISO 8601 + UTC 时间戳支持
    - orjson 高性能 JSON 序列化
    - AsyncLogger Protocol 支持异步日志
    - CallsiteParameterAdder 调用位置信息

Quick Start:
    >>> from df_test_framework.infrastructure.logging import (
    ...     configure_logging,
    ...     get_logger,
    ... )
    >>>
    >>> # 初始化（应用启动时）
    >>> from df_test_framework.infrastructure.config import LoggingConfig
    >>> config = LoggingConfig(level="DEBUG", format="text")
    >>> configure_logging(config)
    >>>
    >>> # 使用
    >>> logger = get_logger(__name__)
    >>> logger.info("用户登录", user_id=123, username="alice")

Features:
    - 结构化日志：JSON 格式，机器可读
    - 上下文传播：request_id/user_id 自动关联
    - OpenTelemetry 集成：trace_id/span_id 自动注入
    - 敏感信息脱敏：自动过滤密码、token 等
    - pytest 原生支持：无需桥接，直接使用 stdlib logging
    - 第三方日志统一格式：httpx、sqlalchemy 等库的日志格式一致
    - 高性能 JSON：支持 orjson 序列化（可选）
"""

from .config import (
    configure_logging,
    create_processor_formatter,
    is_logger_configured,
    is_orjson_available,
    reset_logging,
)
from .interface import AsyncLogger, Logger
from .logger import (
    bind_contextvars,
    clear_contextvars,
    get_logger,
    unbind_contextvars,
)
from .observability import (
    ObservabilityLogger,
    db_logger,
    get_observability_logger,
    http_logger,
    is_observability_enabled,
    redis_logger,
    set_observability_enabled,
    ui_logger,
)

__all__ = [
    # Protocol 接口（用于类型注解）
    "Logger",
    "AsyncLogger",
    # Logger 工厂函数
    "get_logger",
    # 日志配置函数
    "configure_logging",
    "create_processor_formatter",
    "is_logger_configured",
    "reset_logging",
    "is_orjson_available",
    # 上下文管理
    "bind_contextvars",
    "clear_contextvars",
    "unbind_contextvars",
    # 可观测性日志
    "ObservabilityLogger",
    "get_observability_logger",
    "http_logger",
    "db_logger",
    "redis_logger",
    "ui_logger",
    "set_observability_enabled",
    "is_observability_enabled",
]
