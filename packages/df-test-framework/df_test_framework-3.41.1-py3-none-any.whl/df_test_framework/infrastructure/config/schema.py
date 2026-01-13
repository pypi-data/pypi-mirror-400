"""
Configuration schemas used by df-test-framework.

Projects should subclass `FrameworkSettings` to add their own business fields.
"""

from __future__ import annotations

import os
import re
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from df_test_framework.infrastructure.logging import get_logger

from .middleware_schema import (
    BearerTokenMiddlewareConfig,
    MiddlewareConfigUnion,
    SignatureMiddlewareConfig,
)

logger = get_logger(__name__)

# v3.16.0: HTTPSettings 已移除

# v3.35.0: 新增 "local" 环境类型，用于本地开发
EnvLiteral = Literal["local", "dev", "test", "staging", "prod"]
# v3.38.5: 新增 "logfmt" 格式，用于 Loki/Prometheus 等日志系统
LogFormatLiteral = Literal["text", "json", "logfmt"]
LogLevelLiteral = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class PathPattern(BaseModel):
    """路径模式配置

    支持:
    - 精确匹配: "/api/login"
    - 通配符: "/api/**" (匹配所有子路径), "/api/*/health" (匹配单级)
    - 正则表达式: "^/api/v[0-9]+/.*"

    Example:
        >>> pattern = PathPattern(pattern="/api/**", regex=False)
        >>> pattern.matches("/api/master/create")
        True
        >>> pattern.matches("/admin/login")
        False
    """

    pattern: str = Field(description="路径模式")
    regex: bool = Field(default=False, description="是否使用正则表达式")

    def matches(self, path: str) -> bool:
        """检查路径是否匹配

        自动标准化路径，支持有无前导斜杠（仅限通配符模式）。

        Args:
            path: 请求路径 (如: "/api/master/create" 或 "api/master/create")

        Returns:
            是否匹配

        Example:
            >>> pattern = PathPattern(pattern="/api/**")
            >>> pattern.matches("/api/users")  # ✅ True
            >>> pattern.matches("api/users")   # ✅ True (自动标准化)
        """
        # 自动标准化：统一添加前导斜杠
        normalized_path = path if path.startswith("/") else f"/{path}"

        # 正则表达式模式：不做normalize，直接匹配
        if self.regex:
            return bool(re.match(self.pattern, normalized_path))

        # 通配符模式：normalize后再匹配
        normalized_pattern = self.pattern if self.pattern.startswith("/") else f"/{self.pattern}"

        # 通配符匹配:
        # 1. ** → .* (匹配任意字符)
        # 2. * → [^/]* (匹配单级路径，不包含/)
        # 注意: 必须先替换**再替换*,避免**被误替换
        pattern = normalized_pattern.replace("**", "DOUBLE_STAR_PLACEHOLDER")
        pattern = pattern.replace("*", "[^/]*")
        pattern = pattern.replace("DOUBLE_STAR_PLACEHOLDER", ".*")
        return bool(re.match(f"^{pattern}$", normalized_path))


class HTTPConfig(BaseModel):
    """HTTP client configuration.

    v3.16.0: 新增 middlewares 字段
    v3.36.0: 移除已废弃的 interceptors 字段

    v3.22.0: 新增 enable_event_publisher 字段（已废弃）
    v3.23.0: enable_event_publisher 废弃，事件始终发布
    - 事件发布开销极小（无订阅者时几乎为零）
    - 请使用 ObservabilityConfig 控制观察者行为
    """

    base_url: str | None = Field(default="http://localhost:8000", description="API base URL")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout (seconds)")
    max_retries: int = Field(default=3, ge=0, le=10, description="Retry count for transient errors")
    verify_ssl: bool = Field(default=True, description="Whether to verify SSL certificates")
    max_connections: int = Field(default=50, ge=1, le=500, description="Total connection pool size")
    max_keepalive_connections: int = Field(
        default=20, ge=1, le=200, description="Keep-alive pool size"
    )

    # ⚠️ v3.22.0 字段（已废弃）- v3.23.0 起事件始终发布
    # 请使用 ObservabilityConfig 控制 Allure 记录和调试输出
    enable_event_publisher: bool = Field(
        default=True,
        description="⚠️ 已废弃，事件始终发布。请使用 observability.allure_recording 控制 Allure 记录",
    )

    # v3.16.0: 中间件配置系统
    # v3.39.0: 使用 Discriminated Union，Pydantic 根据 type 字段自动解析
    middlewares: list[MiddlewareConfigUnion] = Field(
        default_factory=list, description="HTTP中间件配置列表"
    )

    @field_validator("timeout")
    @classmethod
    def _validate_timeout(cls, value: int) -> int:
        if value < 5:
            raise ValueError("HTTP timeout should not be lower than 5 seconds")
        return value


class DatabaseConfig(BaseModel):
    """Database connectivity configuration."""

    connection_string: str | None = Field(
        default=None,
        description="Database connection string, e.g. mysql+pymysql://user:pass@host/db",
    )
    host: str | None = Field(
        default=None, description="Database host (if connection_string is not set)"
    )
    port: int | None = Field(default=None, ge=1, le=65535, description="Database port")
    name: str | None = Field(default=None, description="Database name/schema")
    user: str | None = Field(default=None, description="Database username")
    password: SecretStr | None = Field(default=None, description="Database password")
    charset: str = Field(default="utf8mb4", description="Connection charset")

    pool_size: int = Field(default=10, ge=1, le=100, description="Connection pool size")
    max_overflow: int = Field(
        default=20, ge=0, le=100, description="Extra connections beyond pool_size"
    )
    pool_timeout: int = Field(default=30, ge=1, le=300, description="Pool timeout (seconds)")
    pool_recycle: int = Field(default=3600, ge=60, description="Connection recycle time (seconds)")
    pool_pre_ping: bool = Field(default=True, description="Enable SQLAlchemy pool pre-ping")
    echo: bool = Field(default=False, description="Enable SQL logging for debugging")

    @field_validator("pool_size")
    @classmethod
    def _validate_pool_size(cls, value: int) -> int:
        if value < 5:
            raise ValueError("Database pool size should not be lower than 5")
        return value

    def resolved_connection_string(self) -> str:
        if self.connection_string:
            return self.connection_string
        required = [self.host, self.port, self.name, self.user, self.password]
        if not all(required):
            raise ValueError(
                "Database configuration incomplete. Set connection_string or provide host/port/name/user/password."
            )
        password = self.password.get_secret_value() if self.password else ""
        return (
            f"mysql+pymysql://{self.user}:{password}"
            f"@{self.host}:{self.port}/{self.name}"
            f"?charset={self.charset}"
        )


class RedisConfig(BaseModel):
    """Redis connectivity configuration."""

    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, ge=1, le=65535, description="Redis port")
    db: int = Field(default=0, ge=0, le=15, description="Redis database index")
    password: SecretStr | None = Field(default=None, description="Redis password")
    decode_responses: bool = Field(default=True, description="Decode bytes to str automatically")
    socket_timeout: int = Field(default=5, ge=1, le=60, description="Socket timeout (seconds)")
    socket_connect_timeout: int = Field(
        default=5, ge=1, le=60, description="Connection timeout (seconds)"
    )
    max_connections: int = Field(default=50, ge=1, le=1000, description="Connection pool size")
    retry_on_timeout: bool = Field(default=True, description="Retry commands on timeout")


class StorageConfig(BaseModel):
    """Storage configuration.

    支持多种存储类型的统一配置

    Example:
        >>> # 配置本地文件存储
        >>> config = StorageConfig(
        ...     local_file=LocalFileConfig(
        ...         base_path="./test-data",
        ...         auto_create_dirs=True
        ...     )
        ... )
        >>>
        >>> # 配置 S3 对象存储
        >>> config = StorageConfig(
        ...     s3=S3Config(
        ...         endpoint_url="http://localhost:9000",
        ...         access_key="minioadmin",
        ...         secret_key="minioadmin",
        ...         bucket_name="test-bucket"
        ...     )
        ... )
        >>>
        >>> # 配置阿里云 OSS 对象存储
        >>> config = StorageConfig(
        ...     oss=OSSConfig(
        ...         access_key_id="LTAI5t...",
        ...         access_key_secret="xxx...",
        ...         bucket_name="my-bucket",
        ...         endpoint="oss-cn-hangzhou.aliyuncs.com"
        ...     )
        ... )
    """

    # 导入存储配置类（延迟导入避免循环依赖）
    local_file: Any | None = Field(
        default=None, description="Local file system storage configuration"
    )
    s3: Any | None = Field(default=None, description="S3-compatible object storage configuration")
    oss: Any | None = Field(default=None, description="Aliyun OSS object storage configuration")


class TestExecutionConfig(BaseModel):
    """Test execution related settings."""

    parallel_workers: int = Field(default=4, ge=1, le=64, description="Parallel worker count")
    retry_times: int = Field(default=0, ge=0, le=5, description="Retry count for flaky tests")
    default_timeout: int = Field(
        default=300, ge=10, le=3600, description="Default case timeout (seconds)"
    )
    keep_test_data: bool = Field(
        default=False,
        description="保留测试数据（不清理），可通过 KEEP_TEST_DATA=1 环境变量或 .env 配置",
    )
    # v3.13.0: Repository 自动发现配置
    repository_package: str | None = Field(
        default=None,
        description="Repository 包路径，启用 UoW 自动发现。例如: 'my_project.repositories'",
    )
    # v3.38.7: API 自动发现配置
    apis_package: str | None = Field(
        default=None,
        description="API 包路径，启用 @api_class 自动发现。例如: 'my_project.apis'",
    )

    @field_validator("keep_test_data", mode="before")
    @classmethod
    def _validate_keep_test_data(cls, value: Any) -> bool:
        """支持多种布尔值表示：1/0, true/false, yes/no"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("1", "true", "yes", "on")
        return bool(value)

    @field_validator("parallel_workers")
    @classmethod
    def _validate_parallel_workers(cls, value: int) -> int:
        cpu_count = os.cpu_count() or 4
        limit = cpu_count * 2
        if value > limit:
            raise ValueError(
                f"parallel_workers ({value}) should not exceed {limit} on this machine"
            )
        return value


class CleanupMapping(BaseModel):
    """单个清理映射配置

    定义清理类型与数据库表的映射关系。

    Attributes:
        table: 数据库表名
        field: 用于清理的字段名（通常是业务主键）

    Example:
        >>> mapping = CleanupMapping(table="card_order", field="customer_order_no")
        >>> # cleanup.add("orders", "ORD001") 会删除 card_order 表中 customer_order_no="ORD001" 的记录
    """

    table: str = Field(description="数据库表名")
    field: str = Field(default="id", description="用于清理的字段名（默认为 id）")


class CleanupConfig(BaseModel):
    """测试数据清理配置（v3.18.0）

    配置驱动的数据清理系统，支持通过环境变量或 .env 文件配置清理映射。

    Attributes:
        enabled: 是否启用配置驱动清理
        mappings: 清理类型到表映射的字典

    Example - .env 配置:
        # 启用清理
        CLEANUP__ENABLED=true

        # 配置映射
        CLEANUP__MAPPINGS__orders__table=card_order
        CLEANUP__MAPPINGS__orders__field=customer_order_no
        CLEANUP__MAPPINGS__cards__table=card_inventory
        CLEANUP__MAPPINGS__cards__field=card_no

    Example - 使用:
        >>> def test_example(cleanup):
        ...     # 创建测试数据
        ...     order_no = create_order()
        ...     # 注册清理
        ...     cleanup.add("orders", order_no)
        ...     # 测试结束后自动清理
    """

    enabled: bool = Field(default=True, description="是否启用配置驱动清理")
    mappings: dict[str, CleanupMapping] = Field(
        default_factory=dict,
        description="清理类型到表映射（如: {'orders': CleanupMapping(table='card_order', field='customer_order_no')}）",
    )

    @field_validator("enabled", mode="before")
    @classmethod
    def _validate_enabled(cls, value: Any) -> bool:
        """支持多种布尔值表示：1/0, true/false, yes/no"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("1", "true", "yes", "on")
        return bool(value)


class ObservabilityConfig(BaseModel):
    """可观测性配置（v3.23.0）

    统一控制事件驱动的可观测性功能：
    - 事件始终由能力层（HTTP/DB/Redis/Storage）发布
    - 通过此配置控制观察者是否消费事件

    设计原则：
    - 事件发布开销极小（无订阅者时几乎为零）
    - 观察者按需订阅，配置集中管理

    Attributes:
        enabled: 总开关，False 时所有观察者都不工作
        allure_recording: 是否将事件记录到 Allure 报告
        debug_output: 是否输出调试信息到控制台

    Example - 环境变量配置:
        # 正常测试：记录 Allure，不输出调试
        OBSERVABILITY__ENABLED=true
        OBSERVABILITY__ALLURE_RECORDING=true
        OBSERVABILITY__DEBUG_OUTPUT=false

        # 调试模式：同时启用
        OBSERVABILITY__DEBUG_OUTPUT=true

        # CI 快速运行：禁用所有
        OBSERVABILITY__ENABLED=false

    Example - 代码中使用:
        >>> from df_test_framework.infrastructure.config import ObservabilityConfig
        >>> config = ObservabilityConfig(
        ...     enabled=True,
        ...     allure_recording=True,
        ...     debug_output=False,
        ... )
    """

    enabled: bool = Field(
        default=True,
        description="总开关：False 时禁用所有可观测性功能（Allure、调试等）",
    )

    allure_recording: bool = Field(
        default=True,
        description="是否将 HTTP/DB/Cache/Storage 事件记录到 Allure 报告",
    )

    debug_output: bool = Field(
        default=False,
        description="是否输出调试信息到控制台（ConsoleDebugObserver）",
    )

    @field_validator("enabled", "allure_recording", "debug_output", mode="before")
    @classmethod
    def _validate_bool(cls, value: Any) -> bool:
        """支持多种布尔值表示：1/0, true/false, yes/no"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("1", "true", "yes", "on")
        return bool(value)


class LoggingConfig(BaseModel):
    """Logging strategy configuration.

    v3.38.4: 新增最佳实践配置项
        - use_utc: 使用 UTC 时间戳（生产环境推荐）
        - use_orjson: 使用 orjson 高性能 JSON 序列化
        - add_callsite: 添加调用位置信息（文件名、函数名、行号）

    v3.38.5: structlog 25.5.0 最佳实践升级
        - format 新增 "logfmt" 选项，用于 Loki/Prometheus 等日志系统
        - add_callsite 在 Python 3.11+ 使用 QUAL_NAME 显示完整限定名
        - 自动处理第三方库的 % 格式化和 extra 参数
    """

    level: LogLevelLiteral = Field(default="INFO", description="Log level")
    format: LogFormatLiteral = Field(
        default="text",
        description="日志输出格式: text(开发), json(生产), logfmt(Loki/Prometheus)",
    )
    file: str | None = Field(default=None, description="Optional log file path")
    rotation: str = Field(
        default="100 MB", description="Log rotation policy (e.g., '100 MB', '1 day')"
    )
    retention: str = Field(
        default="7 days", description="Log retention policy (e.g., '7 days', '30 days')"
    )
    enable_console: bool = Field(default=True, description="Enable console logging")
    # v3.40.0: 已弃用，请使用 FrameworkSettings.sanitize.logging.enabled
    # 保留字段仅为向后兼容，将在 v4.0.0 移除
    sanitize: bool = Field(
        default=True,
        description="[Deprecated] Use sanitize.logging.enabled instead",
    )

    # v3.38.4 新增配置项
    use_utc: bool = Field(
        default=False,
        description="使用 UTC 时间戳（ISO 8601 格式），生产环境推荐启用",
    )
    use_orjson: bool = Field(
        default=True,
        description="使用 orjson 高性能 JSON 序列化（如果已安装）",
    )
    add_callsite: bool = Field(
        default=False,
        description="添加调用位置信息（Python 3.11+ 使用 QUAL_NAME 显示完整限定名）",
    )


class SanitizeStrategy(str, Enum):
    """脱敏策略枚举

    v3.40.0 新增：统一脱敏服务支持多种脱敏策略。

    Attributes:
        FULL: 完全隐藏，替换为 ******
        PARTIAL: 部分保留，保留首尾字符，中间用 **** 替代
        HASH: 哈希值，显示 sha256:a1b2c3...（可用于数据关联但无法还原）
    """

    FULL = "full"
    PARTIAL = "partial"
    HASH = "hash"


class SanitizeContextConfig(BaseModel):
    """各组件独立脱敏开关

    v3.40.0 新增：允许各组件独立控制是否启用脱敏。

    Example:
        >>> config = SanitizeContextConfig(enabled=False)
        >>> # 该组件将不进行脱敏
    """

    enabled: bool = Field(default=True, description="是否启用脱敏")


class SanitizeConfig(BaseModel):
    """统一脱敏配置

    v3.40.0 新增：将日志系统、ConsoleDebugObserver、AllureObserver 的脱敏逻辑统一。

    特性：
    - 共享敏感字段定义（支持正则匹配）
    - 多种脱敏策略（完全隐藏、部分保留、哈希）
    - 各组件独立开关控制
    - 配置驱动（YAML/环境变量）

    Example:
        >>> config = SanitizeConfig(
        ...     enabled=True,
        ...     default_strategy=SanitizeStrategy.PARTIAL,
        ...     sensitive_keys=["password", "token", ".*_secret$"],
        ... )

    环境变量配置示例：
        SANITIZE__ENABLED=true
        SANITIZE__DEFAULT_STRATEGY=partial
        SANITIZE__KEEP_PREFIX=4
        SANITIZE__KEEP_SUFFIX=4
        SANITIZE__LOGGING__ENABLED=true
        SANITIZE__CONSOLE__ENABLED=false  # 本地调试时关闭
        SANITIZE__ALLURE__ENABLED=true
    """

    enabled: bool = Field(default=True, description="是否启用脱敏（全局开关）")

    # 敏感字段列表（支持正则表达式）
    sensitive_keys: list[str] = Field(
        default=[
            # 密码相关
            "password",
            "passwd",
            "pwd",
            # Token 相关
            "token",
            "access_token",
            "refresh_token",
            # 密钥相关
            "secret",
            "api_key",
            "apikey",
            # 认证相关
            "authorization",
            "auth",
            "credential",
            # HTTP Header 风格
            "x-token",
            "x-api-key",
            "x-sign",
            "x-signature",
        ],
        description="敏感字段名列表（支持正则表达式，如 '.*_key$'）",
    )

    # 敏感正则模式（用于消息内容脱敏）
    sensitive_patterns: list[str] = Field(
        default=[
            r'(password["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)',
            r'(token["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)',
            r'(secret["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)',
            r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)',
            r'(authorization["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)',
            r'(credential["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)',
        ],
        description="敏感内容正则表达式（用于日志消息脱敏）",
    )

    # 默认脱敏策略
    default_strategy: SanitizeStrategy = Field(
        default=SanitizeStrategy.PARTIAL,
        description="默认脱敏策略: full(完全隐藏), partial(部分保留), hash(哈希值)",
    )

    # 部分保留策略参数
    keep_prefix: int = Field(default=4, ge=0, description="部分保留时，保留前缀字符数")
    keep_suffix: int = Field(default=4, ge=0, description="部分保留时，保留后缀字符数")

    # 脱敏占位符
    mask_char: str = Field(default="*", max_length=1, description="脱敏占位字符")
    mask_value: str = Field(default="******", description="完全脱敏时的替换值")

    # 各组件独立开关
    logging: SanitizeContextConfig = Field(
        default_factory=SanitizeContextConfig,
        description="日志系统脱敏配置",
    )
    console: SanitizeContextConfig = Field(
        default_factory=SanitizeContextConfig,
        description="控制台调试输出脱敏配置",
    )
    allure: SanitizeContextConfig = Field(
        default_factory=SanitizeContextConfig,
        description="Allure 报告脱敏配置",
    )


class SignatureConfig(BaseModel):
    """Signature authentication configuration.

    用于配置HTTP签名认证的参数

    Example:
        >>> config = SignatureConfig(
        ...     enabled=True,
        ...     algorithm="md5",
        ...     secret="my_secret",
        ...     header_name="X-Sign"
        ... )
    """

    enabled: bool = Field(default=True, description="是否启用签名验证")

    algorithm: Literal["md5", "sha256", "hmac-sha256", "hmac-sha512"] = Field(
        default="md5", description="签名算法"
    )

    secret: str = Field(description="签名密钥")

    header_name: str = Field(default="X-Sign", description="签名Header名称")

    # 高级配置
    include_query_params: bool = Field(default=True, description="是否包含URL查询参数")

    include_json_body: bool = Field(default=True, description="是否包含JSON请求体")

    include_form_data: bool = Field(default=False, description="是否包含表单数据")


class FrameworkSettings(BaseSettings):
    """
    Base configuration schema for df-test-framework.

    Projects should inherit this class and extend with their own business settings.

    ✅ v3.5+: 现代化配置设计
    - 完全声明式配置（不依赖os.getenv()）
    - 嵌套配置（HTTPSettings → Middlewares）
    - 类型安全和自动验证
    - 不需要load_dotenv()

    ✅ v3.18.0: 移除 APP_ 前缀
    - 环境变量和 .env 文件配置统一使用嵌套键分隔符（双下划线）
    - 配置更简洁：TEST__REPOSITORY_PACKAGE 而非 APP_TEST__REPOSITORY_PACKAGE

    ✅ v3.18.1: 顶层中间件配置
    - 签名中间件和 Token 中间件可通过环境变量配置
    - 无需在代码中硬编码中间件配置

    环境变量配置示例：
        # 测试执行配置
        TEST__REPOSITORY_PACKAGE=my_project.repositories  # UoW Repository 自动发现
        TEST__KEEP_TEST_DATA=1                            # 保留测试数据

        # HTTP配置
        HTTP__BASE_URL=https://api.example.com            # API基础URL
        HTTP__TIMEOUT=30                                  # 请求超时时间

        # v3.18.1: 签名中间件配置（顶层）
        SIGNATURE__ENABLED=true                           # 启用签名
        SIGNATURE__ALGORITHM=md5                          # 签名算法
        SIGNATURE__SECRET=your_secret                     # 签名密钥
        SIGNATURE__HEADER=X-Sign                          # 签名 Header
        SIGNATURE__INCLUDE_PATHS=/api/**,/master/**       # 路径白名单

        # v3.18.1: Bearer Token 中间件配置（顶层）
        BEARER_TOKEN__ENABLED=true                        # 启用 Token
        BEARER_TOKEN__SOURCE=login                        # Token 来源
        BEARER_TOKEN__LOGIN_URL=/auth/login               # 登录接口
        BEARER_TOKEN__CREDENTIALS__username=admin         # 用户名
        BEARER_TOKEN__CREDENTIALS__password=pass          # 密码
        BEARER_TOKEN__TOKEN_PATH=data.token               # Token 路径
        BEARER_TOKEN__INCLUDE_PATHS=/admin/**             # 路径白名单
        BEARER_TOKEN__EXCLUDE_PATHS=/admin/login          # 路径黑名单

        # 数据库配置
        DB__HOST=localhost                                # 数据库主机
        DB__PORT=3306                                     # 数据库端口

        # Redis配置
        REDIS__HOST=localhost                             # Redis主机
        REDIS__PORT=6379                                  # Redis端口

        # v3.18.0: 清理配置
        CLEANUP__ENABLED=true                             # 启用清理
        CLEANUP__MAPPINGS__orders__table=card_order       # 清理映射
    """

    env: EnvLiteral = Field(default="test", description="Runtime environment")
    debug: bool = Field(default=False, description="Enable debug mode")

    # v3.23.0: 统一可观测性配置（推荐）
    observability: ObservabilityConfig | None = Field(
        default_factory=ObservabilityConfig,
        description="可观测性配置（v3.23.0）：统一控制 Allure 记录和调试输出",
    )

    # ⚠️ v3.5 旧字段（已废弃，请迁移到 observability 配置）
    # 保留用于向后兼容，v3.24.0 将移除
    enable_observability: bool = Field(
        default=True,
        description="⚠️ 已废弃，请使用 observability.enabled",
    )
    enable_allure: bool = Field(
        default=True,
        description="⚠️ 已废弃，请使用 observability.allure_recording",
    )
    observability_level: LogLevelLiteral = Field(
        default="INFO",
        description="⚠️ 已废弃，请使用 logging.level",
    )

    # v3.16.0: http_settings 字段已移除
    # 请使用 HTTPConfig 和 middleware 配置
    http: HTTPConfig = Field(default_factory=HTTPConfig, description="HTTP configuration")

    db: DatabaseConfig | None = Field(
        default_factory=DatabaseConfig, description="Database configuration"
    )
    redis: RedisConfig | None = Field(
        default_factory=RedisConfig, description="Redis configuration"
    )
    storage: StorageConfig | None = Field(
        default_factory=StorageConfig, description="Storage configuration"
    )
    test: TestExecutionConfig | None = Field(
        default_factory=TestExecutionConfig, description="Test execution configuration"
    )
    # v3.18.0: 配置驱动的数据清理
    cleanup: CleanupConfig | None = Field(
        default=None, description="Data cleanup configuration (v3.18.0)"
    )
    logging: LoggingConfig | None = Field(
        default_factory=LoggingConfig, description="Logging configuration"
    )

    # v3.40.0: 统一脱敏配置
    sanitize: SanitizeConfig | None = Field(
        default_factory=SanitizeConfig,
        description="统一脱敏配置（v3.40.0）：控制日志/调试/报告中的敏感数据脱敏",
    )

    # v3.18.1: 顶层中间件配置（可通过环境变量配置）
    signature: SignatureMiddlewareConfig | None = Field(
        default=None,
        description="签名中间件配置（v3.18.1）。启用后自动添加到 HTTP 中间件链。",
    )
    bearer_token: BearerTokenMiddlewareConfig | None = Field(
        default=None,
        description="Bearer Token 中间件配置（v3.18.1）。启用后自动添加到 HTTP 中间件链。",
    )

    extras: dict = Field(
        default_factory=dict, description="Arbitrary extra configuration namespace"
    )

    # v3.16.0: _init_http_settings 和 get_http_config 已移除
    # http 现在是直接字段，不再是计算属性

    # v3.35.0: 新增 is_local 属性
    @property
    def is_local(self) -> bool:
        return self.env == "local"

    @property
    def is_dev(self) -> bool:
        return self.env == "dev"

    @property
    def is_test(self) -> bool:
        return self.env == "test"

    @property
    def is_staging(self) -> bool:
        return self.env == "staging"

    @property
    def is_prod(self) -> bool:
        return self.env == "prod"

    @field_validator("env")
    @classmethod
    def _validate_env(cls, value: EnvLiteral) -> EnvLiteral:
        if value == "prod" and os.getenv("CI") == "true":
            raise ValueError("Running production configuration in CI is not allowed")
        return value

    @field_validator("debug")
    @classmethod
    def _validate_debug(cls, value: bool, info) -> bool:
        env = info.data.get("env", "test")
        if value and env == "prod":
            raise ValueError("Debug mode must not be enabled in production")
        return value

    @model_validator(mode="after")
    def _merge_toplevel_middlewares(self) -> FrameworkSettings:
        """v3.18.1: 自动将顶层中间件配置合并到 http.middlewares

        合并规则:
        1. 如果 signature 已配置且 enabled=True，添加到 http.middlewares
        2. 如果 bearer_token 已配置且 enabled=True，添加到 http.middlewares
        3. 顶层配置优先级低于 http.middlewares 中已有的同类型中间件

        Note:
            顶层配置只有在对应中间件类型尚未存在于 http.middlewares 中时才会添加。
            这样可以保持向后兼容性：如果用户已经在 http.middlewares 中配置了中间件，
            顶层配置不会覆盖它。
        """
        from .middleware_schema import (
            MiddlewareType,
        )

        # 检查 http.middlewares 中已有的中间件类型
        existing_types = set()
        for mw in self.http.middlewares:
            if hasattr(mw, "type"):
                existing_types.add(mw.type)

        # 合并 signature 配置
        if self.signature is not None and self.signature.enabled:
            if MiddlewareType.SIGNATURE not in existing_types:
                self.http.middlewares.append(self.signature)
                logger.debug(
                    "[FrameworkSettings] ✅ 已将顶层 signature 配置合并到 http.middlewares"
                )
            else:
                logger.debug(
                    "[FrameworkSettings] ⏭️  http.middlewares 已包含 signature 中间件，跳过顶层配置"
                )

        # 合并 bearer_token 配置
        if self.bearer_token is not None and self.bearer_token.enabled:
            if MiddlewareType.BEARER_TOKEN not in existing_types:
                self.http.middlewares.append(self.bearer_token)
                logger.debug(
                    "[FrameworkSettings] ✅ 已将顶层 bearer_token 配置合并到 http.middlewares"
                )
            else:
                logger.debug(
                    "[FrameworkSettings] ⏭️  http.middlewares 已包含 bearer_token 中间件，跳过顶层配置"
                )

        return self

    # v3.35.0: 多环境配置加载
    @classmethod
    def for_environment(cls, env: str) -> FrameworkSettings:
        """为指定环境创建配置对象

        加载顺序（优先级从低到高）：
        1. .env（基础配置）
        2. .env.{env}（环境特定配置）
        3. 环境变量（最高优先级）

        此方法利用 pydantic-settings 的多文件加载特性，自动合并
        基础配置和环境特定配置。

        Args:
            env: 环境名称（local/dev/test/staging/prod）

        Returns:
            配置对象实例

        Example:
            >>> settings = MySettings.for_environment("staging")
            >>> print(settings.http.base_url)  # 来自 .env.staging
            >>> print(settings.env)  # "staging"

            >>> # 也可以使用自定义环境名
            >>> settings = MySettings.for_environment("qa")
            >>> # 加载 .env + .env.qa

        Note:
            - 如果环境特定文件（.env.{env}）不存在，只加载 .env
            - 环境变量始终具有最高优先级，会覆盖文件中的配置
        """
        from pathlib import Path

        # 构建环境文件列表
        env_files: list[str] = [".env"]
        env_specific = f".env.{env}"

        # 检查环境特定文件是否存在
        if Path(env_specific).exists():
            env_files.append(env_specific)

        # 使用 pydantic-settings 的 _env_file 参数加载多个文件
        return cls(_env_file=tuple(env_files))

    # Pydantic v2配置
    # v3.18.0: 移除 APP_ 前缀，与 ConfigPipeline 加载保持一致
    # 配置示例: TEST__REPOSITORY_PACKAGE, DB__HOST, HTTP__BASE_URL
    model_config = SettingsConfigDict(
        env_prefix="",  # v3.18.0: 移除前缀，配置更简洁
        case_sensitive=False,
        env_nested_delimiter="__",
        env_ignore_empty=True,
        extra="allow",
        env_file=".env",
        env_file_encoding="utf-8",
    )
