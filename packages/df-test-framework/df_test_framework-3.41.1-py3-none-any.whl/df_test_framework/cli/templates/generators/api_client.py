"""API客户端生成模板"""

GEN_API_CLIENT_TEMPLATE = """\"\"\"API客户端: {api_name}

封装 {api_name} 相关的 API 调用。

v3.38.0 最佳实践:
- ✅ @api_class 装饰器自动注册 fixture
- ✅ 强类型方法签名（Pydantic Model 参数和返回值）
- ✅ BaseAPI 自动序列化请求/解析响应
- ✅ skip_auth/token 请求级认证控制
\"\"\"

from typing import Any

from df_test_framework import BaseAPI, HttpClient
from df_test_framework.capabilities.clients.http.rest.httpx import BusinessError
from df_test_framework.testing.decorators import api_class

# 强类型方式（v3.38.0 推荐）:
# from ..models.requests.{api_path} import Create{ApiName}Request, Update{ApiName}Request
# from ..models.responses.{api_path} import {ApiName}Response, {ApiName}ListResponse


@api_class("{api_name}_api", scope="session")
class {ApiName}API(BaseAPI):
    \"\"\"{ApiName} API 客户端

    封装 {api_name} 相关的 HTTP API 调用。

    v3.38.0 特性:
    - @api_class 自动注册为 pytest fixture（{api_name}_api）
    - BaseAPI 自动处理 Pydantic 序列化和反序列化
    - 支持 skip_auth/token 请求级认证控制

    使用方式（在测试中）:
        def test_example({api_name}_api):
            result = {api_name}_api.get_{method_name}(1)
            assert result["code"] == 200

    强类型方式:
        def test_typed({api_name}_api):
            request = Create{ApiName}Request(name="test")
            response = {api_name}_api.create_{method_name}(request)
            assert response.code == 200
    \"\"\"

    def __init__(self, http_client: HttpClient):
        \"\"\"初始化 API 客户端

        Args:
            http_client: HTTP 客户端（自动注入中间件）
        \"\"\"
        super().__init__(http_client)
        self.base_path = "/api/{api_path}"

    # ========== 弱类型方法（基础用法）==========

    def get_{method_name}(
        self,
        {method_name}_id: int,
        *,
        skip_auth: bool = False,
        token: str | None = None,
    ) -> dict[str, Any]:
        \"\"\"获取单个 {api_name}

        Args:
            {method_name}_id: {api_name} ID
            skip_auth: 跳过认证（测试未登录场景）
            token: 使用自定义 Token

        Returns:
            dict: {api_name} 数据

        Raises:
            BusinessError: 业务错误
        \"\"\"
        response = self.http_client.get(
            f"{self.base_path}/{{{method_name}_id}}",
            skip_auth=skip_auth,
            token=token,
        )
        data = response.json()
        self._check_business_error(data)
        return data

    def list_{method_name}s(
        self,
        page: int = 1,
        size: int = 10,
        *,
        skip_auth: bool = False,
        token: str | None = None,
    ) -> list[dict[str, Any]]:
        \"\"\"获取 {api_name} 列表

        Args:
            page: 页码
            size: 每页数量
            skip_auth: 跳过认证
            token: 使用自定义 Token

        Returns:
            list[dict]: {api_name} 列表
        \"\"\"
        response = self.http_client.get(
            self.base_path,
            params={"page": page, "size": size},
            skip_auth=skip_auth,
            token=token,
        )
        data = response.json()
        self._check_business_error(data)
        return data.get("data", [])

    def create_{method_name}(
        self,
        request_data: dict[str, Any],
        *,
        skip_auth: bool = False,
        token: str | None = None,
    ) -> dict[str, Any]:
        \"\"\"创建 {api_name}

        Args:
            request_data: 请求数据（或 Pydantic Model）
            skip_auth: 跳过认证
            token: 使用自定义 Token

        Returns:
            dict: 创建结果
        \"\"\"
        response = self.http_client.post(
            self.base_path,
            json=request_data,
            skip_auth=skip_auth,
            token=token,
        )
        data = response.json()
        self._check_business_error(data)
        return data

    def update_{method_name}(
        self,
        {method_name}_id: int,
        request_data: dict[str, Any],
        *,
        skip_auth: bool = False,
        token: str | None = None,
    ) -> dict[str, Any]:
        \"\"\"更新 {api_name}

        Args:
            {method_name}_id: {api_name} ID
            request_data: 请求数据
            skip_auth: 跳过认证
            token: 使用自定义 Token

        Returns:
            dict: 更新结果
        \"\"\"
        response = self.http_client.put(
            f"{self.base_path}/{{{method_name}_id}}",
            json=request_data,
            skip_auth=skip_auth,
            token=token,
        )
        data = response.json()
        self._check_business_error(data)
        return data

    def delete_{method_name}(
        self,
        {method_name}_id: int,
        *,
        skip_auth: bool = False,
        token: str | None = None,
    ) -> None:
        \"\"\"删除 {api_name}

        Args:
            {method_name}_id: {api_name} ID
            skip_auth: 跳过认证
            token: 使用自定义 Token
        \"\"\"
        response = self.http_client.delete(
            f"{self.base_path}/{{{method_name}_id}}",
            skip_auth=skip_auth,
            token=token,
        )
        data = response.json()
        self._check_business_error(data)

    # ========== 强类型方法（v3.38.0 推荐）==========
    # 取消注释并导入对应的 Model 类使用

    # def get_{method_name}_typed(self, {method_name}_id: int) -> {ApiName}Response:
    #     \"\"\"获取单个 {api_name}（强类型）
    #
    #     Returns:
    #         {ApiName}Response: 强类型响应对象
    #     \"\"\"
    #     return self.get(f"{self.base_path}/{{{method_name}_id}}", model={ApiName}Response)

    # def create_{method_name}_typed(self, request: Create{ApiName}Request) -> {ApiName}Response:
    #     \"\"\"创建 {api_name}（强类型）
    #
    #     Args:
    #         request: Create{ApiName}Request 请求模型
    #
    #     Returns:
    #         {ApiName}Response: 强类型响应对象
    #     \"\"\"
    #     return self.post(self.base_path, json=request, model={ApiName}Response)

    def _check_business_error(self, response_data: dict) -> None:
        \"\"\"检查业务错误

        Args:
            response_data: 响应数据

        Raises:
            BusinessError: 业务错误
        \"\"\"
        code = response_data.get("code")
        if code != 200:
            message = response_data.get("message", "未知错误")
            raise BusinessError(message=message, code=code, data=response_data)


__all__ = ["{ApiName}API"]
"""

__all__ = ["GEN_API_CLIENT_TEMPLATE"]
