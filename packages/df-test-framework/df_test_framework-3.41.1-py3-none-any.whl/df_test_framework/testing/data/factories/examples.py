"""预置数据工厂

v3.29.0: 初始实现
v3.31.0: 重构，使用新的 Factory 基类

提供开箱即用的常用业务对象工厂，可直接使用或作为自定义工厂的参考。

包含的工厂:
- UserFactory: 用户对象工厂
- OrderFactory: 订单对象工厂
- ProductFactory: 商品对象工厂
- AddressFactory: 地址对象工厂
- PaymentFactory: 支付对象工厂
- CardFactory: 卡券对象工厂
- ApiResponseFactory: API 响应工厂
- PaginationFactory: 分页数据工厂

使用示例:
    >>> from df_test_framework.testing.data.factories import UserFactory, OrderFactory
    >>>
    >>> # 创建用户
    >>> user = UserFactory.build()
    >>> print(user)
    {'id': 1, 'username': 'user_1', 'email': 'user_1@example.com', ...}
    >>>
    >>> # 创建 VIP 用户
    >>> vip_user = UserFactory.build(vip=True)
    >>>
    >>> # 批量创建订单
    >>> orders = OrderFactory.build_batch(5, paid=True)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import uuid4

from .base import (
    Factory,
    FakerAttribute,
    LazyAttribute,
    PostGenerated,
    Sequence,
    SubFactory,
    Trait,
    Use,
)


def _random_choice(choices: list[Any]) -> Any:
    """随机选择（不依赖 faker）"""
    import random

    return random.choice(choices)


def _random_int(min_val: int, max_val: int) -> int:
    """生成随机整数"""
    import random

    return random.randint(min_val, max_val)


def _random_decimal(
    min_val: float = 0.01,
    max_val: float = 9999.99,
    decimals: int = 2,
) -> Decimal:
    """生成随机金额"""
    import random

    value = random.uniform(min_val, max_val)
    return Decimal(str(round(value, decimals)))


class UserFactory(Factory):
    """用户数据工厂

    生成用户相关测试数据，支持多种预设配置。

    字段说明:
        id: 自增 ID
        user_id: UUID 格式用户 ID
        username: 用户名 (user_1, user_2, ...)
        email: 邮箱 (基于 username 生成)
        phone: 手机号 (Faker 生成)
        name: 真实姓名 (Faker 生成)
        password: 密码哈希
        avatar: 头像 URL
        gender: 性别 (male/female/unknown)
        age: 年龄 (18-60)
        status: 状态 (active/inactive/banned)
        role: 角色 (user/admin/vip)
        is_verified: 是否验证
        created_at: 创建时间
        updated_at: 更新时间

    Traits:
        vip: VIP 用户预设
        admin: 管理员预设
        inactive: 禁用用户预设

    示例:
        >>> user = UserFactory.build()
        >>> admin = UserFactory.build(admin=True)
        >>> vip = UserFactory.build(vip=True, level=10)
        >>> users = UserFactory.build_batch(100)
    """

    class Meta:
        model = dict

    # 基础字段
    id = Sequence()
    user_id = Use(lambda: str(uuid4()))
    username = Sequence(lambda n: f"user_{n}")
    email = LazyAttribute(lambda obj: f"{obj['username']}@example.com")

    # Faker 字段（如果可用，否则使用备选方案）
    try:
        phone = FakerAttribute("phone_number")
        name = FakerAttribute("name")
    except Exception:
        phone = Sequence(lambda n: f"138{str(n).zfill(8)}")
        name = Sequence(lambda n: f"测试用户{n}")

    password = "hashed_password_placeholder"
    avatar = LazyAttribute(lambda obj: f"https://avatar.example.com/{obj['username']}.png")
    gender = Use(lambda: _random_choice(["male", "female", "unknown"]))
    age = Use(lambda: _random_int(18, 60))
    status = "active"
    role = "user"
    is_verified = True
    is_superuser = False
    created_at = Use(datetime.now)
    updated_at = LazyAttribute(lambda obj: obj["created_at"])

    class Params:
        """预设配置"""

        vip = Trait(
            role="vip",
            is_verified=True,
        )
        admin = Trait(
            role="admin",
            is_superuser=True,
            is_verified=True,
        )
        inactive = Trait(
            status="inactive",
            is_verified=False,
        )


class ProductFactory(Factory):
    """商品数据工厂

    生成商品相关测试数据。

    字段说明:
        id: 自增 ID
        product_id: 商品 ID (UUID)
        sku: SKU 编码
        name: 商品名称
        description: 商品描述
        category: 商品分类
        price: 原价
        sale_price: 售价
        cost_price: 成本价
        stock: 库存
        sold_count: 销量
        status: 状态 (on_sale/off_sale/sold_out)
        weight: 重量 (克)
        images: 图片列表
        tags: 标签列表
        created_at: 创建时间

    Traits:
        out_of_stock: 缺货商品
        off_sale: 下架商品

    示例:
        >>> product = ProductFactory.build()
        >>> expensive = ProductFactory.build(price=Decimal("9999.00"))
        >>> sold_out = ProductFactory.build(out_of_stock=True)
    """

    class Meta:
        model = dict

    id = Sequence()
    product_id = Use(lambda: str(uuid4()))
    sku = Sequence(lambda n: f"SKU-{str(n).zfill(8)}")

    try:
        name = FakerAttribute("word")
        description = FakerAttribute("sentence")
    except Exception:
        name = Sequence(lambda n: f"商品{n}")
        description = Sequence(lambda n: f"这是商品{n}的描述")

    category = Use(lambda: _random_choice(["electronics", "clothing", "food", "books", "home"]))
    price = Use(lambda: _random_decimal(10.00, 2000.00))
    sale_price = LazyAttribute(lambda obj: obj["price"] * Decimal("0.9"))
    cost_price = LazyAttribute(lambda obj: obj["price"] * Decimal("0.5"))
    stock = Use(lambda: _random_int(0, 1000))
    sold_count = Use(lambda: _random_int(0, 10000))
    status = "on_sale"
    weight = Use(lambda: _random_int(100, 5000))
    images = LazyAttribute(
        lambda obj: [f"https://img.example.com/{obj['sku']}/{i}.jpg" for i in range(3)]
    )
    tags = Use(lambda: _random_choice([["热销", "推荐"], ["新品"], ["特价", "限时"], []]))
    created_at = Use(datetime.now)

    class Params:
        out_of_stock = Trait(
            stock=0,
            status="sold_out",
        )
        off_sale = Trait(
            status="off_sale",
        )


class AddressFactory(Factory):
    """地址数据工厂

    生成收货地址相关测试数据。

    字段说明:
        id: 自增 ID
        user_id: 用户 ID
        name: 收货人姓名
        phone: 收货人电话
        province: 省份
        city: 城市
        district: 区县
        street: 街道地址
        postal_code: 邮编
        is_default: 是否默认地址
        tag: 标签 (家/公司/学校)

    Traits:
        default: 默认地址预设

    示例:
        >>> addr = AddressFactory.build()
        >>> default_addr = AddressFactory.build(default=True)
    """

    class Meta:
        model = dict

    id = Sequence()
    user_id = Use(lambda: str(uuid4()))

    try:
        name = FakerAttribute("name")
        phone = FakerAttribute("phone_number")
        province = FakerAttribute("province")
        city = FakerAttribute("city")
        district = FakerAttribute("district")
        street = FakerAttribute("street_address")
        postal_code = FakerAttribute("postcode")
    except Exception:
        name = Sequence(lambda n: f"收货人{n}")
        phone = Sequence(lambda n: f"139{str(n).zfill(8)}")
        province = "广东省"
        city = "深圳市"
        district = "南山区"
        street = Sequence(lambda n: f"科技园{n}号")
        postal_code = "518000"

    is_default = False
    tag = Use(lambda: _random_choice(["家", "公司", "学校", ""]))

    class Params:
        default = Trait(is_default=True)


class OrderFactory(Factory):
    """订单数据工厂

    生成订单相关测试数据。

    字段说明:
        id: 自增 ID
        order_no: 订单号 (ORD-20251216-000001)
        user_id: 用户 ID
        status: 订单状态 (pending/paid/shipped/completed/cancelled)
        total_amount: 订单总金额
        discount_amount: 折扣金额
        payment_amount: 实付金额
        quantity: 商品数量
        shipping_fee: 运费
        payment_method: 支付方式
        shipping_address: 收货地址（嵌套 AddressFactory）
        remark: 备注
        created_at: 创建时间
        paid_at: 支付时间
        shipped_at: 发货时间
        completed_at: 完成时间

    Traits:
        paid: 已支付订单
        shipped: 已发货订单
        completed: 已完成订单
        cancelled: 已取消订单

    示例:
        >>> order = OrderFactory.build()
        >>> paid_order = OrderFactory.build(paid=True)
        >>> orders = OrderFactory.build_batch(50, paid=True)
    """

    class Meta:
        model = dict

    id = Sequence()
    order_no = Sequence(lambda n: f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(n).zfill(6)}")
    user_id = Use(lambda: str(uuid4()))
    status = "pending"
    total_amount = Use(lambda: _random_decimal(10.00, 5000.00))
    # 折扣金额不超过总金额的 30%，确保 payment_amount >= 0
    discount_amount = LazyAttribute(
        lambda obj: _random_decimal(0, float(obj["total_amount"]) * 0.3)
    )
    payment_amount = LazyAttribute(lambda obj: obj["total_amount"] - obj["discount_amount"])
    quantity = Use(lambda: _random_int(1, 10))
    shipping_fee = Use(lambda: _random_decimal(0, 20.00))
    payment_method = Use(lambda: _random_choice(["alipay", "wechat", "card", "cash"]))
    shipping_address = SubFactory(AddressFactory)
    remark = ""
    created_at = Use(datetime.now)
    paid_at = None
    shipped_at = None
    completed_at = None

    class Params:
        paid = Trait(
            status="paid",
            paid_at=Use(datetime.now),
        )
        shipped = Trait(
            status="shipped",
            paid_at=Use(lambda: datetime.now() - timedelta(days=1)),
            shipped_at=Use(datetime.now),
        )
        completed = Trait(
            status="completed",
            paid_at=Use(lambda: datetime.now() - timedelta(days=3)),
            shipped_at=Use(lambda: datetime.now() - timedelta(days=2)),
            completed_at=Use(datetime.now),
        )
        cancelled = Trait(
            status="cancelled",
        )


class PaymentFactory(Factory):
    """支付数据工厂

    生成支付相关测试数据。

    字段说明:
        id: 自增 ID
        payment_no: 支付单号
        order_no: 关联订单号
        user_id: 用户 ID
        amount: 支付金额
        method: 支付方式
        status: 支付状态 (pending/success/failed/refunded)
        channel: 支付渠道
        transaction_id: 第三方交易号
        paid_at: 支付时间
        created_at: 创建时间
        metadata: 扩展数据

    Traits:
        success: 成功支付
        failed: 失败支付
        refunded: 已退款

    示例:
        >>> payment = PaymentFactory.build()
        >>> success_payment = PaymentFactory.build(success=True)
    """

    class Meta:
        model = dict

    id = Sequence()
    payment_no = Sequence(lambda n: f"PAY-{datetime.now().strftime('%Y%m%d')}-{str(n).zfill(6)}")
    order_no = Sequence(lambda n: f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(n).zfill(6)}")
    user_id = Use(lambda: str(uuid4()))
    amount = Use(lambda: _random_decimal(1.00, 10000.00))
    method = Use(lambda: _random_choice(["alipay", "wechat", "unionpay", "card"]))
    status = "pending"
    channel = LazyAttribute(lambda obj: f"{obj['method']}_app")
    transaction_id = Use(lambda: f"TXN{uuid4().hex[:16].upper()}")
    paid_at = None
    created_at = Use(datetime.now)
    metadata = Use(lambda: {})

    class Params:
        success = Trait(
            status="success",
            paid_at=Use(datetime.now),
        )
        failed = Trait(
            status="failed",
        )
        refunded = Trait(
            status="refunded",
            paid_at=Use(lambda: datetime.now() - timedelta(days=1)),
        )


class CardFactory(Factory):
    """卡券数据工厂

    生成卡券相关测试数据（礼品卡、优惠券等）。

    字段说明:
        id: 自增 ID
        card_no: 卡号
        card_type: 卡类型 (gift_card/coupon/voucher)
        face_value: 面值
        balance: 余额
        status: 状态 (inactive/active/used/expired)
        user_id: 绑定用户
        expire_at: 过期时间
        created_at: 创建时间
        activated_at: 激活时间
        used_at: 使用时间

    Traits:
        active: 已激活卡券
        used: 已使用卡券
        expired: 已过期卡券

    示例:
        >>> card = CardFactory.build()
        >>> gift_card = CardFactory.build(card_type="gift_card", face_value=Decimal("100.00"))
        >>> active_card = CardFactory.build(active=True)
    """

    class Meta:
        model = dict

    id = Sequence()
    card_no = Sequence(lambda n: f"CARD{str(n).zfill(12)}")
    card_type = "gift_card"
    face_value = Use(
        lambda: _random_choice(
            [Decimal("50.00"), Decimal("100.00"), Decimal("200.00"), Decimal("500.00")]
        )
    )
    balance = LazyAttribute(lambda obj: obj["face_value"])
    status = "inactive"
    user_id = None
    expire_at = Use(lambda: datetime.now() + timedelta(days=365))
    created_at = Use(datetime.now)
    activated_at = None
    used_at = None

    class Params:
        active = Trait(
            status="active",
            user_id=Use(lambda: str(uuid4())),
            activated_at=Use(datetime.now),
        )
        used = Trait(
            status="used",
            balance=Decimal("0.00"),
            user_id=Use(lambda: str(uuid4())),
            activated_at=Use(lambda: datetime.now() - timedelta(days=30)),
            used_at=Use(datetime.now),
        )
        expired = Trait(
            status="expired",
            expire_at=Use(lambda: datetime.now() - timedelta(days=1)),
        )


class ApiResponseFactory(Factory):
    """API 响应数据工厂

    生成标准 API 响应格式测试数据。

    字段说明:
        code: 业务码
        message: 消息
        data: 数据体
        timestamp: 时间戳
        request_id: 请求 ID

    Traits:
        error: 错误响应
        not_found: 404 响应

    示例:
        >>> resp = ApiResponseFactory.build()
        >>> error_resp = ApiResponseFactory.build(error=True, message="参数错误")
    """

    class Meta:
        model = dict

    code = 0
    message = "success"
    data = Use(lambda: {})
    timestamp = Use(lambda: int(datetime.now().timestamp() * 1000))
    request_id = Use(lambda: str(uuid4()))

    class Params:
        error = Trait(
            code=400,
            message="请求错误",
            data=None,
        )
        not_found = Trait(
            code=404,
            message="资源不存在",
            data=None,
        )


class PaginationFactory(Factory):
    """分页数据工厂

    生成分页响应测试数据。

    字段说明:
        items: 数据列表
        total: 总条数
        page: 当前页
        page_size: 每页条数
        total_pages: 总页数
        has_next: 是否有下一页
        has_prev: 是否有上一页

    示例:
        >>> page = PaginationFactory.build(total=100, page=1, page_size=10)
    """

    class Meta:
        model = dict

    items = Use(lambda: [])
    total = 0
    page = 1
    page_size = 20
    total_pages = PostGenerated(
        lambda name, obj: (
            (obj["total"] + obj["page_size"] - 1) // obj["page_size"] if obj["page_size"] > 0 else 0
        )
    )
    has_next = PostGenerated(lambda name, obj: obj["page"] < obj["total_pages"])
    has_prev = PostGenerated(lambda name, obj: obj["page"] > 1)


__all__ = [
    "UserFactory",
    "ProductFactory",
    "AddressFactory",
    "OrderFactory",
    "PaymentFactory",
    "CardFactory",
    "ApiResponseFactory",
    "PaginationFactory",
]
