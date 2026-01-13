"""GraphQL 数据模型

v3.33.0: 扩展请求模型支持中间件系统
"""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, Field


class GraphQLError(BaseModel):
    """GraphQL 错误模型"""

    message: str = Field(..., description="错误消息")
    locations: list[dict[str, int]] | None = Field(None, description="错误位置")
    path: list[str | int] | None = Field(None, description="错误路径")
    extensions: dict[str, Any] | None = Field(None, description="扩展信息")

    def __str__(self) -> str:
        """格式化错误消息"""
        parts = [f"GraphQL Error: {self.message}"]
        if self.path:
            parts.append(f"Path: {'.'.join(str(p) for p in self.path)}")
        if self.locations:
            parts.append(f"Location: {self.locations}")
        return "\n".join(parts)


class GraphQLRequest(BaseModel):
    """GraphQL 请求模型

    v3.33.0: 扩展字段支持中间件系统
    """

    query: str = Field(..., description="GraphQL 查询或变更语句")
    variables: dict[str, Any] | None = Field(None, description="查询变量")
    operation_name: str | None = Field(None, description="操作名称")

    # v3.33.0: 中间件系统所需字段
    url: str = Field(default="", description="请求 URL（中间件使用）")
    headers: dict[str, str] = Field(default_factory=dict, description="请求头（中间件使用）")

    model_config = {"frozen": False}

    @property
    def operation_type(self) -> str:
        """从查询语句中提取操作类型

        Returns:
            操作类型：query、mutation、subscription 或空字符串
        """
        # 简单的正则匹配
        query_stripped = self.query.strip()
        if query_stripped.startswith("mutation"):
            return "mutation"
        elif query_stripped.startswith("subscription"):
            return "subscription"
        elif query_stripped.startswith("query") or query_stripped.startswith("{"):
            return "query"

        # 尝试更复杂的匹配
        match = re.match(r"^\s*(query|mutation|subscription)\s*", self.query, re.IGNORECASE)
        if match:
            return match.group(1).lower()

        return "query"  # 默认为 query

    @property
    def variables_json(self) -> str | None:
        """将变量序列化为 JSON 字符串

        Returns:
            JSON 字符串或 None
        """
        if self.variables is None:
            return None
        try:
            return json.dumps(self.variables, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(self.variables)

    def to_payload(self) -> dict[str, Any]:
        """转换为 HTTP 请求体

        Returns:
            请求体字典
        """
        payload: dict[str, Any] = {"query": self.query}
        if self.variables:
            payload["variables"] = self.variables
        if self.operation_name:
            payload["operationName"] = self.operation_name
        return payload


class GraphQLResponse(BaseModel):
    """GraphQL 响应模型

    v3.33.0: 扩展属性支持中间件系统
    """

    data: dict[str, Any] | None = Field(None, description="响应数据")
    errors: list[GraphQLError] | None = Field(None, description="错误列表")
    extensions: dict[str, Any] | None = Field(None, description="扩展信息")

    model_config = {"frozen": False}

    @property
    def is_success(self) -> bool:
        """是否成功（无错误）"""
        return self.errors is None or len(self.errors) == 0

    @property
    def has_errors(self) -> bool:
        """是否有错误（is_success 的反向）

        v3.33.0: 新增，供中间件使用
        """
        return not self.is_success

    @property
    def has_data(self) -> bool:
        """是否包含数据"""
        return self.data is not None

    @property
    def data_json(self) -> str | None:
        """将数据序列化为 JSON 字符串

        v3.33.0: 新增，供事件发布使用

        Returns:
            JSON 字符串或 None
        """
        if self.data is None:
            return None
        try:
            return json.dumps(self.data, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(self.data)

    def get_field(self, field_name: str) -> Any:
        """获取响应数据中的字段"""
        if not self.has_data:
            return None
        return self.data.get(field_name)  # type: ignore

    def raise_for_errors(self) -> None:
        """如果有错误则抛出异常"""
        if not self.is_success:
            error_messages = "\n".join(str(e) for e in self.errors)  # type: ignore
            raise RuntimeError(f"GraphQL request failed:\n{error_messages}")
