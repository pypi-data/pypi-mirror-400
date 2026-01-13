"""fixtures/message_queue.py 测试模块

测试消息队列 pytest fixtures 功能

v3.36.0 - 技术债务清理：提升测试覆盖率
"""

import pytest


@pytest.mark.unit
class TestKafkaAvailability:
    """测试 Kafka 可用性检查"""

    def test_kafka_available_constant(self):
        """测试 KAFKA_AVAILABLE 常量"""
        from df_test_framework.testing.fixtures import message_queue

        assert isinstance(message_queue.KAFKA_AVAILABLE, bool)

    def test_kafka_config_function_exists(self):
        """测试 kafka_config fixture 函数存在"""
        from df_test_framework.testing.fixtures import message_queue

        assert hasattr(message_queue, "kafka_config")
        assert callable(message_queue.kafka_config)

    def test_kafka_client_function_exists(self):
        """测试 kafka_client fixture 函数存在"""
        from df_test_framework.testing.fixtures import message_queue

        assert hasattr(message_queue, "kafka_client")
        assert callable(message_queue.kafka_client)


@pytest.mark.unit
class TestRabbitMQAvailability:
    """测试 RabbitMQ 可用性检查"""

    def test_rabbitmq_available_constant(self):
        """测试 RABBITMQ_AVAILABLE 常量"""
        from df_test_framework.testing.fixtures import message_queue

        assert isinstance(message_queue.RABBITMQ_AVAILABLE, bool)

    def test_rabbitmq_config_function_exists(self):
        """测试 rabbitmq_config fixture 函数存在"""
        from df_test_framework.testing.fixtures import message_queue

        assert hasattr(message_queue, "rabbitmq_config")
        assert callable(message_queue.rabbitmq_config)

    def test_rabbitmq_client_function_exists(self):
        """测试 rabbitmq_client fixture 函数存在"""
        from df_test_framework.testing.fixtures import message_queue

        assert hasattr(message_queue, "rabbitmq_client")
        assert callable(message_queue.rabbitmq_client)


@pytest.mark.unit
class TestRocketMQAvailability:
    """测试 RocketMQ 可用性检查"""

    def test_rocketmq_available_constant(self):
        """测试 ROCKETMQ_AVAILABLE 常量"""
        from df_test_framework.testing.fixtures import message_queue

        assert isinstance(message_queue.ROCKETMQ_AVAILABLE, bool)

    def test_rocketmq_config_function_exists(self):
        """测试 rocketmq_config fixture 函数存在"""
        from df_test_framework.testing.fixtures import message_queue

        assert hasattr(message_queue, "rocketmq_config")
        assert callable(message_queue.rocketmq_config)

    def test_rocketmq_client_function_exists(self):
        """测试 rocketmq_client fixture 函数存在"""
        from df_test_framework.testing.fixtures import message_queue

        assert hasattr(message_queue, "rocketmq_client")
        assert callable(message_queue.rocketmq_client)


@pytest.mark.unit
class TestFixtureDecorators:
    """测试 fixture 装饰器"""

    def test_kafka_config_is_fixture(self):
        """测试 kafka_config 是 pytest fixture"""
        from df_test_framework.testing.fixtures import message_queue

        # pytest.fixture 包装后的函数名字包含 pytest_fixture
        func_repr = repr(message_queue.kafka_config)
        assert "pytest_fixture" in func_repr or "fixture" in func_repr.lower()

    def test_rabbitmq_config_is_fixture(self):
        """测试 rabbitmq_config 是 pytest fixture"""
        from df_test_framework.testing.fixtures import message_queue

        func_repr = repr(message_queue.rabbitmq_config)
        assert "pytest_fixture" in func_repr or "fixture" in func_repr.lower()

    def test_rocketmq_config_is_fixture(self):
        """测试 rocketmq_config 是 pytest fixture"""
        from df_test_framework.testing.fixtures import message_queue

        func_repr = repr(message_queue.rocketmq_config)
        assert "pytest_fixture" in func_repr or "fixture" in func_repr.lower()


@pytest.mark.unit
class TestModuleExports:
    """测试模块导出"""

    def test_all_exports(self):
        """测试 __all__ 导出"""
        from df_test_framework.testing.fixtures import message_queue

        expected_exports = [
            "kafka_config",
            "kafka_client",
            "rabbitmq_config",
            "rabbitmq_client",
            "rocketmq_config",
            "rocketmq_client",
        ]

        for export in expected_exports:
            assert export in message_queue.__all__, f"Missing export: {export}"
            assert hasattr(message_queue, export), f"Missing attribute: {export}"

    def test_all_exports_count(self):
        """测试导出数量"""
        from df_test_framework.testing.fixtures import message_queue

        assert len(message_queue.__all__) == 6
