"""自定义匹配器测试

v3.30.0: Matchers 测试

测试覆盖:
- 基础匹配器（Regex, Contains, InRange, Equals, Type, Length）
- 组合匹配器（AllOf, AnyOf, Not）
- 快捷函数
- 预定义实例
- 操作符重载
"""

from datetime import date, datetime
from decimal import Decimal

import pytest

from df_test_framework.testing.assertions import (
    AllOfMatcher,
    AnyOfMatcher,
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

# ============================================================
# RegexMatcher 测试
# ============================================================


class TestRegexMatcher:
    """测试正则匹配器"""

    def test_basic_regex(self):
        """基本正则匹配"""
        matcher = RegexMatcher(r"^TEST_\d+$")
        assert matcher.matches("TEST_123")
        assert matcher.matches("TEST_0")
        assert not matcher.matches("test_123")  # 大小写敏感
        assert not matcher.matches("TEST_ABC")

    def test_regex_with_ignore_case(self):
        """忽略大小写"""
        import re

        matcher = RegexMatcher(r"^test$", flags=re.IGNORECASE)
        assert matcher.matches("test")
        assert matcher.matches("TEST")
        assert matcher.matches("TeSt")

    def test_regex_none_value(self):
        """None 值应该返回 False"""
        matcher = RegexMatcher(r".*")
        assert not matcher.matches(None)

    def test_regex_describe(self):
        """描述应该包含模式"""
        matcher = RegexMatcher(r"^\d+$")
        assert r"^\d+$" in matcher.describe()

    def test_matches_regex_function(self):
        """测试快捷函数"""
        assert matches_regex(r"^[A-Z]+$").matches("ABC")
        assert not matches_regex(r"^[A-Z]+$").matches("abc")


# ============================================================
# ContainsMatcher 测试
# ============================================================


class TestContainsMatcher:
    """测试包含匹配器"""

    def test_string_contains(self):
        """字符串包含"""
        matcher = ContainsMatcher("world")
        assert matcher.matches("hello world")
        assert not matcher.matches("hello")

    def test_list_contains(self):
        """列表包含"""
        matcher = ContainsMatcher(2)
        assert matcher.matches([1, 2, 3])
        assert not matcher.matches([1, 3, 5])

    def test_dict_contains_key(self):
        """字典包含键"""
        matcher = ContainsMatcher("key")
        assert matcher.matches({"key": "value"})
        assert not matcher.matches({"other": "value"})

    def test_contains_none(self):
        """None 值应该返回 False"""
        matcher = ContainsMatcher("x")
        assert not matcher.matches(None)

    def test_contains_function(self):
        """测试快捷函数"""
        assert contains("@").matches("test@example.com")


# ============================================================
# InRangeMatcher 测试
# ============================================================


class TestInRangeMatcher:
    """测试范围匹配器"""

    def test_inclusive_range(self):
        """包含边界的范围"""
        matcher = InRangeMatcher(1, 10)
        assert matcher.matches(1)  # 边界
        assert matcher.matches(5)  # 中间
        assert matcher.matches(10)  # 边界
        assert not matcher.matches(0)
        assert not matcher.matches(11)

    def test_exclusive_range(self):
        """不包含边界的范围"""
        matcher = InRangeMatcher(1, 10, inclusive=False)
        assert not matcher.matches(1)  # 边界外
        assert matcher.matches(5)
        assert not matcher.matches(10)  # 边界外

    def test_float_range(self):
        """浮点数范围"""
        matcher = InRangeMatcher(0.0, 1.0)
        assert matcher.matches(0.5)
        assert matcher.matches(0.0)
        assert not matcher.matches(1.1)

    def test_date_range(self):
        """日期范围"""
        start = date(2025, 1, 1)
        end = date(2025, 12, 31)
        matcher = InRangeMatcher(start, end)
        assert matcher.matches(date(2025, 6, 15))
        assert not matcher.matches(date(2024, 12, 31))

    def test_range_none(self):
        """None 值应该返回 False"""
        matcher = InRangeMatcher(0, 10)
        assert not matcher.matches(None)

    def test_in_range_function(self):
        """测试快捷函数"""
        assert in_range(1, 100).matches(50)
        assert in_range(1, 100, inclusive=False).matches(50)


# ============================================================
# EqualsMatcher 测试
# ============================================================


class TestEqualsMatcher:
    """测试相等匹配器"""

    def test_equals_int(self):
        """整数相等"""
        matcher = EqualsMatcher(42)
        assert matcher.matches(42)
        assert not matcher.matches(43)

    def test_equals_string(self):
        """字符串相等"""
        matcher = EqualsMatcher("test")
        assert matcher.matches("test")
        assert not matcher.matches("TEST")

    def test_equals_none(self):
        """None 相等"""
        matcher = EqualsMatcher(None)
        assert matcher.matches(None)
        assert not matcher.matches("")

    def test_equals_function(self):
        """测试快捷函数"""
        assert equals(True).matches(True)
        assert not equals(True).matches(False)


# ============================================================
# TypeMatcher 测试
# ============================================================


class TestTypeMatcher:
    """测试类型匹配器"""

    def test_single_type(self):
        """单一类型匹配"""
        matcher = TypeMatcher(int)
        assert matcher.matches(42)
        assert not matcher.matches("42")

    def test_multiple_types(self):
        """多类型匹配（任一）"""
        matcher = TypeMatcher(int, str)
        assert matcher.matches(42)
        assert matcher.matches("hello")
        assert not matcher.matches([])

    def test_is_type_function(self):
        """测试快捷函数"""
        assert is_type(dict).matches({})
        assert is_type(list, tuple).matches([1, 2])
        assert is_type(list, tuple).matches((1, 2))


# ============================================================
# LengthMatcher 测试
# ============================================================


class TestLengthMatcher:
    """测试长度匹配器"""

    def test_exact_length(self):
        """精确长度"""
        matcher = LengthMatcher(exact=3)
        assert matcher.matches("abc")
        assert matcher.matches([1, 2, 3])
        assert not matcher.matches("ab")

    def test_min_length(self):
        """最小长度"""
        matcher = LengthMatcher(min_len=2)
        assert matcher.matches("ab")
        assert matcher.matches("abc")
        assert not matcher.matches("a")

    def test_max_length(self):
        """最大长度"""
        matcher = LengthMatcher(max_len=3)
        assert matcher.matches("abc")
        assert matcher.matches("ab")
        assert not matcher.matches("abcd")

    def test_range_length(self):
        """范围长度"""
        matcher = LengthMatcher(min_len=2, max_len=4)
        assert matcher.matches("ab")
        assert matcher.matches("abcd")
        assert not matcher.matches("a")
        assert not matcher.matches("abcde")

    def test_has_length_function(self):
        """测试快捷函数"""
        assert has_length(exact=5).matches("hello")
        assert has_length(min_len=1).matches("x")


# ============================================================
# NotMatcher 测试
# ============================================================


class TestNotMatcher:
    """测试取反匹配器"""

    def test_not_equals(self):
        """取反相等"""
        matcher = NotMatcher(EqualsMatcher(""))
        assert matcher.matches("hello")
        assert not matcher.matches("")

    def test_not_contains(self):
        """取反包含"""
        matcher = NotMatcher(ContainsMatcher("error"))
        assert matcher.matches("success")
        assert not matcher.matches("error occurred")

    def test_not_matcher_function(self):
        """测试快捷函数"""
        assert not_matcher(equals(None)).matches("value")


# ============================================================
# AllOfMatcher 测试
# ============================================================


class TestAllOfMatcher:
    """测试组合匹配器（全部满足）"""

    def test_all_pass(self):
        """全部通过"""
        matcher = AllOfMatcher(
            TypeMatcher(str),
            LengthMatcher(min_len=3),
        )
        assert matcher.matches("hello")
        assert not matcher.matches("hi")  # 长度不够
        assert not matcher.matches(123)  # 类型不对

    def test_all_of_function(self):
        """测试快捷函数"""
        matcher = all_of(
            matches_regex(r"^[A-Z]"),
            has_length(min_len=3),
        )
        assert matcher.matches("Hello")
        assert not matcher.matches("hello")  # 不是大写开头


# ============================================================
# AnyOfMatcher 测试
# ============================================================


class TestAnyOfMatcher:
    """测试组合匹配器（任一满足）"""

    def test_any_pass(self):
        """任一通过"""
        matcher = AnyOfMatcher(
            EqualsMatcher(None),
            TypeMatcher(str),
        )
        assert matcher.matches(None)
        assert matcher.matches("hello")
        assert not matcher.matches(123)

    def test_any_of_function(self):
        """测试快捷函数"""
        matcher = any_of(equals(0), equals(1))
        assert matcher.matches(0)
        assert matcher.matches(1)
        assert not matcher.matches(2)


# ============================================================
# PredicateMatcher 测试
# ============================================================


class TestPredicateMatcher:
    """测试自定义谓词匹配器"""

    def test_custom_predicate(self):
        """自定义谓词"""
        is_even = PredicateMatcher(lambda x: x % 2 == 0, "是偶数")
        assert is_even.matches(4)
        assert not is_even.matches(3)

    def test_predicate_with_exception(self):
        """谓词抛异常时返回 False"""

        def bad_predicate(x):
            raise ValueError("oops")

        matcher = PredicateMatcher(bad_predicate, "always fails")
        assert not matcher.matches("anything")

    def test_predicate_function(self):
        """测试快捷函数"""
        is_positive = predicate(lambda x: x > 0, "是正数")
        assert is_positive.matches(1)
        assert not is_positive.matches(-1)


# ============================================================
# StartWithMatcher / EndWithMatcher 测试
# ============================================================


class TestStartEndWithMatcher:
    """测试前后缀匹配器"""

    def test_starts_with(self):
        """前缀匹配"""
        matcher = StartWithMatcher("TEST_")
        assert matcher.matches("TEST_123")
        assert not matcher.matches("test_123")

    def test_starts_with_ignore_case(self):
        """前缀匹配忽略大小写"""
        matcher = StartWithMatcher("TEST_", ignore_case=True)
        assert matcher.matches("TEST_123")
        assert matcher.matches("test_123")

    def test_ends_with(self):
        """后缀匹配"""
        matcher = EndWithMatcher(".json")
        assert matcher.matches("config.json")
        assert not matcher.matches("config.yaml")

    def test_starts_ends_functions(self):
        """测试快捷函数"""
        assert starts_with("http").matches("https://example.com")
        assert ends_with(".py").matches("test.py")


# ============================================================
# GreaterThan / LessThan 测试
# ============================================================


class TestComparisonMatchers:
    """测试比较匹配器"""

    def test_greater_than(self):
        """大于"""
        matcher = GreaterThanMatcher(10)
        assert matcher.matches(11)
        assert not matcher.matches(10)
        assert not matcher.matches(9)

    def test_greater_than_or_equal(self):
        """大于等于"""
        matcher = GreaterThanMatcher(10, or_equal=True)
        assert matcher.matches(11)
        assert matcher.matches(10)
        assert not matcher.matches(9)

    def test_less_than(self):
        """小于"""
        matcher = LessThanMatcher(10)
        assert matcher.matches(9)
        assert not matcher.matches(10)
        assert not matcher.matches(11)

    def test_less_than_or_equal(self):
        """小于等于"""
        matcher = LessThanMatcher(10, or_equal=True)
        assert matcher.matches(9)
        assert matcher.matches(10)
        assert not matcher.matches(11)

    def test_comparison_functions(self):
        """测试快捷函数"""
        assert greater_than(0).matches(1)
        assert less_than(100).matches(50)


# ============================================================
# 操作符重载测试
# ============================================================


class TestOperatorOverloading:
    """测试操作符重载"""

    def test_and_operator(self):
        """& 操作符组合"""
        matcher = is_string & has_length(min_len=3)
        assert matcher.matches("hello")
        assert not matcher.matches("hi")

    def test_or_operator(self):
        """| 操作符组合"""
        matcher = is_none | is_string
        assert matcher.matches(None)
        assert matcher.matches("hello")
        assert not matcher.matches(123)

    def test_invert_operator(self):
        """~ 取反操作符"""
        matcher = ~is_none
        assert matcher.matches("value")
        assert not matcher.matches(None)

    def test_complex_combination(self):
        """复杂组合"""
        # (是字符串 且 长度 >= 3) 或 是 None
        matcher = (is_string & has_length(min_len=3)) | is_none
        assert matcher.matches("hello")
        assert matcher.matches(None)
        assert not matcher.matches("hi")
        assert not matcher.matches(123)


# ============================================================
# 预定义匹配器测试
# ============================================================


class TestPredefinedMatchers:
    """测试预定义匹配器实例"""

    def test_is_none_not_none(self):
        """None 匹配器"""
        assert is_none.matches(None)
        assert not is_none.matches("")
        assert is_not_none.matches("")
        assert not is_not_none.matches(None)

    def test_is_true_false(self):
        """布尔匹配器"""
        assert is_true.matches(True)
        assert not is_true.matches(False)
        assert is_false.matches(False)
        assert not is_false.matches(True)

    def test_is_empty_not_empty(self):
        """空值匹配器"""
        assert is_empty.matches("")
        assert is_empty.matches([])
        assert is_empty.matches({})
        assert is_not_empty.matches("hello")
        assert is_not_empty.matches([1])

    def test_type_matchers(self):
        """类型匹配器"""
        assert is_string.matches("hello")
        assert is_int.matches(42)
        assert is_float.matches(3.14)
        assert is_number.matches(42)
        assert is_number.matches(3.14)
        assert is_number.matches(Decimal("1.5"))
        assert is_bool.matches(True)
        assert is_list.matches([1, 2, 3])
        assert is_dict.matches({"key": "value"})
        assert is_date.matches(date.today())
        assert is_date.matches(datetime.now())


# ============================================================
# assert_matches 方法测试
# ============================================================


class TestAssertMatches:
    """测试 assert_matches 方法"""

    def test_assert_matches_pass(self):
        """断言通过"""
        matcher = is_string
        matcher.assert_matches("hello")  # 不应抛异常

    def test_assert_matches_fail(self):
        """断言失败"""
        matcher = is_string
        with pytest.raises(AssertionError):
            matcher.assert_matches(123)

    def test_assert_matches_custom_message(self):
        """自定义错误消息"""
        matcher = is_string
        with pytest.raises(AssertionError, match="必须是字符串"):
            matcher.assert_matches(123, message="必须是字符串")


__all__ = [
    "TestRegexMatcher",
    "TestContainsMatcher",
    "TestInRangeMatcher",
    "TestEqualsMatcher",
    "TestTypeMatcher",
    "TestLengthMatcher",
    "TestNotMatcher",
    "TestAllOfMatcher",
    "TestAnyOfMatcher",
    "TestPredicateMatcher",
    "TestStartEndWithMatcher",
    "TestComparisonMatchers",
    "TestOperatorOverloading",
    "TestPredefinedMatchers",
    "TestAssertMatches",
]
