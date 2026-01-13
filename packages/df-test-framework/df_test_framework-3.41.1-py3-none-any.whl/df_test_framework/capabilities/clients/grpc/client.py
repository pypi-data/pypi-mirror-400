"""gRPC 客户端实现

注意：此实现提供了 gRPC 客户端的框架和接口，但实际使用需要：
1. 安装 grpcio: pip install grpcio grpcio-tools
2. 使用 protoc 编译 .proto 文件生成 Python 代码
3. 导入生成的 stub 类

示例：
    # 1. 编译 proto 文件
    # python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. service.proto

    # 2. 使用客户端
    from service_pb2_grpc import GreeterStub
    from service_pb2 import HelloRequest

    client = GrpcClient("localhost:50051", GreeterStub)
    request = HelloRequest(name="World")
    response = client.unary_call("SayHello", request)
    print(response.data.message)

v3.32.0:
- 重构为中间件模式（与 HTTP 客户端一致）
- 自动添加 GrpcEventPublisherMiddleware，支持事件发布
- 支持 Allure 报告和控制台调试
"""

from __future__ import annotations

import asyncio
from collections.abc import Iterator
from typing import Any, TypeVar

from df_test_framework.capabilities.clients.grpc.middleware import (
    GrpcEventPublisherMiddleware,
    GrpcMiddleware,
)
from df_test_framework.capabilities.clients.grpc.models import (
    ChannelOptions,
    GrpcRequest,
    GrpcResponse,
    GrpcStatusCode,
)
from df_test_framework.core.middleware import MiddlewareChain
from df_test_framework.infrastructure.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class GrpcClient:
    """gRPC 客户端

    通用 gRPC 客户端，支持所有 RPC 调用模式

    v3.32.0: 重构为中间件模式

    注意：实际使用需要安装 grpcio 并生成 stub 代码
    """

    def __init__(
        self,
        target: str,
        stub_class: type | None = None,
        secure: bool = False,
        credentials: Any = None,
        options: ChannelOptions | None = None,
        middlewares: list[GrpcMiddleware] | None = None,
        enable_events: bool = True,
        service_name: str = "",
    ) -> None:
        """初始化 gRPC 客户端

        Args:
            target: 服务器地址，格式为 "host:port"
            stub_class: gRPC stub 类（由 protoc 生成）
            secure: 是否使用 TLS/SSL
            credentials: gRPC 凭证对象
            options: 通道选项
            middlewares: 中间件列表（v3.32.0 重构，替代原 interceptors）
            enable_events: 是否启用事件发布（默认 True）
            service_name: 服务名称，用于事件记录
        """
        self.target = target
        self.stub_class = stub_class
        self.secure = secure
        self.credentials = credentials
        self.options = options or ChannelOptions()
        self._enable_events = enable_events
        self._service_name = service_name or self._extract_service_name(stub_class)

        self._channel: Any = None
        self._stub: Any = None
        self._metadata: list[tuple[str, str]] = []

        # 初始化中间件链
        self._middlewares: list[GrpcMiddleware] = list(middlewares) if middlewares else []

        # v3.32.0: 自动添加事件发布中间件
        if enable_events:
            event_middleware = GrpcEventPublisherMiddleware(
                service_name=self._service_name,
            )
            self._middlewares.append(event_middleware)

        logger.info(f"Initializing gRPC client for {target}")

    @property
    def middlewares(self) -> list[GrpcMiddleware]:
        """已注册的中间件列表（只读副本）"""
        return self._middlewares.copy()

    def _extract_service_name(self, stub_class: type | None) -> str:
        """从 stub 类名提取服务名称

        Args:
            stub_class: gRPC stub 类

        Returns:
            服务名称
        """
        if stub_class is None:
            return ""
        # 例如 GreeterStub -> Greeter
        name = stub_class.__name__
        if name.endswith("Stub"):
            return name[:-4]
        return name

    def _ensure_grpc_installed(self) -> None:
        """确保 grpcio 已安装"""
        try:
            import grpc  # type: ignore  # noqa: F401
        except ImportError:
            raise ImportError(
                "grpcio is not installed. Please install it with: pip install grpcio grpcio-tools"
            )

    def connect(self) -> None:
        """建立连接"""
        self._ensure_grpc_installed()
        import grpc

        # 创建通道
        if self.secure:
            if self.credentials is None:
                self.credentials = grpc.ssl_channel_credentials()
            self._channel = grpc.secure_channel(
                self.target,
                self.credentials,
                options=self.options.to_grpc_options(),
            )
        else:
            self._channel = grpc.insecure_channel(
                self.target,
                options=self.options.to_grpc_options(),
            )

        # 创建 stub
        if self.stub_class:
            self._stub = self.stub_class(self._channel)

        logger.info(f"Connected to gRPC server at {self.target}")

    def close(self) -> None:
        """关闭连接"""
        if self._channel:
            self._channel.close()
            logger.info("gRPC client closed")

    def add_metadata(self, key: str, value: str) -> None:
        """添加元数据

        Args:
            key: 元数据键
            value: 元数据值
        """
        self._metadata.append((key, value))

    def clear_metadata(self) -> None:
        """清除所有元数据"""
        self._metadata = []

    def use(self, middleware: GrpcMiddleware) -> GrpcClient:
        """添加中间件（链式调用）

        Args:
            middleware: 中间件实例

        Returns:
            self，支持链式调用
        """
        self._middlewares.append(middleware)
        return self

    def _build_middleware_chain(
        self,
        handler: Any,
    ) -> MiddlewareChain[GrpcRequest, GrpcResponse]:
        """构建中间件链

        Args:
            handler: 最终处理函数

        Returns:
            中间件链
        """
        chain: MiddlewareChain[GrpcRequest, GrpcResponse] = MiddlewareChain(handler)
        chain.use_many(self._middlewares)
        return chain

    async def _execute_unary_call(self, request: GrpcRequest) -> GrpcResponse:
        """执行一元调用（内部方法）

        Args:
            request: gRPC 请求对象

        Returns:
            gRPC 响应对象
        """
        try:
            # 获取方法
            rpc_method = getattr(self._stub, request.method)

            # 执行调用（在线程池中运行同步调用）
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: rpc_method(
                    request.message,
                    timeout=request.timeout,
                    metadata=request.metadata,
                ),
            )

            return GrpcResponse(
                data=response,
                status_code=GrpcStatusCode.OK,
            )

        except Exception as e:
            logger.error(f"gRPC call failed: {e}")
            status_code = self._extract_status_code(e)
            return GrpcResponse(
                data=None,
                status_code=status_code,
                message=str(e),
            )

    def unary_call(
        self,
        method: str,
        request: Any,
        timeout: float | None = None,
        metadata: list[tuple[str, str]] | None = None,
    ) -> GrpcResponse[Any]:
        """执行一元调用（Unary RPC）

        Args:
            method: 方法名
            request: 请求对象
            timeout: 超时时间（秒）
            metadata: 请求元数据

        Returns:
            gRPC 响应对象

        Raises:
            RuntimeError: 未连接时调用
        """
        if not self._stub:
            raise RuntimeError("Not connected. Call connect() first.")

        # 合并元数据
        combined_metadata = list(self._metadata)
        if metadata:
            combined_metadata.extend(metadata)

        # 创建请求对象
        grpc_request = GrpcRequest(
            method=method,
            message=request,
            metadata=combined_metadata,
            timeout=timeout,
        )

        # 构建中间件链并执行
        chain = self._build_middleware_chain(self._execute_unary_call)

        # 运行异步中间件链
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # 没有运行的事件循环，创建一个
            loop = None

        if loop is None:
            return asyncio.run(chain.execute(grpc_request))
        else:
            # 已有事件循环，使用 run_until_complete
            future = asyncio.ensure_future(chain.execute(grpc_request))
            return asyncio.get_event_loop().run_until_complete(future)

    def server_streaming_call(
        self,
        method: str,
        request: Any,
        timeout: float | None = None,
        metadata: list[tuple[str, str]] | None = None,
    ) -> Iterator[GrpcResponse[Any]]:
        """执行服务端流式调用（Server Streaming RPC）

        Args:
            method: 方法名
            request: 请求对象
            timeout: 超时时间（秒）
            metadata: 请求元数据

        Yields:
            gRPC 响应对象

        Raises:
            RuntimeError: 未连接时调用
        """
        if not self._stub:
            raise RuntimeError("Not connected. Call connect() first.")

        # 合并元数据
        combined_metadata = list(self._metadata)
        if metadata:
            combined_metadata.extend(metadata)

        response_stream = None
        try:
            # 获取方法
            rpc_method = getattr(self._stub, method)

            # 执行调用
            response_stream = rpc_method(
                request,
                timeout=timeout,
                metadata=combined_metadata,
            )

            # 迭代响应流
            for response in response_stream:
                yield GrpcResponse(
                    data=response,
                    status_code=GrpcStatusCode.OK,
                )

        except Exception as e:
            logger.error(f"gRPC streaming call failed: {e}")
            status_code = self._extract_status_code(e)
            yield GrpcResponse(
                data=None,
                status_code=status_code,
                message=str(e),
            )
        finally:
            # 确保流资源被正确释放
            if response_stream is not None and hasattr(response_stream, "cancel"):
                try:
                    response_stream.cancel()
                    logger.debug(f"Cancelled streaming call for method: {method}")
                except Exception:
                    # 忽略取消时的错误（流可能已经完成或已取消）
                    pass

    def _extract_status_code(self, error: Exception) -> GrpcStatusCode:
        """从异常中提取 gRPC 状态码"""
        # 尝试从 grpc.RpcError 中提取状态码
        if hasattr(error, "code"):
            try:
                code = error.code()  # type: ignore
                return GrpcStatusCode(code.value[0])  # type: ignore
            except (AttributeError, ValueError):
                pass

        # 默认返回 UNKNOWN
        return GrpcStatusCode.UNKNOWN

    def health_check(self, service: str = "") -> bool:
        """健康检查

        Args:
            service: 服务名称（空字符串表示检查整个服务器）

        Returns:
            服务是否健康
        """
        try:
            # 使用 gRPC Health Checking Protocol
            # https://github.com/grpc/grpc/blob/master/doc/health-checking.md
            from grpc_health.v1 import health_pb2, health_pb2_grpc

            if not self._channel:
                self.connect()

            health_stub = health_pb2_grpc.HealthStub(self._channel)
            request = health_pb2.HealthCheckRequest(service=service)
            response = health_stub.Check(request)

            return response.status == health_pb2.HealthCheckResponse.SERVING

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def __enter__(self) -> GrpcClient:
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """上下文管理器退出"""
        self.close()
