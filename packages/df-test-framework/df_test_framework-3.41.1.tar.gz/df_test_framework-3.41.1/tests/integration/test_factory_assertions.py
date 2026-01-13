"""Factory + 断言系统集成测试

测试 Factory 生成的数据与断言系统的协同工作。
"""

from decimal import Decimal

from df_test_framework.testing.assertions import (
    COMMON_SCHEMAS,
    SchemaValidator,
    all_of,
    assert_schema,
    contains,
    create_array_schema,
    create_object_schema,
    in_range,
    is_dict,
    is_int,
    is_list,
    is_not_none,
    is_string,
    matches_regex,
)
from df_test_framework.testing.data.factories import (
    ApiResponseFactory,
    Factory,
    OrderFactory,
    PaginationFactory,
    ProductFactory,
    Sequence,
    SubFactory,
    Trait,
    UserFactory,
)


class TestFactoryWithSchemaValidation:
    """Factory 数据与 Schema 验证集成测试"""

    def test_user_factory_passes_schema(self):
        """用户工厂生成的数据应符合 Schema"""
        # Schema 匹配 UserFactory 实际生成的所有字段
        user_schema = create_object_schema(
            properties={
                "id": {"type": "integer", "minimum": 1},
                "user_id": COMMON_SCHEMAS["uuid"],
                "username": {"type": "string", "minLength": 1},
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "name": {"type": "string"},
                "password": {"type": "string"},
                "avatar": {"type": "string"},
                "gender": {"type": "string", "enum": ["male", "female", "unknown"]},
                "age": {"type": "integer", "minimum": 18, "maximum": 60},
                "status": {"type": "string", "enum": ["active", "inactive", "banned"]},
                "role": {"type": "string", "enum": ["user", "admin", "vip"]},
                "is_verified": {"type": "boolean"},
                "is_superuser": {"type": "boolean"},
            },
            required=["id", "username", "email", "status"],
        )

        validator = SchemaValidator(user_schema)

        # 普通用户
        user = UserFactory.build()
        assert validator.is_valid(user), f"Schema 验证失败: {validator.validate(user)}"

        # VIP 用户
        vip = UserFactory.build(vip=True)
        assert validator.is_valid(vip), f"VIP Schema 验证失败: {validator.validate(vip)}"

        # 管理员
        admin = UserFactory.build(admin=True)
        assert validator.is_valid(admin), f"Admin Schema 验证失败: {validator.validate(admin)}"

    def test_order_factory_passes_schema(self):
        """订单工厂生成的数据应符合 Schema"""
        order_schema = create_object_schema(
            properties={
                "id": {"type": "integer", "minimum": 1},
                "order_no": {"type": "string", "pattern": "^ORD-\\d{8}-\\d{6}$"},
                "user_id": COMMON_SCHEMAS["uuid"],
                "status": {
                    "type": "string",
                    "enum": ["pending", "paid", "shipped", "completed", "cancelled"],
                },
                "total_amount": {"type": "number", "minimum": 0},
                "payment_amount": {"type": "number", "minimum": 0},
                "shipping_address": {"type": "object"},
            },
            required=["id", "order_no", "status"],
        )

        validator = SchemaValidator(order_schema)

        # 各状态订单
        for trait in [None, "paid", "shipped", "completed", "cancelled"]:
            if trait:
                order = OrderFactory.build(**{trait: True})
            else:
                order = OrderFactory.build()
            assert validator.is_valid(order), f"订单状态 {trait or 'pending'} 验证失败"

    def test_batch_factory_with_array_schema(self):
        """批量生成数据与数组 Schema 验证"""
        user_schema = create_object_schema(
            properties={
                "id": {"type": "integer"},
                "username": {"type": "string"},
            },
            required=["id", "username"],
        )

        users_schema = create_array_schema(
            items=user_schema,
            min_items=5,
            max_items=10,
        )

        validator = SchemaValidator(users_schema)

        users = UserFactory.build_batch(7)
        assert validator.is_valid(users)

        # 边界测试
        users_min = UserFactory.build_batch(5)
        assert validator.is_valid(users_min)

        users_max = UserFactory.build_batch(10)
        assert validator.is_valid(users_max)


class TestFactoryWithMatchers:
    """Factory 数据与匹配器集成测试"""

    def test_user_fields_with_matchers(self):
        """用户字段应匹配预期模式"""
        user = UserFactory.build()

        # ID 验证
        assert is_int.matches(user["id"])
        assert in_range(1, 1000000).matches(user["id"])

        # 用户名验证
        assert is_string.matches(user["username"])
        assert matches_regex(r"^user_\d+$").matches(user["username"])

        # 邮箱验证
        assert is_string.matches(user["email"])
        assert contains("@").matches(user["email"])

        # UUID 验证
        uuid_matcher = matches_regex(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        )
        assert uuid_matcher.matches(user["user_id"])

    def test_order_amounts_with_matchers(self):
        """订单金额应在合理范围"""
        order = OrderFactory.build()

        # 金额应为正数
        positive_amount = in_range(Decimal("0"), Decimal("100000"))
        assert positive_amount.matches(order["total_amount"])
        assert positive_amount.matches(order["payment_amount"])

        # 实付金额应 <= 总金额
        assert order["payment_amount"] <= order["total_amount"]

    def test_product_with_composite_matchers(self):
        """商品数据与组合匹配器"""
        product = ProductFactory.build()

        # SKU 格式验证
        sku_matcher = all_of(
            is_string,
            matches_regex(r"^SKU-\d{8}$"),
        )
        assert sku_matcher.matches(product["sku"])

        # 价格验证（正数或 None）
        price_matcher = all_of(
            is_not_none,
            in_range(Decimal("0"), Decimal("100000")),
        )
        assert price_matcher.matches(product["price"])

        # 图片列表验证
        assert is_list.matches(product["images"])
        assert len(product["images"]) >= 1


class TestFactoryWithApiResponse:
    """API 响应工厂与断言集成"""

    def test_success_response_schema(self):
        """成功响应应符合标准格式"""
        schema = create_object_schema(
            properties={
                "code": {"type": "integer", "const": 0},
                "message": {"type": "string", "const": "success"},
                "data": {},
                "timestamp": {"type": "integer"},
                "request_id": COMMON_SCHEMAS["uuid"],
            },
            required=["code", "message", "timestamp", "request_id"],
        )

        response = ApiResponseFactory.build()
        assert_schema(response, schema)

    def test_error_response_schema(self):
        """错误响应应包含错误码"""
        response = ApiResponseFactory.build(error=True)

        assert response["code"] != 0
        assert response["message"] != "success"
        assert is_int.matches(response["code"])

    def test_pagination_factory(self):
        """分页数据验证"""
        page = PaginationFactory.build(total=100, page=2, page_size=10)

        # 分页计算验证
        assert page["total"] == 100
        assert page["page"] == 2
        assert page["page_size"] == 10
        assert page["total_pages"] == 10
        assert page["has_prev"] is True
        assert page["has_next"] is True

        # 边界情况
        first_page = PaginationFactory.build(total=100, page=1, page_size=10)
        assert first_page["has_prev"] is False
        assert first_page["has_next"] is True

        last_page = PaginationFactory.build(total=100, page=10, page_size=10)
        assert last_page["has_prev"] is True
        assert last_page["has_next"] is False


class TestCustomFactoryWithAssertions:
    """自定义 Factory 与断言集成"""

    def test_custom_factory_with_trait(self):
        """自定义工厂 Trait 与断言"""

        class TaskFactory(Factory):
            class Meta:
                model = dict

            id = Sequence()
            title = Sequence(lambda n: f"任务 {n}")
            status = "pending"
            priority = "medium"
            assignee = None

            class Params:
                urgent = Trait(
                    priority="high",
                    status="in_progress",
                )
                completed = Trait(
                    status="completed",
                )

        # 普通任务
        task = TaskFactory.build()
        assert task["status"] == "pending"
        assert task["priority"] == "medium"

        # 紧急任务
        urgent_task = TaskFactory.build(urgent=True)
        assert urgent_task["priority"] == "high"
        assert urgent_task["status"] == "in_progress"

        # Schema 验证
        task_schema = create_object_schema(
            properties={
                "id": {"type": "integer"},
                "title": {"type": "string"},
                "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
            },
            required=["id", "title", "status", "priority"],
        )

        validator = SchemaValidator(task_schema)
        assert validator.is_valid(task)
        assert validator.is_valid(urgent_task)

    def test_nested_factory_with_schema(self):
        """嵌套工厂与 Schema 验证"""

        class DepartmentFactory(Factory):
            class Meta:
                model = dict

            id = Sequence()
            name = Sequence(lambda n: f"部门 {n}")

        class EmployeeFactory(Factory):
            class Meta:
                model = dict

            id = Sequence()
            name = Sequence(lambda n: f"员工 {n}")
            department = SubFactory(DepartmentFactory)

        employee = EmployeeFactory.build()

        # 嵌套结构验证
        assert is_dict.matches(employee["department"])
        assert "id" in employee["department"]
        assert "name" in employee["department"]

        # Schema 验证
        employee_schema = create_object_schema(
            properties={
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "department": create_object_schema(
                    properties={
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                    },
                    required=["id", "name"],
                ),
            },
            required=["id", "name", "department"],
        )

        assert_schema(employee, employee_schema)
