"""示例请求模型模板"""

MODELS_REQUESTS_EXAMPLE_TEMPLATE = """\"\"\"示例请求模型

演示如何定义请求模型，提供：
- IDE 智能提示
- 类型检查
- 自动序列化
- 字段验证

v3.39.0 新增:
- 支持增量合并（--merge 选项）
- 用户扩展区域保留自定义代码

使用方式：
    >>> from {project_name}.models.requests.example import CreateExampleRequest
    >>> request = CreateExampleRequest(name="Test", email="test@example.com")
    >>> print(request.model_dump())
\"\"\"

from pydantic import BaseModel, ConfigDict, Field


# ========== AUTO-GENERATED START ==========
# 此区域由脚手架自动生成，重新生成时会被更新


class CreateExampleRequest(BaseModel):
    \"\"\"创建示例请求模型

    演示常见的请求模型定义方式。

    Attributes:
        name: 名称（必填）
        email: 邮箱地址（必填）
        phone: 手机号（可选）
        age: 年龄（可选，带验证）
    \"\"\"

    model_config = ConfigDict(
        populate_by_name=True,  # 支持别名访问
        str_strip_whitespace=True,  # 自动去除字符串两端空白
    )

    name: str = Field(..., min_length=1, max_length=50, description="名称")
    email: str = Field(..., pattern=r"^[\\w.-]+@[\\w.-]+\\.\\w+$", description="邮箱地址")
    phone: str | None = Field(None, pattern=r"^1[3-9]\\d{9}$", description="手机号")
    age: int | None = Field(None, ge=0, le=150, description="年龄")


class UpdateExampleRequest(BaseModel):
    \"\"\"更新示例请求模型

    所有字段都是可选的，只更新传入的字段。
    \"\"\"

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = Field(None, min_length=1, max_length=50, description="名称")
    email: str | None = Field(None, description="邮箱地址")
    phone: str | None = Field(None, description="手机号")
    age: int | None = Field(None, ge=0, le=150, description="年龄")


class QueryExamplesRequest(BaseModel):
    \"\"\"查询示例列表请求模型\"\"\"

    model_config = ConfigDict(populate_by_name=True)

    keyword: str | None = Field(None, description="搜索关键词")
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页数量")


__all__ = [
    "CreateExampleRequest",
    "UpdateExampleRequest",
    "QueryExamplesRequest",
]

# ========== AUTO-GENERATED END ==========


# ========== USER EXTENSIONS ==========
# 在此区域添加自定义代码，重新生成时会保留

"""

__all__ = ["MODELS_REQUESTS_EXAMPLE_TEMPLATE"]
