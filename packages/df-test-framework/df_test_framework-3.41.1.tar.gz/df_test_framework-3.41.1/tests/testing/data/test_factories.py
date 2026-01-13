"""测试数据工厂模块测试

v3.29.0: 新增 Factory 模式测试
v3.31.0: 更新为声明式 API 测试

测试覆盖:
- Factory 基类功能（声明式字段定义）
- ModelFactory Pydantic 模型支持
- 预定义工厂（UserFactory、OrderFactory、ProductFactory、AddressFactory）
- Trait 预设配置
- 批量创建
- 字段覆盖
"""

from decimal import Decimal

from pydantic import BaseModel

from df_test_framework.testing.data.factories import (
    AddressFactory,
    Factory,
    FactoryMeta,
    FactoryOptions,
    LazyAttribute,
    ModelFactory,
    OrderFactory,
    ProductFactory,
    Sequence,
    SubFactory,
    Trait,
    Use,
    UserFactory,
)

# ============================================================
# Factory 基类测试
# ============================================================


class TestFactory:
    """测试 Factory 基类"""

    def test_factory_basic_fields(self):
        """测试基本字段定义"""

        class SimpleFactory(Factory):
            name = "test"
            value = 100

        result = SimpleFactory.build()
        # 只检查包含预期字段
        assert result["name"] == "test"
        assert result["value"] == 100

    def test_factory_sequence(self):
        """测试 Sequence 字段"""

        class SeqFactory(Factory):
            id = Sequence()
            name = Sequence(lambda n: f"item_{n}")

        r1 = SeqFactory.build()
        r2 = SeqFactory.build()

        assert r1["id"] == 1
        assert r1["name"] == "item_1"
        assert r2["id"] == 2
        assert r2["name"] == "item_2"

    def test_factory_lazy_attribute(self):
        """测试 LazyAttribute 延迟计算"""

        class LazyFactory(Factory):
            username = "alice"
            email = LazyAttribute(lambda obj: f"{obj['username']}@example.com")

        result = LazyFactory.build()
        assert result["email"] == "alice@example.com"

        result2 = LazyFactory.build(username="bob")
        assert result2["email"] == "bob@example.com"

    def test_factory_use_callable(self):
        """测试 Use 包装器"""
        from datetime import datetime

        class UseFactory(Factory):
            created_at = Use(datetime.now)

        result = UseFactory.build()
        assert isinstance(result["created_at"], datetime)

    def test_factory_trait(self):
        """测试 Trait 预设配置"""

        class StatusFactory(Factory):
            id = Sequence()
            status = "pending"
            is_active = True

            class Params:
                approved = Trait(status="approved", is_active=True)
                rejected = Trait(status="rejected", is_active=False)

        pending = StatusFactory.build()
        assert pending["status"] == "pending"

        approved = StatusFactory.build(approved=True)
        assert approved["status"] == "approved"
        assert approved["is_active"] is True

        rejected = StatusFactory.build(rejected=True)
        assert rejected["status"] == "rejected"
        assert rejected["is_active"] is False

    def test_build_with_overrides(self):
        """测试字段覆盖"""

        class TestFactory(Factory):
            id = Sequence()
            name = "default"
            status = "active"

        result = TestFactory.build(name="custom", extra="value")
        assert result["name"] == "custom"
        assert result["status"] == "active"
        assert result["extra"] == "value"

    def test_build_batch(self):
        """测试批量创建"""

        class BatchFactory(Factory):
            id = Sequence()
            value = "test"

        results = BatchFactory.build_batch(5)
        assert len(results) == 5

        # 每个对象应该有不同的 id
        ids = [r["id"] for r in results]
        assert len(set(ids)) == 5  # 5 个不同的 id

    def test_build_batch_with_common_overrides(self):
        """测试批量创建带共同覆盖"""

        class StatusFactory(Factory):
            id = Sequence()
            status = "active"

        results = StatusFactory.build_batch(3, status="vip")
        assert len(results) == 3
        for r in results:
            assert r["status"] == "vip"

    def test_subfactory(self):
        """测试 SubFactory 嵌套工厂"""

        class AddressSubFactory(Factory):
            city = "北京"
            street = "长安街"

        class PersonFactory(Factory):
            name = "张三"
            address = SubFactory(AddressSubFactory)

        result = PersonFactory.build()
        assert result["name"] == "张三"
        assert result["address"]["city"] == "北京"
        assert result["address"]["street"] == "长安街"


# ============================================================
# ModelFactory 测试
# ============================================================


class TestModelFactory:
    """测试 ModelFactory Pydantic 模型支持"""

    def test_create_pydantic_model(self):
        """测试创建 Pydantic 模型"""

        class User(BaseModel):
            id: int
            name: str
            email: str

        class UserModelFactory(ModelFactory):
            class Meta:
                model = User

            id = Sequence()
            name = Sequence(lambda n: f"user_{n}")
            email = LazyAttribute(lambda obj: f"{obj['name']}@example.com")

        user = UserModelFactory.build()
        assert isinstance(user, User)
        assert user.id == 1
        assert user.name == "user_1"
        assert user.email == "user_1@example.com"

    def test_create_batch_pydantic_models(self):
        """测试批量创建 Pydantic 模型"""

        class Product(BaseModel):
            id: int
            name: str
            price: Decimal

        class ProductModelFactory(ModelFactory):
            class Meta:
                model = Product

            id = Sequence()
            name = Sequence(lambda n: f"Product_{n}")
            price = Decimal("99.99")

        products = ProductModelFactory.build_batch(3)
        assert len(products) == 3
        for p in products:
            assert isinstance(p, Product)


# ============================================================
# UserFactory 测试
# ============================================================


class TestUserFactory:
    """测试 UserFactory 用户工厂"""

    def test_create_user(self):
        """测试创建用户"""
        user = UserFactory.build()
        assert isinstance(user, dict)
        assert "id" in user
        assert "username" in user
        assert "email" in user
        assert "role" in user
        assert user["status"] == "active"
        assert user["is_verified"] is True

    def test_create_vip_user(self):
        """测试创建 VIP 用户（使用 Trait）"""
        vip = UserFactory.build(vip=True)
        assert vip["role"] == "vip"
        assert vip["is_verified"] is True

    def test_create_admin_user(self):
        """测试创建管理员用户（使用 Trait）"""
        admin = UserFactory.build(admin=True)
        assert admin["role"] == "admin"
        assert admin["is_superuser"] is True

    def test_create_inactive_user(self):
        """测试创建禁用用户（使用 Trait）"""
        inactive = UserFactory.build(inactive=True)
        assert inactive["status"] == "inactive"
        assert inactive["is_verified"] is False

    def test_create_batch_users(self):
        """测试批量创建用户"""
        users = UserFactory.build_batch(5)
        assert len(users) == 5

        # 每个用户应该有不同的 id
        ids = [u["id"] for u in users]
        assert len(set(ids)) == 5

    def test_override_fields(self):
        """测试字段覆盖"""
        user = UserFactory.build(
            username="zhangsan",
            email="zhangsan@test.com",
            custom_field="custom_value",
        )
        assert user["username"] == "zhangsan"
        assert user["email"] == "zhangsan@test.com"
        assert user["custom_field"] == "custom_value"


# ============================================================
# ProductFactory 测试
# ============================================================


class TestProductFactory:
    """测试 ProductFactory 商品工厂"""

    def test_create_product(self):
        """测试创建商品"""
        product = ProductFactory.build()
        assert isinstance(product, dict)
        assert "id" in product
        assert "name" in product
        assert "sku" in product
        assert "price" in product
        assert "stock" in product
        assert product["status"] == "on_sale"

    def test_price_is_decimal(self):
        """测试价格是 Decimal 类型"""
        product = ProductFactory.build()
        assert isinstance(product["price"], Decimal)

    def test_create_out_of_stock(self):
        """测试创建缺货商品（使用 Trait）"""
        product = ProductFactory.build(out_of_stock=True)
        assert product["stock"] == 0
        assert product["status"] == "sold_out"

    def test_create_off_sale(self):
        """测试创建下架商品（使用 Trait）"""
        product = ProductFactory.build(off_sale=True)
        assert product["status"] == "off_sale"

    def test_category_is_valid(self):
        """测试商品分类有效"""
        product = ProductFactory.build()
        expected_categories = ["electronics", "clothing", "food", "books", "home"]
        assert product["category"] in expected_categories


# ============================================================
# OrderFactory 测试
# ============================================================


class TestOrderFactory:
    """测试 OrderFactory 订单工厂"""

    def test_create_order(self):
        """测试创建订单"""
        order = OrderFactory.build()
        assert isinstance(order, dict)
        assert "id" in order
        assert "order_no" in order
        assert "user_id" in order
        assert "total_amount" in order
        assert "payment_amount" in order
        assert order["status"] == "pending"

    def test_order_has_shipping_address(self):
        """测试订单包含收货地址"""
        order = OrderFactory.build()
        assert "shipping_address" in order
        assert isinstance(order["shipping_address"], dict)
        address = order["shipping_address"]
        assert "name" in address
        assert "phone" in address
        assert "province" in address
        assert "city" in address

    def test_order_payment_amount_calculated(self):
        """测试订单实付金额计算"""
        order = OrderFactory.build()
        expected_payment = order["total_amount"] - order["discount_amount"]
        assert order["payment_amount"] == expected_payment

    def test_create_paid_order(self):
        """测试创建已支付订单（使用 Trait）"""
        order = OrderFactory.build(paid=True)
        assert order["status"] == "paid"
        assert order["paid_at"] is not None

    def test_create_shipped_order(self):
        """测试创建已发货订单（使用 Trait）"""
        order = OrderFactory.build(shipped=True)
        assert order["status"] == "shipped"
        assert order["shipped_at"] is not None
        assert order["paid_at"] is not None

    def test_create_completed_order(self):
        """测试创建已完成订单（使用 Trait）"""
        order = OrderFactory.build(completed=True)
        assert order["status"] == "completed"
        assert order["completed_at"] is not None
        assert order["shipped_at"] is not None
        assert order["paid_at"] is not None

    def test_create_cancelled_order(self):
        """测试创建已取消订单（使用 Trait）"""
        order = OrderFactory.build(cancelled=True)
        assert order["status"] == "cancelled"

    def test_create_batch_with_same_user(self):
        """测试批量创建同一用户的订单"""
        user_id = "USR_TEST_001"
        orders = OrderFactory.build_batch(3, user_id=user_id)
        assert len(orders) == 3
        for order in orders:
            assert order["user_id"] == user_id


# ============================================================
# AddressFactory 测试
# ============================================================


class TestAddressFactory:
    """测试 AddressFactory 地址工厂"""

    def test_create_address(self):
        """测试创建地址"""
        address = AddressFactory.build()
        assert isinstance(address, dict)
        assert "id" in address
        assert "user_id" in address
        assert "name" in address
        assert "phone" in address
        assert "province" in address
        assert "city" in address
        assert "district" in address
        assert "street" in address
        assert address["is_default"] is False

    def test_create_default_address(self):
        """测试创建默认地址（使用 Trait）"""
        address = AddressFactory.build(default=True)
        assert address["is_default"] is True

    def test_address_has_tag(self):
        """测试地址有标签字段"""
        address = AddressFactory.build()
        assert "tag" in address
        # tag 可能是 "家", "公司", "学校" 或空字符串
        assert address["tag"] in ["家", "公司", "学校", ""]


# ============================================================
# FactoryMeta / FactoryOptions 测试
# ============================================================


class TestFactoryMeta:
    """测试 Factory 元类和配置"""

    def test_default_model_is_dict(self):
        """测试默认模型是 dict"""

        class NoMetaFactory(Factory):
            id = Sequence()

        result = NoMetaFactory.build()
        assert isinstance(result, dict)

    def test_custom_model_in_meta(self):
        """测试 Meta 中定义模型"""

        class Data(BaseModel):
            id: int
            name: str

        class DataFactory(ModelFactory):
            class Meta:
                model = Data

            id = Sequence()
            name = "test"

        result = DataFactory.build()
        assert isinstance(result, Data)

    def test_factory_options_dataclass(self):
        """测试 FactoryOptions 数据类"""
        options = FactoryOptions(model=dict)
        assert options.model is dict
        assert options.abstract is False

    def test_factory_meta_is_abcmeta_subclass(self):
        """测试 FactoryMeta 是 ABCMeta 的子类"""
        from abc import ABCMeta

        assert issubclass(FactoryMeta, ABCMeta)


__all__ = [
    "TestFactory",
    "TestModelFactory",
    "TestUserFactory",
    "TestProductFactory",
    "TestOrderFactory",
    "TestAddressFactory",
    "TestFactoryMeta",
]
