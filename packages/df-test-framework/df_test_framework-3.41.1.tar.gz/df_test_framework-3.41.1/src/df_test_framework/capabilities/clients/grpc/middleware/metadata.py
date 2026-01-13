"""gRPC 元数据中间件

v3.32.0 新增
"""

from __future__ import annotations

from collections.abc import Callable, Coroutine

from df_test_framework.capabilities.clients.grpc.middleware.base import GrpcMiddleware
from df_test_framework.capabilities.clients.grpc.models import GrpcRequest, GrpcResponse


class GrpcMetadataMiddleware(GrpcMiddleware):
    """gRPC 元数据中间件

    自动添加通用元数据到所有请求

    v3.32.0 新增

    使用方式:
        middleware = GrpcMetadataMiddleware({
            "Authorization": "Bearer token",
            "X-Request-ID": "123",
        })
        client = GrpcClient(..., middlewares=[middleware])

        # 动态添加/移除
        middleware.add_metadata("X-Trace-ID", "abc")
        middleware.remove_metadata("X-Trace-ID")
    """

    def __init__(
        self,
        metadata: dict[str, str] | None = None,
        priority: int = 50,
    ):
        """初始化元数据中间件

        Args:
            metadata: 初始元数据字典
            priority: 优先级（默认 50）
        """
        super().__init__(name="GrpcMetadataMiddleware", priority=priority)
        self._metadata = metadata.copy() if metadata else {}

    @property
    def metadata(self) -> dict[str, str]:
        """当前元数据（只读副本）"""
        return self._metadata.copy()

    def add_metadata(self, key: str, value: str) -> None:
        """添加元数据

        Args:
            key: 元数据键
            value: 元数据值
        """
        self._metadata[key] = value

    def remove_metadata(self, key: str) -> None:
        """移除元数据

        Args:
            key: 元数据键
        """
        self._metadata.pop(key, None)

    def clear_metadata(self) -> None:
        """清除所有元数据"""
        self._metadata.clear()

    async def __call__(
        self,
        request: GrpcRequest,
        call_next: Callable[[GrpcRequest], Coroutine[None, None, GrpcResponse]],
    ) -> GrpcResponse:
        """添加元数据到请求"""
        # 合并元数据
        new_request = request
        for key, value in self._metadata.items():
            new_request = new_request.with_metadata(key, value)

        # 调用下一个中间件
        return await call_next(new_request)
