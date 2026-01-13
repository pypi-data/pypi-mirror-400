"""gRPC 追踪中间件

为 gRPC 请求添加分布式追踪支持

v3.12.0 新增 - 基础设施层 gRPC 追踪
v3.32.0 重构 - 从拦截器模式迁移到中间件模式
"""

from __future__ import annotations

import time
from collections.abc import Callable, Coroutine
from typing import Any

from df_test_framework.capabilities.clients.grpc.middleware import GrpcMiddleware
from df_test_framework.capabilities.clients.grpc.models import GrpcRequest, GrpcResponse

from ..context import TracingContext
from ..manager import OTEL_AVAILABLE, get_tracing_manager

if OTEL_AVAILABLE:
    from opentelemetry import trace


class GrpcTracingMiddleware(GrpcMiddleware):
    """gRPC 追踪中间件

    v3.32.0: 从拦截器模式重构为中间件模式

    自动为 gRPC 请求创建追踪 span，记录:
    - RPC 方法名称
    - 请求/响应元数据（可选）
    - 状态码
    - 响应时间
    - 异常信息

    使用示例:
        >>> from df_test_framework.infrastructure.tracing.interceptors import (
        ...     GrpcTracingMiddleware
        ... )
        >>>
        >>> # 基础用法
        >>> middleware = GrpcTracingMiddleware()
        >>> client.use(middleware)
        >>>
        >>> # 自定义配置
        >>> middleware = GrpcTracingMiddleware(
        ...     record_metadata=True,
        ...     propagate_context=True
        ... )

    追踪属性:
        - rpc.system: "grpc"
        - rpc.service: 服务名称
        - rpc.method: 方法名称
        - rpc.grpc.status_code: gRPC 状态码
        - rpc.request.duration_ms: 请求耗时（毫秒）
    """

    # W3C Trace Context 标准头名称
    TRACEPARENT_HEADER = "traceparent"
    TRACESTATE_HEADER = "tracestate"

    def __init__(
        self,
        record_metadata: bool = False,
        propagate_context: bool = True,
        sensitive_keys: list[str] | None = None,
        priority: int = 10,
    ):
        """初始化 gRPC 追踪中间件

        Args:
            record_metadata: 是否记录请求/响应元数据
            propagate_context: 是否传播追踪上下文（注入 traceparent 头）
            sensitive_keys: 敏感元数据键列表，记录时会脱敏
            priority: 中间件优先级（默认 10，较早执行）
        """
        super().__init__(name="GrpcTracingMiddleware", priority=priority)
        self.record_metadata = record_metadata
        self.propagate_context = propagate_context
        self.sensitive_keys = sensitive_keys or [
            "authorization",
            "x-api-key",
            "x-auth-token",
            "cookie",
        ]

    async def __call__(
        self,
        request: GrpcRequest,
        call_next: Callable[[GrpcRequest], Coroutine[None, None, GrpcResponse]],
    ) -> GrpcResponse:
        """执行追踪中间件"""
        if not OTEL_AVAILABLE:
            return await call_next(request)

        manager = get_tracing_manager()

        # 解析服务名和方法名
        service_name, method_name = self._parse_method(request.method)

        # 创建 span
        span_name = f"gRPC {service_name}/{method_name}"
        attributes = self._build_request_attributes(
            request.method, service_name, method_name, request.metadata
        )
        span = manager.start_span_no_context(span_name, attributes=attributes)

        # 记录开始时间
        start_time = time.perf_counter()

        # 传播追踪上下文
        if self.propagate_context and span:
            metadata_dict = dict(request.metadata)
            TracingContext.inject(metadata_dict)
            # 重建请求的 metadata
            request = GrpcRequest(
                method=request.method,
                message=request.message,
                metadata=[(k, v) for k, v in metadata_dict.items()],
                timeout=request.timeout,
            )

        try:
            # 执行请求
            response = await call_next(request)

            # 计算耗时并记录
            if span and span.is_recording():
                duration_ms = (time.perf_counter() - start_time) * 1000
                span.set_attribute("rpc.request.duration_ms", duration_ms)

                # 记录响应元数据
                if self.record_metadata and response.metadata:
                    for key, value in response.metadata.items():
                        sanitized = self._sanitize_value(key, str(value))
                        span.set_attribute(f"rpc.response.metadata.{key}", sanitized)

                # 设置成功状态
                span.set_attribute("rpc.grpc.status_code", response.status_code.value)
                span.set_status(trace.Status(trace.StatusCode.OK))
                span.end()

            return response

        except Exception as e:
            # 记录错误
            if span and span.is_recording():
                duration_ms = (time.perf_counter() - start_time) * 1000
                span.set_attribute("rpc.request.duration_ms", duration_ms)
                span.record_exception(e)
                span.set_attribute("rpc.grpc.status_code", 2)  # UNKNOWN
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                span.end()
            raise

    def _parse_method(self, method: str) -> tuple[str, str]:
        """解析 gRPC 方法名

        Args:
            method: 完整方法名（格式: /package.Service/Method）

        Returns:
            (服务名, 方法名)
        """
        # 格式: /package.Service/Method
        parts = method.strip("/").split("/")
        if len(parts) >= 2:
            return parts[0], parts[1]
        return method, "unknown"

    def _build_request_attributes(
        self,
        full_method: str,
        service_name: str,
        method_name: str,
        metadata: list[tuple[str, str]],
    ) -> dict[str, Any]:
        """构建请求属性

        Args:
            full_method: 完整方法名
            service_name: 服务名
            method_name: 方法名
            metadata: 元数据列表

        Returns:
            属性字典
        """
        attrs: dict[str, Any] = {
            "rpc.system": "grpc",
            "rpc.service": service_name,
            "rpc.method": method_name,
            "rpc.grpc.full_method": full_method,
        }

        # 记录请求元数据
        if self.record_metadata:
            for key, value in metadata:
                if key.startswith("x-tracing-"):
                    continue  # 跳过内部键
                sanitized = self._sanitize_value(key, value)
                attrs[f"rpc.request.metadata.{key}"] = sanitized

        return attrs

    def _sanitize_value(self, key: str, value: str) -> str:
        """脱敏元数据值

        Args:
            key: 键名
            value: 值

        Returns:
            脱敏后的值
        """
        if key.lower() in self.sensitive_keys:
            return "***"
        return value


# 向后兼容别名
GrpcTracingInterceptor = GrpcTracingMiddleware

__all__ = ["GrpcTracingMiddleware", "GrpcTracingInterceptor"]
