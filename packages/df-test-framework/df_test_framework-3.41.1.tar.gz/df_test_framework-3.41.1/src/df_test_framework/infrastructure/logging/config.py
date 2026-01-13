"""日志配置模块

配置 structlog 和 OpenTelemetry 集成。

v3.38.2: 新增，基于 structlog 的现代化日志配置
v3.38.3: 简化 API，只接受 LoggingConfig 对象
v3.38.4: 最佳实践改进
    - 添加 ProcessorFormatter 统一第三方日志格式
    - 支持 ISO 8601 + UTC 时间戳（生产环境）
    - 支持 orjson 高性能 JSON 序列化
    - 添加 CallsiteParameterAdder 调用位置信息
    - 优化脱敏处理器位置
v3.38.5: structlog 25.5.0 最佳实践升级
    - 添加 PositionalArgumentsFormatter 支持第三方库 % 格式化
    - 添加 ExtraAdder 支持第三方库 extra 参数
    - 添加 LogfmtRenderer 输出格式支持
    - 使用 QUAL_NAME 替代 FUNC_NAME (Python 3.11+)
    - 优化 processor 链顺序
"""

from __future__ import annotations

import logging
import re
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog
from structlog.typing import EventDict, Processor

if TYPE_CHECKING:
    from df_test_framework.infrastructure.config.schema import LoggingConfig

# 全局配置状态
_LOGGER_CONFIGURED = False

# orjson 可用性检查
_ORJSON_AVAILABLE = False
try:
    import orjson

    _ORJSON_AVAILABLE = True
except ImportError:
    pass


def _parse_size(size_str: str) -> int:
    """解析大小字符串为字节数

    支持格式: "100 MB", "1 GB", "500 KB"

    Args:
        size_str: 大小字符串

    Returns:
        字节数
    """
    size_str = size_str.strip().upper()
    # 按单位长度从大到小排序，避免 "MB" 被 "B" 先匹配
    units = [
        ("GB", 1024 * 1024 * 1024),
        ("MB", 1024 * 1024),
        ("KB", 1024),
        ("B", 1),
    ]
    for unit, multiplier in units:
        if size_str.endswith(unit):
            number = size_str[: -len(unit)].strip()
            return int(float(number) * multiplier)
    # 默认为字节
    return int(size_str)


def _parse_retention(retention_str: str) -> int:
    """解析保留策略为备份文件数量

    支持格式: "7 days", "30 days", "5" (直接数字表示文件数)

    注意: RotatingFileHandler 使用 backupCount 而非时间，
    这里简化处理：每天假设1个轮转，天数即为 backupCount。

    Args:
        retention_str: 保留策略字符串

    Returns:
        备份文件数量
    """
    retention_str = retention_str.strip().lower()

    # 直接数字
    if retention_str.isdigit():
        return int(retention_str)

    # "7 days" 格式
    match = re.match(r"(\d+)\s*(day|days)", retention_str)
    if match:
        return int(match.group(1))

    # 默认 7 个备份
    return 7


def _add_trace_info(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """添加 OpenTelemetry trace 信息到日志"""
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        span_context = span.get_span_context()

        if span_context.is_valid:
            event_dict["trace_id"] = format(span_context.trace_id, "032x")
            event_dict["span_id"] = format(span_context.span_id, "016x")
    except ImportError:
        pass
    except Exception:
        pass

    return event_dict


def _sanitize_sensitive_data(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """脱敏敏感信息

    v3.40.0 重构：使用统一脱敏服务 SanitizeService，支持：
    - 可配置的敏感字段列表（支持正则）
    - 多种脱敏策略（full/partial/hash）
    - 通过 SanitizeConfig.logging.enabled 独立控制

    原有行为保持兼容，但现在通过配置文件统一管理敏感字段。
    """
    try:
        from df_test_framework.infrastructure.sanitize import get_sanitize_service

        service = get_sanitize_service()

        # 检查 logging 上下文是否启用脱敏
        if not service.is_context_enabled("logging"):
            return event_dict

        # 脱敏字段值
        for key in list(event_dict.keys()):
            value = event_dict[key]
            if isinstance(value, str) and service.is_sensitive(key):
                event_dict[key] = service.sanitize_value(key, value)

        # 脱敏消息内容
        if "event" in event_dict and isinstance(event_dict["event"], str):
            event_dict["event"] = service.sanitize_message(event_dict["event"])

        return event_dict

    except Exception:
        # 防御性处理：脱敏失败时保持原始日志，避免日志系统崩溃
        return event_dict


def _get_json_renderer(config: LoggingConfig) -> Processor:
    """获取 JSON 渲染器

    如果 orjson 可用且配置启用，使用 orjson 获得更好的性能。

    Args:
        config: 日志配置

    Returns:
        JSON 渲染处理器
    """
    if _ORJSON_AVAILABLE and getattr(config, "use_orjson", True):
        # orjson 返回 bytes，需要解码为 str（因为我们使用 StreamHandler）
        def orjson_serializer(obj: Any, **kwargs: Any) -> str:
            return orjson.dumps(obj).decode("utf-8")

        return structlog.processors.JSONRenderer(serializer=orjson_serializer)
    else:
        return structlog.processors.JSONRenderer(ensure_ascii=False)


def _get_logfmt_renderer(config: LoggingConfig) -> Processor:
    """获取 Logfmt 渲染器

    Logfmt 是 Loki、Prometheus 等日志系统的原生格式。

    Args:
        config: 日志配置

    Returns:
        Logfmt 渲染处理器
    """
    return structlog.processors.LogfmtRenderer(
        key_order=["timestamp", "level", "logger", "event"],
        drop_missing=True,
    )


def _build_shared_processors(config: LoggingConfig) -> list[Processor]:
    """构建共享的 processor 链（用于 structlog 和第三方日志）

    按照 structlog 25.5.0 官方推荐顺序排列。

    Args:
        config: 日志配置

    Returns:
        共享的 processor 列表
    """
    processors: list[Processor] = [
        # 1. 合并上下文变量（必须第一位）
        structlog.contextvars.merge_contextvars,
        # 2. 添加 logger 名称
        structlog.stdlib.add_logger_name,
        # 3. 添加日志级别
        structlog.stdlib.add_log_level,
        # 4. 处理第三方库的 % 格式化参数（v3.38.5 新增）
        # 例如: logging.info("User %s logged in", user_id)
        structlog.stdlib.PositionalArgumentsFormatter(),
    ]

    # 5. 脱敏处理器（放在格式化之后，避免脱敏原始格式字符串）
    if config.sanitize:
        processors.append(_sanitize_sensitive_data)

    # 6. 时间戳（根据环境选择格式）
    if getattr(config, "use_utc", False) or config.format == "json":
        # 生产环境：ISO 8601 + UTC
        processors.append(structlog.processors.TimeStamper(fmt="iso", utc=True))
    else:
        # 开发环境：本地时间，更易读
        processors.append(structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f"))

    # 7. 添加调用位置信息（可选，便于调试）
    if getattr(config, "add_callsite", False):
        # v3.38.5: 使用 QUAL_NAME（限定名称，包含类名）
        # 项目要求 Python 3.12+，直接使用 QUAL_NAME
        # 例如: "AuthService.login" 而非 "login"
        callsite_params = {
            structlog.processors.CallsiteParameter.FILENAME,
            structlog.processors.CallsiteParameter.LINENO,
            structlog.processors.CallsiteParameter.QUAL_NAME,
        }
        processors.append(structlog.processors.CallsiteParameterAdder(callsite_params))

    # 8. OpenTelemetry trace 信息
    processors.append(_add_trace_info)

    # 9. 堆栈信息渲染
    processors.append(structlog.processors.StackInfoRenderer())

    # 10. Unicode 解码（放在渲染器之前）
    processors.append(structlog.processors.UnicodeDecoder())

    # 注意：format_exc_info 不在此处添加
    # - ConsoleRenderer 使用 plain_traceback 自己处理异常，添加 format_exc_info 会产生警告
    # - JSONRenderer/LogfmtRenderer 需要 format_exc_info，在 ProcessorFormatter 中按需添加

    return processors


def _build_foreign_pre_chain(config: LoggingConfig) -> list[Processor]:
    """构建第三方日志的预处理链

    第三方库（httpx、sqlalchemy 等）的日志需要额外处理 extra 参数。

    Args:
        config: 日志配置

    Returns:
        第三方日志的 processor 列表
    """
    # 基础共享处理器
    processors = _build_shared_processors(config)

    # 在共享处理器之前添加 ExtraAdder（v3.38.5 新增）
    # 处理第三方库通过 extra 参数传递的额外字段
    # 例如: logging.info("msg", extra={"request_id": "abc"})
    extra_adder = structlog.stdlib.ExtraAdder()

    # ExtraAdder 应该在 add_log_level 之后（索引 2），PositionalArgumentsFormatter 之后（索引 3）
    # 插入到索引 4 的位置
    processors.insert(4, extra_adder)

    return processors


def _get_renderer(config: LoggingConfig) -> Processor:
    """根据配置获取最终的渲染器

    Args:
        config: 日志配置

    Returns:
        渲染处理器
    """
    format_type = getattr(config, "format", "text")

    if format_type == "json":
        return _get_json_renderer(config)
    elif format_type == "logfmt":
        # v3.38.5 新增: Logfmt 格式支持
        return _get_logfmt_renderer(config)
    else:
        # 使用 plain_traceback 避免对 Rich 库的依赖
        # rich_traceback 需要安装 Rich 库，plain_traceback 是内置的
        return structlog.dev.ConsoleRenderer(
            colors=True, exception_formatter=structlog.dev.plain_traceback
        )


def configure_logging(config: LoggingConfig) -> None:
    """配置日志系统

    使用 ProcessorFormatter 统一处理 structlog 和第三方库的日志，
    确保所有日志具有一致的格式（时间戳、trace_id 等）。

    v3.38.5 改进:
    - 添加 PositionalArgumentsFormatter 支持 % 格式化
    - 添加 ExtraAdder 支持 extra 参数
    - 支持 logfmt 输出格式
    - 使用 QUAL_NAME (Python 3.11+)

    Args:
        config: LoggingConfig 配置对象

    Example:
        >>> from df_test_framework.infrastructure.config import LoggingConfig
        >>> config = LoggingConfig(level="DEBUG", format="json", file="logs/app.log")
        >>> configure_logging(config)
    """
    global _LOGGER_CONFIGURED

    # 构建共享 processors（用于 structlog 日志）
    shared_processors = _build_shared_processors(config)

    # 构建第三方日志的预处理链（包含 ExtraAdder）
    foreign_pre_chain = _build_foreign_pre_chain(config)

    # 构建 structlog 专用 processors
    # 末尾添加 wrap_for_formatter 以便 ProcessorFormatter 处理
    structlog_processors: list[Processor] = [
        structlog.stdlib.filter_by_level,
        *shared_processors,
        # 将 event_dict 包装为 ProcessorFormatter 可识别的格式
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    # 配置 structlog
    structlog.configure(
        processors=structlog_processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # 配置标准 logging
    log_level = getattr(logging, config.level.upper())
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()

    # 创建 ProcessorFormatter（统一格式化 structlog 和第三方日志）
    # foreign_pre_chain 用于处理非 structlog 的日志（如 httpx、sqlalchemy）
    #
    # 注意：format_exc_info 只在 JSON/logfmt 格式时添加
    # - ConsoleRenderer 使用 plain_traceback 自己处理异常
    # - JSONRenderer/LogfmtRenderer 需要 format_exc_info 将异常转为字符串
    format_type = getattr(config, "format", "text")
    final_processors: list[Processor] = [
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
    ]
    if format_type in ("json", "logfmt"):
        final_processors.append(structlog.processors.format_exc_info)
    final_processors.append(_get_renderer(config))

    processor_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=foreign_pre_chain,
        processors=final_processors,
    )

    # 添加控制台 handler
    if config.enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(processor_formatter)
        root_logger.addHandler(console_handler)

    # 添加文件 handler
    if config.file:
        log_path = Path(config.file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=_parse_size(config.rotation),
            backupCount=_parse_retention(config.retention),
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        # 文件日志也使用 ProcessorFormatter，但强制使用 JSON 格式
        # 文件日志需要 format_exc_info 将异常转为字符串
        file_processor_formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=foreign_pre_chain,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.format_exc_info,
                _get_json_renderer(config),
            ],
        )
        file_handler.setFormatter(file_processor_formatter)
        root_logger.addHandler(file_handler)

    _LOGGER_CONFIGURED = True


def is_logger_configured() -> bool:
    """检查日志是否已配置"""
    return _LOGGER_CONFIGURED


def reset_logging() -> None:
    """重置日志配置"""
    global _LOGGER_CONFIGURED
    structlog.reset_defaults()
    logging.getLogger().handlers.clear()
    _LOGGER_CONFIGURED = False


def is_orjson_available() -> bool:
    """检查 orjson 是否可用"""
    return _ORJSON_AVAILABLE


def create_processor_formatter(config: LoggingConfig) -> structlog.stdlib.ProcessorFormatter:
    """创建 ProcessorFormatter（用于 pytest 集成）

    此函数用于创建一个 ProcessorFormatter，可以替换 pytest handlers 的 formatter，
    实现统一的日志格式。

    Args:
        config: 日志配置

    Returns:
        ProcessorFormatter 实例

    Example:
        >>> formatter = create_processor_formatter(config)
        >>> pytest_handler.setFormatter(formatter)
    """
    foreign_pre_chain = _build_foreign_pre_chain(config)
    format_type = getattr(config, "format", "text")

    final_processors: list[Processor] = [
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
    ]
    if format_type in ("json", "logfmt"):
        final_processors.append(structlog.processors.format_exc_info)
    final_processors.append(_get_renderer(config))

    return structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=foreign_pre_chain,
        processors=final_processors,
    )


__all__ = [
    "configure_logging",
    "create_processor_formatter",
    "is_logger_configured",
    "reset_logging",
    "is_orjson_available",
]
