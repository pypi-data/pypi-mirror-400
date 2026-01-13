# Factory 系统使用指南

> **版本**: v3.38.0 | **更新**: 2025-12-24
> **引入版本**: v3.31.0
> **模块**: `df_test_framework.testing.data.factories`

Factory 系统是 DF Test Framework 的测试数据生成核心，融合了 [factory_boy](https://factoryboy.readthedocs.io/) 和 [polyfactory](https://polyfactory.litestar.dev/) 的最佳实践，提供声明式、类型安全的测试数据创建方式。

---

## 快速开始

### 安装依赖

Factory 系统已内置于框架中，无需额外安装。如需 Faker 支持：

```bash
uv add faker  # 或 pip install faker
```

### 基本使用

```python
from df_test_framework.testing.data.factories import (
    Factory,
    Sequence,
    LazyAttribute,
    UserFactory,  # 预置工厂
)

# 使用预置工厂
user = UserFactory.build()
# {'id': 1, 'username': 'user_1', 'email': 'user_1@example.com', ...}

# 批量创建
users = UserFactory.build_batch(10)

# 使用 Trait 预设
admin = UserFactory.build(admin=True)
vip = UserFactory.build(vip=True)

# 覆盖字段
custom_user = UserFactory.build(
    username="test_admin",
    role="admin",
    age=30,
)
```

---

## 核心概念

### Factory 与 DataGenerator 的区别

| 特性 | DataGenerator | Factory |
|------|---------------|---------|
| **职责** | 生成单个字段值（原子数据） | 组装完整业务对象 |
| **返回值** | 字符串、数字、日期等 | dict、Pydantic 模型、dataclass |
| **使用场景** | 需要单个随机值 | 需要完整测试数据对象 |
| **示例** | `gen.email()` → `"user@example.com"` | `UserFactory.build()` → `{...}` |

```
+-------------------+
|     Factory       |  ← 业务对象层（用户、订单、商品）
+-------------------+
         |
         | 内部使用
         v
+-------------------+
|   DataGenerator   |  ← 原子数据层（邮箱、手机号、地址）
+-------------------+
         |
         | 内部使用
         v
+-------------------+
|      Faker        |  ← 假数据生成库
+-------------------+
```

---

## 自定义 Factory

### 基础示例

```python
from df_test_framework.testing.data.factories import (
    Factory,
    Sequence,
    LazyAttribute,
    Use,
)
from datetime import datetime

class ArticleFactory(Factory):
    """文章数据工厂"""

    class Meta:
        model = dict  # 输出类型：dict

    # 自增 ID
    id = Sequence()

    # 带格式的序列
    slug = Sequence(lambda n: f"article-{n}")

    # 静态值
    status = "draft"

    # 延迟执行（每次调用都执行）
    created_at = Use(datetime.now)

    # 延迟计算（可访问其他字段）
    title = Sequence(lambda n: f"文章标题 {n}")
    url = LazyAttribute(lambda obj: f"/articles/{obj['slug']}")

# 使用
article = ArticleFactory.build()
# {
#     'id': 1,
#     'slug': 'article-1',
#     'status': 'draft',
#     'created_at': datetime(...),
#     'title': '文章标题 1',
#     'url': '/articles/article-1'
# }
```

### 支持 Pydantic 模型

```python
from pydantic import BaseModel
from df_test_framework.testing.data.factories import Factory, Sequence, ModelFactory

class User(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool = True

class UserFactory(ModelFactory[User]):
    """用户模型工厂 - 返回 Pydantic 实例"""

    class Meta:
        model = User  # 指定 Pydantic 模型

    id = Sequence()
    name = Sequence(lambda n: f"用户{n}")
    email = LazyAttribute(lambda obj: f"user_{obj['id']}@example.com")
    is_active = True

# build() 返回 User 实例
user: User = UserFactory.build()
assert isinstance(user, User)
assert user.id == 1
assert user.email == "user_1@example.com"
```

---

## 字段类型详解

### 1. Sequence - 自增序列

生成递增的序列值，每个字段有独立的计数器。

```python
class OrderFactory(Factory):
    class Meta:
        model = dict

    # 简单序列：1, 2, 3, ...
    id = Sequence()

    # 格式化序列
    order_no = Sequence(lambda n: f"ORD-{n:08d}")
    # ORD-00000001, ORD-00000002, ...

    # 日期格式序列
    code = Sequence(lambda n: f"ORD-{datetime.now():%Y%m%d}-{n:06d}")
    # ORD-20251218-000001, ORD-20251218-000002, ...
```

**重置计数器**：

```python
# 重置所有计数器
Sequence.reset()

# 重置特定计数器
Sequence.reset("OrderFactory.id")
```

### 2. LazyAttribute - 延迟计算

属性值在 build 时动态计算，可以访问其他已生成的字段。

```python
class UserFactory(Factory):
    class Meta:
        model = dict

    first_name = "张"
    last_name = Sequence(lambda n: f"三{n}")

    # 访问其他字段
    full_name = LazyAttribute(lambda obj: f"{obj['first_name']}{obj['last_name']}")
    email = LazyAttribute(lambda obj: f"{obj['full_name']}@example.com")

    # 使用 get 避免 KeyError
    display_name = LazyAttribute(
        lambda obj: obj.get('nickname') or obj['full_name']
    )
```

### 3. PostGenerated - 后处理字段

在所有其他字段生成完成后计算，确保能访问完整的对象。

```python
class OrderFactory(Factory):
    class Meta:
        model = dict

    items = Use(lambda: [
        {"name": "商品A", "price": 100, "quantity": 2},
        {"name": "商品B", "price": 50, "quantity": 1},
    ])
    shipping_fee = Use(lambda: Decimal("10.00"))

    # 在所有字段生成后计算总价
    total = PostGenerated(
        lambda name, values: sum(
            item["price"] * item["quantity"]
            for item in values["items"]
        ) + values["shipping_fee"]
    )
    # total = 100*2 + 50*1 + 10 = 260
```

### 4. SubFactory - 嵌套工厂

使用另一个 Factory 生成嵌套对象。

```python
class AddressFactory(Factory):
    class Meta:
        model = dict

    city = "北京"
    street = Sequence(lambda n: f"街道{n}号")
    postal_code = "100000"

class UserFactory(Factory):
    class Meta:
        model = dict

    name = Sequence(lambda n: f"用户{n}")

    # 嵌套地址
    address = SubFactory(AddressFactory)

    # 带默认值的嵌套
    work_address = SubFactory(AddressFactory, city="上海")

user = UserFactory.build()
# {
#     'name': '用户1',
#     'address': {'city': '北京', 'street': '街道1号', 'postal_code': '100000'},
#     'work_address': {'city': '上海', 'street': '街道2号', 'postal_code': '100000'}
# }

# 覆盖嵌套字段（使用 __ 分隔）
user = UserFactory.build(address__city="深圳")
# address.city = "深圳"
```

### 5. FakerAttribute - Faker 集成

使用 Faker 库生成假数据。

```python
class UserFactory(Factory):
    class Meta:
        model = dict

    # 常用 Faker providers
    name = FakerAttribute("name")           # 姓名
    email = FakerAttribute("email")         # 邮箱
    phone = FakerAttribute("phone_number")  # 电话
    address = FakerAttribute("address")     # 地址
    company = FakerAttribute("company")     # 公司
    job = FakerAttribute("job")             # 职位

    # 带参数
    text = FakerAttribute("text", max_nb_chars=200)

    # 日期相关
    birthday = FakerAttribute("date_of_birth", minimum_age=18, maximum_age=60)
```

> **注意**: 需要安装 faker 包：`uv add faker`

### 6. Use - 延迟执行

包装一个可调用对象，在 build 时执行。比 LazyAttribute 更简单。

```python
from datetime import datetime
from uuid import uuid4

class OrderFactory(Factory):
    class Meta:
        model = dict

    # 每次生成新的 UUID
    order_id = Use(lambda: str(uuid4()))

    # 当前时间
    created_at = Use(datetime.now)

    # 随机选择
    status = Use(lambda: random.choice(["pending", "processing", "completed"]))
```

---

## Trait 预设配置

Trait 允许定义一组相关的属性覆盖，通过布尔参数激活。

### 定义 Trait

```python
class OrderFactory(Factory):
    class Meta:
        model = dict

    status = "pending"
    paid_at = None
    shipped_at = None
    completed_at = None

    class Params:
        """预设配置"""

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
```

### 使用 Trait

```python
# 激活单个 Trait
paid_order = OrderFactory.build(paid=True)
# {'status': 'paid', 'paid_at': datetime(...), ...}

shipped_order = OrderFactory.build(shipped=True)
# {'status': 'shipped', 'paid_at': ..., 'shipped_at': ..., ...}

# 激活多个 Trait（后面的覆盖前面的）
# 注意：通常不建议同时激活冲突的 Trait

# Trait + 额外覆盖（覆盖优先级更高）
order = OrderFactory.build(paid=True, payment_method="alipay")
```

---

## 预置工厂

框架提供了 8 个开箱即用的工厂：

| 工厂 | 用途 | Traits |
|------|------|--------|
| `UserFactory` | 用户数据 | `admin`, `vip`, `inactive` |
| `ProductFactory` | 商品数据 | `out_of_stock`, `off_sale` |
| `OrderFactory` | 订单数据 | `paid`, `shipped`, `completed`, `cancelled` |
| `AddressFactory` | 地址数据 | `default` |
| `PaymentFactory` | 支付数据 | `success`, `failed`, `refunded` |
| `CardFactory` | 卡券数据 | `active`, `used`, `expired` |
| `ApiResponseFactory` | API 响应 | `error`, `not_found` |
| `PaginationFactory` | 分页数据 | - |

### 使用示例

```python
from df_test_framework.testing.data.factories import (
    UserFactory,
    OrderFactory,
    ProductFactory,
    PaymentFactory,
)

# 用户
user = UserFactory.build()
admin = UserFactory.build(admin=True)
vip_users = UserFactory.build_batch(10, vip=True)

# 订单
order = OrderFactory.build()
paid_order = OrderFactory.build(paid=True)
completed_orders = OrderFactory.build_batch(5, completed=True)

# 商品
product = ProductFactory.build()
sold_out = ProductFactory.build(out_of_stock=True)

# 支付
payment = PaymentFactory.build(success=True)
failed_payment = PaymentFactory.build(failed=True)
```

---

## 最佳实践

### 1. 为项目创建专用 Factory

```python
# tests/factories.py
from df_test_framework.testing.data.factories import (
    Factory,
    Sequence,
    LazyAttribute,
    SubFactory,
    Trait,
    Use,
)
from myapp.models import User, Order

class MyUserFactory(Factory):
    """项目专用用户工厂"""

    class Meta:
        model = User  # 使用项目的 Pydantic/ORM 模型

    id = Sequence()
    username = Sequence(lambda n: f"testuser_{n}")
    email = LazyAttribute(lambda obj: f"{obj['username']}@mycompany.com")
    department = "engineering"

    class Params:
        manager = Trait(
            role="manager",
            department="management",
        )
```

### 2. 测试中使用 Factory

```python
import pytest
from tests.factories import MyUserFactory, MyOrderFactory

class TestOrderAPI:

    def test_create_order(self, http_client):
        # Arrange
        user = MyUserFactory.build()
        order_data = MyOrderFactory.build_dict(
            user_id=user["id"],
            status="pending",
        )

        # Act
        response = http_client.post("/orders", json=order_data)

        # Assert
        assert response.status_code == 201
        assert response.json()["status"] == "pending"

    def test_list_paid_orders(self, http_client):
        # 批量创建测试数据
        orders = MyOrderFactory.build_batch(10, paid=True)

        # 测试分页
        response = http_client.get("/orders?status=paid&page=1&size=5")

        assert response.status_code == 200
        assert len(response.json()["items"]) == 5
```

### 3. 使用 Fixture 集成

```python
# conftest.py
import pytest
from tests.factories import MyUserFactory

@pytest.fixture
def test_user():
    """创建测试用户"""
    return MyUserFactory.build()

@pytest.fixture
def admin_user():
    """创建管理员用户"""
    return MyUserFactory.build(admin=True)

@pytest.fixture(autouse=True)
def reset_sequences():
    """每个测试前重置序列"""
    yield
    Sequence.reset()
```

### 4. 避免测试间干扰

```python
import pytest
from df_test_framework.testing.data.factories import Sequence

@pytest.fixture(autouse=True, scope="function")
def reset_factory_sequences():
    """每个测试函数后重置序列计数器"""
    yield
    Sequence.reset()
```

---

## 从旧版迁移

如果你使用的是 v3.29.0 之前的 Factory：

```python
# 旧路径（已废弃，v4.0.0 移除）
from df_test_framework.testing.factories import UserFactory

# 新路径（推荐）
from df_test_framework.testing.data.factories import UserFactory
```

### API 变更

```python
# v3.29.0 (旧)
factory = UserFactory()
user = factory.create()
users = factory.create_batch(10)

# v3.31.0+ (新) - 类方法，无需实例化
user = UserFactory.build()
users = UserFactory.build_batch(10)
```

---

## API 参考

### Factory 类方法

| 方法 | 说明 |
|------|------|
| `build(**overrides)` | 构建单个对象 |
| `build_batch(size, **overrides)` | 批量构建对象 |
| `build_dict(**overrides)` | 构建字典（即使 Meta.model 是其他类型） |
| `reset_sequences()` | 重置所有序列计数器 |

### 字段类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `Sequence(func)` | 自增序列 | `Sequence(lambda n: f"user_{n}")` |
| `LazyAttribute(func)` | 延迟计算 | `LazyAttribute(lambda obj: obj['name'])` |
| `PostGenerated(func)` | 后处理 | `PostGenerated(lambda name, obj: sum(...))` |
| `SubFactory(factory)` | 嵌套工厂 | `SubFactory(AddressFactory)` |
| `FakerAttribute(provider)` | Faker 数据 | `FakerAttribute("email")` |
| `Use(func)` | 延迟执行 | `Use(datetime.now)` |
| `Trait(**overrides)` | 预设配置 | `Trait(status="active")` |

---

## 相关文档

- [测试数据生成指南](test_data.md) - DataGenerator 使用
- [Mock 指南](mocking.md) - 测试替身
- [断言指南](assertions_guide.md) - 断言增强
