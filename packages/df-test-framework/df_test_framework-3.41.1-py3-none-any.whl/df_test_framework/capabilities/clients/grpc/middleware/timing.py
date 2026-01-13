"""gRPC 计时中间件

v3.32.0 新增
"""

from __future__ import annotations

import time
from collections.abc import Callable, Coroutine

from df_test_framework.capabilities.clients.grpc.middleware.base import GrpcMiddleware
from df_test_framework.capabilities.clients.grpc.models import GrpcRequest, GrpcResponse
from df_test_framework.infrastructure.logging import get_logger

logger = get_logger(__name__)


class GrpcTimingMiddleware(GrpcMiddleware):
    """gRPC 计时中间件

    记录每个 RPC 调用的耗时，支持统计分析

    v3.32.0 新增

    使用方式:
        middleware = GrpcTimingMiddleware()
        client = GrpcClient(..., middlewares=[middleware])

        # 执行一些调用后获取统计
        avg = middleware.get_average_timing("SayHello")
        stats = middleware.get_all_timings()
    """

    def __init__(self, priority: int = 15):
        """初始化计时中间件

        Args:
            priority: 优先级（默认 15，在日志之后执行）
        """
        super().__init__(name="GrpcTimingMiddleware", priority=priority)
        self.timings: dict[str, list[float]] = {}

    async def __call__(
        self,
        request: GrpcRequest,
        call_next: Callable[[GrpcRequest], Coroutine[None, None, GrpcResponse]],
    ) -> GrpcResponse:
        """记录调用耗时"""
        start_time = time.time()

        # 调用下一个中间件
        response = await call_next(request)

        # 计算耗时
        duration = time.time() - start_time

        # 记录耗时
        if request.method not in self.timings:
            self.timings[request.method] = []
        self.timings[request.method].append(duration)

        logger.info(f"{request.method} took {duration * 1000:.2f}ms")

        return response

    def get_average_timing(self, method: str) -> float | None:
        """获取方法的平均耗时

        Args:
            method: RPC 方法名

        Returns:
            平均耗时（秒），如果没有记录则返回 None
        """
        if method not in self.timings:
            return None

        timings = self.timings[method]
        return sum(timings) / len(timings) if timings else None

    def get_all_timings(self) -> dict[str, dict[str, float]]:
        """获取所有方法的耗时统计

        Returns:
            方法名到统计信息的映射，每个统计包含:
            - count: 调用次数
            - total: 总耗时
            - average: 平均耗时
            - min: 最小耗时
            - max: 最大耗时
        """
        result = {}
        for method, timings in self.timings.items():
            if not timings:
                continue

            result[method] = {
                "count": len(timings),
                "total": sum(timings),
                "average": sum(timings) / len(timings),
                "min": min(timings),
                "max": max(timings),
            }

        return result

    def clear_timings(self) -> None:
        """清除所有耗时记录"""
        self.timings.clear()
