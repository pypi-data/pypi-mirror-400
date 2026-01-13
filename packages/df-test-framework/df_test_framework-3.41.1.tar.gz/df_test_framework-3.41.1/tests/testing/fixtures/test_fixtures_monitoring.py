"""fixtures/monitoring.py 测试模块

测试性能监控 pytest fixtures 功能

v3.36.0 - 技术债务清理：提升测试覆盖率
"""

import pytest


@pytest.mark.unit
class TestMonitoringModuleImport:
    """测试 monitoring 模块导入"""

    def test_monitoring_module_exists(self):
        """测试 monitoring 模块文件存在"""
        from pathlib import Path

        import df_test_framework.testing.fixtures

        fixtures_path = Path(df_test_framework.testing.fixtures.__file__).parent
        monitoring_path = fixtures_path / "monitoring.py"

        assert monitoring_path.exists(), f"monitoring.py not found at {monitoring_path}"

    def test_monitoring_module_imports_successfully(self):
        """测试 monitoring 模块可以正常导入"""
        from df_test_framework.testing.fixtures import monitoring

        assert monitoring is not None

    def test_monitoring_has_allure_available_flag(self):
        """测试 monitoring 模块有 ALLURE_AVAILABLE 标志"""
        from df_test_framework.testing.fixtures import monitoring

        assert hasattr(monitoring, "ALLURE_AVAILABLE")
        assert isinstance(monitoring.ALLURE_AVAILABLE, bool)


@pytest.mark.unit
class TestMonitoringFixtures:
    """测试 monitoring fixture 函数"""

    def test_api_performance_tracker_fixture_exists(self):
        """测试 api_performance_tracker fixture 存在"""
        from df_test_framework.testing.fixtures import monitoring

        assert hasattr(monitoring, "api_performance_tracker")
        assert callable(monitoring.api_performance_tracker)

    def test_api_tracker_fixture_exists(self):
        """测试 api_tracker fixture 存在"""
        from df_test_framework.testing.fixtures import monitoring

        assert hasattr(monitoring, "api_tracker")
        assert callable(monitoring.api_tracker)

    def test_slow_query_monitor_fixture_exists(self):
        """测试 slow_query_monitor fixture 存在"""
        from df_test_framework.testing.fixtures import monitoring

        assert hasattr(monitoring, "slow_query_monitor")
        assert callable(monitoring.slow_query_monitor)

    def test_auto_attach_performance_fixture_exists(self):
        """测试 auto_attach_performance fixture 存在"""
        from df_test_framework.testing.fixtures import monitoring

        assert hasattr(monitoring, "auto_attach_performance")
        assert callable(monitoring.auto_attach_performance)

    def test_fixtures_are_pytest_fixtures(self):
        """测试所有 fixture 都是 pytest fixture"""
        from df_test_framework.testing.fixtures import monitoring

        fixtures = [
            "api_performance_tracker",
            "api_tracker",
            "slow_query_monitor",
            "auto_attach_performance",
        ]

        for fixture_name in fixtures:
            fixture = getattr(monitoring, fixture_name)
            func_repr = repr(fixture)
            assert "pytest_fixture" in func_repr or "fixture" in func_repr.lower(), (
                f"{fixture_name} is not a pytest fixture"
            )


@pytest.mark.unit
class TestMonitoringModuleContent:
    """测试 monitoring 模块内容"""

    def test_monitoring_file_contains_fixtures(self):
        """测试 monitoring 文件包含 fixture 定义"""
        from pathlib import Path

        import df_test_framework.testing.fixtures

        fixtures_path = Path(df_test_framework.testing.fixtures.__file__).parent
        monitoring_path = fixtures_path / "monitoring.py"

        content = monitoring_path.read_text(encoding="utf-8")

        # 验证文件包含预期的 fixture 定义
        assert "@pytest.fixture" in content
        assert "api_performance_tracker" in content
        assert "api_tracker" in content
        assert "slow_query_monitor" in content
        assert "auto_attach_performance" in content

    def test_monitoring_file_contains_allure_check(self):
        """测试 monitoring 文件包含 Allure 可用性检查"""
        from pathlib import Path

        import df_test_framework.testing.fixtures

        fixtures_path = Path(df_test_framework.testing.fixtures.__file__).parent
        monitoring_path = fixtures_path / "monitoring.py"

        content = monitoring_path.read_text(encoding="utf-8")

        assert "ALLURE_AVAILABLE" in content
        assert "import allure" in content

    def test_monitoring_file_contains_logger(self):
        """测试 monitoring 文件使用 loguru logger"""
        from pathlib import Path

        import df_test_framework.testing.fixtures

        fixtures_path = Path(df_test_framework.testing.fixtures.__file__).parent
        monitoring_path = fixtures_path / "monitoring.py"

        content = monitoring_path.read_text(encoding="utf-8")

        # v3.38.2: 使用 get_logger 替代 loguru
        assert "get_logger" in content

    def test_monitoring_file_has_docstring(self):
        """测试 monitoring 文件有文档字符串"""
        from pathlib import Path

        import df_test_framework.testing.fixtures

        fixtures_path = Path(df_test_framework.testing.fixtures.__file__).parent
        monitoring_path = fixtures_path / "monitoring.py"

        content = monitoring_path.read_text(encoding="utf-8")

        # 检查文件开头的文档字符串
        assert content.startswith('"""')

    def test_monitoring_file_imports_from_infrastructure(self):
        """测试 monitoring 文件从 infrastructure.metrics.performance 导入"""
        from pathlib import Path

        import df_test_framework.testing.fixtures

        fixtures_path = Path(df_test_framework.testing.fixtures.__file__).parent
        monitoring_path = fixtures_path / "monitoring.py"

        content = monitoring_path.read_text(encoding="utf-8")

        # 验证导入语句
        assert "from ...infrastructure.metrics.performance import" in content
        assert "APIPerformanceTracker" in content
        assert "SlowQueryMonitor" in content


@pytest.mark.unit
class TestMonitoringFixtureScopes:
    """测试 monitoring fixture scope 定义"""

    def test_fixture_scopes_defined(self):
        """测试 fixture scope 定义正确"""
        from pathlib import Path

        import df_test_framework.testing.fixtures

        fixtures_path = Path(df_test_framework.testing.fixtures.__file__).parent
        monitoring_path = fixtures_path / "monitoring.py"

        content = monitoring_path.read_text(encoding="utf-8")

        # api_performance_tracker 应该是 session scope
        assert 'scope="session"' in content
        # api_tracker 应该是 function scope
        assert 'scope="function"' in content

    def test_auto_attach_not_autouse(self):
        """测试 auto_attach_performance 不是 autouse"""
        from pathlib import Path

        import df_test_framework.testing.fixtures

        fixtures_path = Path(df_test_framework.testing.fixtures.__file__).parent
        monitoring_path = fixtures_path / "monitoring.py"

        content = monitoring_path.read_text(encoding="utf-8")

        # 应该有 autouse=False
        assert "autouse=False" in content


@pytest.mark.unit
class TestAPIPerformanceTrackerClass:
    """测试 APIPerformanceTracker 类"""

    def test_api_performance_tracker_import(self):
        """测试 APIPerformanceTracker 可以导入"""
        from df_test_framework.infrastructure.metrics.performance import (
            APIPerformanceTracker,
        )

        assert APIPerformanceTracker is not None

    def test_api_performance_tracker_instantiate(self):
        """测试 APIPerformanceTracker 实例化"""
        from df_test_framework.infrastructure.metrics.performance import (
            APIPerformanceTracker,
        )

        tracker = APIPerformanceTracker(slow_threshold_ms=200)
        assert tracker.slow_threshold_ms == 200

    def test_api_performance_tracker_record(self):
        """测试 APIPerformanceTracker 记录功能"""
        from df_test_framework.infrastructure.metrics.performance import (
            APIPerformanceTracker,
        )

        tracker = APIPerformanceTracker(slow_threshold_ms=100)
        tracker.record("test_api", 50.0, success=True)
        tracker.record("test_api", 150.0, success=True)

        summary = tracker.get_summary()
        assert "test_api" in summary

    def test_api_performance_tracker_slow_calls(self):
        """测试 APIPerformanceTracker 慢调用检测"""
        from df_test_framework.infrastructure.metrics.performance import (
            APIPerformanceTracker,
        )

        tracker = APIPerformanceTracker(slow_threshold_ms=100)
        tracker.record("fast_api", 50.0, success=True)
        tracker.record("slow_api", 200.0, success=True)

        slow_calls = tracker.get_slow_calls()
        assert len(slow_calls) == 1
        assert slow_calls[0]["api_name"] == "slow_api"

    def test_api_performance_tracker_report(self):
        """测试 APIPerformanceTracker 报告生成"""
        from df_test_framework.infrastructure.metrics.performance import (
            APIPerformanceTracker,
        )

        tracker = APIPerformanceTracker(slow_threshold_ms=100)
        tracker.record("test_api", 50.0, success=True)

        report = tracker.get_report()
        assert isinstance(report, str)
        assert "test_api" in report

    def test_api_performance_tracker_reset(self):
        """测试 APIPerformanceTracker 重置功能"""
        from df_test_framework.infrastructure.metrics.performance import (
            APIPerformanceTracker,
        )

        tracker = APIPerformanceTracker(slow_threshold_ms=100)
        tracker.record("test_api", 50.0, success=True)

        tracker.reset()

        summary = tracker.get_summary()
        assert len(summary) == 0


@pytest.mark.unit
class TestSlowQueryMonitorClass:
    """测试 SlowQueryMonitor 类"""

    def test_slow_query_monitor_import(self):
        """测试 SlowQueryMonitor 可以导入"""
        from df_test_framework.infrastructure.metrics.performance import (
            SlowQueryMonitor,
        )

        assert SlowQueryMonitor is not None

    def test_slow_query_monitor_instantiate(self):
        """测试 SlowQueryMonitor 实例化"""
        from df_test_framework.infrastructure.metrics.performance import (
            SlowQueryMonitor,
        )

        monitor = SlowQueryMonitor(threshold_ms=100, max_records=500)
        assert monitor.threshold_ms == 100
        assert monitor.max_records == 500

    def test_slow_query_monitor_record(self):
        """测试 SlowQueryMonitor 记录功能"""
        from df_test_framework.infrastructure.metrics.performance import (
            SlowQueryMonitor,
        )

        monitor = SlowQueryMonitor(threshold_ms=100)
        monitor.record("SELECT * FROM users", 50.0)
        monitor.record("SELECT * FROM orders", 150.0)

        stats = monitor.get_statistics()
        assert stats["总查询数"] == 2
        assert stats["慢查询数"] == 1

    def test_slow_query_monitor_get_slow_queries(self):
        """测试 SlowQueryMonitor 获取慢查询"""
        from df_test_framework.infrastructure.metrics.performance import (
            SlowQueryMonitor,
        )

        monitor = SlowQueryMonitor(threshold_ms=100)
        monitor.record("SELECT * FROM users", 50.0)
        monitor.record("SELECT * FROM orders", 200.0)
        monitor.record("SELECT * FROM products", 150.0)

        slow_queries = monitor.get_slow_queries(limit=2)
        assert len(slow_queries) == 2
        # 按耗时降序排序
        assert slow_queries[0]["duration_ms"] >= slow_queries[1]["duration_ms"]

    def test_slow_query_monitor_reset(self):
        """测试 SlowQueryMonitor 重置功能"""
        from df_test_framework.infrastructure.metrics.performance import (
            SlowQueryMonitor,
        )

        monitor = SlowQueryMonitor(threshold_ms=100)
        monitor.record("SELECT * FROM users", 50.0)

        monitor.reset()

        stats = monitor.get_statistics()
        assert stats["总查询数"] == 0
