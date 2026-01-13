"""gRPC 重试中间件

v3.32.0 新增
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine

from df_test_framework.capabilities.clients.grpc.middleware.base import GrpcMiddleware
from df_test_framework.capabilities.clients.grpc.models import (
    GrpcRequest,
    GrpcResponse,
    GrpcStatusCode,
)
from df_test_framework.infrastructure.logging import get_logger

logger = get_logger(__name__)


class GrpcRetryMiddleware(GrpcMiddleware):
    """gRPC 重试中间件

    在失败时自动重试，支持指数退避

    v3.32.0 新增

    使用方式:
        middleware = GrpcRetryMiddleware(
            max_retries=3,
            retry_on_codes=[GrpcStatusCode.UNAVAILABLE, GrpcStatusCode.INTERNAL],
        )
        client = GrpcClient(..., middlewares=[middleware])
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_on_codes: list[int | GrpcStatusCode] | None = None,
        backoff_multiplier: float = 2.0,
        initial_backoff: float = 0.1,
        priority: int = 20,
    ):
        """初始化重试中间件

        Args:
            max_retries: 最大重试次数
            retry_on_codes: 需要重试的状态码列表（默认 [UNAVAILABLE]）
            backoff_multiplier: 退避倍数
            initial_backoff: 初始退避时间（秒）
            priority: 优先级（默认 20）
        """
        super().__init__(name="GrpcRetryMiddleware", priority=priority)
        self.max_retries = max_retries
        self.retry_on_codes = [
            c.value if isinstance(c, GrpcStatusCode) else c
            for c in (retry_on_codes or [GrpcStatusCode.UNAVAILABLE])
        ]
        self.backoff_multiplier = backoff_multiplier
        self.initial_backoff = initial_backoff

    def should_retry(self, status_code: GrpcStatusCode | int) -> bool:
        """判断是否应该重试

        Args:
            status_code: gRPC 状态码

        Returns:
            是否应该重试
        """
        code = status_code.value if isinstance(status_code, GrpcStatusCode) else status_code
        return code in self.retry_on_codes

    def calculate_backoff(self, attempt: int) -> float:
        """计算退避时间

        Args:
            attempt: 当前重试次数（从 0 开始）

        Returns:
            退避时间（秒）
        """
        return self.initial_backoff * (self.backoff_multiplier**attempt)

    async def __call__(
        self,
        request: GrpcRequest,
        call_next: Callable[[GrpcRequest], Coroutine[None, None, GrpcResponse]],
    ) -> GrpcResponse:
        """执行重试逻辑"""
        last_response: GrpcResponse | None = None

        for attempt in range(self.max_retries + 1):
            response = await call_next(request)

            # 成功则直接返回
            if response.is_success:
                return response

            last_response = response

            # 检查是否应该重试
            if not self.should_retry(response.status_code):
                return response

            # 最后一次尝试，不再重试
            if attempt >= self.max_retries:
                break

            # 计算退避时间并等待
            backoff = self.calculate_backoff(attempt)
            logger.warning(
                f"gRPC call {request.method} failed with {response.status_code.name}, "
                f"retrying in {backoff:.2f}s (attempt {attempt + 1}/{self.max_retries})"
            )
            await asyncio.sleep(backoff)

        return last_response  # type: ignore
