"""GraphQL 测试示例模板

v3.35.5+: 新增 GraphQL 测试示例
"""

GEN_TEST_GRAPHQL_TEMPLATE = '''"""GraphQL API 测试示例

演示如何使用 df-test-framework 测试 GraphQL API。
包含查询、变更、错误处理等常见场景。
"""

import pytest

from df_test_framework import DataGenerator
from df_test_framework.capabilities.clients.graphql import GraphQLClient


class TestGraphQLUserAPI:
    """用户 GraphQL API 测试

    演示 GraphQL 测试的最佳实践:
    - Query 查询测试
    - Mutation 变更测试
    - 错误处理测试
    - 参数化测试
    """

    # ==================== Query 测试 ====================

    def test_query_user_by_id(self, graphql_client: GraphQLClient):
        """测试查询单个用户"""
        # Arrange
        query = """
            query GetUser($id: ID!) {
                user(id: $id) {
                    id
                    name
                    email
                }
            }
        """

        # Act
        response = graphql_client.execute(query, {"id": "1"})

        # Assert
        assert response.is_success, f"查询失败: {response.errors}"
        assert response.data is not None
        user = response.data.get("user")
        assert user is not None
        assert user["id"] == "1"

    def test_query_users_with_pagination(self, graphql_client: GraphQLClient):
        """测试分页查询用户列表"""
        # Arrange
        query = """
            query ListUsers($page: Int!, $size: Int!) {
                users(page: $page, size: $size) {
                    items {
                        id
                        name
                    }
                    total
                    hasNext
                }
            }
        """

        # Act
        response = graphql_client.execute(query, {"page": 1, "size": 10})

        # Assert
        assert response.is_success
        users = response.data.get("users")
        assert users is not None
        assert isinstance(users.get("items"), list)
        assert "total" in users
        assert "hasNext" in users

    def test_query_nonexistent_user_returns_null(self, graphql_client: GraphQLClient):
        """测试查询不存在的用户返回 null"""
        # Arrange
        query = """
            query GetUser($id: ID!) {
                user(id: $id) {
                    id
                    name
                }
            }
        """

        # Act
        response = graphql_client.execute(query, {"id": "nonexistent-id"})

        # Assert
        assert response.is_success
        assert response.data.get("user") is None

    # ==================== Mutation 测试 ====================

    def test_mutation_create_user(self, graphql_client: GraphQLClient, cleanup):
        """测试创建用户"""
        # Arrange
        test_email = DataGenerator.test_id("test_") + "@example.com"
        mutation = """
            mutation CreateUser($input: CreateUserInput!) {
                createUser(input: $input) {
                    id
                    name
                    email
                }
            }
        """

        # Act
        response = graphql_client.execute(
            mutation,
            {
                "input": {
                    "name": "测试用户",
                    "email": test_email,
                    "password": "password123",
                }
            },
        )

        # Assert
        assert response.is_success, f"创建失败: {response.errors}"
        user = response.data.get("createUser")
        assert user is not None
        assert user["email"] == test_email

        # 注册清理（可选，如果需要清理测试数据）
        if user:
            cleanup.add("users", user["id"])

    def test_mutation_update_user(self, graphql_client: GraphQLClient):
        """测试更新用户"""
        # Arrange
        mutation = """
            mutation UpdateUser($id: ID!, $input: UpdateUserInput!) {
                updateUser(id: $id, input: $input) {
                    id
                    name
                    updatedAt
                }
            }
        """

        # Act
        response = graphql_client.execute(
            mutation,
            {
                "id": "1",
                "input": {"name": "更新后的名称"},
            },
        )

        # Assert
        assert response.is_success
        user = response.data.get("updateUser")
        assert user is not None
        assert user["name"] == "更新后的名称"

    def test_mutation_delete_user(self, graphql_client: GraphQLClient):
        """测试删除用户"""
        # Arrange
        mutation = """
            mutation DeleteUser($id: ID!) {
                deleteUser(id: $id) {
                    success
                    message
                }
            }
        """

        # Act
        response = graphql_client.execute(mutation, {"id": "test-delete-id"})

        # Assert
        assert response.is_success
        result = response.data.get("deleteUser")
        assert result is not None
        assert result.get("success") is True

    # ==================== 错误处理测试 ====================

    def test_mutation_validation_error(self, graphql_client: GraphQLClient):
        """测试输入验证错误"""
        # Arrange - 使用无效的邮箱格式
        mutation = """
            mutation CreateUser($input: CreateUserInput!) {
                createUser(input: $input) {
                    id
                }
            }
        """

        # Act
        response = graphql_client.execute(
            mutation,
            {
                "input": {
                    "name": "Test",
                    "email": "invalid-email",  # 无效邮箱
                    "password": "123",  # 密码太短
                }
            },
        )

        # Assert - 期望返回验证错误
        assert not response.is_success or response.has_errors
        # GraphQL 错误可能在 errors 字段或 data 中的业务错误

    def test_query_with_missing_required_variable(self, graphql_client: GraphQLClient):
        """测试缺少必需变量"""
        # Arrange
        query = """
            query GetUser($id: ID!) {
                user(id: $id) {
                    id
                    name
                }
            }
        """

        # Act - 不传递必需的 id 变量
        response = graphql_client.execute(query, {})

        # Assert
        assert response.has_errors
        assert any("id" in str(err).lower() for err in response.errors)

    # ==================== 参数化测试 ====================

    @pytest.mark.parametrize(
        "field,expected_type",
        [
            ("id", str),
            ("name", str),
            ("email", str),
        ],
    )
    def test_user_fields_type(
        self,
        graphql_client: GraphQLClient,
        field: str,
        expected_type: type,
    ):
        """测试用户字段类型"""
        # Arrange
        query = f"""
            query GetUser($id: ID!) {{
                user(id: $id) {{
                    {field}
                }}
            }}
        """

        # Act
        response = graphql_client.execute(query, {"id": "1"})

        # Assert
        assert response.is_success
        user = response.data.get("user")
        if user:
            assert isinstance(user.get(field), expected_type)


class TestGraphQLBatchOperations:
    """GraphQL 批量操作测试"""

    def test_batch_query(self, graphql_client: GraphQLClient):
        """测试批量查询"""
        # Arrange
        operations = [
            (
                "query {{ user(id: \\"1\\") {{ id name }} }}",
                None,
            ),
            (
                "query {{ user(id: \\"2\\") {{ id name }} }}",
                None,
            ),
        ]

        # Act
        responses = graphql_client.execute_batch(operations)

        # Assert
        assert len(responses) == 2
        for response in responses:
            # 批量查询的每个响应都应该成功（即使 user 为 null）
            assert response.data is not None or response.errors is not None


# ==================== Fixture 定义 ====================


@pytest.fixture
def graphql_client(settings):
    """GraphQL 客户端 fixture

    根据项目配置创建 GraphQL 客户端。
    测试结束后自动关闭连接。
    """
    # 从配置获取 GraphQL 端点（可根据实际项目调整）
    url = getattr(settings, "graphql_url", "http://localhost:8000/graphql")

    client = GraphQLClient(
        url=url,
        timeout=30,
    )

    # 如果需要认证，设置 token
    token = getattr(settings, "graphql_token", None)
    if token:
        client.set_header("Authorization", f"Bearer {token}")

    yield client

    client.close()
'''

__all__ = ["GEN_TEST_GRAPHQL_TEMPLATE"]
