"""轻量级性能监控工具

提供简单的性能计时和统计功能，无需 Prometheus 依赖。
适用于测试调试和简单性能分析场景。

核心组件:
- track_performance: 性能跟踪装饰器
- PerformanceTimer: 性能计时器上下文管理器
- PerformanceCollector: 性能数据收集器

与 Prometheus 指标的区别:
- 本模块：轻量级、日志输出、无外部依赖
- Prometheus 指标：生产级、可导出、需要 Prometheus 服务

v3.29.0 从 utils.performance 迁移
"""

from __future__ import annotations

import time
from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any, TypeVar

from df_test_framework.infrastructure.logging import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    pass

try:
    import allure

    ALLURE_AVAILABLE = True
except ImportError:
    ALLURE_AVAILABLE = False

F = TypeVar("F", bound=Callable[..., Any])


def track_performance(threshold_ms: float = 1000, log_result: bool = True) -> Callable[[F], F]:
    """性能跟踪装饰器

    自动记录函数执行时间，并在超过阈值时发出警告。

    Args:
        threshold_ms: 性能阈值（毫秒），超过此值将记录警告
        log_result: 是否记录执行结果

    Returns:
        装饰器函数

    Example:
        >>> @track_performance(threshold_ms=500)
        ... def test_api_response():
        ...     response = api.get("/users")
        ...     assert response.status_code == 200

        >>> @track_performance(threshold_ms=100, log_result=False)
        ... def quick_operation():
        ...     return sum(range(1000))
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            func_name = func.__name__
            start_time = time.perf_counter()

            try:
                # 执行函数
                result = func(*args, **kwargs)

                # 计算执行时间
                duration_ms = (time.perf_counter() - start_time) * 1000

                # 记录性能日志
                if log_result:
                    logger.info(f"[性能] {func_name} 执行时间: {duration_ms:.2f}ms")

                # Allure 报告附件
                if ALLURE_AVAILABLE:
                    allure.attach(
                        f"{duration_ms:.2f}ms",
                        name=f"{func_name}_执行时间",
                        attachment_type=allure.attachment_type.TEXT,
                    )

                # 性能警告
                if duration_ms > threshold_ms:
                    logger.warning(
                        f"[性能警告] {func_name} 执行时间 {duration_ms:.2f}ms "
                        f"超过阈值 {threshold_ms}ms"
                    )

                    if ALLURE_AVAILABLE:
                        allure.attach(
                            f"执行时间 {duration_ms:.2f}ms 超过阈值 {threshold_ms}ms",
                            name="性能警告",
                            attachment_type=allure.attachment_type.TEXT,
                        )

                return result

            except Exception as e:
                # 即使出错也记录执行时间
                duration_ms = (time.perf_counter() - start_time) * 1000
                logger.error(f"[性能] {func_name} 执行失败 (耗时 {duration_ms:.2f}ms): {str(e)}")
                raise

        return wrapper  # type: ignore[return-value]

    return decorator


class PerformanceTimer:
    """性能计时器上下文管理器

    用于测量代码块的执行时间。

    Attributes:
        name: 计时器名称
        threshold_ms: 性能阈值（毫秒）
        log_result: 是否记录结果
        duration_ms: 执行时间（毫秒），在退出上下文后可用

    Example:
        >>> with PerformanceTimer("数据库查询") as timer:
        ...     result = db.query_all("SELECT * FROM users")
        >>> print(f"查询耗时: {timer.duration_ms}ms")

        >>> with PerformanceTimer("API请求", threshold_ms=200) as timer:
        ...     response = api.get("/users")
        >>> # 超过 200ms 会自动记录警告
    """

    def __init__(
        self,
        name: str,
        threshold_ms: float | None = None,
        log_result: bool = True,
    ) -> None:
        """初始化性能计时器

        Args:
            name: 计时器名称
            threshold_ms: 性能阈值（毫秒），如果设置则超过阈值时记录警告
            log_result: 是否记录结果
        """
        self.name = name
        self.threshold_ms = threshold_ms
        self.log_result = log_result
        self._start_time: float | None = None
        self._end_time: float | None = None
        self.duration_ms: float | None = None

    def __enter__(self) -> PerformanceTimer:
        """进入上下文"""
        self._start_time = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """退出上下文"""
        self._end_time = time.perf_counter()
        self.duration_ms = (self._end_time - self._start_time) * 1000  # type: ignore[operator]

        if self.log_result:
            logger.info(f"[性能] {self.name} 执行时间: {self.duration_ms:.2f}ms")

        # 性能警告
        if self.threshold_ms and self.duration_ms > self.threshold_ms:
            logger.warning(
                f"[性能警告] {self.name} 执行时间 {self.duration_ms:.2f}ms "
                f"超过阈值 {self.threshold_ms}ms"
            )

    @property
    def start_time(self) -> float | None:
        """开始时间（秒）"""
        return self._start_time

    @property
    def end_time(self) -> float | None:
        """结束时间（秒）"""
        return self._end_time


class PerformanceCollector:
    """性能数据收集器

    用于收集和统计多次操作的性能数据。

    Attributes:
        name: 收集器名称
        durations: 收集的执行时间列表（毫秒）

    Example:
        >>> collector = PerformanceCollector("API请求")
        >>> for i in range(100):
        ...     with collector.measure():
        ...         api.get("/users")
        >>> print(collector.summary())
        {'name': 'API请求', 'count': 100, 'total_ms': 1234.56, 'avg_ms': 12.35, ...}

        >>> collector.log_summary()  # 输出到日志
        >>> collector.reset()  # 重置收集器
    """

    def __init__(self, name: str) -> None:
        """初始化性能收集器

        Args:
            name: 收集器名称
        """
        self.name = name
        self.durations: list[float] = []
        self._current_start: float | None = None

    def measure(self) -> _MeasureContext:
        """返回计时上下文管理器

        Returns:
            计时上下文管理器

        Example:
            >>> with collector.measure():
            ...     # 要测量的代码
            ...     pass
        """
        return _MeasureContext(self)

    def add_duration(self, duration_ms: float) -> None:
        """手动添加一个执行时间记录

        Args:
            duration_ms: 执行时间（毫秒）
        """
        self.durations.append(duration_ms)

    def summary(self) -> dict[str, Any]:
        """获取性能统计摘要

        Returns:
            包含统计数据的字典，包括:
            - name: 收集器名称
            - count: 测量次数
            - total_ms: 总耗时（毫秒）
            - avg_ms: 平均耗时（毫秒）
            - min_ms: 最小耗时（毫秒）
            - max_ms: 最大耗时（毫秒）
        """
        if not self.durations:
            return {
                "name": self.name,
                "count": 0,
                "total_ms": 0.0,
                "avg_ms": 0.0,
                "min_ms": 0.0,
                "max_ms": 0.0,
            }

        total = sum(self.durations)
        count = len(self.durations)

        return {
            "name": self.name,
            "count": count,
            "total_ms": round(total, 2),
            "avg_ms": round(total / count, 2),
            "min_ms": round(min(self.durations), 2),
            "max_ms": round(max(self.durations), 2),
        }

    def log_summary(self) -> None:
        """记录性能统计摘要到日志"""
        summary = self.summary()
        logger.info(
            f"[性能统计] {summary['name']} - "
            f"次数: {summary['count']}, "
            f"总耗时: {summary['total_ms']}ms, "
            f"平均: {summary['avg_ms']}ms, "
            f"最小: {summary['min_ms']}ms, "
            f"最大: {summary['max_ms']}ms"
        )

    def reset(self) -> None:
        """重置收集器，清除所有已收集的数据"""
        self.durations.clear()
        self._current_start = None


class _MeasureContext:
    """内部计时上下文管理器"""

    def __init__(self, collector: PerformanceCollector) -> None:
        self._collector = collector

    def __enter__(self) -> _MeasureContext:
        self._collector._current_start = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        if self._collector._current_start is not None:
            duration = (time.perf_counter() - self._collector._current_start) * 1000
            self._collector.durations.append(duration)
            self._collector._current_start = None


class APIPerformanceTracker:
    """API性能追踪器

    用于追踪和统计API调用的性能数据，支持慢调用检测。

    Attributes:
        slow_threshold_ms: 慢调用阈值（毫秒）
        records: API调用记录

    Example:
        >>> tracker = APIPerformanceTracker(slow_threshold_ms=200)
        >>> tracker.record("get_users", 150, success=True)
        >>> tracker.record("get_users", 250, success=True)  # 慢调用
        >>> tracker.record("create_user", 100, success=False)
        >>> print(tracker.get_summary())
        >>> print(tracker.get_slow_calls())
    """

    def __init__(self, slow_threshold_ms: float = 200) -> None:
        """初始化API性能追踪器

        Args:
            slow_threshold_ms: 慢调用阈值（毫秒），超过此值的调用被视为慢调用
        """
        self.slow_threshold_ms = slow_threshold_ms
        self._records: dict[str, list[dict[str, Any]]] = {}
        self._slow_calls: list[dict[str, Any]] = []

    def record(
        self,
        api_name: str,
        duration_ms: float,
        success: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """记录一次API调用

        Args:
            api_name: API名称
            duration_ms: 调用耗时（毫秒）
            success: 是否成功
            metadata: 附加元数据
        """
        record = {
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": time.time(),
            "metadata": metadata or {},
        }

        if api_name not in self._records:
            self._records[api_name] = []
        self._records[api_name].append(record)

        # 检测慢调用
        if duration_ms > self.slow_threshold_ms:
            self._slow_calls.append(
                {
                    "api_name": api_name,
                    "duration_ms": duration_ms,
                    "success": success,
                    "timestamp": record["timestamp"],
                }
            )

    def get_summary(self) -> dict[str, dict[str, Any]]:
        """获取性能统计摘要

        Returns:
            按API名称分组的统计数据字典
        """
        summary = {}
        for api_name, records in self._records.items():
            durations = [r["duration_ms"] for r in records]
            success_count = sum(1 for r in records if r["success"])
            fail_count = len(records) - success_count

            summary[api_name] = {
                "总调用次数": len(records),
                "成功次数": success_count,
                "失败次数": fail_count,
                "平均响应时间(ms)": round(sum(durations) / len(durations), 2) if durations else 0,
                "最小响应时间(ms)": round(min(durations), 2) if durations else 0,
                "最大响应时间(ms)": round(max(durations), 2) if durations else 0,
                "慢调用次数": sum(1 for d in durations if d > self.slow_threshold_ms),
            }
        return summary

    def get_slow_calls(self, limit: int = 10) -> list[dict[str, Any]]:
        """获取慢调用列表

        Args:
            limit: 返回的最大记录数

        Returns:
            慢调用记录列表（按耗时降序）
        """
        sorted_calls = sorted(
            self._slow_calls,
            key=lambda x: x["duration_ms"],
            reverse=True,
        )
        return sorted_calls[:limit]

    def get_report(self) -> str:
        """获取格式化的性能报告

        Returns:
            格式化的报告字符串
        """
        lines = ["=" * 60, "API 性能报告", "=" * 60]

        summary = self.get_summary()
        if not summary:
            lines.append("暂无数据")
        else:
            for api_name, stats in summary.items():
                lines.append(f"\n{api_name}:")
                for key, value in stats.items():
                    lines.append(f"  {key}: {value}")

        slow_calls = self.get_slow_calls()
        if slow_calls:
            lines.append("\n" + "-" * 40)
            lines.append("慢调用 Top 10:")
            for call in slow_calls:
                lines.append(f"  {call['api_name']}: {call['duration_ms']:.2f}ms")

        lines.append("=" * 60)
        return "\n".join(lines)

    def reset(self) -> None:
        """重置追踪器，清除所有记录"""
        self._records.clear()
        self._slow_calls.clear()


class SlowQueryMonitor:
    """慢查询监控器

    用于监控和统计数据库慢查询。

    Attributes:
        threshold_ms: 慢查询阈值（毫秒）
        max_records: 最大记录数

    Example:
        >>> monitor = SlowQueryMonitor(threshold_ms=100, max_records=1000)
        >>> monitor.record("SELECT * FROM users", 150)  # 慢查询
        >>> monitor.record("SELECT 1", 5)  # 正常查询
        >>> print(monitor.get_statistics())
        >>> print(monitor.get_slow_queries(limit=10))
    """

    def __init__(
        self,
        threshold_ms: float = 100,
        max_records: int = 1000,
    ) -> None:
        """初始化慢查询监控器

        Args:
            threshold_ms: 慢查询阈值（毫秒）
            max_records: 最大记录数（超过后删除最早的记录）
        """
        self.threshold_ms = threshold_ms
        self.max_records = max_records
        self._all_queries: list[dict[str, Any]] = []
        self._slow_queries: list[dict[str, Any]] = []

    def record(
        self,
        sql: str,
        duration_ms: float,
        params: dict[str, Any] | None = None,
    ) -> None:
        """记录一次查询

        Args:
            sql: SQL语句
            duration_ms: 查询耗时（毫秒）
            params: SQL参数
        """
        record = {
            "sql": sql[:500] if len(sql) > 500 else sql,  # 截断长SQL
            "duration_ms": duration_ms,
            "timestamp": time.time(),
            "params": params,
        }

        self._all_queries.append(record)

        # 限制记录数量
        if len(self._all_queries) > self.max_records:
            self._all_queries = self._all_queries[-self.max_records :]

        # 记录慢查询
        if duration_ms > self.threshold_ms:
            self._slow_queries.append(record)
            if len(self._slow_queries) > self.max_records:
                self._slow_queries = self._slow_queries[-self.max_records :]

    def get_statistics(self) -> dict[str, Any]:
        """获取查询统计

        Returns:
            统计数据字典
        """
        total = len(self._all_queries)
        slow_count = len(self._slow_queries)

        if total == 0:
            return {
                "总查询数": 0,
                "慢查询数": 0,
                "慢查询比例(%)": 0.0,
                "平均响应时间(ms)": 0.0,
            }

        durations = [q["duration_ms"] for q in self._all_queries]
        avg_duration = sum(durations) / len(durations)

        return {
            "总查询数": total,
            "慢查询数": slow_count,
            "慢查询比例(%)": round(slow_count / total * 100, 2),
            "平均响应时间(ms)": round(avg_duration, 2),
            "最大响应时间(ms)": round(max(durations), 2),
            "慢查询阈值(ms)": self.threshold_ms,
        }

    def get_slow_queries(self, limit: int = 20) -> list[dict[str, Any]]:
        """获取慢查询列表

        Args:
            limit: 返回的最大记录数

        Returns:
            慢查询记录列表（按耗时降序）
        """
        sorted_queries = sorted(
            self._slow_queries,
            key=lambda x: x["duration_ms"],
            reverse=True,
        )
        return sorted_queries[:limit]

    def reset(self) -> None:
        """重置监控器，清除所有记录"""
        self._all_queries.clear()
        self._slow_queries.clear()


__all__ = [
    "track_performance",
    "PerformanceTimer",
    "PerformanceCollector",
    "APIPerformanceTracker",
    "SlowQueryMonitor",
]
