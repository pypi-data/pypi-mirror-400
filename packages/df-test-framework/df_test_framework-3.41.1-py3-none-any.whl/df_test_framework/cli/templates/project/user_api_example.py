"""示例 API 客户端模板"""

EXAMPLE_API_TEMPLATE = """\"\"\"示例 API 客户端

演示如何使用 BaseAPI 封装 API 调用，提供：
- 强类型方法签名
- IDE 智能提示
- 请求级认证控制（skip_auth/token）
- 自动 Pydantic 模型序列化

v3.39.0 新增:
- 支持增量合并（--merge 选项）
- 用户扩展区域保留自定义代码

使用方式：
    # 方式 1: 直接实例化
    >>> from {project_name}.apis.example_api import ExampleAPI
    >>> api = ExampleAPI(http_client)
    >>> response = api.get_example(example_id=1)

    # 方式 2: 使用 fixture（推荐）
    >>> def test_example(example_api):
    ...     response = example_api.list_examples()
\"\"\"

from typing import Any

from df_test_framework import BaseAPI, HttpClient
from df_test_framework.testing.decorators import api_class

from ..models.requests.example import (
    CreateExampleRequest,
    QueryExamplesRequest,
    UpdateExampleRequest,
)


# ========== AUTO-GENERATED START ==========
# 此区域由脚手架自动生成，重新生成时会被更新


@api_class("example_api", scope="function")
class ExampleAPI(BaseAPI):
    \"\"\"示例 API 客户端

    使用 @api_class 装饰器自动注册为 pytest fixture。

    Fixture 使用:
        1. 确保 conftest.py 中有: load_api_fixtures(globals(), apis_package="{project_name}.apis")
        2. 在测试中直接使用 example_api fixture（自动发现，无需手动导入）

    Attributes:
        base_path: API 路径前缀
    \"\"\"

    def __init__(self, http_client: HttpClient):
        super().__init__(http_client)
        self.base_path = "/api/v1"

    # ========== 查询接口 ==========

    def get_example(
        self,
        example_id: int,
        *,
        skip_auth: bool = False,
        token: str | None = None,
    ) -> dict[str, Any]:
        \"\"\"获取示例详情

        Args:
            example_id: 示例 ID
            skip_auth: 跳过认证（测试公开接口）
            token: 自定义 Token（覆盖全局配置）

        Returns:
            API 响应数据

        Example:
            >>> response = example_api.get_example(example_id=123)
            >>> print(response["data"]["name"])
        \"\"\"
        return self.get(
            f"/examples/{example_id}",
            skip_auth=skip_auth,
            token=token,
        )

    def list_examples(
        self,
        request: QueryExamplesRequest | None = None,
        *,
        page: int = 1,
        size: int = 20,
    ) -> dict[str, Any]:
        \"\"\"获取示例列表

        Args:
            request: 查询请求模型（可选）
            page: 页码（当 request 为 None 时使用）
            size: 每页数量（当 request 为 None 时使用）

        Returns:
            分页示例列表
        \"\"\"
        if request:
            params = request.model_dump(exclude_none=True)
        else:
            params = {"page": page, "size": size}

        return self.get("/examples", params=params)

    # ========== 写入接口 ==========

    def create_example(self, request: CreateExampleRequest) -> dict[str, Any]:
        \"\"\"创建示例

        Args:
            request: 创建请求模型

        Returns:
            创建成功的数据

        Example:
            >>> request = CreateExampleRequest(name="Test", email="test@example.com")
            >>> response = example_api.create_example(request)
            >>> example_id = response["data"]["id"]
        \"\"\"
        # BaseAPI.post() 自动将 Pydantic 模型序列化为 JSON
        return self.post("/examples", json=request)

    def update_example(
        self,
        example_id: int,
        request: UpdateExampleRequest,
    ) -> dict[str, Any]:
        \"\"\"更新示例信息

        Args:
            example_id: 示例 ID
            request: 更新请求模型（只包含要更新的字段）

        Returns:
            更新后的数据
        \"\"\"
        # 排除 None 值，只发送有值的字段
        return self.put(
            f"/examples/{example_id}",
            json=request.model_dump(exclude_none=True),
        )

    def delete_example(self, example_id: int) -> dict[str, Any]:
        \"\"\"删除示例

        Args:
            example_id: 示例 ID

        Returns:
            删除结果
        \"\"\"
        return self.delete(f"/examples/{example_id}")

    # ========== 业务接口示例 ==========

    def check_email_exists(self, email: str) -> bool:
        \"\"\"检查邮箱是否已存在

        演示返回非 dict 类型的方法。

        Args:
            email: 邮箱地址

        Returns:
            True 表示已存在，False 表示不存在
        \"\"\"
        response = self.get("/examples/check-email", params={"email": email})
        return response.get("data", {}).get("exists", False)


__all__ = ["ExampleAPI"]

# ========== AUTO-GENERATED END ==========


# ========== USER EXTENSIONS ==========
# 在此区域添加自定义代码，重新生成时会保留

"""

__all__ = ["EXAMPLE_API_TEMPLATE"]
