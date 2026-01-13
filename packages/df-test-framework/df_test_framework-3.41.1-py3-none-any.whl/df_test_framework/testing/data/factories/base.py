"""测试数据工厂基类

v3.29.0: 初始 Factory 模式实现
v3.31.0: 重构合并，融合 factory_boy 和 polyfactory 最佳实践

核心特性:
- 声明式定义数据结构（factory_boy 风格）
- 序列化字段 Sequence（自增 ID、序列值等）
- 延迟计算 LazyAttribute（依赖其他字段）
- 后处理字段 PostGenerated（基于已生成的全部字段）
- 预设配置 Trait（条件化设置多个属性）
- Faker/DataGenerator 集成（生成假数据）
- 泛型支持 Factory[T]（polyfactory 风格）
- Pydantic 模型原生支持

设计理念:
- DataGenerator: 生成原子字段值（字符串、数字、日期等）
- Factory: 组合字段值创建完整业务对象

使用示例:
    >>> from df_test_framework.testing.data.factories import Factory, Sequence, LazyAttribute
    >>>
    >>> class UserFactory(Factory):
    ...     class Meta:
    ...         model = dict
    ...
    ...     id = Sequence()
    ...     username = Sequence(lambda n: f"user_{n}")
    ...     email = LazyAttribute(lambda obj: f"{obj['username']}@example.com")
    ...     status = "active"
    >>>
    >>> # 构建单个用户
    >>> user = UserFactory.build()
    >>> # {'id': 1, 'username': 'user_1', 'email': 'user_1@example.com', 'status': 'active'}
    >>>
    >>> # 构建指定字段的用户
    >>> vip_user = UserFactory.build(status="vip", level=10)
    >>>
    >>> # 批量构建
    >>> users = UserFactory.build_batch(5)

参考:
- factory_boy: https://factoryboy.readthedocs.io/
- polyfactory: https://polyfactory.litestar.dev/
"""

from __future__ import annotations

from abc import ABC, ABCMeta
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, ClassVar, Generic, TypeVar

T = TypeVar("T")


# ============ 字段类型 ============


class Sequence:
    """序列生成器

    生成递增的序列值，支持自定义格式化函数。
    每个 Factory 类的每个 Sequence 字段有独立的计数器。

    Args:
        func: 格式化函数，接收序列号 n 作为参数，返回最终值。
              如果为 None，直接返回序列号。

    示例:
        >>> class UserFactory(Factory):
        ...     id = Sequence()  # 1, 2, 3, ...
        ...     username = Sequence(lambda n: f"user_{n}")  # user_1, user_2, ...
        ...     code = Sequence(lambda n: f"USR{n:06d}")  # USR000001, USR000002, ...
    """

    # 全局计数器存储
    _counters: ClassVar[dict[str, int]] = {}

    def __init__(self, func: Callable[[int], Any] | None = None):
        self.func = func or (lambda n: n)
        self._counter_name: str | None = None

    def _bind(self, factory_name: str, field_name: str) -> None:
        """绑定到具体的 Factory 和字段"""
        self._counter_name = f"{factory_name}.{field_name}"

    def next_value(self) -> Any:
        """获取下一个序列值"""
        counter_name = self._counter_name or "__default__"

        if counter_name not in self._counters:
            self._counters[counter_name] = 0

        self._counters[counter_name] += 1
        return self.func(self._counters[counter_name])

    @classmethod
    def reset(cls, name: str | None = None) -> None:
        """重置计数器

        Args:
            name: 计数器名称（None 表示重置所有）
        """
        if name is None:
            cls._counters.clear()
        elif name in cls._counters:
            cls._counters[name] = 0


class LazyAttribute:
    """延迟计算属性

    属性值在 build 时动态计算，可以访问其他已生成的字段。
    计算函数接收当前已构建的对象（字典）作为参数。

    Args:
        func: 计算函数，接收当前对象（dict）作为参数

    示例:
        >>> class UserFactory(Factory):
        ...     username = Sequence(lambda n: f"user_{n}")
        ...     email = LazyAttribute(lambda obj: f"{obj['username']}@example.com")
        ...     full_name = LazyAttribute(lambda obj: f"{obj.get('first_name', '')} {obj.get('last_name', '')}")
    """

    def __init__(self, func: Callable[[dict[str, Any]], Any]):
        self.func = func

    def evaluate(self, obj: dict[str, Any]) -> Any:
        """计算属性值"""
        return self.func(obj)


class PostGenerated:
    """后处理字段

    在所有其他字段生成完成后计算，可以访问完整的生成结果。
    与 LazyAttribute 的区别是：PostGenerated 在最后执行，确保能访问所有字段。

    Args:
        func: 计算函数，接收字段名和已生成的完整对象

    示例:
        >>> class OrderFactory(Factory):
        ...     items = LazyAttribute(lambda _: [{"price": 100}, {"price": 200}])
        ...     total = PostGenerated(lambda name, values: sum(i["price"] for i in values["items"]))
    """

    def __init__(self, func: Callable[[str, dict[str, Any]], Any]):
        self.func = func

    def evaluate(self, field_name: str, obj: dict[str, Any]) -> Any:
        """计算属性值"""
        return self.func(field_name, obj)


class SubFactory:
    """嵌套工厂

    使用另一个 Factory 生成嵌套对象。

    Args:
        factory: 嵌套的 Factory 类
        **defaults: 传递给嵌套 Factory 的默认参数

    示例:
        >>> class AddressFactory(Factory):
        ...     city = "北京"
        ...     street = Sequence(lambda n: f"街道{n}号")
        >>>
        >>> class UserFactory(Factory):
        ...     name = "张三"
        ...     address = SubFactory(AddressFactory)
        ...     work_address = SubFactory(AddressFactory, city="上海")
    """

    def __init__(self, factory: type[Factory], **defaults: Any):
        self.factory = factory
        self.defaults = defaults

    def build(self, **overrides: Any) -> Any:
        """构建嵌套对象"""
        params = {**self.defaults, **overrides}
        return self.factory.build(**params)


class FakerAttribute:
    """Faker 属性（生成假数据）

    使用 Faker 库生成假数据，需要安装 faker 包。

    Args:
        provider: Faker provider 名称（如 "name", "email", "phone_number"）
        *args: 传递给 provider 的位置参数
        **kwargs: 传递给 provider 的关键字参数

    示例:
        >>> class UserFactory(Factory):
        ...     name = FakerAttribute("name")
        ...     email = FakerAttribute("email")
        ...     phone = FakerAttribute("phone_number")
        ...     address = FakerAttribute("address")
    """

    _faker: ClassVar[Any] = None
    _faker_available: ClassVar[bool | None] = None

    def __init__(self, provider: str, *args: Any, **kwargs: Any):
        self.provider = provider
        self.args = args
        self.kwargs = kwargs

        # 延迟检查 faker 可用性
        if FakerAttribute._faker_available is None:
            try:
                from faker import Faker

                FakerAttribute._faker = Faker(locale="zh_CN")
                FakerAttribute._faker_available = True
            except ImportError:
                FakerAttribute._faker_available = False

    def generate(self) -> Any:
        """生成假数据"""
        if not FakerAttribute._faker_available:
            raise ImportError("faker 未安装，请执行: pip install faker 或 uv add faker")
        method = getattr(FakerAttribute._faker, self.provider)
        return method(*self.args, **self.kwargs)


class Use:
    """延迟执行的值包装器

    包装一个可调用对象，在 build 时执行。
    比 LazyAttribute 更简单，不需要访问其他字段时使用。

    Args:
        func: 无参数的可调用对象

    示例:
        >>> from datetime import datetime
        >>> class OrderFactory(Factory):
        ...     created_at = Use(datetime.now)
        ...     order_id = Use(lambda: str(uuid4()))
    """

    def __init__(self, func: Callable[[], Any]):
        self.func = func

    def evaluate(self) -> Any:
        """执行并返回值"""
        return self.func()


# ============ Trait 支持 ============


class Trait:
    """预设配置组合

    定义一组相关的属性覆盖，可以通过布尔参数激活。

    Args:
        **overrides: 激活时要设置的属性值

    示例:
        >>> class OrderFactory(Factory):
        ...     status = "pending"
        ...     paid_at = None
        ...     shipped_at = None
        ...
        ...     class Params:
        ...         shipped = Trait(
        ...             status="shipped",
        ...             shipped_at=Use(datetime.now),
        ...         )
        ...         paid = Trait(
        ...             status="paid",
        ...             paid_at=Use(datetime.now),
        ...         )
        >>>
        >>> # 激活 trait
        >>> order = OrderFactory.build(shipped=True)
        >>> # {'status': 'shipped', 'shipped_at': datetime(...), ...}
    """

    def __init__(self, **overrides: Any):
        self.overrides = overrides


# ============ Factory 配置 ============


@dataclass
class FactoryOptions:
    """Factory 配置选项"""

    model: type | None = None  # 目标模型类（dict、Pydantic、dataclass 等）
    abstract: bool = False  # 是否为抽象 Factory（不能直接实例化）


# ============ Factory 元类 ============


class FactoryMeta(ABCMeta):
    """Factory 元类

    负责处理类定义时的声明式属性，提取字段定义并绑定 Sequence。
    继承 ABCMeta 以支持 ABC 抽象基类。
    """

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
    ) -> type:
        # 提取 Meta 配置
        meta = namespace.get("Meta")
        if meta:
            options = FactoryOptions(
                model=getattr(meta, "model", None),
                abstract=getattr(meta, "abstract", False),
            )
        else:
            options = FactoryOptions()

        namespace["_options"] = options

        # 提取 Params（Trait 定义）
        params_class = namespace.get("Params")
        traits: dict[str, Trait] = {}
        if params_class:
            for attr_name in dir(params_class):
                if not attr_name.startswith("_"):
                    attr_value = getattr(params_class, attr_name)
                    if isinstance(attr_value, Trait):
                        traits[attr_name] = attr_value

        namespace["_traits"] = traits

        # 从父类继承字段
        inherited_fields: dict[str, Any] = {}
        for base in bases:
            if hasattr(base, "_fields"):
                inherited_fields.update(base._fields)

        # 提取当前类的字段定义
        fields: dict[str, Any] = dict(inherited_fields)
        for key, value in namespace.items():
            if key.startswith("_") or key in ("Meta", "Params"):
                continue
            # 跳过类方法、静态方法和普通方法
            if isinstance(value, (classmethod, staticmethod)):
                continue
            if callable(value) and not isinstance(
                value,
                (
                    Sequence,
                    LazyAttribute,
                    PostGenerated,
                    SubFactory,
                    FakerAttribute,
                    Use,
                ),
            ):
                # 跳过普通方法/函数
                continue
            fields[key] = value

        namespace["_fields"] = fields

        # 为 Sequence 绑定计数器名称
        for field_name, field_value in fields.items():
            if isinstance(field_value, Sequence):
                field_value._bind(name, field_name)

        return super().__new__(mcs, name, bases, namespace)


# ============ Factory 基类 ============


class Factory(ABC, Generic[T], metaclass=FactoryMeta):  # noqa: UP046
    """测试数据工厂基类

    使用声明式语法定义测试数据结构，支持多种字段类型。

    配置选项 (Meta 内部类):
        model: 目标模型类型（dict、Pydantic BaseModel、dataclass 等）
        abstract: 是否为抽象工厂

    字段类型:
        - 普通值: 直接赋值（如 status = "active"）
        - Sequence: 自增序列
        - LazyAttribute: 延迟计算（可访问其他字段）
        - PostGenerated: 后处理（在所有字段生成后执行）
        - SubFactory: 嵌套工厂
        - FakerAttribute: Faker 假数据
        - Use: 延迟执行的可调用对象

    示例:
        >>> class UserFactory(Factory):
        ...     class Meta:
        ...         model = dict  # 或 Pydantic 模型
        ...
        ...     id = Sequence()
        ...     username = Sequence(lambda n: f"user_{n}")
        ...     email = LazyAttribute(lambda obj: f"{obj['username']}@example.com")
        ...     name = FakerAttribute("name")
        ...     age = 25
        ...     is_active = True
        ...
        ...     class Params:
        ...         admin = Trait(role="admin", is_superuser=True)
        >>>
        >>> # 构建
        >>> user = UserFactory.build()
        >>> admin = UserFactory.build(admin=True)
        >>> users = UserFactory.build_batch(10)
    """

    _options: ClassVar[FactoryOptions]
    _fields: ClassVar[dict[str, Any]]
    _traits: ClassVar[dict[str, Trait]]

    class Meta:
        model = dict
        abstract = True

    @classmethod
    def build(cls, **overrides: Any) -> T:
        """构建单个对象

        生成测试数据对象，不进行持久化。

        Args:
            **overrides: 要覆盖的字段值，也可以传入 Trait 名称=True 来激活预设

        Returns:
            构建的对象（类型取决于 Meta.model）

        示例:
            >>> user = UserFactory.build()
            >>> vip = UserFactory.build(status="vip", level=10)
            >>> admin = UserFactory.build(admin=True)  # 激活 admin trait
        """
        obj: dict[str, Any] = {}
        post_generated_fields: list[tuple[str, PostGenerated]] = []

        # 1. 处理 Trait 激活
        trait_overrides: dict[str, Any] = {}
        non_trait_overrides: dict[str, Any] = {}

        for key, value in overrides.items():
            if key in cls._traits and value is True:
                # 激活 Trait
                trait_overrides.update(cls._traits[key].overrides)
            else:
                non_trait_overrides[key] = value

        # 合并覆盖（非 Trait 覆盖优先级更高）
        effective_overrides = {**trait_overrides, **non_trait_overrides}

        # 2. 处理普通字段和 Sequence
        for field_name, field_value in cls._fields.items():
            if field_name in effective_overrides:
                # 使用覆盖值
                value = effective_overrides[field_name]
                # 如果覆盖值本身是特殊类型，也需要处理
                if isinstance(value, Use):
                    obj[field_name] = value.evaluate()
                else:
                    obj[field_name] = value
            elif isinstance(field_value, Sequence):
                obj[field_name] = field_value.next_value()
            elif isinstance(field_value, FakerAttribute):
                obj[field_name] = field_value.generate()
            elif isinstance(field_value, Use):
                obj[field_name] = field_value.evaluate()
            elif isinstance(field_value, SubFactory):
                # 提取嵌套参数（field__subfield 格式）
                sub_overrides = {}
                prefix = f"{field_name}__"
                for k, v in effective_overrides.items():
                    if k.startswith(prefix):
                        sub_key = k[len(prefix) :]
                        sub_overrides[sub_key] = v
                obj[field_name] = field_value.build(**sub_overrides)
            elif isinstance(field_value, (LazyAttribute, PostGenerated)):
                # 延迟处理
                pass
            else:
                # 普通值
                obj[field_name] = field_value

        # 3. 处理 LazyAttribute（依赖其他字段）
        for field_name, field_value in cls._fields.items():
            if isinstance(field_value, LazyAttribute):
                if field_name in effective_overrides:
                    obj[field_name] = effective_overrides[field_name]
                else:
                    obj[field_name] = field_value.evaluate(obj)
            elif isinstance(field_value, PostGenerated):
                post_generated_fields.append((field_name, field_value))

        # 4. 处理 PostGenerated（最后执行）
        for field_name, field_value in post_generated_fields:
            if field_name in effective_overrides:
                obj[field_name] = effective_overrides[field_name]
            else:
                obj[field_name] = field_value.evaluate(field_name, obj)

        # 5. 添加覆盖中的额外字段
        for key, value in effective_overrides.items():
            if key not in obj and not key.startswith("__"):
                obj[key] = value

        # 6. 构建最终对象
        return cls._build_object(obj)

    @classmethod
    def _build_object(cls, data: dict[str, Any]) -> T:
        """根据 Meta.model 构建最终对象"""
        model = getattr(cls._options, "model", None) or dict

        # dict 类型直接返回
        if model is dict:
            return data  # type: ignore

        # Pydantic v2 模型
        if hasattr(model, "model_validate"):
            return model.model_validate(data)

        # Pydantic v1 模型
        if hasattr(model, "parse_obj"):
            return model.parse_obj(data)

        # dataclass 或其他类型
        return model(**data)

    @classmethod
    def build_batch(cls, size: int, **common_overrides: Any) -> list[T]:
        """批量构建对象

        Args:
            size: 要构建的数量
            **common_overrides: 应用到所有对象的覆盖值

        Returns:
            构建的对象列表

        示例:
            >>> users = UserFactory.build_batch(5)
            >>> vips = UserFactory.build_batch(3, status="vip")
        """
        return [cls.build(**common_overrides) for _ in range(size)]

    @classmethod
    def build_dict(cls, **overrides: Any) -> dict[str, Any]:
        """构建字典（确保返回 dict）

        当只需要字典数据而不需要模型实例时使用。

        Args:
            **overrides: 要覆盖的字段值

        Returns:
            字段数据字典
        """
        obj = cls.build(**overrides)

        if isinstance(obj, dict):
            return obj

        # Pydantic v2
        if hasattr(obj, "model_dump"):
            return obj.model_dump()

        # Pydantic v1
        if hasattr(obj, "dict"):
            return obj.dict()

        # dataclass 或普通对象
        if hasattr(obj, "__dict__"):
            return dict(obj.__dict__)

        return dict(obj)

    @classmethod
    def reset_sequences(cls) -> None:
        """重置所有序列计数器"""
        Sequence.reset()


class ModelFactory(Factory[T]):
    """带类型提示的工厂基类

    为 Pydantic 模型或 dataclass 提供更好的类型支持。

    示例:
        >>> from pydantic import BaseModel
        >>>
        >>> class User(BaseModel):
        ...     id: int
        ...     name: str
        ...     email: str
        >>>
        >>> class UserFactory(ModelFactory[User]):
        ...     class Meta:
        ...         model = User
        ...
        ...     id = Sequence()
        ...     name = FakerAttribute("name")
        ...     email = LazyAttribute(lambda obj: f"user_{obj['id']}@example.com")
        >>>
        >>> user: User = UserFactory.build()  # 类型提示正确
    """

    pass


# ============ 导出 ============

__all__ = [
    # 核心类
    "Factory",
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
]
