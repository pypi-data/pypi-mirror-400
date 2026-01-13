"""GraphQL 重试中间件

v3.33.0 新增
"""

from __future__ import annotations

import asyncio

import httpx

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


class GraphQLRetryMiddleware(GraphQLMiddleware):
    """GraphQL 重试中间件

    v3.33.0 新增

    在网络错误或 GraphQL 错误时自动重试请求。

    使用方式:
        client = GraphQLClient(url).use(GraphQLRetryMiddleware())

        # 自定义配置
        client = GraphQLClient(url).use(
            GraphQLRetryMiddleware(
                max_retries=3,
                retry_delay=1.0,
                retry_on_network_error=True,
                retry_on_graphql_error=False,
            )
        )
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        retry_on_network_error: bool = True,
        retry_on_graphql_error: bool = False,
        priority: int = 10,
    ) -> None:
        """初始化重试中间件

        Args:
            max_retries: 最大重试次数（默认 3）
            retry_delay: 重试延迟秒数（默认 1.0）
            retry_on_network_error: 是否在网络错误时重试（默认 True）
            retry_on_graphql_error: 是否在 GraphQL 错误时重试（默认 False）
            priority: 优先级（默认 10）
        """
        super().__init__(name="GraphQLRetryMiddleware", priority=priority)
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._retry_on_network_error = retry_on_network_error
        self._retry_on_graphql_error = retry_on_graphql_error

    async def __call__(
        self,
        request: GraphQLRequest,
        call_next: Next[GraphQLRequest, GraphQLResponse],
    ) -> GraphQLResponse:
        """执行重试逻辑"""
        last_error: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = await call_next(request)

                # 检查是否需要重试 GraphQL 错误
                if self._retry_on_graphql_error and response.has_errors:
                    if attempt < self._max_retries:
                        logger.warning(
                            f"GraphQL errors detected, retrying "
                            f"(attempt {attempt + 1}/{self._max_retries + 1})"
                        )
                        await asyncio.sleep(self._retry_delay)
                        continue

                return response

            except (httpx.HTTPError, httpx.TimeoutException, ConnectionError) as e:
                last_error = e

                if not self._retry_on_network_error:
                    raise

                if attempt >= self._max_retries:
                    logger.error(
                        f"GraphQL request failed after {self._max_retries + 1} attempts: {e}"
                    )
                    raise

                logger.warning(
                    f"Network error: {e}, retrying (attempt {attempt + 1}/{self._max_retries + 1})"
                )
                await asyncio.sleep(self._retry_delay)

        # 不应该到达这里，但为了类型安全
        if last_error:
            raise last_error
        raise RuntimeError("Unexpected retry loop exit")
