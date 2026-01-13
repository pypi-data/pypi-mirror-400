"""增强的 settings.py 生成模板

v3.35.5: 推荐使用 YAML 配置，此模板作为 .env 模式的增强版本
"""

SETTINGS_ENHANCED_TEMPLATE = """\"\"\"项目配置 - v3.35.5 完全声明式配置

基于 df-test-framework v3.35.5 的测试项目配置。

配置方式（v3.35.0+）:

方式1: YAML 分层配置（推荐）
    配置目录结构:
    config/
    ├── base.yaml              # 基础配置
    ├── environments/
    │   ├── dev.yaml           # 开发环境
    │   ├── test.yaml          # 测试环境
    │   ├── staging.yaml       # 预发布环境
    │   ├── prod.yaml          # 生产环境
    │   └── local.yaml         # 本地配置（不提交git）
    └── secrets/
        └── .env.local         # 敏感信息（不提交git）

    使用:
        pytest tests/ --env=local -s  # 使用本地配置

方式2: .env 环境变量（回退模式）
    - 当 config/base.yaml 不存在时自动回退
    - 无 APP_ 前缀
    - 使用 __ 嵌套分隔符

使用示例:
    # 在 pytest 中使用（通过 env_plugin 自动加载）
    >>> def test_example(settings, current_env):
    ...     print(f"当前环境: {{current_env}}")
    ...     base_url = settings.http.base_url

    # 程序化使用（v3.36.0 现代化 API）
    >>> from df_test_framework import get_settings_for_class
    >>> from myproject.config import MySettings
    >>> settings = get_settings_for_class(MySettings, env="local")
\"\"\"

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from df_test_framework.infrastructure.config import (
    FrameworkSettings,
    HTTPConfig,
    DatabaseConfig,
    RedisConfig,
    ObservabilityConfig,
    LoggingConfig,
    SignatureMiddlewareConfig,
    BearerTokenMiddlewareConfig,
    SignatureAlgorithm,
    TokenSource,
)


# ============================================================
# 业务配置类
# ============================================================

class BusinessConfig:
    \"\"\"业务配置

    清晰的配置分层:
    - 独立于框架配置
    - 包含业务特定的测试数据和配置
    - 使用 BUSINESS_ 前缀的环境变量

    环境变量:
        BUSINESS_TEST_USER_ID - 测试用户ID
        BUSINESS_TEST_ROLE - 测试角色
        BUSINESS_MAX_RETRY_COUNT - 最大重试次数
        BUSINESS_TIMEOUT_SECONDS - 超时时间
    \"\"\"

    def __init__(self):
        import os
        self.test_user_id = os.getenv("BUSINESS_TEST_USER_ID", "test_user_001")
        self.test_role = os.getenv("BUSINESS_TEST_ROLE", "admin")
        self.max_retry_count = int(os.getenv("BUSINESS_MAX_RETRY_COUNT", "3"))
        self.timeout_seconds = int(os.getenv("BUSINESS_TIMEOUT_SECONDS", "30"))


# ============================================================
# 主配置类
# ============================================================

class {ProjectName}Settings(FrameworkSettings):
    \"\"\"项目测试配置（v3.35.5 完全声明式配置）

    v3.35.5 特性:
    - ✅ YAML 分层配置（推荐）
    - ✅ _extends 继承机制
    - ✅ 完全声明式（不需要 load_dotenv() 和 os.getenv()）
    - ✅ 中间件系统配置（自动按优先级排序）
    - ✅ 可观测性集成（日志/Allure 自动记录）
    - ✅ --env 参数切换环境

    配置方式:
        1. YAML 配置（推荐）: config/base.yaml + config/environments/{{env}}.yaml
        2. .env 环境变量（回退模式）

    环境变量配置（.env 回退模式）:
        # 基础配置
        ENV - 环境（dev/test/staging/prod）

        # HTTP 配置
        HTTP__BASE_URL - API基础URL
        HTTP__TIMEOUT - 请求超时时间
        HTTP__MAX_RETRIES - 最大重试次数

        # 签名中间件配置
        SIGNATURE__ENABLED - 签名中间件开关
        SIGNATURE__ALGORITHM - 签名算法（md5/sha256/hmac-sha256）
        SIGNATURE__SECRET - 签名密钥

        # Token 中间件配置
        BEARER_TOKEN__ENABLED - Token中间件开关
        BEARER_TOKEN__SOURCE - Token来源（login/static/env）
        BEARER_TOKEN__LOGIN_URL - 登录URL
        BEARER_TOKEN__CREDENTIALS__USERNAME - 登录用户名
        BEARER_TOKEN__CREDENTIALS__PASSWORD - 登录密码

        # 可观测性配置
        OBSERVABILITY__ENABLED - 总开关
        OBSERVABILITY__DEBUG_OUTPUT - 调试输出（需要 pytest -s）
        OBSERVABILITY__ALLURE_RECORDING - Allure记录

    使用示例:
        # 在 pytest 中使用
        >>> def test_example(settings, current_env):
        ...     print(f"当前环境: {{current_env}}")
        ...     print(settings.http.base_url)
    \"\"\"

    # ========== HTTP 配置 ==========
    http: HTTPConfig = Field(
        default_factory=lambda: HTTPConfig(
            base_url="http://localhost:8000/api",
            timeout=30,
            max_retries=3,
        ),
        description="HTTP配置"
    )

    # ========== 签名中间件配置（可选）==========
    # 取消注释以启用签名中间件
    # signature: SignatureMiddlewareConfig = Field(
    #     default_factory=lambda: SignatureMiddlewareConfig(
    #         enabled=True,
    #         priority=10,
    #         algorithm=SignatureAlgorithm.MD5,
    #         secret="your-secret-key",  # ⚠️ 通过环境变量或 YAML 覆盖
    #         header="X-Sign",
    #         include_paths=["/api/**"],
    #         exclude_paths=["/health", "/metrics"],
    #     ),
    #     description="签名中间件配置"
    # )

    # ========== Bearer Token 中间件配置（可选）==========
    # 取消注释以启用 Bearer Token 中间件
    # bearer_token: BearerTokenMiddlewareConfig = Field(
    #     default_factory=lambda: BearerTokenMiddlewareConfig(
    #         enabled=True,
    #         priority=20,
    #         source=TokenSource.LOGIN,
    #         login_url="/auth/login",
    #         credentials={{"username": "admin", "password": "password"}},  # ⚠️ 通过环境变量或 YAML 覆盖
    #         token_path="data.token",
    #         header="Authorization",
    #         token_prefix="Bearer",
    #         include_paths=["/api/**"],
    #         exclude_paths=["/auth/login", "/auth/register"],
    #     ),
    #     description="Bearer Token中间件配置"
    # )

    # ========== 数据库配置（可选）==========
    # 取消注释以启用数据库
    # db: DatabaseConfig = Field(
    #     default_factory=lambda: DatabaseConfig(
    #         host="localhost",
    #         port=3306,
    #         name="test_db",
    #         user="root",
    #         password="password",  # ⚠️ 通过环境变量或 YAML 覆盖
    #         pool_size=10,
    #         charset="utf8mb4",
    #     ),
    #     description="数据库配置"
    # )

    # ========== Redis 配置（可选）==========
    # 取消注释以启用 Redis
    # redis: RedisConfig = Field(
    #     default_factory=lambda: RedisConfig(
    #         host="localhost",
    #         port=6379,
    #         db=0,
    #         password=None,
    #     ),
    #     description="Redis配置"
    # )

    # ========== 日志配置（v3.38.4 最佳实践） ==========
    logging: LoggingConfig = Field(
        default_factory=lambda: LoggingConfig(
            level="INFO",
            format="text",        # text（开发）或 json（生产）
            # use_utc=False,      # 生产环境建议启用
            # add_callsite=False, # 调试时启用
        ),
        description="日志配置"
    )

    # ========== 可观测性配置 ==========
    observability: ObservabilityConfig = Field(
        default_factory=lambda: ObservabilityConfig(
            enabled=True,
            debug_output=False,  # 设为 True 启用调试输出（需要 pytest -s）
            allure_recording=True,
        ),
        description="可观测性配置"
    )

    # ========== 业务配置 ==========
    @property
    def business(self) -> BusinessConfig:
        \"\"\"获取业务配置\"\"\"
        return BusinessConfig()

    # Pydantic v2 配置
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# ============================================================
# 导出
# ============================================================

__all__ = [
    "{ProjectName}Settings",
    "BusinessConfig",
]
"""

__all__ = ["SETTINGS_ENHANCED_TEMPLATE"]
