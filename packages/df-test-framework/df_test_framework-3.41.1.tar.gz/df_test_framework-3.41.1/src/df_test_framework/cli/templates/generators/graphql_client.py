"""GraphQL 客户端生成器模板

v3.35.5+: 新增 GraphQL 客户端模板
"""

GEN_GRAPHQL_CLIENT_TEMPLATE = '''"""GraphQL 客户端封装

基于 df-test-framework GraphQL 客户端
支持:
- Query/Mutation/Subscription 操作
- 中间件系统（日志、重试、认证）
- EventBus 事件追踪
- Allure 报告集成
"""

from typing import Any

from df_test_framework.capabilities.clients.graphql import (
    GraphQLClient,
    GraphQLResponse,
)
from df_test_framework.capabilities.clients.graphql.middleware import (
    GraphQLLoggingMiddleware,
    GraphQLRetryMiddleware,
)


class {ProjectName}GraphQLClient:
    """项目 GraphQL 客户端

    封装 GraphQL 操作，提供类型安全的查询方法。

    使用示例:
        >>> client = {ProjectName}GraphQLClient("https://api.example.com/graphql")
        >>> user = client.get_user(user_id="123")
        >>> print(user["name"])
    """

    def __init__(
        self,
        url: str,
        token: str | None = None,
        timeout: int = 30,
    ) -> None:
        """初始化 GraphQL 客户端

        Args:
            url: GraphQL 端点 URL
            token: Bearer Token（可选）
            timeout: 请求超时时间（秒）
        """
        middlewares = [
            GraphQLLoggingMiddleware(),
            GraphQLRetryMiddleware(max_retries=3),
        ]

        self._client = GraphQLClient(
            url=url,
            timeout=timeout,
            middlewares=middlewares,
        )

        if token:
            self._client.set_header("Authorization", f"Bearer {token}")

    # ==================== 查询示例 ====================

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        """获取用户信息

        Args:
            user_id: 用户 ID

        Returns:
            用户数据，不存在返回 None
        """
        query = """
            query GetUser($id: ID!) {
                user(id: $id) {
                    id
                    name
                    email
                    createdAt
                }
            }
        """
        response = self._client.execute(query, {"id": user_id})
        return response.data.get("user") if response.is_success else None

    def list_users(
        self,
        page: int = 1,
        size: int = 10,
    ) -> list[dict[str, Any]]:
        """获取用户列表

        Args:
            page: 页码
            size: 每页数量

        Returns:
            用户列表
        """
        query = """
            query ListUsers($page: Int!, $size: Int!) {
                users(page: $page, size: $size) {
                    items {
                        id
                        name
                        email
                    }
                    total
                    hasNext
                }
            }
        """
        response = self._client.execute(query, {"page": page, "size": size})
        if response.is_success:
            return response.data.get("users", {}).get("items", [])
        return []

    # ==================== 变更示例 ====================

    def create_user(
        self,
        name: str,
        email: str,
        password: str,
    ) -> dict[str, Any] | None:
        """创建用户

        Args:
            name: 用户名
            email: 邮箱
            password: 密码

        Returns:
            创建的用户数据
        """
        mutation = """
            mutation CreateUser($input: CreateUserInput!) {
                createUser(input: $input) {
                    id
                    name
                    email
                }
            }
        """
        response = self._client.execute(
            mutation,
            {
                "input": {
                    "name": name,
                    "email": email,
                    "password": password,
                }
            },
        )
        return response.data.get("createUser") if response.is_success else None

    def update_user(
        self,
        user_id: str,
        **updates: Any,
    ) -> dict[str, Any] | None:
        """更新用户

        Args:
            user_id: 用户 ID
            **updates: 要更新的字段

        Returns:
            更新后的用户数据
        """
        mutation = """
            mutation UpdateUser($id: ID!, $input: UpdateUserInput!) {
                updateUser(id: $id, input: $input) {
                    id
                    name
                    email
                    updatedAt
                }
            }
        """
        response = self._client.execute(
            mutation,
            {"id": user_id, "input": updates},
        )
        return response.data.get("updateUser") if response.is_success else None

    def delete_user(self, user_id: str) -> bool:
        """删除用户

        Args:
            user_id: 用户 ID

        Returns:
            是否删除成功
        """
        mutation = """
            mutation DeleteUser($id: ID!) {
                deleteUser(id: $id) {
                    success
                }
            }
        """
        response = self._client.execute(mutation, {"id": user_id})
        if response.is_success:
            return response.data.get("deleteUser", {}).get("success", False)
        return False

    # ==================== 辅助方法 ====================

    def execute(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
    ) -> GraphQLResponse:
        """执行任意 GraphQL 操作

        用于执行自定义查询或变更。

        Args:
            query: GraphQL 查询语句
            variables: 变量字典
            operation_name: 操作名称

        Returns:
            GraphQL 响应对象

        Example:
            >>> response = client.execute(
            ...     "query {{ user(id: \\"123\\") {{ name }} }}"
            ... )
            >>> print(response.data)
        """
        return self._client.execute(query, variables, operation_name)

    def close(self) -> None:
        """关闭客户端"""
        self._client.close()

    def __enter__(self) -> "{ProjectName}GraphQLClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


__all__ = ["{ProjectName}GraphQLClient"]
'''

__all__ = ["GEN_GRAPHQL_CLIENT_TEMPLATE"]
