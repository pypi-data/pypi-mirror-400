"""测试数据工厂模块

v3.29.0: 初始 Factory 模式实现
v3.31.0: 重构合并，融合 factory_boy 和 polyfactory 最佳实践

提供强大的测试数据构建能力，基于 Factory Pattern。

核心特性:
- 声明式定义数据结构
- 支持序列化字段（自增 ID、序列值等）
- 支持延迟属性（依赖其他字段计算）
- 支持 Faker 集成（生成假数据）
- 支持嵌套工厂（SubFactory）
- 支持预设配置（Trait）
- 支持 Pydantic 模型

使用示例:
    >>> from df_test_framework.testing.data.factories import (
    ...     Factory, Sequence, LazyAttribute, Trait,
    ...     UserFactory, OrderFactory,
    ... )
    >>>
    >>> # 使用预置工厂
    >>> user = UserFactory.build()
    >>> admin = UserFactory.build(admin=True)
    >>> users = UserFactory.build_batch(100)
    >>>
    >>> # 自定义工厂
    >>> from datetime import datetime
    >>> class MyFactory(Factory):
    ...     id = Sequence()
    ...     name = Sequence(lambda n: f"item_{n}")
    ...     created_at = Use(datetime.now)
    >>>
    >>> item = MyFactory.build()

参考:
- factory_boy: https://factoryboy.readthedocs.io/
- polyfactory: https://polyfactory.litestar.dev/
"""

from .base import (
    Factory,
    FactoryMeta,
    FactoryOptions,
    FakerAttribute,
    LazyAttribute,
    ModelFactory,
    PostGenerated,
    Sequence,
    SubFactory,
    Trait,
    Use,
)
from .examples import (
    AddressFactory,
    ApiResponseFactory,
    CardFactory,
    OrderFactory,
    PaginationFactory,
    PaymentFactory,
    ProductFactory,
    UserFactory,
)

__all__ = [
    # 核心类
    "Factory",
    "FactoryMeta",
    "ModelFactory",
    "FactoryOptions",
    # 字段类型
    "Sequence",
    "LazyAttribute",
    "PostGenerated",
    "SubFactory",
    "FakerAttribute",
    "Use",
    # Trait
    "Trait",
    # 预置工厂
    "UserFactory",
    "ProductFactory",
    "AddressFactory",
    "OrderFactory",
    "PaymentFactory",
    "CardFactory",
    "ApiResponseFactory",
    "PaginationFactory",
]
