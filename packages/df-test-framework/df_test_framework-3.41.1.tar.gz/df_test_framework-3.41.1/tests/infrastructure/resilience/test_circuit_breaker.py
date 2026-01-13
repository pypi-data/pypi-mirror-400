"""测试 CircuitBreaker - 熔断器

测试覆盖:
- CircuitState 枚举
- CircuitBreaker 类（状态转换、阈值控制、超时恢复）
- CircuitOpenError 异常
- circuit_breaker 装饰器
"""

import time

import pytest

from df_test_framework.infrastructure.resilience import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
    circuit_breaker,
)


class TestCircuitState:
    """测试熔断器状态枚举"""

    def test_state_values(self):
        """测试状态枚举值"""
        assert CircuitState.CLOSED.value == "closed"
        assert CircuitState.OPEN.value == "open"
        assert CircuitState.HALF_OPEN.value == "half_open"


class TestCircuitBreakerInit:
    """测试熔断器初始化"""

    def test_default_values(self):
        """测试默认参数值"""
        breaker = CircuitBreaker()
        assert breaker.failure_threshold == 5
        assert breaker.success_threshold == 2
        assert breaker.timeout == 60
        assert breaker.exception_whitelist == ()

    def test_custom_values(self):
        """测试自定义参数值"""
        breaker = CircuitBreaker(
            failure_threshold=3,
            success_threshold=1,
            timeout=30,
            exception_whitelist=(ValueError,),
        )
        assert breaker.failure_threshold == 3
        assert breaker.success_threshold == 1
        assert breaker.timeout == 30
        assert breaker.exception_whitelist == (ValueError,)

    def test_initial_state(self):
        """测试初始状态"""
        breaker = CircuitBreaker()
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.success_count == 0
        assert breaker.last_failure_time is None

    def test_invalid_failure_threshold(self):
        """测试无效失败阈值"""
        with pytest.raises(ValueError, match="failure_threshold必须大于0"):
            CircuitBreaker(failure_threshold=0)

        with pytest.raises(ValueError, match="failure_threshold必须大于0"):
            CircuitBreaker(failure_threshold=-1)

    def test_invalid_success_threshold(self):
        """测试无效成功阈值"""
        with pytest.raises(ValueError, match="success_threshold必须大于0"):
            CircuitBreaker(success_threshold=0)

    def test_invalid_timeout(self):
        """测试无效超时时间"""
        with pytest.raises(ValueError, match="timeout必须大于0"):
            CircuitBreaker(timeout=0)


class TestCircuitBreakerStateProperties:
    """测试熔断器状态属性"""

    def test_is_closed(self):
        """测试 is_closed 属性"""
        breaker = CircuitBreaker()
        assert breaker.is_closed is True
        assert breaker.is_open is False
        assert breaker.is_half_open is False

    def test_is_open(self):
        """测试 is_open 属性"""
        breaker = CircuitBreaker(failure_threshold=1)
        # 触发一次失败来打开熔断器
        with pytest.raises(ValueError):
            breaker.call(lambda: (_ for _ in ()).throw(ValueError("test")))

        assert breaker.is_closed is False
        assert breaker.is_open is True
        assert breaker.is_half_open is False


class TestCircuitBreakerClosed:
    """测试 CLOSED 状态行为"""

    def test_success_in_closed_state(self):
        """测试关闭状态成功调用"""
        breaker = CircuitBreaker()

        result = breaker.call(lambda: "success")

        assert result == "success"
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_failure_count_increases(self):
        """测试失败计数增加"""
        breaker = CircuitBreaker(failure_threshold=3)

        for i in range(2):
            with pytest.raises(ValueError):
                breaker.call(lambda: (_ for _ in ()).throw(ValueError("test")))

        assert breaker.failure_count == 2
        assert breaker.state == CircuitState.CLOSED  # 还未达到阈值

    def test_failure_count_resets_on_success(self):
        """测试成功后失败计数重置"""
        breaker = CircuitBreaker(failure_threshold=3)

        # 失败两次
        for _ in range(2):
            with pytest.raises(ValueError):
                breaker.call(lambda: (_ for _ in ()).throw(ValueError("test")))

        assert breaker.failure_count == 2

        # 成功一次
        breaker.call(lambda: "success")

        assert breaker.failure_count == 0


class TestCircuitBreakerOpen:
    """测试 OPEN 状态行为"""

    def test_opens_after_threshold(self):
        """测试达到阈值后打开"""
        breaker = CircuitBreaker(failure_threshold=3)

        for _ in range(3):
            with pytest.raises(ValueError):
                breaker.call(lambda: (_ for _ in ()).throw(ValueError("test")))

        assert breaker.state == CircuitState.OPEN

    def test_rejects_calls_when_open(self):
        """测试打开状态拒绝调用"""
        breaker = CircuitBreaker(failure_threshold=1, timeout=60)

        # 触发熔断
        with pytest.raises(ValueError):
            breaker.call(lambda: (_ for _ in ()).throw(ValueError("test")))

        assert breaker.state == CircuitState.OPEN

        # 再次调用应该抛出 CircuitOpenError
        with pytest.raises(CircuitOpenError):
            breaker.call(lambda: "should not execute")


class TestCircuitBreakerHalfOpen:
    """测试 HALF_OPEN 状态行为"""

    def test_transitions_to_half_open_after_timeout(self):
        """测试超时后转为半开状态"""
        breaker = CircuitBreaker(failure_threshold=1, timeout=1)

        # 触发熔断
        with pytest.raises(ValueError):
            breaker.call(lambda: (_ for _ in ()).throw(ValueError("test")))

        assert breaker.state == CircuitState.OPEN

        # 等待超时
        time.sleep(1.1)

        # 再次调用应该转为 HALF_OPEN
        result = breaker.call(lambda: "success")

        assert result == "success"
        # 成功后应该开始计数恢复
        assert breaker.state in (CircuitState.HALF_OPEN, CircuitState.CLOSED)

    def test_half_open_success_closes_circuit(self):
        """测试半开状态成功后关闭熔断器"""
        breaker = CircuitBreaker(failure_threshold=1, success_threshold=2, timeout=1)

        # 触发熔断
        with pytest.raises(ValueError):
            breaker.call(lambda: (_ for _ in ()).throw(ValueError("test")))

        # 等待超时
        time.sleep(1.1)

        # 连续成功两次
        breaker.call(lambda: "success1")
        breaker.call(lambda: "success2")

        assert breaker.state == CircuitState.CLOSED

    def test_half_open_failure_reopens_circuit(self):
        """测试半开状态失败后重新打开熔断器"""
        breaker = CircuitBreaker(failure_threshold=1, timeout=1)

        # 触发熔断
        with pytest.raises(ValueError):
            breaker.call(lambda: (_ for _ in ()).throw(ValueError("test")))

        # 等待超时
        time.sleep(1.1)

        # 半开状态下失败
        with pytest.raises(ValueError):
            breaker.call(lambda: (_ for _ in ()).throw(ValueError("test again")))

        assert breaker.state == CircuitState.OPEN


class TestCircuitBreakerWhitelist:
    """测试异常白名单"""

    def test_whitelist_exception_not_counted(self):
        """测试白名单异常不计入失败"""
        breaker = CircuitBreaker(
            failure_threshold=2,
            exception_whitelist=(ValueError,),
        )

        # ValueError 在白名单中，不应计入失败
        for _ in range(5):
            with pytest.raises(ValueError):
                breaker.call(lambda: (_ for _ in ()).throw(ValueError("test")))

        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_non_whitelist_exception_counted(self):
        """测试非白名单异常计入失败"""
        breaker = CircuitBreaker(
            failure_threshold=2,
            exception_whitelist=(ValueError,),
        )

        # TypeError 不在白名单中，应计入失败
        for _ in range(2):
            with pytest.raises(TypeError):
                breaker.call(lambda: (_ for _ in ()).throw(TypeError("test")))

        assert breaker.state == CircuitState.OPEN


class TestCircuitBreakerReset:
    """测试手动重置"""

    def test_reset_clears_all_state(self):
        """测试重置清除所有状态"""
        breaker = CircuitBreaker(failure_threshold=1)

        # 触发熔断
        with pytest.raises(ValueError):
            breaker.call(lambda: (_ for _ in ()).throw(ValueError("test")))

        assert breaker.state == CircuitState.OPEN
        assert breaker.failure_count == 1
        assert breaker.last_failure_time is not None

        # 重置
        breaker.reset()

        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.success_count == 0
        assert breaker.last_failure_time is None


class TestCircuitBreakerDecorator:
    """测试熔断器装饰器"""

    def test_decorator_basic(self):
        """测试装饰器基本功能"""

        @circuit_breaker(failure_threshold=2)
        def protected_func():
            return "success"

        result = protected_func()
        assert result == "success"

    def test_decorator_opens_circuit(self):
        """测试装饰器触发熔断"""
        call_count = 0

        @circuit_breaker(failure_threshold=2, timeout=60)
        def failing_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("always fails")

        # 失败两次触发熔断
        for _ in range(2):
            with pytest.raises(ValueError):
                failing_func()

        # 第三次应该是 CircuitOpenError
        with pytest.raises(CircuitOpenError):
            failing_func()

        # 确保函数没有被调用（被熔断器拦截）
        assert call_count == 2

    def test_decorator_preserves_function_name(self):
        """测试装饰器保留函数名"""

        @circuit_breaker()
        def my_protected_function():
            pass

        assert my_protected_function.__name__ == "my_protected_function"

    def test_decorator_exposes_breaker(self):
        """测试装饰器暴露熔断器实例"""

        @circuit_breaker(failure_threshold=3)
        def func():
            return "success"

        assert hasattr(func, "breaker")
        assert isinstance(func.breaker, CircuitBreaker)
        assert func.breaker.failure_threshold == 3

    def test_decorator_with_whitelist(self):
        """测试装饰器白名单异常"""

        @circuit_breaker(failure_threshold=2, exception_whitelist=(ValueError,))
        def func_with_whitelist(should_fail: bool, error_type: str):
            if should_fail:
                if error_type == "value":
                    raise ValueError("value error")
                else:
                    raise TypeError("type error")
            return "success"

        # ValueError 在白名单中，不计入失败
        for _ in range(5):
            with pytest.raises(ValueError):
                func_with_whitelist(True, "value")

        assert func_with_whitelist.breaker.state == CircuitState.CLOSED

        # TypeError 不在白名单中
        for _ in range(2):
            with pytest.raises(TypeError):
                func_with_whitelist(True, "type")

        assert func_with_whitelist.breaker.state == CircuitState.OPEN


class TestCircuitBreakerWithArgs:
    """测试带参数的函数调用"""

    def test_call_with_args(self):
        """测试带位置参数调用"""
        breaker = CircuitBreaker()

        def add(a, b):
            return a + b

        result = breaker.call(add, 1, 2)
        assert result == 3

    def test_call_with_kwargs(self):
        """测试带关键字参数调用"""
        breaker = CircuitBreaker()

        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        result = breaker.call(greet, "World", greeting="Hi")
        assert result == "Hi, World!"

    def test_call_with_mixed_args(self):
        """测试混合参数调用"""
        breaker = CircuitBreaker()

        def complex_func(a, b, c=3, d=4):
            return a + b + c + d

        result = breaker.call(complex_func, 1, 2, d=10)
        assert result == 16  # 1 + 2 + 3 + 10
