"""核心数据模型

v3.41.1 重构：
- 从 df_test_framework.models 迁移到 df_test_framework.core.models
- 更符合五层架构设计，基础模型属于 Layer 0 核心层

包含：
- BaseRequest: 请求基类（默认排除 None 值）
- BaseResponse: 响应基类
- PageResponse: 分页响应基类
"""

from df_test_framework.core.models.base import (
    BaseRequest,
    BaseResponse,
    PageResponse,
)

__all__ = [
    "BaseRequest",
    "BaseResponse",
    "PageResponse",
]
