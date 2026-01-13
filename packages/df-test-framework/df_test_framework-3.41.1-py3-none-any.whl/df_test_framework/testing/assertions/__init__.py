"""测试断言辅助

提供丰富的断言辅助方法，简化测试代码

模块:
- response: HTTP响应断言
- helper: 通用断言助手
- json_schema: JSON Schema 验证器 (v3.30.0)
- matchers: 自定义匹配器 (v3.30.0)

使用示例:
    >>> from df_test_framework.testing.assertions import (
    ...     ResponseAssertions,
    ...     assert_status,
    ...     assert_json_has,
    ...     AssertHelper,
    ...     SchemaValidator,
    ...     matches_regex,
    ...     in_range,
    ... )
    >>>
    >>> # 静态方法
    >>> assert_status(response, 200)
    >>> assert_json_has(response, "user_id", "name")
    >>>
    >>> # 链式调用
    >>> ResponseAssertions(response).status(200).json_has("id")
    >>>
    >>> # 通用断言 (v3.29.0)
    >>> AssertHelper.assert_field_equals(data, "name", "Alice")
    >>>
    >>> # Schema 验证 (v3.30.0)
    >>> validator = SchemaValidator({"type": "object", "required": ["id"]})
    >>> validator.validate(data)
    >>>
    >>> # 匹配器 (v3.30.0)
    >>> assert matches_regex(r"^TEST_\\d+$").matches("TEST_123")

v3.10.0 新增 - P2.2 测试数据工具增强
v3.29.0 新增 - AssertHelper (从 utils/ 迁移)
v3.30.0 新增 - SchemaValidator、自定义匹配器
"""

from .helper import AssertHelper
from .json_schema import (
    COMMON_SCHEMAS,
    SchemaValidationError,
    SchemaValidator,
    assert_schema,
    create_array_schema,
    create_object_schema,
    validate_response_schema,
)
from .matchers import (
    AllOfMatcher,
    AnyOfMatcher,
    BaseMatcher,
    ContainsMatcher,
    EndWithMatcher,
    EqualsMatcher,
    GreaterThanMatcher,
    InRangeMatcher,
    LengthMatcher,
    LessThanMatcher,
    NotMatcher,
    PredicateMatcher,
    RegexMatcher,
    StartWithMatcher,
    TypeMatcher,
    all_of,
    any_of,
    contains,
    ends_with,
    equals,
    greater_than,
    has_length,
    in_range,
    is_bool,
    is_date,
    is_dict,
    is_empty,
    is_false,
    is_float,
    is_int,
    is_list,
    is_none,
    is_not_empty,
    is_not_none,
    is_number,
    is_string,
    is_true,
    is_type,
    less_than,
    matches_regex,
    not_matcher,
    predicate,
    starts_with,
)
from .response import (
    ResponseAssertions,
    assert_content_type,
    assert_header_has,
    assert_json_equals,
    assert_json_has,
    assert_json_path_equals,
    assert_json_schema,
    assert_response_time_lt,
    assert_status,
    assert_success,
)

__all__ = [
    # 响应断言类
    "ResponseAssertions",
    # 通用断言助手 (v3.29.0)
    "AssertHelper",
    # 便捷函数
    "assert_status",
    "assert_success",
    "assert_json_has",
    "assert_json_equals",
    "assert_json_schema",
    "assert_json_path_equals",
    "assert_response_time_lt",
    "assert_header_has",
    "assert_content_type",
    # JSON Schema 验证 (v3.30.0)
    "SchemaValidator",
    "SchemaValidationError",
    "assert_schema",
    "validate_response_schema",
    "create_object_schema",
    "create_array_schema",
    "COMMON_SCHEMAS",
    # 匹配器基类 (v3.30.0)
    "BaseMatcher",
    # 匹配器类
    "RegexMatcher",
    "ContainsMatcher",
    "InRangeMatcher",
    "EqualsMatcher",
    "TypeMatcher",
    "LengthMatcher",
    "NotMatcher",
    "AllOfMatcher",
    "AnyOfMatcher",
    "PredicateMatcher",
    "StartWithMatcher",
    "EndWithMatcher",
    "GreaterThanMatcher",
    "LessThanMatcher",
    # 匹配器快捷函数
    "matches_regex",
    "contains",
    "in_range",
    "equals",
    "is_type",
    "has_length",
    "all_of",
    "any_of",
    "not_matcher",
    "predicate",
    "starts_with",
    "ends_with",
    "greater_than",
    "less_than",
    # 预定义匹配器实例
    "is_none",
    "is_not_none",
    "is_true",
    "is_false",
    "is_empty",
    "is_not_empty",
    "is_string",
    "is_int",
    "is_float",
    "is_number",
    "is_bool",
    "is_list",
    "is_dict",
    "is_date",
]
