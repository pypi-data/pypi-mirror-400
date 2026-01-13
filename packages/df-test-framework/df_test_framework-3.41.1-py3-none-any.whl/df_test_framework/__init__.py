"""
DF 测试自动化框架 v3.40.0

企业级测试平台架构升级，基于五层架构 + 事件驱动 + 可观测性。

v3.40.0 核心特性:
- 🔒 统一脱敏服务 - SanitizeService 整合日志/Console/Allure 脱敏逻辑
- 🎯 多策略支持 - partial/full/hash 三种脱敏策略
- ⚙️ 配置驱动 - 支持正则匹配敏感字段，各组件独立开关
- 📦 零配置使用 - 默认配置覆盖 17 个常见敏感字段

v3.38.7 核心特性:
- 🔄 统一日志系统 - 全框架使用 get_logger()，消除 structlog/logging 混用
- 📋 YAML logging.level 生效 - 修复 pytest log_level 覆盖问题
- 🎯 命名空间级别控制 - 框架内部模块日志级别独立于用户配置

v3.38.4 核心特性:
- 🔄 ProcessorFormatter 统一格式 - 第三方库日志与 structlog 格式一致
- ⏰ ISO 8601 + UTC 时间戳 - 生产环境最佳实践
- ⚡ orjson 高性能序列化 - 比标准库快 5-10 倍（可选）
- 📍 CallsiteParameterAdder - 调用位置信息，便于调试
- 🔀 AsyncLogger Protocol - 异步日志接口支持

v3.38.2 核心特性:
- 🔄 日志系统迁移 - 从 loguru 迁移到 structlog
- 🔌 pytest 原生支持 - structlog 使用 stdlib logging，无需桥接
- ⏰ 时间格式统一 - 使用 strftime 格式，与 pytest 一致
- 🔗 OpenTelemetry 集成 - 自动注入 trace_id/span_id
- 🔒 敏感信息脱敏 - 自动过滤密码、token 等

v3.37.0 核心特性:
- 🔌 pytest11 Entry Points - pip install 后插件自动加载，无需手动配置
- 📝 pytest 9.0 原生 TOML - 使用 [tool.pytest] 替代 [tool.pytest.ini_options]
- 🎯 config 属性状态管理 - pytest 官方推荐方式，使用 config._df_* 属性
- 🧹 移除 managers.py - 简化架构，状态管理直接使用 config 对象

v3.35.0 核心特性:
- 📁 YAML 分层配置 - base.yaml + environments/{env}.yaml，支持继承和深度合并
- 🏛️ ConfigRegistry - 全局单例，点号路径访问配置（registry.get("http.timeout")）
- 🛠️ CLI 环境管理 - df-test env show/init/validate 命令
- 🧪 pytest 插件增强 - --env/--config-dir 参数，config_registry/settings fixtures

v3.34.0/v3.34.1 核心特性:
- 📬 MQ 事件三态模式 - Start/End/Error 统一架构，与 HTTP/gRPC/GraphQL 一致
- 🔗 correlation_id 关联 - 完整的消息发布/消费追踪

v3.33.0 核心特性:
- 🔧 GraphQL 中间件系统 - 洋葱模型，EventPublisher/Retry/Logging 中间件
- 📡 GraphQL 事件集成 - Start/End/Error 事件自动发布

v3.32.0 核心特性:
- 📡 gRPC 事件统一 - Start/End/Error 事件，Allure/Console 自动记录

v3.31.0 核心特性:
- 🏭 Factory 系统重构 - 融合 factory_boy 和 polyfactory 最佳实践
- 🎯 Trait 支持 - 预设配置组，通过布尔标志激活（如 admin=True）
- 🔗 SubFactory/PostGenerated - 嵌套工厂和后处理字段
- 📦 8 个预置工厂 - UserFactory、ProductFactory、OrderFactory 等

v3.30.0 核心特性:
- 🔍 SchemaValidator - 独立的 JSON Schema 验证器，支持文件加载和预定义 Schema
- 🎯 自定义匹配器 - 15+ 匹配器类，支持组合、取反、操作符重载
- 📋 COMMON_SCHEMAS - 预定义常用 Schema（id、uuid、email、phone_cn、pagination 等）

v3.29.0 核心特性:
- 🏗️ utils/ 模块重构 - 功能迁移到正确的架构层级
- 🏭 Factory 模式 - 新增 testing.data.factories，创建完整业务对象
- ♻️ 向后兼容 - utils 模块保留废弃导出，将在 v4.0.0 移除

v3.29.0 迁移路径:
- DataGenerator → testing.data.generators
- AssertHelper → testing.assertions
- CircuitBreaker → infrastructure.resilience
- 装饰器 → core.decorators
- 类型 → core.types

v3.28.0 特性:
- 🎯 调试系统统一 - 移除 HTTPDebugger/DBDebugger，统一使用 ConsoleDebugObserver

v3.27.0 特性:
- 🔧 ConsoleDebugObserver pytest 集成 - 自动检测 pytest 模式，原生日志输出

v3.26.0 特性:
- 📋 pytest 原生日志 - 解决日志与测试名混行问题

v3.25.0 特性:
- 🔐 reset_auth_state() - 组合方法，一次调用完全清除认证状态
- 🍪 Cookie 精细控制 - clear_cookie(name) / get_cookies()

v3.19.0 特性:
- ✨ 认证控制增强 - skip_auth 跳过认证 / token 自定义 Token
- 🔐 clear_auth_cache() - 清除 Token 缓存支持完整认证流程测试
- 📋 Request.metadata - 请求元数据支持中间件行为控制

v3.18.1 特性:
- ✨ 顶层中间件配置 - SIGNATURE__* / BEARER_TOKEN__* 环境变量配置
- 🔧 配置前缀统一 - 移除 APP_ 前缀，env vars 与 .env 一致
- ✨ 配置驱动清理 - CLEANUP__MAPPINGS__* 零代码配置
- ✨ prepare_data fixture - 回调式数据准备，自动提交
- ✨ data_preparer fixture - 上下文管理器式数据准备
- 📦 ConfigDrivenCleanupManager - 配置驱动的清理管理器

架构层级:
- Layer 0 (core/): 纯抽象，无第三方依赖
- Layer 1 (infrastructure/): 基础设施，配置/插件/遥测/事件
- Layer 2 (capabilities/): 能力层，HTTP/DB/MQ/Storage
- Layer 3 (testing/ + cli/): 门面层
- Layer 4 (bootstrap/): 引导层，框架组装和初始化
- 横切 (plugins/): 插件实现

历史版本特性:
- 🔄 事件系统重构 - EventBus 与 Allure 深度整合（v3.17）
- 🔗 OpenTelemetry 整合 - trace_id/span_id 自动注入（v3.17）
- 🧪 测试隔离 - 每个测试独立的 EventBus（v3.17）
- 🏗️ 五层架构 - Layer 4 Bootstrap 引导层（v3.16）
- 🧅 统一中间件系统（v3.14）
- 📡 可观测性融合（v3.14）
- 🔗 上下文传播（v3.14）
- 📢 事件驱动（v3.14）
- 🏗️ Testing 模块架构重构（v3.12）
- 🌐 协议扩展 - GraphQL/gRPC 客户端（v3.11）
- 🎭 Mock 增强 - DatabaseMocker/RedisMocker（v3.11）
- 📊 可观测性增强 - OpenTelemetry/Prometheus（v3.10）
- 💾 存储客户端 - LocalFile/S3/OSS（v3.10）
- 🚀 异步HTTP客户端 - 性能提升40倍（v3.8）
- 🔄 Unit of Work 模式支持（v3.7）
"""

__version__ = "3.41.1"
__author__ = "DF QA Team"

# ============= 异常体系 =============
# HTTP核心对象
# GraphQL客户端
# ============= 引导层 (Layer 4) =============
# ============= 工具函数 (v3.29.0 迁移) =============
# v3.29.0: 从 utils 迁移到正确的架构层级
from assertpy import assert_that  # 直接从 assertpy 导入

from .bootstrap import (
    # Bootstrap
    Bootstrap,
    BootstrapApp,
    # Providers
    Provider,
    ProviderRegistry,
    # Runtime
    RuntimeBuilder,
    RuntimeContext,
    SingletonProvider,
    default_providers,
)
from .capabilities.clients.graphql import (
    GraphQLClient,
    GraphQLError,
    GraphQLRequest,
    GraphQLResponse,
    QueryBuilder,
)

# gRPC客户端
from .capabilities.clients.grpc import (
    GrpcClient,
    GrpcError,
    GrpcResponse,
)
from .capabilities.clients.http.core import FilesTypes, FileTypes, Request, Response

# v3.16.0: HTTP拦截器已完全移除，请使用中间件系统
# Capabilities 层 - HTTP 中间件
from .capabilities.clients.http.middleware import (
    BearerTokenMiddleware,
    HttpTelemetryMiddleware,
    LoggingMiddleware,
    RetryMiddleware,
    SignatureMiddleware,
)

# ============= 核心功能层 =============
# HTTP客户端
from .capabilities.clients.http.rest.httpx import (
    AsyncHttpClient,
    BaseAPI,
    BusinessError,
    HttpClient,
)

# 数据库
from .capabilities.databases.database import Database
from .capabilities.databases.redis.redis_client import RedisClient

# Repository模式
from .capabilities.databases.repositories.base import BaseRepository
from .capabilities.databases.repositories.query_spec import QuerySpec

# Unit of Work 模式
from .capabilities.databases.uow import UnitOfWork

# ============= UI模块 =============
from .capabilities.drivers.web import (
    BasePage,
    BrowserManager,
    BrowserType,
    ElementLocator,
    LocatorType,
    WaitHelper,
)

# ============= 异常体系 (v3.14.0 统一到 core) =============
from .core import (
    ConfigurationError,
    DatabaseError,
    ExtensionError,
    FrameworkError,
    HttpError,
    MiddlewareAbort,
    MiddlewareError,
    ProviderError,
    RedisError,
    ResourceError,
    TestError,
    ValidationError,
)
from .core.context import (
    ExecutionContext,
    get_current_context,
    get_or_create_context,
    with_context,
    with_context_async,
)
from .core.decorators import (
    cache_result,
    deprecated,
    log_execution,
    retry_on_failure,
)
from .core.events import (
    DatabaseQueryEndEvent,
    DatabaseQueryStartEvent,
    Event,
    HttpRequestEndEvent,
    HttpRequestErrorEvent,
    HttpRequestStartEvent,
    TestEndEvent,
    TestStartEvent,
)
from .core.middleware import (
    BaseMiddleware,
    Middleware,
    MiddlewareChain,
    SyncMiddleware,
    middleware,
)

# ============= 数据模型 =============
# v3.41.1: 基础模型迁移到 core 层
from .core.models import (
    BaseRequest,
    BaseResponse,
    PageResponse,
)

# 类型和枚举
from .core.types import (
    CaseType,
    DatabaseOperation,
    Decimal,
    DecimalAsCurrency,
    DecimalAsFloat,
    Environment,
    HttpMethod,
    HttpStatus,
    HttpStatusGroup,
    LogLevel,
    Priority,
)

# ============= 扩展系统 (向后兼容，已废弃) =============
# 注意：extensions 模块已废弃，推荐使用 infrastructure.plugins
# ============= 基础设施层 (Layer 1) =============
from .infrastructure import (
    # Config 模型
    DatabaseConfig,
    FrameworkSettings,
    HTTPConfig,
    LoggingConfig,
    RedisConfig,
    SignatureConfig,
    TestExecutionConfig,
    # Config API（v3.36.0 推荐）
    clear_settings_cache,
    get_config,
    get_settings,
    get_settings_for_class,
)
from .infrastructure.context import (
    GrpcContextCarrier,
    HttpContextCarrier,
    MqContextCarrier,
)
from .infrastructure.events import (
    EventBus,
    get_event_bus,
    set_event_bus,
)
from .infrastructure.metrics import (
    PerformanceCollector,
    PerformanceTimer,
    track_performance,
)

# Infrastructure 层 - 插件系统 (v3.14.0 推荐)
from .infrastructure.plugins import (
    HookSpecs,
    PluggyPluginManager,
    hookimpl,  # v3.14.0 统一使用 infrastructure.plugins.hookimpl
)

# v3.40.0: 统一脱敏服务
from .infrastructure.sanitize import (
    SanitizeService,
    clear_sanitize_service,
    get_sanitize_service,
    set_sanitize_service,
)
from .infrastructure.telemetry import (
    NoopTelemetry,
    SpanContext,
    Telemetry,
)

# Plugins - 横切关注点
from .plugins.builtin.monitoring import MonitoringPlugin
from .plugins.builtin.reporting import AllurePlugin

# ============= 设计模式层 =============
# Builder模式
from .testing.data.builders.base import BaseBuilder, DictBuilder
from .testing.data.generators import DataGenerator
from .testing.debugging import (
    ConsoleDebugObserver,  # v3.22.0+，事件驱动调试器
    create_console_debugger,  # v3.22.0+，工厂函数
)

# ============= 测试支持层 =============
# API 自动发现装饰器
from .testing.decorators import api_class, load_api_fixtures
from .testing.fixtures import (
    CleanupManager,
    ListCleanup,
    SimpleCleanupManager,
    database,
    http_client,
    redis_client,
    runtime,
    should_keep_test_data,
)
from .testing.plugins import (
    EnvironmentMarker,
    dev_only,
    get_env,
    is_env,
    prod_only,
    skip_if_dev,
    skip_if_prod,
)
from .testing.reporting.allure import (
    AllureHelper,
    attach_json,
    attach_log,
    attach_screenshot,
    step,
)

# ============= 全部导出 =============
__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    # ===== 异常体系 =====
    "FrameworkError",
    "ConfigurationError",
    "ResourceError",
    "DatabaseError",
    "RedisError",
    "HttpError",
    "ValidationError",
    "ExtensionError",
    "ProviderError",
    "TestError",
    # ===== 基础设施层 =====
    # Bootstrap
    "Bootstrap",
    "BootstrapApp",
    # Runtime
    "RuntimeContext",
    "RuntimeBuilder",
    # Config 模型
    "FrameworkSettings",
    "HTTPConfig",
    "DatabaseConfig",
    "RedisConfig",
    "LoggingConfig",
    "TestExecutionConfig",
    "SignatureConfig",
    # Config API（v3.36.0 推荐）
    "get_settings",
    "get_config",
    "get_settings_for_class",
    "clear_settings_cache",
    # Providers
    "ProviderRegistry",
    "Provider",
    "SingletonProvider",
    "default_providers",
    # ===== 核心功能层 =====
    # HTTP客户端
    "HttpClient",
    "AsyncHttpClient",
    "BaseAPI",
    "BusinessError",
    # HTTP核心对象
    "Request",
    "Response",
    # v3.20.0: 文件类型
    "FileTypes",
    "FilesTypes",
    # v3.16.0: HTTP拦截器已移除
    # GraphQL客户端 (v3.11)
    "GraphQLClient",
    "GraphQLRequest",
    "GraphQLResponse",
    "GraphQLError",
    "QueryBuilder",
    # gRPC客户端 (v3.11)
    "GrpcClient",
    "GrpcResponse",
    "GrpcError",
    # 数据库
    "Database",
    "RedisClient",
    # ===== 设计模式层 =====
    "BaseBuilder",
    "DictBuilder",
    "BaseRepository",
    "QuerySpec",
    # Unit of Work
    "UnitOfWork",
    # ===== 测试支持层 =====
    # Fixtures
    "runtime",
    "http_client",
    "database",
    "redis_client",
    # 数据清理 (v3.11.1)
    "should_keep_test_data",
    "CleanupManager",
    "SimpleCleanupManager",
    "ListCleanup",
    # Plugins
    "AllureHelper",
    "EnvironmentMarker",
    "attach_json",
    "attach_log",
    "attach_screenshot",
    "step",
    "get_env",
    "is_env",
    "skip_if_prod",
    "skip_if_dev",
    "dev_only",
    "prod_only",
    # Debug工具（v3.28.0 重构，统一使用 ConsoleDebugObserver）
    "ConsoleDebugObserver",
    "create_console_debugger",
    # ===== 数据模型 =====
    "BaseRequest",
    "BaseResponse",
    "PageResponse",
    "HttpMethod",
    "Environment",
    "LogLevel",
    "HttpStatus",
    "HttpStatusGroup",
    "DatabaseOperation",
    "Priority",
    "CaseType",
    # ===== 工具函数 =====
    "cache_result",
    "deprecated",
    "log_execution",
    "retry_on_failure",
    "track_performance",
    "PerformanceTimer",
    "PerformanceCollector",
    "DataGenerator",
    "assert_that",
    # ===== 类型工具 (v3.6) =====
    "Decimal",
    "DecimalAsFloat",
    "DecimalAsCurrency",
    # ===== UI模块 =====
    "BasePage",
    "BrowserManager",
    "BrowserType",
    "ElementLocator",
    "LocatorType",
    "WaitHelper",
    # ===== v3.14.0 新增 =====
    # Core 层 - 中间件
    "Middleware",
    "BaseMiddleware",
    "SyncMiddleware",
    "MiddlewareChain",
    "middleware",
    "MiddlewareAbort",
    "MiddlewareError",
    # Core 层 - 上下文
    "ExecutionContext",
    "get_current_context",
    "get_or_create_context",
    "with_context",
    "with_context_async",
    # Core 层 - 事件
    "Event",
    "HttpRequestStartEvent",
    "HttpRequestEndEvent",
    "HttpRequestErrorEvent",
    "DatabaseQueryStartEvent",
    "DatabaseQueryEndEvent",
    "TestStartEvent",
    "TestEndEvent",
    # Infrastructure - 插件系统
    "HookSpecs",
    "PluggyPluginManager",
    "hookimpl",
    # Infrastructure - 遥测
    "Telemetry",
    "NoopTelemetry",
    "SpanContext",
    # Infrastructure - 事件总线
    "EventBus",
    "get_event_bus",
    "set_event_bus",
    # Infrastructure - 上下文载体
    "HttpContextCarrier",
    "GrpcContextCarrier",
    "MqContextCarrier",
    # Infrastructure - 脱敏服务（v3.40.0）
    "SanitizeService",
    "get_sanitize_service",
    "set_sanitize_service",
    "clear_sanitize_service",
    # Capabilities - HTTP 中间件
    "SignatureMiddleware",
    "BearerTokenMiddleware",
    "RetryMiddleware",
    "LoggingMiddleware",
    "HttpTelemetryMiddleware",
    # Plugins
    "MonitoringPlugin",
    "AllurePlugin",
    # Testing - API 自动发现
    "api_class",
    "load_api_fixtures",
]
