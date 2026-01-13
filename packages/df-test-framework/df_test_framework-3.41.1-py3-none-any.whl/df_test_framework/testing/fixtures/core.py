"""
df-test-framework 核心 pytest 插件

v3.37.0: 现代化重构
- 使用 pytest11 Entry Points 自动发现（pip install 即用）
- 使用 config 对象属性管理状态（pytest 官方推荐）
- 简化插件实现，移除不必要的管理器类

Usage:
    # 方式1: pip install df-test-framework 后自动加载（推荐）

    # 方式2: 手动声明（向后兼容）
    pytest_plugins = ["df_test_framework.testing.fixtures.core"]
"""

from __future__ import annotations

import importlib
import os
from collections.abc import Iterable
from typing import TYPE_CHECKING, cast

import pytest

from df_test_framework.bootstrap import Bootstrap, RuntimeContext
from df_test_framework.infrastructure.config import FrameworkSettings
from df_test_framework.infrastructure.logging import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from df_test_framework.infrastructure.events import EventBus


# ============================================================================
# 辅助函数
# ============================================================================


def _resolve_settings_class(path: str) -> type[FrameworkSettings]:
    """解析配置类路径"""
    module_name, _, class_name = path.rpartition(".")
    if not module_name:
        raise RuntimeError(f"无效的配置类路径: {path!r}")
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    if not issubclass(cls, FrameworkSettings):
        raise TypeError(f"{path!r} 不是 FrameworkSettings 的子类")
    return cast(type[FrameworkSettings], cls)


def _get_settings_path(config: pytest.Config) -> str:
    """获取配置类路径（优先级：CLI > ini > 环境变量 > 默认）"""
    ini_value = config.getini("df_settings_class") if "df_settings_class" in config.inicfg else None
    cli_value = config.getoption("--df-settings-class", default=None)
    env_value = os.getenv("DF_SETTINGS_CLASS")
    return (
        cli_value
        or ini_value
        or env_value
        or "df_test_framework.infrastructure.config.schema.FrameworkSettings"
    )


def _get_plugin_paths(config: pytest.Config) -> Iterable[str]:
    """获取插件路径列表"""
    collected = []
    cli_value = config.getoption("df_plugin") or []
    ini_value = config.getini("df_plugins") if "df_plugins" in config.inicfg else ""
    env_value = os.getenv("DF_PLUGINS", "")

    def parse(value):
        if not value:
            return []
        if isinstance(value, (list, tuple)):
            return [item.strip() for item in value if item and item.strip()]
        return [item.strip() for item in str(value).split(",") if item.strip()]

    for source in (cli_value, ini_value, env_value):
        collected.extend(parse(source))

    # 保持顺序，去重
    seen = set()
    for plugin in collected:
        if plugin not in seen:
            seen.add(plugin)
            yield plugin


def _get_test_event_bus(config: pytest.Config, test_id: str) -> EventBus:
    """获取测试专用 EventBus（测试隔离）"""
    from df_test_framework.infrastructure.events import EventBus

    if not hasattr(config, "_df_test_buses"):
        config._df_test_buses = {}  # type: ignore[attr-defined]

    buses = config._df_test_buses
    if test_id not in buses:
        buses[test_id] = EventBus()
        logger.debug(f"创建测试 EventBus: {test_id}")

    return buses[test_id]


def _cleanup_test_event_bus(config: pytest.Config, test_id: str) -> None:
    """清理测试专用 EventBus"""
    if hasattr(config, "_df_test_buses"):
        buses = config._df_test_buses
        if test_id in buses:
            bus = buses[test_id]
            if hasattr(bus, "clear"):
                bus.clear()
            del buses[test_id]
            logger.debug(f"清理测试 EventBus: {test_id}")


# ============================================================================
# pytest hooks
# ============================================================================


def pytest_addoption(parser: pytest.Parser) -> None:
    """注册命令行选项和 ini 配置"""
    parser.addoption(
        "--df-settings-class",
        action="store",
        default=None,
        help="配置类的完整路径（如 myproject.config.MySettings）",
    )
    parser.addini(
        "df_settings_class",
        "配置类的完整路径",
        type="string",
        default="",
    )
    parser.addoption(
        "--df-plugin",
        action="append",
        default=[],
        help="df-test-framework 插件路径（可重复使用）",
    )
    parser.addini(
        "df_plugins",
        "df-test-framework 插件列表（逗号分隔）",
        type="string",
        default="",
    )
    parser.addoption(
        "--keep-test-data",
        action="store_true",
        default=False,
        help="保留所有测试数据（调试用）",
    )


def pytest_configure(config: pytest.Config) -> None:
    """配置 pytest - 初始化 RuntimeContext"""
    # 检查 env_plugin 是否已加载配置
    if hasattr(config, "_df_settings"):
        # 使用 env_plugin 加载的配置
        settings = config._df_settings
        logger.debug(f"[core] 使用 env_plugin 配置, env={settings.env}")

        from df_test_framework.bootstrap.runtime import RuntimeBuilder

        runtime_context = RuntimeBuilder().with_settings(settings).with_logger(logger).build()
    else:
        # 传统方式：使用 Bootstrap 加载配置
        logger.debug("[core] env_plugin 未加载，使用 Bootstrap")
        settings_path = _get_settings_path(config)
        settings_cls = _resolve_settings_class(settings_path)

        bootstrap = Bootstrap().with_settings(settings_cls)
        for plugin_path in _get_plugin_paths(config):
            bootstrap.with_plugin(plugin_path)

        app = bootstrap.build()
        runtime_context = app.run(force_reload=True)

    # 存储到 config 对象（pytest 官方推荐方式）
    config._df_runtime = runtime_context  # type: ignore[attr-defined]

    # 注册 marker
    config.addinivalue_line(
        "markers",
        "keep_data: 保留此测试的所有数据（调试用）",
    )


def pytest_unconfigure(config: pytest.Config) -> None:
    """清理 pytest - 关闭 RuntimeContext"""
    # 关闭 RuntimeContext
    if hasattr(config, "_df_runtime"):
        try:
            config._df_runtime.close()
            logger.debug("[core] RuntimeContext 已关闭")
        except Exception as e:
            logger.error(f"[core] 关闭 RuntimeContext 失败: {e}")

    # 清理所有测试 EventBus
    if hasattr(config, "_df_test_buses"):
        for bus in config._df_test_buses.values():
            if hasattr(bus, "clear"):
                bus.clear()
        config._df_test_buses.clear()
        logger.debug("[core] 所有测试 EventBus 已清理")


# ============================================================================
# pytest fixtures
# ============================================================================


@pytest.fixture(scope="session")
def runtime(request: pytest.FixtureRequest) -> RuntimeContext:
    """RuntimeContext fixture（session 级别）"""
    if not hasattr(request.config, "_df_runtime"):
        raise RuntimeError(
            "RuntimeContext 未初始化。确保 df_test_framework.testing.fixtures.core 插件已加载。"
        )
    return request.config._df_runtime


@pytest.fixture(scope="session")
def http_client(runtime: RuntimeContext):
    """HTTP 客户端 fixture"""
    return runtime.http_client()


@pytest.fixture(scope="session")
def database(runtime: RuntimeContext):
    """数据库 fixture"""
    return runtime.database()


@pytest.fixture(scope="session")
def redis_client(runtime: RuntimeContext):
    """Redis 客户端 fixture"""
    return runtime.redis()


@pytest.fixture(scope="session")
def local_file_client(runtime: RuntimeContext):
    """本地文件存储客户端 fixture"""
    return runtime.local_file()


@pytest.fixture(scope="session")
def s3_client(runtime: RuntimeContext):
    """S3 对象存储客户端 fixture"""
    return runtime.s3()


@pytest.fixture(scope="session")
def oss_client(runtime: RuntimeContext):
    """阿里云 OSS 对象存储客户端 fixture"""
    return runtime.oss()


@pytest.fixture
def http_mock(http_client):
    """HTTP Mock fixture"""
    from ..mocking import HttpMocker

    mocker = HttpMocker(http_client)
    yield mocker
    mocker.reset()


@pytest.fixture
def time_mock():
    """时间 Mock fixture"""
    from ..mocking import TimeMocker

    mocker = TimeMocker()
    yield mocker
    mocker.stop()


@pytest.fixture
def uow(database, request: pytest.FixtureRequest, runtime: RuntimeContext):
    """Unit of Work fixture（function 级别）

    提供 UnitOfWork 实例，管理事务边界和 Repository 生命周期。
    测试结束后自动回滚（默认），可配置保留数据。
    """
    from df_test_framework.capabilities.databases.uow import UnitOfWork

    from .cleanup import should_keep_test_data

    # 检查是否保留数据
    auto_commit = should_keep_test_data(request)
    if auto_commit:
        logger.info("检测到保留数据配置，测试数据将被提交")

    # 获取 repository_package 配置
    repository_package = None
    if runtime.settings.test:
        repository_package = runtime.settings.test.repository_package

    # 获取测试隔离的 EventBus
    test_id = request.node.nodeid
    test_event_bus = _get_test_event_bus(request.config, test_id)

    # 创建 UnitOfWork
    unit_of_work = UnitOfWork(
        database.session_factory,
        repository_package=repository_package,
        event_bus=test_event_bus,
    )

    try:
        with unit_of_work:
            yield unit_of_work

            # 如果配置了自动提交且未手动提交
            if auto_commit and not unit_of_work._committed:
                unit_of_work.commit()
    finally:
        # 清理测试专用 EventBus
        _cleanup_test_event_bus(request.config, test_id)


@pytest.fixture
def cleanup(database, request: pytest.FixtureRequest, runtime: RuntimeContext):
    """配置驱动的数据清理 fixture"""
    from .cleanup import ConfigDrivenCleanupManager, SimpleCleanupManager

    # 获取清理配置
    cleanup_config = runtime.settings.cleanup

    if cleanup_config and cleanup_config.enabled and cleanup_config.mappings:
        logger.debug(f"使用配置驱动清理管理器: {len(cleanup_config.mappings)} 个映射")
        manager = ConfigDrivenCleanupManager(
            request=request,
            database=database,
            mappings=cleanup_config.mappings,
        )
    else:
        logger.debug("未配置清理映射，使用基础 SimpleCleanupManager")
        manager = SimpleCleanupManager(request=request, database=database)

    yield manager
    manager.cleanup()


@pytest.fixture
def prepare_data(database, request: pytest.FixtureRequest, runtime: RuntimeContext, cleanup):
    """数据准备 fixture（回调式）"""
    from df_test_framework.capabilities.databases.uow import UnitOfWork

    def _execute(callback, cleanup_items=None):
        """执行数据准备

        Args:
            callback: 接收 UoW 的回调函数
            cleanup_items: 清理项列表 [(type, id), ...]

        Returns:
            回调函数的返回值
        """
        repository_package = None
        if runtime.settings.test:
            repository_package = runtime.settings.test.repository_package

        # 获取测试隔离的 EventBus
        test_id = request.node.nodeid
        test_event_bus = _get_test_event_bus(request.config, test_id)

        # 创建临时 UoW
        uow = UnitOfWork(
            database.session_factory,
            repository_package=repository_package,
            event_bus=test_event_bus,
        )

        # 执行回调并提交
        with uow:
            result = callback(uow)
            uow.commit()
            logger.debug("prepare_data: 事务已提交")

        # 注册清理项
        if cleanup_items:
            for item_type, item_id in cleanup_items:
                cleanup.add(item_type, item_id)
                logger.debug(f"prepare_data: 已注册清理 {item_type}={item_id}")

        return result

    return _execute


@pytest.fixture
def data_preparer(database, request: pytest.FixtureRequest, runtime: RuntimeContext, cleanup):
    """数据准备器 fixture（上下文管理器式）"""
    from typing import Any

    from df_test_framework.capabilities.databases.uow import UnitOfWork

    class DataPreparer:
        """数据准备器上下文管理器"""

        def __init__(self, database, runtime, cleanup_manager, config, test_id):
            self._database = database
            self._runtime = runtime
            self._cleanup_manager = cleanup_manager
            self._config = config
            self._test_id = test_id
            self._uow: UnitOfWork | None = None
            self._cleanup_items: list[tuple[str, Any]] = []

        def __enter__(self) -> DataPreparer:
            """进入上下文：创建 UoW"""
            repository_package = None
            if self._runtime.settings.test:
                repository_package = self._runtime.settings.test.repository_package

            event_bus = _get_test_event_bus(self._config, self._test_id)

            self._uow = UnitOfWork(
                self._database.session_factory,
                repository_package=repository_package,
                event_bus=event_bus,
            )
            self._uow.__enter__()
            self._cleanup_items = []
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            """退出上下文：提交或回滚"""
            try:
                if exc_type is None:
                    self._uow.commit()
                    logger.debug("data_preparer: 事务已提交")

                    for item_type, item_id in self._cleanup_items:
                        self._cleanup_manager.add(item_type, item_id)
                        logger.debug(f"data_preparer: 已注册清理 {item_type}={item_id}")
                else:
                    logger.warning("data_preparer: 检测到异常，不注册清理")
            finally:
                self._uow.__exit__(exc_type, exc_val, exc_tb)
                self._uow = None

        @property
        def uow(self) -> UnitOfWork:
            """获取 UnitOfWork 实例"""
            if self._uow is None:
                raise RuntimeError("DataPreparer 必须在 with 语句中使用")
            return self._uow

        def cleanup(self, item_type: str, item_id: Any) -> DataPreparer:
            """注册清理项（支持链式调用）"""
            self._cleanup_items.append((item_type, item_id))
            return self

    test_id = request.node.nodeid
    return DataPreparer(database, runtime, cleanup, request.config, test_id)
