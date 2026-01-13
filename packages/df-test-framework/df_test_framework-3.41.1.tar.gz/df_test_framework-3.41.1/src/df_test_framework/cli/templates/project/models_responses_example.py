"""示例响应模型模板"""

MODELS_RESPONSES_EXAMPLE_TEMPLATE = """\"\"\"示例响应模型

演示如何定义响应模型，提供：
- IDE 智能提示
- 类型检查
- 自动反序列化
- 别名支持（如 createdAt -> created_at）

v3.39.0 新增:
- 支持增量合并（--merge 选项）
- 用户扩展区域保留自定义代码

使用方式：
    >>> from {project_name}.models.responses.example import ExampleResponse
    >>> item = ExampleResponse.model_validate(api_response["data"])
    >>> print(item.name)
\"\"\"

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ========== AUTO-GENERATED START ==========
# 此区域由脚手架自动生成，重新生成时会被更新


class ExampleResponse(BaseModel):
    \"\"\"示例响应模型\"\"\"

    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(..., description="ID")
    name: str = Field(..., description="名称")
    email: str = Field(..., description="邮箱地址")
    phone: str | None = Field(None, description="手机号")
    created_at: str | None = Field(None, alias="createdAt", description="创建时间")


class PagedExamplesResponse(BaseModel):
    \"\"\"分页示例列表响应模型\"\"\"

    model_config = ConfigDict(populate_by_name=True)

    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    items: list[ExampleResponse] = Field(default_factory=list, description="数据列表")


class ApiResponse(BaseModel):
    \"\"\"通用 API 响应包装

    常见格式:
        {"code": 200, "message": "success", "data": {...}}
    \"\"\"

    model_config = ConfigDict(populate_by_name=True)

    code: int = Field(..., description="业务状态码")
    message: str = Field(..., description="响应消息")
    data: dict[str, Any] | list[Any] | None = Field(None, description="响应数据")


__all__ = [
    "ExampleResponse",
    "PagedExamplesResponse",
    "ApiResponse",
]

# ========== AUTO-GENERATED END ==========


# ========== USER EXTENSIONS ==========
# 在此区域添加自定义代码，重新生成时会保留

"""

__all__ = ["MODELS_RESPONSES_EXAMPLE_TEMPLATE"]
