"""JSON Schema 验证器测试

v3.30.0: SchemaValidator 测试

测试覆盖:
- SchemaValidator 基本验证
- 错误收集和报告
- 文件加载
- Schema 构建器
- 预定义 Schema
"""

import json
import tempfile
from pathlib import Path

import pytest

from df_test_framework.testing.assertions import (
    COMMON_SCHEMAS,
    SchemaValidationError,
    SchemaValidator,
    assert_schema,
    create_array_schema,
    create_object_schema,
)

# ============================================================
# SchemaValidator 基本功能测试
# ============================================================


class TestSchemaValidator:
    """测试 SchemaValidator 基本功能"""

    def test_validate_valid_data(self):
        """验证有效数据应该通过"""
        schema = {
            "type": "object",
            "required": ["id", "name"],
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
            },
        }
        validator = SchemaValidator(schema)

        # 应该返回 True
        result = validator.validate({"id": 1, "name": "test"})
        assert result is True

    def test_validate_invalid_data_raises_error(self):
        """验证无效数据应该抛出错误"""
        schema = {
            "type": "object",
            "required": ["id"],
            "properties": {
                "id": {"type": "integer"},
            },
        }
        validator = SchemaValidator(schema)

        with pytest.raises(SchemaValidationError) as exc_info:
            validator.validate({})  # 缺少必填字段

        assert "Schema 验证失败" in str(exc_info.value)
        assert len(exc_info.value.errors) > 0

    def test_validate_type_mismatch(self):
        """验证类型不匹配"""
        schema = {"type": "string"}
        validator = SchemaValidator(schema)

        with pytest.raises(SchemaValidationError):
            validator.validate(123)  # 不是字符串

    def test_is_valid_returns_bool(self):
        """is_valid 方法应该返回布尔值，不抛异常"""
        schema = {"type": "integer"}
        validator = SchemaValidator(schema)

        assert validator.is_valid(42) is True
        assert validator.is_valid("not an int") is False

    def test_get_errors_returns_list(self):
        """get_errors 方法应该返回错误列表"""
        schema = {
            "type": "object",
            "required": ["a", "b"],
        }
        validator = SchemaValidator(schema)

        errors = validator.get_errors({})  # 缺少 a 和 b
        assert len(errors) == 2
        assert all("message" in e for e in errors)

    def test_schema_property(self):
        """schema 属性应该返回原始 schema"""
        schema = {"type": "string"}
        validator = SchemaValidator(schema)
        assert validator.schema == schema


# ============================================================
# 文件加载测试
# ============================================================


class TestSchemaValidatorFileLoading:
    """测试从文件加载 Schema"""

    def test_from_json_file(self):
        """从 JSON 文件加载"""
        schema = {"type": "integer", "minimum": 0}

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(schema, f)
            temp_path = f.name

        try:
            validator = SchemaValidator.from_file(temp_path)
            assert validator.is_valid(10)
            assert not validator.is_valid(-1)
        finally:
            Path(temp_path).unlink()

    def test_from_yaml_file(self):
        """从 YAML 文件加载"""
        yaml_content = """
type: object
required:
  - name
properties:
  name:
    type: string
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            validator = SchemaValidator.from_file(temp_path)
            assert validator.is_valid({"name": "test"})
            assert not validator.is_valid({})
        finally:
            Path(temp_path).unlink()

    def test_from_file_not_found(self):
        """文件不存在应该抛出 FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            SchemaValidator.from_file("nonexistent.json")

    def test_from_file_unsupported_format(self):
        """不支持的格式应该抛出 ValueError"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="不支持的文件格式"):
                SchemaValidator.from_file(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_from_string_json(self):
        """从 JSON 字符串加载"""
        schema_str = '{"type": "boolean"}'
        validator = SchemaValidator.from_string(schema_str, format="json")

        assert validator.is_valid(True)
        assert not validator.is_valid("true")

    def test_from_string_yaml(self):
        """从 YAML 字符串加载"""
        schema_str = "type: number"
        validator = SchemaValidator.from_string(schema_str, format="yaml")

        assert validator.is_valid(3.14)
        assert not validator.is_valid("3.14")


# ============================================================
# assert_schema 快捷函数测试
# ============================================================


class TestAssertSchema:
    """测试 assert_schema 快捷函数"""

    def test_assert_schema_pass(self):
        """验证通过时不抛异常"""
        schema = {"type": "string", "minLength": 1}
        assert_schema("hello", schema)  # 不应抛异常

    def test_assert_schema_fail(self):
        """验证失败时抛出 SchemaValidationError"""
        schema = {"type": "string", "minLength": 5}
        with pytest.raises(SchemaValidationError):
            assert_schema("hi", schema)


# ============================================================
# Schema 构建器测试
# ============================================================


class TestSchemaBuilders:
    """测试 Schema 构建器函数"""

    def test_create_object_schema(self):
        """测试创建对象 Schema"""
        schema = create_object_schema(
            properties={
                "id": {"type": "integer"},
                "name": {"type": "string"},
            },
            required=["id"],
        )

        validator = SchemaValidator(schema)
        assert validator.is_valid({"id": 1})
        assert validator.is_valid({"id": 1, "name": "test"})
        assert not validator.is_valid({})  # 缺少 id

    def test_create_object_schema_no_additional(self):
        """测试禁止额外属性"""
        schema = create_object_schema(
            properties={"id": {"type": "integer"}},
            additional_properties=False,
        )

        validator = SchemaValidator(schema)
        assert validator.is_valid({"id": 1})
        assert not validator.is_valid({"id": 1, "extra": "field"})

    def test_create_array_schema(self):
        """测试创建数组 Schema"""
        schema = create_array_schema(
            items={"type": "integer"},
            min_items=1,
        )

        validator = SchemaValidator(schema)
        assert validator.is_valid([1, 2, 3])
        assert not validator.is_valid([])  # 至少 1 个元素

    def test_create_array_schema_unique(self):
        """测试唯一元素约束"""
        schema = create_array_schema(
            items={"type": "string"},
            unique_items=True,
        )

        validator = SchemaValidator(schema)
        assert validator.is_valid(["a", "b", "c"])
        assert not validator.is_valid(["a", "a"])  # 有重复


# ============================================================
# 预定义 Schema 测试
# ============================================================


class TestCommonSchemas:
    """测试预定义 Schema"""

    def test_id_schema(self):
        """测试 ID Schema"""
        validator = SchemaValidator(COMMON_SCHEMAS["id"])
        assert validator.is_valid(1)
        assert validator.is_valid(100)
        assert not validator.is_valid(0)  # 最小值 1
        assert not validator.is_valid("1")  # 必须是整数

    def test_uuid_schema(self):
        """测试 UUID Schema"""
        validator = SchemaValidator(COMMON_SCHEMAS["uuid"])
        assert validator.is_valid("550e8400-e29b-41d4-a716-446655440000")
        assert not validator.is_valid("not-a-uuid")

    def test_email_schema(self):
        """测试 Email Schema"""
        validator = SchemaValidator(COMMON_SCHEMAS["email"])
        assert validator.is_valid("test@example.com")

    def test_phone_cn_schema(self):
        """测试中国手机号 Schema"""
        validator = SchemaValidator(COMMON_SCHEMAS["phone_cn"])
        assert validator.is_valid("13812345678")
        assert not validator.is_valid("12345678901")  # 不以 1 开头的 3-9
        assert not validator.is_valid("1381234567")  # 位数不对

    def test_pagination_schema(self):
        """测试分页 Schema"""
        validator = SchemaValidator(COMMON_SCHEMAS["pagination"])
        assert validator.is_valid({"page": 1, "page_size": 10, "total": 100})
        assert not validator.is_valid({"page": 1})  # 缺少字段

    def test_api_response_schema(self):
        """测试 API 响应 Schema"""
        validator = SchemaValidator(COMMON_SCHEMAS["api_response"])
        assert validator.is_valid(
            {
                "success": True,
                "code": "200",
                "message": "OK",
                "data": {"id": 1},
            }
        )
        assert not validator.is_valid({"success": True})  # 缺少字段


# ============================================================
# 错误信息测试
# ============================================================


class TestSchemaValidationError:
    """测试 SchemaValidationError 错误信息"""

    def test_error_message_contains_count(self):
        """错误消息应包含错误数量"""
        schema = {
            "type": "object",
            "required": ["a", "b", "c"],
        }
        validator = SchemaValidator(schema)

        try:
            validator.validate({})
        except SchemaValidationError as e:
            assert "3 个错误" in str(e)

    def test_error_contains_path(self):
        """错误消息应包含错误路径"""
        schema = {
            "type": "object",
            "properties": {
                "nested": {
                    "type": "object",
                    "required": ["value"],
                },
            },
        }
        validator = SchemaValidator(schema)

        try:
            validator.validate({"nested": {}})
        except SchemaValidationError as e:
            error_str = str(e)
            assert "nested" in error_str

    def test_error_data_preserved(self):
        """错误应保留原始数据"""
        schema = {"type": "string"}
        validator = SchemaValidator(schema)

        try:
            validator.validate(123)
        except SchemaValidationError as e:
            assert e.data == 123
            assert e.schema == schema


__all__ = [
    "TestSchemaValidator",
    "TestSchemaValidatorFileLoading",
    "TestAssertSchema",
    "TestSchemaBuilders",
    "TestCommonSchemas",
    "TestSchemaValidationError",
]
