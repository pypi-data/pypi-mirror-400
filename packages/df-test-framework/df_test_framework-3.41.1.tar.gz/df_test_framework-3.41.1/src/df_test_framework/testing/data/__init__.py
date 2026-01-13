"""测试数据管理

提供测试数据的构建、生成、加载和工厂能力

模块:
- builders: 数据构建器 (Builder模式)
- generators: 数据生成器 (基于 Faker)
- loaders: 数据加载器 (JSON/CSV/YAML)
- factories: 数据工厂 (Factory模式)

使用示例:
    >>> from df_test_framework.testing.data import DictBuilder, JSONLoader, CSVLoader
    >>>
    >>> # 构建数据
    >>> data = DictBuilder().set("name", "Alice").set("age", 25).build()
    >>>
    >>> # 加载数据
    >>> users = JSONLoader.load("tests/data/users.json")
    >>> products = CSVLoader.load("tests/data/products.csv")
    >>>
    >>> # 生成数据 (v3.29.0)
    >>> from df_test_framework.testing.data import DataGenerator
    >>> gen = DataGenerator()
    >>> name = gen.name()
    >>> email = gen.email()
    >>>
    >>> # 工厂模式 (v3.29.0)
    >>> from df_test_framework.testing.data import Factory
    >>> class UserFactory(Factory):
    ...     @classmethod
    ...     def _default_fields(cls) -> dict:
    ...         gen = cls._get_generator()
    ...         return {"id": gen.user_id(), "name": gen.name()}
    >>> user = UserFactory.create()

v3.10.0新增 (P2.2):
- 数据加载器: JSONLoader, CSVLoader, YAMLLoader

v3.29.0新增:
- 数据生成器: DataGenerator (从 utils/ 迁移)
- 数据工厂: Factory, ModelFactory
"""

from .builders.base import BaseBuilder, DictBuilder
from .factories import (
    AddressFactory,
    Factory,
    FactoryMeta,
    ModelFactory,
    OrderFactory,
    ProductFactory,
    UserFactory,
)
from .generators import DataGenerator
from .loaders import CSVLoader, DataLoader, JSONLoader, YAMLLoader

__all__ = [
    # 构建器
    "BaseBuilder",
    "DictBuilder",
    # 生成器 (v3.29.0)
    "DataGenerator",
    # 工厂 (v3.29.0)
    "Factory",
    "ModelFactory",
    "FactoryMeta",
    # 预定义工厂 (v3.29.0)
    "UserFactory",
    "ProductFactory",
    "OrderFactory",
    "AddressFactory",
    # 加载器 (v3.10.0)
    "DataLoader",
    "JSONLoader",
    "CSVLoader",
    "YAMLLoader",
]
