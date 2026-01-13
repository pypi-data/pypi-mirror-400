"""基础数据模型

v3.41.1 重构：
- 从 df_test_framework.models.base 迁移到 df_test_framework.core.models.base
- 属于 Layer 0 核心层，与 types.py 中的类型定义同级

v3.41.1 改进：
- BaseRequest 默认序列化时排除 None 值和使用别名
- 避免发送 null 值导致后端问题
"""

from datetime import datetime
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseRequest(BaseModel):
    """请求基类

    v3.41.1 改进：
    - 默认序列化时排除 None 值（exclude_none=True）
    - 默认使用字段别名（by_alias=True）
    - 避免自动生成的模型发送大量 null 值

    使用示例：
        >>> request = MyRequest(name="test")  # other_field 默认为 None
        >>> request.model_dump()
        {"name": "test"}  # 不包含 other_field: null
    """

    model_config = ConfigDict(
        extra="forbid",  # 禁止额外字段
        str_strip_whitespace=True,  # 自动去除字符串前后空格
        populate_by_name=True,  # 支持 snake_case 和 camelCase
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """序列化模型，默认排除 None 值和使用别名

        Args:
            **kwargs: 传递给父类 model_dump 的参数

        Returns:
            序列化后的字典
        """
        kwargs.setdefault("exclude_none", True)
        kwargs.setdefault("by_alias", True)
        return super().model_dump(**kwargs)

    def model_dump_json(self, **kwargs: Any) -> str:
        """序列化为 JSON 字符串，默认排除 None 值和使用别名

        Args:
            **kwargs: 传递给父类 model_dump_json 的参数

        Returns:
            JSON 字符串
        """
        kwargs.setdefault("exclude_none", True)
        kwargs.setdefault("by_alias", True)
        return super().model_dump_json(**kwargs)


class BaseResponse[T](BaseModel):
    """
    通用响应模型

    适用于标准的API响应格式:
    {
        "success": true,
        "code": "200",
        "message": "操作成功",
        "data": {...},
        "timestamp": "2025-10-29T14:30:00"
    }
    """

    success: bool = Field(description="是否成功")
    code: str = Field(description="响应码")
    message: str = Field(description="响应消息")
    data: T | None = Field(default=None, description="响应数据")
    timestamp: datetime | None = Field(default=None, description="时间戳")

    model_config = {
        "extra": "allow",  # 允许额外字段
    }


class PageResponse[T](BaseModel):
    """
    分页响应模型

    适用于分页查询的响应:
    {
        "items": [...],
        "total": 100,
        "page": 1,
        "page_size": 20,
        "total_pages": 5
    }
    """

    items: list[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(description="总记录数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页大小")
    total_pages: int | None = Field(default=None, description="总页数")

    model_config = {
        "extra": "allow",
    }

    def __init__(self, **data):
        super().__init__(**data)
        # 自动计算总页数
        if self.total_pages is None and self.page_size > 0:
            self.total_pages = (self.total + self.page_size - 1) // self.page_size


__all__ = ["BaseRequest", "BaseResponse", "PageResponse"]
