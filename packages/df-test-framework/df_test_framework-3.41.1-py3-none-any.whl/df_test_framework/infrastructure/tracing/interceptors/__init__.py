"""追踪拦截器/中间件

提供不同协议的追踪拦截器/中间件实现：
- TracingInterceptor - HTTP 追踪拦截器
- GrpcTracingMiddleware - gRPC 追踪中间件 (v3.32.0 重构为中间件模式)
- 未来可扩展 WebSocket 等拦截器

v3.32.0:
- GrpcTracingInterceptor 重构为 GrpcTracingMiddleware（提供向后兼容别名）
"""

from .grpc import GrpcTracingInterceptor, GrpcTracingMiddleware
from .http import SpanContextCarrier, TracingInterceptor

__all__ = [
    # HTTP
    "TracingInterceptor",
    "SpanContextCarrier",
    # gRPC（v3.32.0 新增中间件模式）
    "GrpcTracingMiddleware",
    "GrpcTracingInterceptor",  # 向后兼容别名
]
