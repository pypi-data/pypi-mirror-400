"""
DF Test Framework - Core Layer (Layer 0)

纯抽象层，无第三方依赖。

包含:
- protocols/: 协议定义（依赖反转基础）
- middleware/: 统一中间件系统
- context/: 上下文传播系统
- events/: 事件类型定义
- models/: 基础数据模型 (v3.41.1)
- decorators: 通用装饰器 (v3.29.0)
- exceptions: 异常体系
- types: 类型定义
"""

from df_test_framework.core.decorators import (
    cache_result,
    deprecated,
    log_execution,
    retry_on_failure,
)
from df_test_framework.core.exceptions import (
    ConfigurationError,
    DatabaseError,
    ExtensionError,
    FrameworkError,
    HttpError,
    MessengerError,
    MiddlewareAbort,
    MiddlewareError,
    PluginError,
    ProviderError,
    RedisError,
    ResourceError,
    StorageError,
    TelemetryError,
    TestError,
    ValidationError,
)

# v3.41.1: 基础数据模型迁移到 core 层
from df_test_framework.core.models import (
    BaseRequest,
    BaseResponse,
    PageResponse,
)
from df_test_framework.core.types import (
    CaseType,
    DatabaseDialect,
    DatabaseOperation,
    DecimalAsCurrency,
    DecimalAsFloat,
    Environment,
    Headers,
    HttpMethod,
    HttpStatus,
    HttpStatusGroup,
    JsonDict,
    LogLevel,
    MessageQueueType,
    Priority,
    QueryParams,
    StorageType,
    TRequest,
    TResponse,
)

__all__ = [
    # 装饰器 (v3.29.0)
    "retry_on_failure",
    "log_execution",
    "deprecated",
    "cache_result",
    # 异常
    "FrameworkError",
    "ConfigurationError",
    "HttpError",
    "DatabaseError",
    "MessengerError",
    "StorageError",
    "MiddlewareError",
    "MiddlewareAbort",
    "PluginError",
    "TelemetryError",
    "ResourceError",
    "RedisError",
    "ValidationError",
    "ExtensionError",
    "ProviderError",
    "TestError",
    # 类型
    "Environment",
    "LogLevel",
    "HttpMethod",
    "HttpStatus",
    "HttpStatusGroup",
    "DatabaseDialect",
    "DatabaseOperation",
    "MessageQueueType",
    "StorageType",
    "Priority",
    "CaseType",
    "TRequest",
    "TResponse",
    "JsonDict",
    "Headers",
    "QueryParams",
    # Pydantic 序列化类型 (v3.29.0)
    "DecimalAsFloat",
    "DecimalAsCurrency",
    # 基础数据模型 (v3.41.1)
    "BaseRequest",
    "BaseResponse",
    "PageResponse",
]
