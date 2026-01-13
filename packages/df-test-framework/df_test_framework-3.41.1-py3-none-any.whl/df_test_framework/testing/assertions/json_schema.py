"""JSON Schema 验证器

v3.30.0: 独立的 JSON Schema 验证工具

提供 Schema 验证、文件加载、自定义验证规则等功能。

使用示例:
    >>> from df_test_framework.testing.assertions import SchemaValidator, assert_schema
    >>>
    >>> # 直接验证
    >>> schema = {"type": "object", "required": ["id", "name"]}
    >>> assert_schema(data, schema)
    >>>
    >>> # 使用 SchemaValidator 类
    >>> validator = SchemaValidator(schema)
    >>> validator.validate(data)
    >>>
    >>> # 从文件加载
    >>> validator = SchemaValidator.from_file("schemas/user.json")
    >>> validator.validate(user_data)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator, ValidationError


class SchemaValidationError(AssertionError):
    """Schema 验证错误

    包含详细的验证错误信息，便于调试。
    """

    def __init__(
        self,
        message: str,
        errors: list[ValidationError] | None = None,
        data: Any = None,
        schema: dict | None = None,
    ):
        super().__init__(message)
        self.errors = errors or []
        self.data = data
        self.schema = schema

    def __str__(self) -> str:
        lines = [super().__str__()]
        if self.errors:
            lines.append("\n详细错误:")
            for i, error in enumerate(self.errors[:5], 1):  # 最多显示 5 个
                path = ".".join(str(p) for p in error.path) or "(root)"
                lines.append(f"  {i}. 路径 '{path}': {error.message}")
            if len(self.errors) > 5:
                lines.append(f"  ... 还有 {len(self.errors) - 5} 个错误")
        return "\n".join(lines)


class SchemaValidator:
    """JSON Schema 验证器

    支持 Draft 7 JSON Schema 规范，提供丰富的验证功能。

    特性:
    - 支持从 dict 或文件加载 Schema
    - 收集所有验证错误（不是遇到第一个就停止）
    - 详细的错误信息输出
    - 支持引用($ref)解析

    使用示例:
        >>> schema = {
        ...     "type": "object",
        ...     "required": ["id", "name"],
        ...     "properties": {
        ...         "id": {"type": "integer", "minimum": 1},
        ...         "name": {"type": "string", "minLength": 1},
        ...         "email": {"type": "string", "format": "email"}
        ...     }
        ... }
        >>> validator = SchemaValidator(schema)
        >>> validator.validate({"id": 1, "name": "Alice"})
        True
        >>> validator.is_valid({"id": -1})  # 不抛异常
        False
    """

    def __init__(self, schema: dict[str, Any]):
        """初始化验证器

        Args:
            schema: JSON Schema 定义（dict）
        """
        self._schema = schema
        # 使用 Draft7Validator，检查 schema 本身是否有效
        Draft7Validator.check_schema(schema)
        self._validator = Draft7Validator(schema)

    @property
    def schema(self) -> dict[str, Any]:
        """获取 Schema 定义"""
        return self._schema

    def validate(self, data: Any) -> bool:
        """验证数据是否符合 Schema

        如果验证失败，抛出 SchemaValidationError。

        Args:
            data: 待验证的数据

        Returns:
            True（验证通过）

        Raises:
            SchemaValidationError: 验证失败时抛出
        """
        errors = list(self._validator.iter_errors(data))

        if errors:
            # 按路径排序，方便阅读
            errors.sort(key=lambda e: list(e.path))
            raise SchemaValidationError(
                message=f"Schema 验证失败，共 {len(errors)} 个错误",
                errors=errors,
                data=data,
                schema=self._schema,
            )

        return True

    def is_valid(self, data: Any) -> bool:
        """检查数据是否符合 Schema（不抛异常）

        Args:
            data: 待验证的数据

        Returns:
            True 如果验证通过，False 如果验证失败
        """
        return self._validator.is_valid(data)

    def get_errors(self, data: Any) -> list[dict[str, Any]]:
        """获取所有验证错误（不抛异常）

        Args:
            data: 待验证的数据

        Returns:
            错误列表，每个错误包含 path、message、value 等信息
        """
        errors = []
        for error in self._validator.iter_errors(data):
            errors.append(
                {
                    "path": list(error.path),
                    "message": error.message,
                    "value": error.instance,
                    "schema_path": list(error.schema_path),
                    "validator": error.validator,
                }
            )
        return errors

    @classmethod
    def from_file(cls, file_path: str | Path) -> SchemaValidator:
        """从文件加载 Schema

        支持 JSON 和 YAML 格式（根据扩展名自动识别）。

        Args:
            file_path: Schema 文件路径

        Returns:
            SchemaValidator 实例

        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON 解析失败
            ValueError: 不支持的文件格式
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Schema 文件不存在: {path}")

        suffix = path.suffix.lower()

        if suffix == ".json":
            with open(path, encoding="utf-8") as f:
                schema = json.load(f)
        elif suffix in (".yaml", ".yml"):
            try:
                import yaml
            except ImportError:
                raise ImportError("YAML 格式需要 pyyaml 库: pip install pyyaml")
            with open(path, encoding="utf-8") as f:
                schema = yaml.safe_load(f)
        else:
            raise ValueError(f"不支持的文件格式: {suffix}，支持 .json, .yaml, .yml")

        return cls(schema)

    @classmethod
    def from_string(cls, schema_str: str, format: str = "json") -> SchemaValidator:
        """从字符串加载 Schema

        Args:
            schema_str: Schema 字符串
            format: 格式，"json" 或 "yaml"

        Returns:
            SchemaValidator 实例
        """
        if format == "json":
            schema = json.loads(schema_str)
        elif format in ("yaml", "yml"):
            try:
                import yaml
            except ImportError:
                raise ImportError("YAML 格式需要 pyyaml 库: pip install pyyaml")
            schema = yaml.safe_load(schema_str)
        else:
            raise ValueError(f"不支持的格式: {format}")

        return cls(schema)


def assert_schema(data: Any, schema: dict[str, Any]) -> None:
    """快捷 Schema 验证函数

    Args:
        data: 待验证的数据
        schema: JSON Schema 定义

    Raises:
        SchemaValidationError: 验证失败时抛出

    示例:
        >>> schema = {"type": "object", "required": ["id"]}
        >>> assert_schema({"id": 1}, schema)  # 通过
        >>> assert_schema({}, schema)  # 抛出 SchemaValidationError
    """
    SchemaValidator(schema).validate(data)


def validate_response_schema(response: Any, schema: dict[str, Any]) -> None:
    """验证 HTTP 响应的 JSON 数据是否符合 Schema

    Args:
        response: HTTP 响应对象（需要有 json() 方法）
        schema: JSON Schema 定义

    Raises:
        SchemaValidationError: 验证失败时抛出
    """
    data = response.json()
    assert_schema(data, schema)


# 预定义的常用 Schema 片段
COMMON_SCHEMAS = {
    "id": {"type": "integer", "minimum": 1},
    "uuid": {
        "type": "string",
        "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    },
    "email": {"type": "string", "format": "email"},
    "datetime": {"type": "string", "format": "date-time"},
    "date": {"type": "string", "format": "date"},
    "url": {"type": "string", "format": "uri"},
    "phone_cn": {"type": "string", "pattern": "^1[3-9]\\d{9}$"},
    "non_empty_string": {"type": "string", "minLength": 1},
    "positive_number": {"type": "number", "exclusiveMinimum": 0},
    "non_negative_number": {"type": "number", "minimum": 0},
    "pagination": {
        "type": "object",
        "properties": {
            "page": {"type": "integer", "minimum": 1},
            "page_size": {"type": "integer", "minimum": 1, "maximum": 100},
            "total": {"type": "integer", "minimum": 0},
        },
        "required": ["page", "page_size", "total"],
    },
    "api_response": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "code": {"type": "string"},
            "message": {"type": "string"},
            "data": {},
        },
        "required": ["success", "code", "message"],
    },
}


def create_object_schema(
    properties: dict[str, dict],
    required: list[str] | None = None,
    additional_properties: bool = True,
) -> dict[str, Any]:
    """创建对象类型的 Schema

    Args:
        properties: 属性定义
        required: 必填字段列表
        additional_properties: 是否允许额外属性

    Returns:
        JSON Schema 定义

    示例:
        >>> schema = create_object_schema(
        ...     properties={
        ...         "id": COMMON_SCHEMAS["id"],
        ...         "name": {"type": "string"},
        ...         "email": COMMON_SCHEMAS["email"],
        ...     },
        ...     required=["id", "name"],
        ... )
    """
    schema: dict[str, Any] = {
        "type": "object",
        "properties": properties,
        "additionalProperties": additional_properties,
    }
    if required:
        schema["required"] = required
    return schema


def create_array_schema(
    items: dict[str, Any],
    min_items: int | None = None,
    max_items: int | None = None,
    unique_items: bool = False,
) -> dict[str, Any]:
    """创建数组类型的 Schema

    Args:
        items: 数组元素的 Schema
        min_items: 最小元素数量
        max_items: 最大元素数量
        unique_items: 元素是否必须唯一

    Returns:
        JSON Schema 定义

    示例:
        >>> schema = create_array_schema(
        ...     items={"type": "integer"},
        ...     min_items=1,
        ...     unique_items=True,
        ... )
    """
    schema: dict[str, Any] = {
        "type": "array",
        "items": items,
    }
    if min_items is not None:
        schema["minItems"] = min_items
    if max_items is not None:
        schema["maxItems"] = max_items
    if unique_items:
        schema["uniqueItems"] = True
    return schema


__all__ = [
    # 核心类
    "SchemaValidator",
    "SchemaValidationError",
    # 快捷函数
    "assert_schema",
    "validate_response_schema",
    # Schema 构建器
    "create_object_schema",
    "create_array_schema",
    # 预定义 Schema
    "COMMON_SCHEMAS",
]
