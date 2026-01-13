"""弹性工具模块

提供系统弹性相关的工具，包括熔断器、重试等机制。

模块:
- circuit_breaker: 熔断器模式实现

使用示例:
    >>> from df_test_framework.infrastructure.resilience import (
    ...     CircuitBreaker,
    ...     CircuitOpenError,
    ...     CircuitState,
    ...     circuit_breaker,
    ... )
    >>>
    >>> # 基础使用
    >>> breaker = CircuitBreaker(failure_threshold=3)
    >>> result = breaker.call(risky_function)
    >>>
    >>> # 装饰器使用
    >>> @circuit_breaker(failure_threshold=5)
    ... def call_api():
    ...     return requests.get("https://api.example.com")

v3.7.0: 初始实现 (utils/resilience.py)
v3.29.0: 迁移到 infrastructure/resilience/
"""

from .circuit_breaker import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
    circuit_breaker,
)

__all__ = [
    "CircuitState",
    "CircuitBreaker",
    "CircuitOpenError",
    "circuit_breaker",
]
