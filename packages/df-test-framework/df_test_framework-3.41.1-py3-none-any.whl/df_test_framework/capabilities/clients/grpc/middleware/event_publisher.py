"""gRPC 事件发布中间件

v3.32.0 新增

在中间件链的最内层发布 gRPC 事件，确保能记录到所有中间件修改后的完整请求信息。
"""

from __future__ import annotations

import time
from collections.abc import Callable, Coroutine
from typing import Any

from df_test_framework.capabilities.clients.grpc.middleware.base import GrpcMiddleware
from df_test_framework.capabilities.clients.grpc.models import GrpcRequest, GrpcResponse
from df_test_framework.core.events import (
    GrpcRequestEndEvent,
    GrpcRequestErrorEvent,
    GrpcRequestStartEvent,
)
from df_test_framework.infrastructure.events import EventBus, get_event_bus


class GrpcEventPublisherMiddleware(GrpcMiddleware):
    """gRPC 事件发布中间件

    v3.32.0 新增

    关键特性：
    - priority=999: 在所有业务中间件之后执行（洋葱模型最内层）
    - 能记录到所有中间件修改后的完整 metadata
    - 使用 correlation_id 关联 Start/End/Error 事件
    - 集成 OpenTelemetry 追踪上下文

    执行流程（洋葱模型）：
        MetadataMiddleware.before → LoggingMiddleware.before → EventPublisher.before
                                        ↓
                                  发布 StartEvent
                                        ↓
                                   send_request
                                        ↓
                                  发布 EndEvent
                                        ↓
        MetadataMiddleware.after ← LoggingMiddleware.after ← EventPublisher.after

    使用方式:
        # 自动添加（GrpcClient 默认行为）
        client = GrpcClient("localhost:50051", stub_class=MyStub)

        # 或手动添加
        client = GrpcClient(
            "localhost:50051",
            stub_class=MyStub,
            enable_events=False,  # 禁用自动添加
            middlewares=[GrpcEventPublisherMiddleware()],
        )
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
        service_name: str = "",
        enabled: bool = True,
        log_request_data: bool = True,
        log_response_data: bool = True,
        max_data_length: int = 1000,
    ):
        """初始化事件发布中间件

        Args:
            event_bus: EventBus 实例（可选，默认使用全局 EventBus）
            service_name: 服务名称（用于事件记录）
            enabled: 是否启用事件发布（默认 True）
            log_request_data: 是否记录请求数据（默认 True）
            log_response_data: 是否记录响应数据（默认 True）
            max_data_length: 数据最大长度（超过则截断）
        """
        # priority=999: 最后执行 before，能看到所有中间件的修改
        super().__init__(name="GrpcEventPublisherMiddleware", priority=999)
        self._event_bus = event_bus
        self._service_name = service_name
        self._enabled = enabled
        self._log_request_data = log_request_data
        self._log_response_data = log_response_data
        self._max_data_length = max_data_length

    def _get_event_bus(self) -> EventBus | None:
        """获取 EventBus（优先使用注入的，否则获取全局的）"""
        if self._event_bus:
            return self._event_bus
        return get_event_bus()

    def _serialize_data(self, data: Any) -> str | None:
        """序列化数据为字符串

        Args:
            data: 要序列化的数据

        Returns:
            序列化后的字符串，或 None
        """
        if data is None:
            return None

        try:
            # 尝试使用 protobuf 的 MessageToJson
            try:
                from google.protobuf.json_format import MessageToJson

                result = MessageToJson(data, preserving_proto_field_name=True)
            except (ImportError, AttributeError, TypeError):
                # 回退到 str
                result = str(data)

            # 截断过长的数据
            if len(result) > self._max_data_length:
                result = result[: self._max_data_length] + "... (truncated)"

            return result
        except Exception:
            return f"<unable to serialize: {type(data).__name__}>"

    async def __call__(
        self,
        request: GrpcRequest,
        call_next: Callable[[GrpcRequest], Coroutine[None, None, GrpcResponse]],
    ) -> GrpcResponse:
        """发布 gRPC 事件"""
        if not self._enabled:
            return await call_next(request)

        event_bus = self._get_event_bus()
        if not event_bus:
            return await call_next(request)

        # 准备请求数据
        request_data = None
        if self._log_request_data:
            request_data = self._serialize_data(request.message)

        # 发布开始事件
        start_event, correlation_id = GrpcRequestStartEvent.create(
            service=self._service_name,
            method=request.method,
            metadata=request.metadata_dict,
            request_data=request_data,
        )
        await event_bus.publish(start_event)

        # 记录开始时间
        start_time = time.time()

        # 添加 correlation_id 到 metadata
        request = request.with_metadata("x-correlation-id", correlation_id)

        try:
            # 调用下一个中间件
            response = await call_next(request)

            # 计算耗时
            duration = time.time() - start_time

            # 准备响应数据
            response_data = None
            if self._log_response_data:
                response_data = self._serialize_data(response.data)

            # 发布结束事件
            end_event = GrpcRequestEndEvent.create(
                correlation_id=correlation_id,
                service=self._service_name,
                method=request.method,
                status_code=response.status_code.value,
                duration=duration,
                response_data=response_data,
            )
            await event_bus.publish(end_event)

            return response

        except Exception as e:
            # 计算耗时
            duration = time.time() - start_time

            # 尝试从 gRPC 错误中提取状态码
            error_code = 2  # UNKNOWN
            if hasattr(e, "code"):
                try:
                    code = e.code()
                    error_code = code.value[0] if hasattr(code, "value") else 2
                except Exception:
                    pass

            # 发布错误事件
            error_event = GrpcRequestErrorEvent.create(
                correlation_id=correlation_id,
                service=self._service_name,
                method=request.method,
                error=e,
                duration=duration,
                error_code=error_code,
            )
            await event_bus.publish(error_event)

            raise
