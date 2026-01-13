"""GraphQL 中间件基类

v3.33.0 新增

提供 GraphQL 客户端的中间件抽象，复用 core/middleware 的洋葱模型。
"""

from __future__ import annotations

from df_test_framework.capabilities.clients.graphql.models import (
    GraphQLRequest,
    GraphQLResponse,
)
from df_test_framework.core.middleware import BaseMiddleware


class GraphQLMiddleware(BaseMiddleware[GraphQLRequest, GraphQLResponse]):
    """GraphQL 中间件基类

    继承自通用的 BaseMiddleware，专门用于 GraphQL 请求/响应处理。

    v3.33.0 新增

    与 HttpMiddleware、GrpcMiddleware 保持一致的设计。

    使用方式:
        class MyMiddleware(GraphQLMiddleware):
            async def __call__(
                self,
                request: GraphQLRequest,
                call_next: Next[GraphQLRequest, GraphQLResponse],
            ) -> GraphQLResponse:
                # 前置处理
                print(f"Executing {request.operation_type}: {request.operation_name}")

                # 调用下一个中间件
                response = await call_next(request)

                # 后置处理
                print(f"Response has_errors: {response.has_errors}")
                return response

    优先级说明:
        - priority 越小越先执行 before
        - priority 越大越先执行 after（洋葱模型）
        - 默认 priority=100
        - EventPublisherMiddleware 使用 priority=999（最内层）
    """

    def __init__(
        self,
        name: str | None = None,
        priority: int = 100,
    ):
        """初始化 GraphQL 中间件

        Args:
            name: 中间件名称（默认使用类名）
            priority: 优先级（默认 100，数字越小越先执行）
        """
        super().__init__(name=name, priority=priority)
