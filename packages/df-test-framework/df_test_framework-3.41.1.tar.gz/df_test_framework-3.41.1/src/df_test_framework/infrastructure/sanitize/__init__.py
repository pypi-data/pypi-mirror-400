"""统一脱敏服务模块

v3.40.0 新增：将日志系统、ConsoleDebugObserver、AllureObserver 的脱敏逻辑统一。

使用方式：

    # 1. 获取服务（推荐）
    >>> from df_test_framework.infrastructure.sanitize import get_sanitize_service
    >>> service = get_sanitize_service()
    >>> service.sanitize_value("password", "secret123")
    'secr****t123'

    # 2. 脱敏字典
    >>> service.sanitize_dict({"password": "secret", "name": "test"})
    {'password': 'secr****', 'name': 'test'}

    # 3. 脱敏消息
    >>> service.sanitize_message('Login with password="secret123"')
    'Login with password="******"'

    # 4. 检查敏感字段
    >>> service.is_sensitive("api_key")
    True
    >>> service.is_sensitive("username")
    False

配置示例（config.yaml）：

    sanitize:
      enabled: true
      default_strategy: partial
      keep_prefix: 4
      keep_suffix: 4
      sensitive_keys:
        - password
        - token
        - ".*_secret$"
      logging:
        enabled: true
      console:
        enabled: true
      allure:
        enabled: true
"""

from .service import (
    SanitizeService,
    clear_sanitize_service,
    get_sanitize_service,
    set_sanitize_service,
)

__all__ = [
    "SanitizeService",
    "get_sanitize_service",
    "set_sanitize_service",
    "clear_sanitize_service",
]
