"""gRPC 日志中间件

v3.32.0 新增
"""

from __future__ import annotations

from collections.abc import Callable, Coroutine

from df_test_framework.capabilities.clients.grpc.middleware.base import GrpcMiddleware
from df_test_framework.capabilities.clients.grpc.models import GrpcRequest, GrpcResponse
from df_test_framework.infrastructure.logging import get_logger

logger = get_logger(__name__)


class GrpcLoggingMiddleware(GrpcMiddleware):
    """gRPC 日志中间件

    记录所有 gRPC 调用的日志

    v3.32.0 新增

    使用方式:
        middleware = GrpcLoggingMiddleware(
            log_request=True,
            log_response=True,
        )
        client = GrpcClient(..., middlewares=[middleware])
    """

    def __init__(
        self,
        log_request: bool = True,
        log_response: bool = True,
        priority: int = 10,
    ):
        """初始化日志中间件

        Args:
            log_request: 是否记录请求日志
            log_response: 是否记录响应日志
            priority: 优先级（默认 10，较早执行）
        """
        super().__init__(name="GrpcLoggingMiddleware", priority=priority)
        self.log_request = log_request
        self.log_response = log_response

    async def __call__(
        self,
        request: GrpcRequest,
        call_next: Callable[[GrpcRequest], Coroutine[None, None, GrpcResponse]],
    ) -> GrpcResponse:
        """执行日志记录"""
        # 前置：记录请求
        if self.log_request:
            logger.info(f"gRPC Request: {request.method}")
            logger.debug(f"Request data: {request.message}")
            logger.debug(f"Metadata: {request.metadata_dict}")

        # 调用下一个中间件
        response = await call_next(request)

        # 后置：记录响应
        if self.log_response:
            logger.info(f"gRPC Response: {request.method} -> {response.status_code.name}")
            logger.debug(f"Response data: {response.data}")

        return response
