"""gRPC 客户端模块

提供 gRPC 服务测试能力，支持：
- Unary RPC（一元调用）
- Server Streaming RPC（服务端流式）
- 元数据（Metadata）管理
- 中间件（Middleware）支持（v3.32.0 重构）
- 健康检查
- 重试策略

v3.32.0:
- 重构为中间件模式（与 HTTP 客户端一致）
- 新增 GrpcEventPublisherMiddleware - gRPC 事件发布中间件
- 支持 Allure 报告和控制台调试

注意：Client Streaming 和 Bidirectional Streaming 计划在后续版本实现。
"""

from df_test_framework.capabilities.clients.grpc.client import GrpcClient
from df_test_framework.capabilities.clients.grpc.middleware import (
    GrpcEventPublisherMiddleware,
    GrpcLoggingMiddleware,
    GrpcMetadataMiddleware,
    GrpcMiddleware,
    GrpcRetryMiddleware,
    GrpcTimingMiddleware,
)
from df_test_framework.capabilities.clients.grpc.models import (
    GrpcError,
    GrpcRequest,
    GrpcResponse,
)

__all__ = [
    # 客户端
    "GrpcClient",
    # 数据模型
    "GrpcRequest",
    "GrpcResponse",
    "GrpcError",
    # 中间件基类
    "GrpcMiddleware",
    # 中间件
    "GrpcLoggingMiddleware",
    "GrpcMetadataMiddleware",
    "GrpcRetryMiddleware",
    "GrpcTimingMiddleware",
    "GrpcEventPublisherMiddleware",
]
