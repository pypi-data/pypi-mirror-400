"""
事件类型定义

定义框架中使用的各种事件类型。

注意: 事件总线的具体实现在 infrastructure/events/ 中。
"""

from df_test_framework.core.events.types import (
    # Cache 事件
    CacheOperationEndEvent,
    CacheOperationErrorEvent,
    CacheOperationStartEvent,
    DatabaseQueryEndEvent,
    DatabaseQueryErrorEvent,
    # Database 事件
    DatabaseQueryStartEvent,
    Event,
    # GraphQL 事件 (v3.33.0)
    GraphQLRequestEndEvent,
    GraphQLRequestErrorEvent,
    GraphQLRequestStartEvent,
    # gRPC 事件 (v3.32.0)
    GrpcRequestEndEvent,
    GrpcRequestErrorEvent,
    GrpcRequestStartEvent,
    HttpRequestEndEvent,
    HttpRequestErrorEvent,
    # HTTP 事件
    HttpRequestStartEvent,
    # MQ 消费事件 (v3.34.1 重构)
    MessageConsumeEndEvent,
    MessageConsumeErrorEvent,
    MessageConsumeStartEvent,
    # MQ 发布事件 (v3.34.1 重构)
    MessagePublishEndEvent,
    MessagePublishErrorEvent,
    MessagePublishStartEvent,
    # 中间件事件
    MiddlewareExecuteEvent,
    # Storage 事件
    StorageOperationEndEvent,
    StorageOperationErrorEvent,
    StorageOperationStartEvent,
    TestEndEvent,
    # 测试事件
    TestStartEvent,
    # 事务事件
    TransactionCommitEvent,
    TransactionRollbackEvent,
    # UI 事件 (v3.35.7)
    UIClickEvent,
    UIErrorEvent,
    UIInputEvent,
    UINavigationEndEvent,
    UINavigationStartEvent,
    UIScreenshotEvent,
    UIWaitEvent,
)

__all__ = [
    "Event",
    # HTTP
    "HttpRequestStartEvent",
    "HttpRequestEndEvent",
    "HttpRequestErrorEvent",
    # 中间件
    "MiddlewareExecuteEvent",
    # GraphQL (v3.33.0)
    "GraphQLRequestStartEvent",
    "GraphQLRequestEndEvent",
    "GraphQLRequestErrorEvent",
    # gRPC (v3.32.0)
    "GrpcRequestStartEvent",
    "GrpcRequestEndEvent",
    "GrpcRequestErrorEvent",
    # Database
    "DatabaseQueryStartEvent",
    "DatabaseQueryEndEvent",
    "DatabaseQueryErrorEvent",
    # Cache
    "CacheOperationStartEvent",
    "CacheOperationEndEvent",
    "CacheOperationErrorEvent",
    # MQ 发布 (v3.34.1 重构)
    "MessagePublishStartEvent",
    "MessagePublishEndEvent",
    "MessagePublishErrorEvent",
    # MQ 消费 (v3.34.1 重构)
    "MessageConsumeStartEvent",
    "MessageConsumeEndEvent",
    "MessageConsumeErrorEvent",
    # Storage
    "StorageOperationStartEvent",
    "StorageOperationEndEvent",
    "StorageOperationErrorEvent",
    # 测试
    "TestStartEvent",
    "TestEndEvent",
    # 事务
    "TransactionCommitEvent",
    "TransactionRollbackEvent",
    # UI (v3.35.7)
    "UINavigationStartEvent",
    "UINavigationEndEvent",
    "UIClickEvent",
    "UIInputEvent",
    "UIScreenshotEvent",
    "UIWaitEvent",
    "UIErrorEvent",
]
