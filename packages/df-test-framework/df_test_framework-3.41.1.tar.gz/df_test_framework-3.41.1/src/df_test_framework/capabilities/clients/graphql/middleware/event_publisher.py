"""GraphQL 事件发布中间件

v3.33.0 新增

在中间件链的最内层发布 GraphQL 事件，确保能记录到所有中间件修改后的完整请求信息。
"""

from __future__ import annotations

import time

from df_test_framework.capabilities.clients.graphql.middleware.base import (
    GraphQLMiddleware,
)
from df_test_framework.capabilities.clients.graphql.models import (
    GraphQLRequest,
    GraphQLResponse,
)
from df_test_framework.core.events import (
    GraphQLRequestEndEvent,
    GraphQLRequestErrorEvent,
    GraphQLRequestStartEvent,
)
from df_test_framework.core.middleware import Next
from df_test_framework.infrastructure.events import EventBus, get_event_bus


class GraphQLEventPublisherMiddleware(GraphQLMiddleware):
    """GraphQL 事件发布中间件

    v3.33.0 新增

    关键特性：
    - priority=999: 在所有业务中间件之后执行（洋葱模型最内层）
    - 能记录到所有中间件修改后的完整 headers
    - 使用 correlation_id 关联 Start/End 事件

    执行流程（洋葱模型）：
        LoggingMiddleware.before  →  RetryMiddleware.before  →  EventPublisher.before
                                                ↓
                                          发布 StartEvent
                                                ↓
                                           send_request
                                                ↓
                                          发布 EndEvent
                                                ↓
        LoggingMiddleware.after  ←  RetryMiddleware.after  ←  EventPublisher.after

    使用方式:
        # 自动添加（GraphQLClient 默认行为）
        client = GraphQLClient(url="...")

        # 或手动添加
        client.use(GraphQLEventPublisherMiddleware())
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
        enabled: bool = True,
        include_query: bool = True,
        include_variables: bool = False,
        include_response_data: bool = False,
        max_query_length: int = 500,
    ) -> None:
        """初始化事件发布中间件

        Args:
            event_bus: EventBus 实例（可选，默认使用全局 EventBus）
            enabled: 是否启用事件发布（默认 True）
            include_query: 是否在事件中包含查询语句（默认 True）
            include_variables: 是否在事件中包含变量（默认 False，可能包含敏感信息）
            include_response_data: 是否在事件中包含响应数据（默认 False）
            max_query_length: 查询语句最大长度（默认 500，超出则截断）
        """
        # priority=999: 最后执行 before，能看到所有中间件的修改
        super().__init__(name="GraphQLEventPublisherMiddleware", priority=999)
        self._event_bus = event_bus
        self._enabled = enabled
        self._include_query = include_query
        self._include_variables = include_variables
        self._include_response_data = include_response_data
        self._max_query_length = max_query_length

    def _get_event_bus(self) -> EventBus | None:
        """获取 EventBus（优先使用注入的，否则获取全局的）"""
        if self._event_bus:
            return self._event_bus
        return get_event_bus()

    async def __call__(
        self,
        request: GraphQLRequest,
        call_next: Next[GraphQLRequest, GraphQLResponse],
    ) -> GraphQLResponse:
        """发布 GraphQL 事件

        在发送请求前发布 StartEvent，在收到响应后发布 EndEvent。
        此时 request 已经被所有中间件处理过，包含完整的 headers。
        """
        if not self._enabled:
            return await call_next(request)

        event_bus = self._get_event_bus()
        if not event_bus:
            return await call_next(request)

        # 提取请求信息
        query = self._truncate_query(request.query) if self._include_query else None
        variables = request.variables_json if self._include_variables else None

        # 发布请求开始事件
        start_event, correlation_id = GraphQLRequestStartEvent.create(
            url=request.url,
            operation_type=request.operation_type,
            operation_name=request.operation_name,
            query=query,
            variables=variables,
        )
        await event_bus.publish(start_event)

        start_time = time.time()

        try:
            # 调用下一个中间件或发送请求
            response = await call_next(request)
            duration = time.time() - start_time

            # 提取响应数据
            response_data = response.data_json if self._include_response_data else None

            # 发布请求结束事件
            end_event = GraphQLRequestEndEvent.create(
                correlation_id=correlation_id,
                url=request.url,
                operation_type=request.operation_type,
                duration=duration,
                operation_name=request.operation_name,
                has_errors=response.has_errors,
                error_count=len(response.errors) if response.errors else 0,
                data=response_data,
            )
            await event_bus.publish(end_event)

            return response

        except Exception as e:
            duration = time.time() - start_time

            # 发布请求错误事件
            error_event = GraphQLRequestErrorEvent.create(
                correlation_id=correlation_id,
                url=request.url,
                operation_type=request.operation_type,
                error=e,
                duration=duration,
                operation_name=request.operation_name,
            )
            await event_bus.publish(error_event)

            raise

    def _truncate_query(self, query: str) -> str:
        """截断过长的查询语句

        Args:
            query: 原始查询语句

        Returns:
            截断后的查询语句
        """
        if len(query) <= self._max_query_length:
            return query
        return query[: self._max_query_length] + "..."
