"""测试 gRPC 客户端

注意：由于 gRPC 需要安装额外的依赖（grpcio），这里主要测试客户端的基本功能和接口

v3.32.0: 重构为中间件模式
"""

import pytest

from df_test_framework.capabilities.clients.grpc import GrpcClient
from df_test_framework.capabilities.clients.grpc.middleware import (
    GrpcEventPublisherMiddleware,
    GrpcMetadataMiddleware,
)
from df_test_framework.capabilities.clients.grpc.models import ChannelOptions


class TestGrpcClient:
    """测试 GrpcClient"""

    def test_init_client(self) -> None:
        """测试初始化客户端"""
        client = GrpcClient("localhost:50051", enable_events=False)

        assert client.target == "localhost:50051"
        assert client.secure is False
        assert isinstance(client.options, ChannelOptions)
        assert len(client.middlewares) == 0

    def test_init_with_custom_options(self) -> None:
        """测试使用自定义选项初始化"""
        options = ChannelOptions(
            max_send_message_length=1024 * 1024,
            keepalive_time_ms=30000,
        )

        client = GrpcClient(
            "localhost:50051",
            options=options,
            enable_events=False,
        )

        assert client.options.max_send_message_length == 1024 * 1024
        assert client.options.keepalive_time_ms == 30000

    def test_init_with_middlewares(self) -> None:
        """测试使用中间件初始化"""
        middleware = GrpcMetadataMiddleware({"Authorization": "Bearer token"})
        client = GrpcClient(
            "localhost:50051",
            middlewares=[middleware],
            enable_events=False,
        )

        assert len(client.middlewares) == 1
        assert isinstance(client.middlewares[0], GrpcMetadataMiddleware)

    def test_init_secure_client(self) -> None:
        """测试初始化安全客户端"""
        client = GrpcClient(
            "localhost:50051",
            secure=True,
            enable_events=False,
        )

        assert client.secure is True

    def test_add_metadata(self) -> None:
        """测试添加元数据"""
        client = GrpcClient("localhost:50051", enable_events=False)
        client.add_metadata("Authorization", "Bearer token123")
        client.add_metadata("X-Request-ID", "abc")

        assert len(client._metadata) == 2
        assert ("Authorization", "Bearer token123") in client._metadata
        assert ("X-Request-ID", "abc") in client._metadata

    def test_clear_metadata(self) -> None:
        """测试清除元数据"""
        client = GrpcClient("localhost:50051", enable_events=False)
        client.add_metadata("key", "value")
        client.clear_metadata()

        assert len(client._metadata) == 0

    def test_use_middleware(self) -> None:
        """测试添加中间件（链式调用）"""
        client = GrpcClient("localhost:50051", enable_events=False)
        middleware = GrpcMetadataMiddleware()

        result = client.use(middleware)

        assert result is client  # 链式调用
        assert len(client.middlewares) == 1
        assert client.middlewares[0] == middleware

    def test_ensure_grpc_not_installed(self) -> None:
        """测试 grpcio 未安装时的错误"""
        client = GrpcClient("localhost:50051", enable_events=False)

        # 如果 grpcio 未安装，应该抛出 ImportError
        # 如果已安装，这个测试会被跳过
        try:
            import grpc  # noqa: F401

            pytest.skip("grpcio is installed, skipping this test")
        except ImportError:
            with pytest.raises(ImportError, match="grpcio is not installed"):
                client.connect()

    def test_unary_call_without_connection(self) -> None:
        """测试未连接时调用"""
        client = GrpcClient("localhost:50051", enable_events=False)

        with pytest.raises(RuntimeError, match="Not connected"):
            client.unary_call("TestMethod", {})

    def test_server_streaming_call_without_connection(self) -> None:
        """测试未连接时流式调用"""
        client = GrpcClient("localhost:50051", enable_events=False)

        with pytest.raises(RuntimeError, match="Not connected"):
            list(client.server_streaming_call("TestMethod", {}))

    # ========== 新增测试：连接和关闭 ==========

    def test_connect_insecure(self) -> None:
        """测试非安全连接"""
        from unittest.mock import MagicMock, patch

        mock_grpc = MagicMock()
        mock_channel = MagicMock()
        mock_grpc.insecure_channel.return_value = mock_channel

        with patch.dict("sys.modules", {"grpc": mock_grpc}):
            client = GrpcClient("localhost:50051", enable_events=False)
            client.connect()

            mock_grpc.insecure_channel.assert_called_once()
            assert client._channel == mock_channel

    def test_connect_secure_with_default_credentials(self) -> None:
        """测试安全连接（默认凭证）"""
        from unittest.mock import MagicMock, patch

        mock_grpc = MagicMock()
        mock_channel = MagicMock()
        mock_credentials = MagicMock()
        mock_grpc.secure_channel.return_value = mock_channel
        mock_grpc.ssl_channel_credentials.return_value = mock_credentials

        with patch.dict("sys.modules", {"grpc": mock_grpc}):
            client = GrpcClient("localhost:50051", secure=True, enable_events=False)
            client.connect()

            mock_grpc.ssl_channel_credentials.assert_called_once()
            mock_grpc.secure_channel.assert_called_once()
            assert client._channel == mock_channel

    def test_connect_secure_with_custom_credentials(self) -> None:
        """测试安全连接（自定义凭证）"""
        from unittest.mock import MagicMock, patch

        mock_grpc = MagicMock()
        mock_channel = MagicMock()
        custom_credentials = MagicMock()
        mock_grpc.secure_channel.return_value = mock_channel

        with patch.dict("sys.modules", {"grpc": mock_grpc}):
            client = GrpcClient(
                "localhost:50051",
                secure=True,
                credentials=custom_credentials,
                enable_events=False,
            )
            client.connect()

            # 不应调用默认凭证
            mock_grpc.ssl_channel_credentials.assert_not_called()
            mock_grpc.secure_channel.assert_called_once()
            assert client._channel == mock_channel
            assert client.credentials == custom_credentials

    def test_connect_with_stub_class(self) -> None:
        """测试连接时创建 stub"""
        from unittest.mock import MagicMock, patch

        mock_grpc = MagicMock()
        mock_channel = MagicMock()
        mock_stub_class = MagicMock()
        mock_stub_class.__name__ = "TestServiceStub"
        mock_stub_instance = MagicMock()
        mock_stub_class.return_value = mock_stub_instance
        mock_grpc.insecure_channel.return_value = mock_channel

        with patch.dict("sys.modules", {"grpc": mock_grpc}):
            client = GrpcClient("localhost:50051", stub_class=mock_stub_class, enable_events=False)
            client.connect()

            mock_stub_class.assert_called_once_with(mock_channel)
            assert client._stub == mock_stub_instance

    def test_close(self) -> None:
        """测试关闭连接"""
        from unittest.mock import MagicMock

        client = GrpcClient("localhost:50051", enable_events=False)
        mock_channel = MagicMock()
        client._channel = mock_channel

        client.close()

        mock_channel.close.assert_called_once()

    def test_close_without_connection(self) -> None:
        """测试未连接时关闭"""
        client = GrpcClient("localhost:50051", enable_events=False)

        # 不应抛出异常
        client.close()

    # ========== 新增测试：上下文管理器 ==========

    def test_context_manager(self) -> None:
        """测试上下文管理器"""
        from unittest.mock import MagicMock, patch

        mock_grpc = MagicMock()
        mock_channel = MagicMock()
        mock_grpc.insecure_channel.return_value = mock_channel

        with patch.dict("sys.modules", {"grpc": mock_grpc}):
            with GrpcClient("localhost:50051", enable_events=False) as client:
                assert client._channel == mock_channel

            mock_channel.close.assert_called_once()

    # ========== 新增测试：状态码提取 ==========

    def test_extract_status_code_from_grpc_error(self) -> None:
        """测试从 gRPC 错误提取状态码"""
        from unittest.mock import MagicMock

        from df_test_framework.capabilities.clients.grpc.models import GrpcStatusCode

        client = GrpcClient("localhost:50051", enable_events=False)

        # 模拟 gRPC RpcError
        mock_code = MagicMock()
        mock_code.value = (14,)  # UNAVAILABLE
        mock_error = MagicMock()
        mock_error.code.return_value = mock_code

        status_code = client._extract_status_code(mock_error)

        assert status_code == GrpcStatusCode.UNAVAILABLE

    def test_extract_status_code_invalid_code(self) -> None:
        """测试提取无效状态码"""
        from unittest.mock import MagicMock

        from df_test_framework.capabilities.clients.grpc.models import GrpcStatusCode

        client = GrpcClient("localhost:50051", enable_events=False)

        # 模拟无效的状态码
        mock_error = MagicMock()
        mock_error.code.side_effect = AttributeError()

        status_code = client._extract_status_code(mock_error)

        assert status_code == GrpcStatusCode.UNKNOWN

    def test_extract_status_code_no_code_attr(self) -> None:
        """测试错误没有 code 属性"""
        from df_test_framework.capabilities.clients.grpc.models import GrpcStatusCode

        client = GrpcClient("localhost:50051", enable_events=False)

        # 普通异常没有 code 属性
        error = Exception("Simple error")

        status_code = client._extract_status_code(error)

        assert status_code == GrpcStatusCode.UNKNOWN

    # ========== 新增测试：健康检查 ==========

    def test_health_check_exception(self) -> None:
        """测试健康检查异常"""
        from unittest.mock import MagicMock

        client = GrpcClient("localhost:50051", enable_events=False)
        client._channel = MagicMock()

        # 直接调用原始方法，让 grpc_health 模块导入失败返回 False
        result = client.health_check()
        # 如果 grpc_health 未安装，会捕获 ImportError 返回 False
        assert result is False

    # ========== v3.32.0 新增测试：中间件系统集成 ==========

    def test_event_publisher_middleware_enabled_by_default(self) -> None:
        """测试事件发布中间件默认启用"""
        client = GrpcClient("localhost:50051")

        # 默认启用事件，应有 GrpcEventPublisherMiddleware
        assert len(client.middlewares) == 1
        assert isinstance(client.middlewares[0], GrpcEventPublisherMiddleware)

    def test_event_publisher_middleware_can_be_disabled(self) -> None:
        """测试事件发布中间件可以禁用"""
        client = GrpcClient("localhost:50051", enable_events=False)

        # 禁用事件后无中间件
        assert len(client.middlewares) == 0

    def test_event_publisher_middleware_with_service_name(self) -> None:
        """测试事件发布中间件使用自定义服务名称"""
        client = GrpcClient(
            "localhost:50051",
            service_name="CustomService",
        )

        assert len(client.middlewares) == 1
        assert isinstance(client.middlewares[0], GrpcEventPublisherMiddleware)
        assert client.middlewares[0]._service_name == "CustomService"

    def test_extract_service_name_from_stub_class(self) -> None:
        """测试从 stub 类提取服务名称"""
        from unittest.mock import MagicMock

        client = GrpcClient("localhost:50051", enable_events=False)

        # 测试 Stub 后缀
        mock_stub = MagicMock()
        mock_stub.__name__ = "GreeterStub"
        assert client._extract_service_name(mock_stub) == "Greeter"

        # 测试无 Stub 后缀
        mock_stub.__name__ = "UserService"
        assert client._extract_service_name(mock_stub) == "UserService"

        # 测试 None
        assert client._extract_service_name(None) == ""

    def test_middleware_ordering(self) -> None:
        """测试中间件排序（事件发布中间件在最后）"""
        middleware = GrpcMetadataMiddleware({"key": "value"})
        client = GrpcClient(
            "localhost:50051",
            middlewares=[middleware],
            enable_events=True,
        )

        # 事件发布中间件 priority=999，排在最后
        assert len(client.middlewares) == 2
        assert isinstance(client.middlewares[0], GrpcMetadataMiddleware)
        assert isinstance(client.middlewares[1], GrpcEventPublisherMiddleware)
