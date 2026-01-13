"""基础设施层 (Layer 1) - Config、Logging、Telemetry、Events、Plugins、Resilience

v3.16.0 架构重构:
- Bootstrap、Providers、Runtime 已迁移到 bootstrap/ (Layer 4)
- 请从 df_test_framework.bootstrap 导入这些模块

v3.29.0:
- 新增 resilience 模块 (从 utils/ 迁移)

v3.35.0:
- 新增多环境配置支持 (for_environment 方法)

v3.36.0:
- 现代化配置 API: get_settings(), get_config(), get_settings_for_class()
- 删除废弃的 manager.py（configure_settings/clear_settings）
- 删除 registry.py（ConfigRegistry 已移除）

v3.38.2:
- 日志系统迁移: loguru → structlog
- 新增: configure_logging(), get_logger(), Logger Protocol
- 移除: LoggerStrategy, LoguruStructuredStrategy, NoOpStrategy, strategies.py, pytest_integration.py

v3.40.0:
- 新增统一脱敏服务 (infrastructure/sanitize/)
- SanitizeConfig 配置类，支持多策略脱敏
- 日志/Console/Allure 统一脱敏规则
"""

from .config import (
    # 配置模型
    DatabaseConfig,
    FrameworkSettings,
    HTTPConfig,
    LoggingConfig,
    RedisConfig,
    SanitizeConfig,
    SanitizeContextConfig,
    SanitizeStrategy,
    SignatureConfig,
    TestExecutionConfig,
    # 配置 API（v3.36.0 推荐）
    clear_settings_cache,
    get_config,
    get_settings,
    get_settings_for_class,
)
from .logging import (
    # v3.38.2: structlog 日志系统
    Logger,
    configure_logging,
    get_logger,
    is_logger_configured,
    reset_logging,
)
from .resilience import CircuitBreaker, CircuitOpenError, CircuitState, circuit_breaker

__all__ = [
    # Config 模型
    "FrameworkSettings",
    "HTTPConfig",
    "DatabaseConfig",
    "RedisConfig",
    "LoggingConfig",
    "TestExecutionConfig",
    "SignatureConfig",
    # Sanitize Config（v3.40.0）
    "SanitizeConfig",
    "SanitizeContextConfig",
    "SanitizeStrategy",
    # Config API（v3.36.0 推荐）
    "get_settings",
    "get_config",
    "get_settings_for_class",
    "clear_settings_cache",
    # Logging（v3.38.2 structlog）
    "Logger",
    "configure_logging",
    "get_logger",
    "is_logger_configured",
    "reset_logging",
    # Resilience (v3.29.0)
    "CircuitState",
    "CircuitBreaker",
    "CircuitOpenError",
    "circuit_breaker",
]
