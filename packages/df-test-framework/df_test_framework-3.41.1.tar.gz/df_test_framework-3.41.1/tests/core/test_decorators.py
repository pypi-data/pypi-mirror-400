"""测试 core.decorators - 装饰器工具

测试覆盖:
- retry_on_failure: 失败重试装饰器
- log_execution: 执行日志装饰器
- deprecated: 废弃标记装饰器
- cache_result: 结果缓存装饰器
"""

import time

import pytest

from df_test_framework.core.decorators import (
    cache_result,
    deprecated,
    log_execution,
    retry_on_failure,
)


class TestRetryOnFailure:
    """测试失败重试装饰器"""

    def test_success_no_retry(self):
        """测试成功时不重试"""
        call_count = 0

        @retry_on_failure(max_retries=3, delay=0.01)
        def success_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = success_func()
        assert result == "success"
        assert call_count == 1

    def test_retry_then_success(self):
        """测试重试后成功"""
        call_count = 0

        @retry_on_failure(max_retries=3, delay=0.01)
        def fail_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("模拟失败")
            return "success"

        result = fail_twice()
        assert result == "success"
        assert call_count == 3

    def test_max_retries_exceeded(self):
        """测试超过最大重试次数"""
        call_count = 0

        @retry_on_failure(max_retries=2, delay=0.01)
        def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("总是失败")

        with pytest.raises(ValueError, match="总是失败"):
            always_fail()

        assert call_count == 3  # 初始调用 + 2次重试

    def test_specific_exception(self):
        """测试只重试特定异常"""
        call_count = 0

        @retry_on_failure(max_retries=3, delay=0.01, exceptions=(ValueError,))
        def raise_type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("类型错误")

        with pytest.raises(TypeError):
            raise_type_error()

        # TypeError 不在重试列表中，应该只调用一次
        assert call_count == 1

    def test_backoff_delay(self):
        """测试指数退避延迟"""
        call_count = 0
        timestamps = []

        @retry_on_failure(max_retries=2, delay=0.05, backoff=2.0)
        def fail_with_timing():
            nonlocal call_count
            call_count += 1
            timestamps.append(time.time())
            if call_count <= 2:
                raise ValueError("失败")
            return "success"

        result = fail_with_timing()
        assert result == "success"
        assert call_count == 3

        # 验证延迟时间（大约）
        delay1 = timestamps[1] - timestamps[0]
        delay2 = timestamps[2] - timestamps[1]
        assert delay1 >= 0.04  # 约 0.05 秒
        assert delay2 >= 0.08  # 约 0.10 秒（0.05 * 2）


class TestLogExecution:
    """测试执行日志装饰器"""

    def test_log_execution_success(self, caplog):
        """测试成功执行时的日志"""

        @log_execution(log_args=True, log_result=True)
        def add(a, b):
            return a + b

        with caplog.at_level("DEBUG"):
            result = add(1, 2)

        assert result == 3

    def test_log_execution_without_args(self, caplog):
        """测试不记录参数"""

        @log_execution(log_args=False, log_result=False)
        def simple_func():
            return "done"

        result = simple_func()
        assert result == "done"

    def test_log_execution_with_exception(self):
        """测试异常时的日志"""

        @log_execution()
        def raise_error():
            raise ValueError("测试错误")

        with pytest.raises(ValueError):
            raise_error()

    def test_preserves_function_name(self):
        """测试保留函数名"""

        @log_execution()
        def my_function():
            pass

        assert my_function.__name__ == "my_function"


class TestDeprecated:
    """测试废弃标记装饰器"""

    def test_deprecated_basic(self, caplog):
        """测试基本废弃警告"""

        @deprecated()
        def old_function():
            return "result"

        with caplog.at_level("WARNING"):
            result = old_function()

        assert result == "result"

    def test_deprecated_with_message(self, caplog):
        """测试带消息的废弃警告"""

        @deprecated(message="请使用 new_function")
        def old_function():
            return "result"

        with caplog.at_level("WARNING"):
            result = old_function()

        assert result == "result"

    def test_deprecated_with_version(self, caplog):
        """测试带版本的废弃警告"""

        @deprecated(version="2.0.0")
        def old_function():
            return "result"

        with caplog.at_level("WARNING"):
            result = old_function()

        assert result == "result"

    def test_deprecated_full_info(self, caplog):
        """测试完整废弃信息"""

        @deprecated(message="请使用 new_function", version="2.0.0")
        def old_function():
            return "result"

        with caplog.at_level("WARNING"):
            result = old_function()

        assert result == "result"

    def test_preserves_function_name(self):
        """测试保留函数名"""

        @deprecated()
        def my_function():
            pass

        assert my_function.__name__ == "my_function"


class TestCacheResult:
    """测试结果缓存装饰器"""

    def test_cache_basic(self):
        """测试基本缓存功能"""
        call_count = 0

        @cache_result()
        def expensive_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # 第一次调用
        result1 = expensive_func(5)
        assert result1 == 10
        assert call_count == 1

        # 第二次调用（应该命中缓存）
        result2 = expensive_func(5)
        assert result2 == 10
        assert call_count == 1  # 没有增加

        # 不同参数（缓存未命中）
        result3 = expensive_func(10)
        assert result3 == 20
        assert call_count == 2

    def test_cache_with_kwargs(self):
        """测试带关键字参数的缓存"""
        call_count = 0

        @cache_result()
        def func_with_kwargs(a, b=1):
            nonlocal call_count
            call_count += 1
            return a + b

        result1 = func_with_kwargs(1, b=2)
        result2 = func_with_kwargs(1, b=2)

        assert result1 == 3
        assert result2 == 3
        assert call_count == 1

        # 不同的 kwargs
        result3 = func_with_kwargs(1, b=3)
        assert result3 == 4
        assert call_count == 2

    def test_cache_ttl(self):
        """测试缓存过期"""
        call_count = 0

        @cache_result(ttl=1.0)  # 1 秒过期（CI 环境需要更长时间避免偶发失败）
        def short_lived_cache(x):
            nonlocal call_count
            call_count += 1
            return x

        short_lived_cache(1)
        assert call_count == 1

        # 立即再次调用（应该命中缓存）
        short_lived_cache(1)
        assert call_count == 1

        # 等待过期
        time.sleep(1.1)

        # 缓存过期后再次调用
        short_lived_cache(1)
        assert call_count == 2

    def test_cache_maxsize(self):
        """测试缓存大小限制"""
        call_count = 0

        @cache_result(maxsize=3)
        def limited_cache(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # 填满缓存
        limited_cache(1)  # 缓存: {1}
        limited_cache(2)  # 缓存: {1, 2}
        limited_cache(3)  # 缓存: {1, 2, 3}
        assert call_count == 3

        # 添加第4个，应该淘汰最旧的
        limited_cache(4)  # 缓存: {2, 3, 4}
        assert call_count == 4

        # 访问被淘汰的 1（缓存未命中）
        limited_cache(1)
        assert call_count == 5

        # 访问还在缓存中的 3（缓存命中）
        limited_cache(3)
        assert call_count == 5

    def test_clear_cache(self):
        """测试清除缓存"""
        call_count = 0

        @cache_result()
        def cached_func(x):
            nonlocal call_count
            call_count += 1
            return x

        cached_func(1)
        cached_func(1)
        assert call_count == 1

        # 清除缓存
        cached_func.clear_cache()

        # 再次调用（缓存已清空）
        cached_func(1)
        assert call_count == 2

    def test_cache_info(self):
        """测试缓存信息"""

        @cache_result(ttl=60, maxsize=100)
        def func_with_info(x):
            return x

        func_with_info(1)
        func_with_info(2)

        info = func_with_info.cache_info()
        assert info["size"] == 2
        assert info["maxsize"] == 100
        assert info["ttl"] == 60
        assert len(info["keys"]) == 2

    def test_preserves_function_name(self):
        """测试保留函数名"""

        @cache_result()
        def my_cached_function():
            pass

        assert my_cached_function.__name__ == "my_cached_function"
