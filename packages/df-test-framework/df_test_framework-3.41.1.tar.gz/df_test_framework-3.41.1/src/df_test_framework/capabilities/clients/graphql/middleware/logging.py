"""GraphQL 日志中间件

v3.33.0 新增
"""

from __future__ import annotations

from df_test_framework.capabilities.clients.graphql.middleware.base import (
    GraphQLMiddleware,
)
from df_test_framework.capabilities.clients.graphql.models import (
    GraphQLRequest,
    GraphQLResponse,
)
from df_test_framework.core.middleware import Next
from df_test_framework.infrastructure.logging import get_logger

logger = get_logger(__name__)


class GraphQLLoggingMiddleware(GraphQLMiddleware):
    """GraphQL 日志中间件

    v3.33.0 新增

    记录 GraphQL 请求和响应的日志信息。

    使用方式:
        client = GraphQLClient(url).use(GraphQLLoggingMiddleware())

        # 自定义配置
        client = GraphQLClient(url).use(
            GraphQLLoggingMiddleware(
                log_query=True,
                log_variables=False,  # 不记录变量（可能包含敏感信息）
                log_response=False,
                max_query_length=200,
            )
        )
    """

    def __init__(
        self,
        log_query: bool = True,
        log_variables: bool = False,
        log_response: bool = False,
        max_query_length: int = 200,
        priority: int = 0,
    ) -> None:
        """初始化日志中间件

        Args:
            log_query: 是否记录查询语句（默认 True）
            log_variables: 是否记录变量（默认 False，可能包含敏感信息）
            log_response: 是否记录响应数据（默认 False）
            max_query_length: 查询语句最大显示长度（默认 200）
            priority: 优先级（默认 0，最先执行）
        """
        super().__init__(name="GraphQLLoggingMiddleware", priority=priority)
        self._log_query = log_query
        self._log_variables = log_variables
        self._log_response = log_response
        self._max_query_length = max_query_length

    async def __call__(
        self,
        request: GraphQLRequest,
        call_next: Next[GraphQLRequest, GraphQLResponse],
    ) -> GraphQLResponse:
        """执行日志记录"""
        # 记录请求信息
        operation_name = request.operation_name or "anonymous"
        logger.info(f"GraphQL {request.operation_type}: {operation_name}")

        if self._log_query:
            query_display = request.query
            if len(query_display) > self._max_query_length:
                query_display = query_display[: self._max_query_length] + "..."
            logger.debug(f"Query: {query_display}")

        if self._log_variables and request.variables:
            logger.debug(f"Variables: {request.variables}")

        # 调用下一个中间件
        response = await call_next(request)

        # 记录响应信息
        if response.has_errors:
            error_count = len(response.errors) if response.errors else 0
            logger.warning(f"GraphQL response has {error_count} error(s)")
            if response.errors:
                for error in response.errors[:3]:  # 最多显示 3 个错误
                    logger.warning(f"  - {error.message}")
        else:
            logger.info("GraphQL response: success")

        if self._log_response and response.data:
            logger.debug(f"Response data: {response.data_json}")

        return response
