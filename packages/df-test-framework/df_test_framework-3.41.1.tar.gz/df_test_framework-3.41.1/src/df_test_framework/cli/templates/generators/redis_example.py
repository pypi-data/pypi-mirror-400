"""Redis 使用示例模板

v3.35.5+: 新增 Redis 使用示例
"""

# Redis Fixture 模板
GEN_REDIS_FIXTURE_TEMPLATE = '''"""Redis Fixture 定义

提供 Redis 客户端 fixture，支持:
- 自动连接管理
- 测试隔离（可选前缀）
- 测试后自动清理
"""

import pytest

from df_test_framework.capabilities.databases.redis import RedisClient


@pytest.fixture(scope="session")
def redis_client(settings):
    """Redis 客户端 fixture（会话级别）

    整个测试会话共享一个连接。
    适用于只读查询或不需要隔离的场景。

    Example:
        >>> def test_redis_get(redis_client):
        ...     value = redis_client.get("key")
        ...     assert value is not None
    """
    # 从配置读取 Redis 连接信息
    redis_config = getattr(settings, "redis", None) or {}

    client = RedisClient(
        host=redis_config.get("host", "localhost"),
        port=redis_config.get("port", 6379),
        db=redis_config.get("db", 0),
        password=redis_config.get("password"),
    )

    yield client

    client.close()


@pytest.fixture
def redis_test_client(redis_client, request):
    """隔离的 Redis 测试客户端

    每个测试使用独立的键前缀，测试后自动清理。
    推荐用于写入操作，确保测试隔离。

    Example:
        >>> def test_redis_set(redis_test_client):
        ...     # 键会自动添加前缀
        ...     redis_test_client.set("user:1", "value")
        ...     # 测试结束后自动清理
    """
    # 生成测试专用前缀
    test_prefix = f"test:{request.node.name}:"
    created_keys = []

    class IsolatedRedisClient:
        """带前缀的 Redis 客户端包装器"""

        def __init__(self, client: RedisClient, prefix: str):
            self._client = client
            self._prefix = prefix

        def _key(self, key: str) -> str:
            """添加测试前缀"""
            return f"{self._prefix}{key}"

        def set(self, key: str, value, **kwargs):
            full_key = self._key(key)
            created_keys.append(full_key)
            return self._client.set(full_key, value, **kwargs)

        def get(self, key: str):
            return self._client.get(self._key(key))

        def delete(self, *keys: str):
            full_keys = [self._key(k) for k in keys]
            return self._client.delete(*full_keys)

        def hset(self, name: str, key: str, value):
            full_name = self._key(name)
            created_keys.append(full_name)
            return self._client.hset(full_name, key, value)

        def hget(self, name: str, key: str):
            return self._client.hget(self._key(name), key)

        def hgetall(self, name: str):
            return self._client.hgetall(self._key(name))

        def lpush(self, name: str, *values):
            full_name = self._key(name)
            created_keys.append(full_name)
            return self._client.lpush(full_name, *values)

        def rpush(self, name: str, *values):
            full_name = self._key(name)
            created_keys.append(full_name)
            return self._client.rpush(full_name, *values)

        def lrange(self, name: str, start: int, end: int):
            return self._client.lrange(self._key(name), start, end)

        def sadd(self, name: str, *values):
            full_name = self._key(name)
            created_keys.append(full_name)
            return self._client.sadd(full_name, *values)

        def smembers(self, name: str):
            return self._client.smembers(self._key(name))

        def zadd(self, name: str, mapping: dict):
            full_name = self._key(name)
            created_keys.append(full_name)
            return self._client.zadd(full_name, mapping)

        def zrange(self, name: str, start: int, end: int, **kwargs):
            return self._client.zrange(self._key(name), start, end, **kwargs)

        @property
        def raw(self) -> RedisClient:
            """获取原始客户端（不带前缀）"""
            return self._client

    isolated_client = IsolatedRedisClient(redis_client, test_prefix)

    yield isolated_client

    # 测试结束后清理创建的键
    if created_keys:
        redis_client.delete(*created_keys)
'''

# Redis 测试示例模板
GEN_TEST_REDIS_TEMPLATE = '''"""Redis 测试示例

演示如何测试与 Redis 交互的业务逻辑。
"""

import pytest


class TestRedisBasicOperations:
    """Redis 基础操作测试

    演示字符串、哈希、列表、集合操作。
    """

    def test_string_set_and_get(self, redis_test_client):
        """测试字符串设置和获取"""
        # Arrange
        key = "user:session"
        value = "session_token_123"

        # Act
        redis_test_client.set(key, value, ex=3600)  # 1小时过期
        result = redis_test_client.get(key)

        # Assert
        assert result == value

    def test_hash_operations(self, redis_test_client):
        """测试哈希操作"""
        # Arrange
        user_key = "user:profile:1"

        # Act
        redis_test_client.hset(user_key, "name", "张三")
        redis_test_client.hset(user_key, "email", "zhangsan@example.com")

        # Assert
        profile = redis_test_client.hgetall(user_key)
        assert profile["name"] == "张三"
        assert profile["email"] == "zhangsan@example.com"

    def test_list_operations(self, redis_test_client):
        """测试列表操作"""
        # Arrange
        queue_key = "task:queue"
        tasks = ["task1", "task2", "task3"]

        # Act
        for task in tasks:
            redis_test_client.rpush(queue_key, task)

        # Assert
        result = redis_test_client.lrange(queue_key, 0, -1)
        assert result == tasks

    def test_set_operations(self, redis_test_client):
        """测试集合操作"""
        # Arrange
        tags_key = "article:tags"
        tags = ["python", "redis", "testing"]

        # Act
        for tag in tags:
            redis_test_client.sadd(tags_key, tag)

        # Assert
        result = redis_test_client.smembers(tags_key)
        assert result == set(tags)

    def test_sorted_set_operations(self, redis_test_client):
        """测试有序集合操作"""
        # Arrange
        leaderboard_key = "game:leaderboard"
        scores = {"player1": 100, "player2": 200, "player3": 150}

        # Act
        redis_test_client.zadd(leaderboard_key, scores)

        # Assert
        top_players = redis_test_client.zrange(leaderboard_key, 0, -1, withscores=True)
        # 默认按分数升序排列
        assert len(top_players) == 3


class TestRedisCacheScenarios:
    """Redis 缓存场景测试

    演示常见的缓存使用模式。
    """

    def test_cache_miss_and_fill(self, redis_test_client):
        """测试缓存未命中和填充"""
        # Arrange
        cache_key = "api:response:users"

        # Act - 首次访问（缓存未命中）
        cached = redis_test_client.get(cache_key)

        # Assert
        assert cached is None

        # 模拟填充缓存
        api_response = '{"users": [{"id": 1, "name": "Test"}]}'
        redis_test_client.set(cache_key, api_response, ex=300)

        # Act - 再次访问（缓存命中）
        cached = redis_test_client.get(cache_key)

        # Assert
        assert cached == api_response

    def test_counter_increment(self, redis_test_client):
        """测试计数器"""
        # Arrange
        counter_key = "stats:page_views"

        # 使用原始客户端进行 incr 操作
        prefix = f"test:{redis_test_client._prefix}"
        full_key = f"{redis_test_client._prefix}{counter_key}"

        # Act
        redis_test_client.set(counter_key, "0")

        # 使用原始客户端进行自增
        for _ in range(5):
            redis_test_client.raw.incr(full_key)

        # Assert
        result = redis_test_client.get(counter_key)
        assert int(result) == 5

    def test_session_management(self, redis_test_client):
        """测试会话管理"""
        # Arrange
        session_id = "sess_abc123"
        session_key = f"session:{session_id}"
        user_data = {"user_id": "1", "role": "admin"}

        # Act - 创建会话
        for field, value in user_data.items():
            redis_test_client.hset(session_key, field, value)

        # Assert
        session = redis_test_client.hgetall(session_key)
        assert session["user_id"] == "1"
        assert session["role"] == "admin"


class TestRedisWithMock:
    """使用 Mock 的 Redis 测试

    演示如何使用 redis_mock 进行单元测试。
    """

    def test_service_with_redis_mock(self, redis_mock):
        """测试服务层使用 Redis Mock"""
        # redis_mock 是 df-test-framework 提供的内存 Mock
        # 无需真实 Redis 连接

        # Arrange
        redis_mock.set("config:feature_flag", "enabled")

        # Act
        flag = redis_mock.get("config:feature_flag")

        # Assert
        assert flag == "enabled"

    @pytest.mark.skip(reason="需要根据实际业务实现")
    def test_cache_service_integration(self, redis_mock):
        """测试缓存服务集成"""
        # 示例：测试使用 Redis 的缓存服务
        # from your_project.services import CacheService
        # cache_service = CacheService(redis_client=redis_mock)
        # result = cache_service.get_or_set("key", lambda: "computed_value")
        # assert result == "computed_value"
        pass
'''

__all__ = ["GEN_REDIS_FIXTURE_TEMPLATE", "GEN_TEST_REDIS_TEMPLATE"]
