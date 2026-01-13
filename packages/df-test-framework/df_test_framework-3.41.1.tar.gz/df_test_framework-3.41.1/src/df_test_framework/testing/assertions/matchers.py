"""自定义匹配器

v3.30.0: 提供灵活的值匹配能力

匹配器可以用于断言，支持与其他断言方法组合使用。

使用示例:
    >>> from df_test_framework.testing.assertions.matchers import (
    ...     matches_regex,
    ...     contains,
    ...     in_range,
    ...     any_of,
    ...     all_of,
    ... )
    >>>
    >>> # 正则匹配
    >>> assert matches_regex(r"^TEST_\\d+$").matches("TEST_123")
    >>>
    >>> # 范围匹配
    >>> assert in_range(1, 100).matches(50)
    >>>
    >>> # 组合匹配
    >>> matcher = all_of(
    ...     matches_regex(r"^[A-Z]+$"),
    ...     lambda x: len(x) >= 3,
    ... )
    >>> assert matcher.matches("ABC")
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import date, datetime
from decimal import Decimal
from typing import Any, TypeVar

T = TypeVar("T")


class BaseMatcher(ABC):
    """匹配器基类

    所有自定义匹配器都应继承此类，实现 matches 和 describe 方法。
    """

    @abstractmethod
    def matches(self, actual: Any) -> bool:
        """检查值是否匹配

        Args:
            actual: 实际值

        Returns:
            True 如果匹配，False 如果不匹配
        """
        pass

    @abstractmethod
    def describe(self) -> str:
        """描述匹配条件

        Returns:
            匹配条件的描述字符串
        """
        pass

    def assert_matches(self, actual: Any, message: str | None = None) -> None:
        """断言值匹配

        Args:
            actual: 实际值
            message: 自定义错误消息

        Raises:
            AssertionError: 不匹配时抛出
        """
        if not self.matches(actual):
            error_msg = message or f"期望 {self.describe()}，实际值: {actual!r}"
            raise AssertionError(error_msg)

    def __and__(self, other: BaseMatcher) -> AllOfMatcher:
        """组合匹配器（AND）"""
        return AllOfMatcher(self, other)

    def __or__(self, other: BaseMatcher) -> AnyOfMatcher:
        """组合匹配器（OR）"""
        return AnyOfMatcher(self, other)

    def __invert__(self) -> NotMatcher:
        """取反匹配器"""
        return NotMatcher(self)


class RegexMatcher(BaseMatcher):
    """正则表达式匹配器

    使用示例:
        >>> matcher = RegexMatcher(r"^TEST_\\d{3}$")
        >>> matcher.matches("TEST_123")  # True
        >>> matcher.matches("TEST_12")   # False
    """

    def __init__(self, pattern: str, flags: int = 0):
        """初始化正则匹配器

        Args:
            pattern: 正则表达式模式
            flags: 正则表达式标志（如 re.IGNORECASE）
        """
        self._pattern = pattern
        self._flags = flags
        self._compiled = re.compile(pattern, flags)

    def matches(self, actual: Any) -> bool:
        if actual is None:
            return False
        return bool(self._compiled.match(str(actual)))

    def describe(self) -> str:
        flags_str = ""
        if self._flags & re.IGNORECASE:
            flags_str = " (忽略大小写)"
        return f"匹配正则 '{self._pattern}'{flags_str}"


class ContainsMatcher(BaseMatcher):
    """包含匹配器

    支持字符串、列表、字典等容器类型。

    使用示例:
        >>> ContainsMatcher("hello").matches("hello world")  # True
        >>> ContainsMatcher(1).matches([1, 2, 3])  # True
        >>> ContainsMatcher("key").matches({"key": "value"})  # True
    """

    def __init__(self, value: Any):
        """初始化包含匹配器

        Args:
            value: 期望包含的值
        """
        self._value = value

    def matches(self, actual: Any) -> bool:
        if actual is None:
            return False
        try:
            return self._value in actual
        except TypeError:
            return False

    def describe(self) -> str:
        return f"包含 {self._value!r}"


class InRangeMatcher(BaseMatcher):
    """范围匹配器

    支持数值和日期类型。

    使用示例:
        >>> InRangeMatcher(1, 100).matches(50)  # True
        >>> InRangeMatcher(1, 100, inclusive=False).matches(100)  # False
    """

    def __init__(
        self,
        min_value: Any,
        max_value: Any,
        inclusive: bool = True,
    ):
        """初始化范围匹配器

        Args:
            min_value: 最小值
            max_value: 最大值
            inclusive: 是否包含边界值（默认 True）
        """
        self._min = min_value
        self._max = max_value
        self._inclusive = inclusive

    def matches(self, actual: Any) -> bool:
        if actual is None:
            return False
        try:
            if self._inclusive:
                return self._min <= actual <= self._max
            else:
                return self._min < actual < self._max
        except TypeError:
            return False

    def describe(self) -> str:
        if self._inclusive:
            return f"在范围 [{self._min}, {self._max}] 内"
        else:
            return f"在范围 ({self._min}, {self._max}) 内"


class EqualsMatcher(BaseMatcher):
    """相等匹配器

    使用示例:
        >>> EqualsMatcher(42).matches(42)  # True
        >>> EqualsMatcher("test").matches("test")  # True
    """

    def __init__(self, expected: Any):
        self._expected = expected

    def matches(self, actual: Any) -> bool:
        return actual == self._expected

    def describe(self) -> str:
        return f"等于 {self._expected!r}"


class TypeMatcher(BaseMatcher):
    """类型匹配器

    使用示例:
        >>> TypeMatcher(int).matches(42)  # True
        >>> TypeMatcher(str, int).matches(42)  # True（任一类型）
    """

    def __init__(self, *expected_types: type):
        self._expected_types = expected_types

    def matches(self, actual: Any) -> bool:
        return isinstance(actual, self._expected_types)

    def describe(self) -> str:
        type_names = [t.__name__ for t in self._expected_types]
        return f"类型为 {' 或 '.join(type_names)}"


class LengthMatcher(BaseMatcher):
    """长度匹配器

    使用示例:
        >>> LengthMatcher(3).matches("abc")  # True
        >>> LengthMatcher(min_len=1, max_len=5).matches([1, 2])  # True
    """

    def __init__(
        self,
        exact: int | None = None,
        min_len: int | None = None,
        max_len: int | None = None,
    ):
        self._exact = exact
        self._min = min_len
        self._max = max_len

    def matches(self, actual: Any) -> bool:
        try:
            length = len(actual)
        except TypeError:
            return False

        if self._exact is not None:
            return length == self._exact

        if self._min is not None and length < self._min:
            return False
        if self._max is not None and length > self._max:
            return False

        return True

    def describe(self) -> str:
        if self._exact is not None:
            return f"长度为 {self._exact}"

        parts = []
        if self._min is not None:
            parts.append(f">= {self._min}")
        if self._max is not None:
            parts.append(f"<= {self._max}")

        return f"长度 {' 且 '.join(parts)}"


class NotMatcher(BaseMatcher):
    """取反匹配器

    使用示例:
        >>> not_empty = NotMatcher(EqualsMatcher(""))
        >>> not_empty.matches("hello")  # True
        >>> not_empty.matches("")  # False
    """

    def __init__(self, matcher: BaseMatcher):
        self._matcher = matcher

    def matches(self, actual: Any) -> bool:
        return not self._matcher.matches(actual)

    def describe(self) -> str:
        return f"不{self._matcher.describe()}"


class AllOfMatcher(BaseMatcher):
    """组合匹配器（全部满足）

    使用示例:
        >>> matcher = AllOfMatcher(
        ...     TypeMatcher(str),
        ...     LengthMatcher(min_len=3),
        ... )
        >>> matcher.matches("hello")  # True
        >>> matcher.matches("hi")  # False
    """

    def __init__(self, *matchers: BaseMatcher):
        self._matchers = matchers

    def matches(self, actual: Any) -> bool:
        return all(m.matches(actual) for m in self._matchers)

    def describe(self) -> str:
        descriptions = [m.describe() for m in self._matchers]
        return " 且 ".join(descriptions)


class AnyOfMatcher(BaseMatcher):
    """组合匹配器（任一满足）

    使用示例:
        >>> matcher = AnyOfMatcher(
        ...     EqualsMatcher(None),
        ...     TypeMatcher(str),
        ... )
        >>> matcher.matches(None)  # True
        >>> matcher.matches("hello")  # True
        >>> matcher.matches(42)  # False
    """

    def __init__(self, *matchers: BaseMatcher):
        self._matchers = matchers

    def matches(self, actual: Any) -> bool:
        return any(m.matches(actual) for m in self._matchers)

    def describe(self) -> str:
        descriptions = [m.describe() for m in self._matchers]
        return " 或 ".join(descriptions)


class PredicateMatcher(BaseMatcher):
    """自定义谓词匹配器

    使用示例:
        >>> is_even = PredicateMatcher(lambda x: x % 2 == 0, "是偶数")
        >>> is_even.matches(4)  # True
    """

    def __init__(self, predicate: Callable[[Any], bool], description: str):
        self._predicate = predicate
        self._description = description

    def matches(self, actual: Any) -> bool:
        try:
            return bool(self._predicate(actual))
        except Exception:
            return False

    def describe(self) -> str:
        return self._description


class StartWithMatcher(BaseMatcher):
    """前缀匹配器"""

    def __init__(self, prefix: str, ignore_case: bool = False):
        self._prefix = prefix
        self._ignore_case = ignore_case

    def matches(self, actual: Any) -> bool:
        if not isinstance(actual, str):
            return False
        if self._ignore_case:
            return actual.lower().startswith(self._prefix.lower())
        return actual.startswith(self._prefix)

    def describe(self) -> str:
        case_str = " (忽略大小写)" if self._ignore_case else ""
        return f"以 '{self._prefix}' 开头{case_str}"


class EndWithMatcher(BaseMatcher):
    """后缀匹配器"""

    def __init__(self, suffix: str, ignore_case: bool = False):
        self._suffix = suffix
        self._ignore_case = ignore_case

    def matches(self, actual: Any) -> bool:
        if not isinstance(actual, str):
            return False
        if self._ignore_case:
            return actual.lower().endswith(self._suffix.lower())
        return actual.endswith(self._suffix)

    def describe(self) -> str:
        case_str = " (忽略大小写)" if self._ignore_case else ""
        return f"以 '{self._suffix}' 结尾{case_str}"


class GreaterThanMatcher(BaseMatcher):
    """大于匹配器"""

    def __init__(self, value: Any, or_equal: bool = False):
        self._value = value
        self._or_equal = or_equal

    def matches(self, actual: Any) -> bool:
        try:
            if self._or_equal:
                return actual >= self._value
            return actual > self._value
        except TypeError:
            return False

    def describe(self) -> str:
        op = ">=" if self._or_equal else ">"
        return f"{op} {self._value}"


class LessThanMatcher(BaseMatcher):
    """小于匹配器"""

    def __init__(self, value: Any, or_equal: bool = False):
        self._value = value
        self._or_equal = or_equal

    def matches(self, actual: Any) -> bool:
        try:
            if self._or_equal:
                return actual <= self._value
            return actual < self._value
        except TypeError:
            return False

    def describe(self) -> str:
        op = "<=" if self._or_equal else "<"
        return f"{op} {self._value}"


# ============ 快捷函数 ============


def matches_regex(pattern: str, flags: int = 0) -> RegexMatcher:
    """创建正则匹配器"""
    return RegexMatcher(pattern, flags)


def contains(value: Any) -> ContainsMatcher:
    """创建包含匹配器"""
    return ContainsMatcher(value)


def in_range(
    min_value: Any,
    max_value: Any,
    inclusive: bool = True,
) -> InRangeMatcher:
    """创建范围匹配器"""
    return InRangeMatcher(min_value, max_value, inclusive)


def equals(expected: Any) -> EqualsMatcher:
    """创建相等匹配器"""
    return EqualsMatcher(expected)


def is_type(*types: type) -> TypeMatcher:
    """创建类型匹配器"""
    return TypeMatcher(*types)


def has_length(
    exact: int | None = None,
    min_len: int | None = None,
    max_len: int | None = None,
) -> LengthMatcher:
    """创建长度匹配器"""
    return LengthMatcher(exact, min_len, max_len)


def all_of(*matchers: BaseMatcher) -> AllOfMatcher:
    """创建组合匹配器（全部满足）"""
    return AllOfMatcher(*matchers)


def any_of(*matchers: BaseMatcher) -> AnyOfMatcher:
    """创建组合匹配器（任一满足）"""
    return AnyOfMatcher(*matchers)


def not_matcher(matcher: BaseMatcher) -> NotMatcher:
    """创建取反匹配器"""
    return NotMatcher(matcher)


def predicate(func: Callable[[Any], bool], description: str) -> PredicateMatcher:
    """创建自定义谓词匹配器"""
    return PredicateMatcher(func, description)


def starts_with(prefix: str, ignore_case: bool = False) -> StartWithMatcher:
    """创建前缀匹配器"""
    return StartWithMatcher(prefix, ignore_case)


def ends_with(suffix: str, ignore_case: bool = False) -> EndWithMatcher:
    """创建后缀匹配器"""
    return EndWithMatcher(suffix, ignore_case)


def greater_than(value: Any, or_equal: bool = False) -> GreaterThanMatcher:
    """创建大于匹配器"""
    return GreaterThanMatcher(value, or_equal)


def less_than(value: Any, or_equal: bool = False) -> LessThanMatcher:
    """创建小于匹配器"""
    return LessThanMatcher(value, or_equal)


# ============ 预定义匹配器 ============


# 常用匹配器实例
is_none = EqualsMatcher(None)
is_not_none = NotMatcher(is_none)
is_true = EqualsMatcher(True)
is_false = EqualsMatcher(False)
is_empty = LengthMatcher(exact=0)
is_not_empty = NotMatcher(is_empty)

# 类型匹配器
is_string = TypeMatcher(str)
is_int = TypeMatcher(int)
is_float = TypeMatcher(float)
is_number = TypeMatcher(int, float, Decimal)
is_bool = TypeMatcher(bool)
is_list = TypeMatcher(list)
is_dict = TypeMatcher(dict)
is_date = TypeMatcher(date, datetime)


__all__ = [
    # 基类
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
    # 快捷函数
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
    # 预定义实例
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
