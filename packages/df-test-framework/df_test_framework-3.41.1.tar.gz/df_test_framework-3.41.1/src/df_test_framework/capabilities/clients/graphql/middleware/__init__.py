"""GraphQL 中间件模块

v3.33.0 新增

提供 GraphQL 客户端的中间件系统，复用 core/middleware 的洋葱模型。

使用方式:
    from df_test_framework.capabilities.clients.graphql import GraphQLClient
    from df_test_framework.capabilities.clients.graphql.middleware import (
        GraphQLMiddleware,
        GraphQLLoggingMiddleware,
        GraphQLRetryMiddleware,
        GraphQLEventPublisherMiddleware,
    )

    # 使用内置中间件
    client = GraphQLClient(url).use(
        GraphQLLoggingMiddleware(),
        GraphQLRetryMiddleware(max_retries=3),
    )

    # 自定义中间件
    class MyMiddleware(GraphQLMiddleware):
        async def __call__(self, request, call_next):
            # 前置处理
            response = await call_next(request)
            # 后置处理
            return response

    client.use(MyMiddleware())

优先级说明:
    - priority 越小越先执行 before
    - priority 越大越先执行 after（洋葱模型）
    - GraphQLLoggingMiddleware: priority=0（最先执行）
    - GraphQLRetryMiddleware: priority=10
    - 自定义中间件默认: priority=100
    - GraphQLEventPublisherMiddleware: priority=999（最内层）
"""

from df_test_framework.capabilities.clients.graphql.middleware.base import (
    GraphQLMiddleware,
)
from df_test_framework.capabilities.clients.graphql.middleware.event_publisher import (
    GraphQLEventPublisherMiddleware,
)
from df_test_framework.capabilities.clients.graphql.middleware.logging import (
    GraphQLLoggingMiddleware,
)
from df_test_framework.capabilities.clients.graphql.middleware.retry import (
    GraphQLRetryMiddleware,
)

__all__ = [
    "GraphQLMiddleware",
    "GraphQLEventPublisherMiddleware",
    "GraphQLLoggingMiddleware",
    "GraphQLRetryMiddleware",
]
