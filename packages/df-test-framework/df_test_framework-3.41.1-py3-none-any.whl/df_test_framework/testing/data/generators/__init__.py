"""数据生成器模块

v3.29.0 新增: 从 utils/ 迁移到 testing/data/generators/

提供测试数据生成能力:
- DataGenerator: 基于 Faker 的原子数据生成器

使用示例:
    >>> from df_test_framework.testing.data.generators import DataGenerator
    >>>
    >>> gen = DataGenerator()
    >>> name = gen.name()  # "张三"
    >>> email = gen.email()  # "test@example.com"
    >>> order_no = gen.order_no()  # "TEST_ORD_1734567890123"
    >>>
    >>> # 类方法（无需实例化）
    >>> test_id = DataGenerator.test_id("TEST_USER")  # "TEST_USER20251216..."
"""

from .data_generator import DataGenerator

__all__ = ["DataGenerator"]
