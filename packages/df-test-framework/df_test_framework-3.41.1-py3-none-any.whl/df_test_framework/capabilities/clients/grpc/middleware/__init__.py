"""gRPC 中间件模块

v3.32.0 新增

提供 gRPC 客户端的中间件支持，采用与 HTTP 客户端一致的洋葱模型。

中间件执行流程:
    LoggingMiddleware.before → MetadataMiddleware.before → EventPublisherMiddleware.before
                                        ↓
                                   send_request
                                        ↓
    LoggingMiddleware.after ← MetadataMiddleware.after ← EventPublisherMiddleware.after

使用方式:
    from df_test_framework.capabilities.clients.grpc import GrpcClient
    from df_test_framework.capabilities.clients.grpc.middleware import (
        GrpcLoggingMiddleware,
        GrpcMetadataMiddleware,
    )

    client = GrpcClient(
        "localhost:50051",
        stub_class=MyStub,
        middlewares=[
            GrpcLoggingMiddleware(),
            GrpcMetadataMiddleware({"Authorization": "Bearer token"}),
        ],
    )
"""

from df_test_framework.capabilities.clients.grpc.middleware.base import (
    GrpcMiddleware,
)
from df_test_framework.capabilities.clients.grpc.middleware.event_publisher import (
    GrpcEventPublisherMiddleware,
)
from df_test_framework.capabilities.clients.grpc.middleware.logging import (
    GrpcLoggingMiddleware,
)
from df_test_framework.capabilities.clients.grpc.middleware.metadata import (
    GrpcMetadataMiddleware,
)
from df_test_framework.capabilities.clients.grpc.middleware.retry import (
    GrpcRetryMiddleware,
)
from df_test_framework.capabilities.clients.grpc.middleware.timing import (
    GrpcTimingMiddleware,
)

__all__ = [
    # 基类
    "GrpcMiddleware",
    # 中间件
    "GrpcLoggingMiddleware",
    "GrpcMetadataMiddleware",
    "GrpcRetryMiddleware",
    "GrpcTimingMiddleware",
    "GrpcEventPublisherMiddleware",
]
