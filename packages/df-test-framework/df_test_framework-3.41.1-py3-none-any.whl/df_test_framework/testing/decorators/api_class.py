"""API 类自动注册装饰器

提供 @api_class 装饰器，自动将 API 类注册为 pytest fixture。
"""

from collections.abc import Callable
from typing import Any, Literal, cast

import pytest

from df_test_framework.capabilities.clients.http.rest.httpx.base_api import BaseAPI

# 全局 API 注册表
# 格式: {fixture_name: (api_class, scope, dependencies)}
_api_registry: dict[str, tuple[type[BaseAPI], str, dict[str, Any]]] = {}


def api_class(
    name: str | None = None,
    scope: str = "session",
    **dependencies: Any,
):
    """API 类装饰器，自动注册为 pytest fixture

    将 API 类自动注册为 pytest fixture，无需手动创建 fixture 函数。

    Args:
        name: fixture 名称，默认为类名转小写并去掉 'api' 后缀
              例如: MasterCardAPI -> master_card (或 master_card_api)
        scope: pytest fixture scope，默认 "session"
               可选: "session", "module", "class", "function"
        **dependencies: fixture 依赖项，会自动注入到 API 类构造函数
                       例如: http_client="http_client", settings="settings"

    Returns:
        装饰后的类（不改变类本身）

    Example:
        >>> # 基本用法
        >>> @api_class("master_card_api")
        >>> class MasterCardAPI(BaseAPI):
        ...     def __init__(self, http_client, settings):
        ...         super().__init__(http_client)
        ...         self.settings = settings
        ...
        ...     def create_cards(self, request):
        ...         return self.post("/master/card/create", json=request)
        >>>
        >>> # 自动生成 fixture，测试中直接使用
        >>> def test_create(master_card_api):
        ...     response = master_card_api.create_cards(...)
        ...     assert response["success"]

        >>> # 自定义 fixture 名称
        >>> @api_class("my_api")
        >>> class MyAPI(BaseAPI):
        ...     pass
        >>>
        >>> def test_xxx(my_api):  # 使用自定义名称
        ...     pass

        >>> # 指定 scope
        >>> @api_class("temp_api", scope="function")  # 每个测试创建新实例
        >>> class TempAPI(BaseAPI):
        ...     pass

        >>> # 自定义依赖
        >>> @api_class("custom_api", http_client="custom_http", db="database")
        >>> class CustomAPI(BaseAPI):
        ...     def __init__(self, http_client, db):
        ...         super().__init__(http_client)
        ...         self.db = db
    """

    def decorator(cls: type[BaseAPI]) -> type[BaseAPI]:
        # 生成 fixture 名称
        fixture_name = name
        if fixture_name is None:
            # 自动生成：MasterCardAPI -> master_card_api
            fixture_name = cls.__name__
            # 移除 'API' 后缀
            if fixture_name.endswith("API"):
                fixture_name = fixture_name[:-3]
            # 转换为 snake_case
            import re

            fixture_name = re.sub(r"(?<!^)(?=[A-Z])", "_", fixture_name).lower()
            # 确保以 _api 结尾
            if not fixture_name.endswith("_api"):
                fixture_name = f"{fixture_name}_api"

        # 注册到全局注册表
        _api_registry[fixture_name] = (cls, scope, dependencies)

        # 返回原始类（不修改）
        return cls

    return decorator


def get_api_registry() -> dict[str, tuple[type[BaseAPI], str, dict[str, Any]]]:
    """获取 API 注册表

    Returns:
        API 注册表字典
    """
    return _api_registry.copy()


ScopeType = Literal["session", "package", "module", "class", "function"]


def create_api_fixture(
    cls: type[BaseAPI],
    fixture_name: str,
    scope: ScopeType = "session",
    **dependencies: Any,
) -> Callable[..., Any]:
    """为单个 API 类创建 pytest fixture

    Args:
        cls: API 类
        fixture_name: fixture 名称
        scope: fixture scope
        **dependencies: 依赖注入配置

    Returns:
        pytest fixture 函数

    Example:
        >>> # 手动创建 fixture
        >>> my_api_fixture = create_api_fixture(
        ...     MyAPI,
        ...     "my_api",
        ...     scope="session",
        ...     http_client="http_client",
        ...     settings="settings"
        ... )
    """
    # 如果没有指定依赖，自动推断
    if not dependencies:
        import inspect

        sig = inspect.signature(cls.__init__)
        params = list(sig.parameters.keys())

        # 移除 self
        if "self" in params:
            params.remove("self")

        # 自动推断依赖
        if "http_client" in params:
            dependencies["http_client"] = "http_client"
        if "settings" in params:
            dependencies["settings"] = "settings"
        if "runtime" in params:
            dependencies["runtime"] = "runtime"

    # 创建 fixture 函数
    @pytest.fixture(scope=scope, name=fixture_name)
    def api_fixture(request):
        """自动生成的 API fixture"""
        # 解析依赖项
        resolved_deps = {}
        for param_name, fixture_name_or_value in dependencies.items():
            if isinstance(fixture_name_or_value, str):
                # 字符串表示 fixture 名称，从 request 获取
                try:
                    resolved_deps[param_name] = request.getfixturevalue(fixture_name_or_value)
                except Exception:
                    # 如果获取失败，尝试直接使用值
                    resolved_deps[param_name] = fixture_name_or_value
            else:
                # 直接使用值
                resolved_deps[param_name] = fixture_name_or_value

        # 创建 API 实例
        return cls(**resolved_deps)

    # 设置函数名称和文档
    api_fixture.__name__ = fixture_name
    api_fixture.__doc__ = f"Auto-generated fixture for {cls.__name__}"

    return cast(Callable[..., Any], api_fixture)


def load_api_fixtures(module_globals: dict, apis_package: str | None = None) -> None:
    """加载所有注册的 API fixture 到指定模块

    在 conftest.py 中调用此函数，自动注册所有 @api_class 装饰的 API 为 fixture。

    Args:
        module_globals: 模块的 globals() 字典，通常在 conftest.py 中传入
        apis_package: API 包路径（如 "master_test.apis"），如果提供则自动导入该包下所有模块

    Example:
        >>> # conftest.py - 自动发现模式（推荐）
        >>> from df_test_framework.testing.decorators import load_api_fixtures
        >>>
        >>> # 自动导入 apis 包下所有模块，无需手动 import
        >>> load_api_fixtures(globals(), apis_package="master_test.apis")

        >>> # conftest.py - 手动导入模式
        >>> from df_test_framework.testing.decorators import load_api_fixtures
        >>> from master_test.apis.xxx_api import XxxAPI  # noqa: F401
        >>>
        >>> load_api_fixtures(globals())
    """
    # 如果指定了 apis_package，自动导入该包下所有模块
    if apis_package:
        import importlib
        import pkgutil

        try:
            package = importlib.import_module(apis_package)
            # 遍历包下所有模块并导入（触发 @api_class 装饰器）
            for _, modname, _ in pkgutil.iter_modules(package.__path__):
                try:
                    importlib.import_module(f"{apis_package}.{modname}")
                except ImportError as e:
                    import warnings

                    warnings.warn(f"无法导入模块 {apis_package}.{modname}: {e}")
        except ImportError as e:
            import warnings

            warnings.warn(f"无法导入 API 包 {apis_package}: {e}")

    # 从注册表创建 fixture
    for fixture_name, (api_cls, scope, deps) in _api_registry.items():
        # 创建 fixture
        fixture_func = create_api_fixture(api_cls, fixture_name, scope, **deps)
        # 添加到模块全局变量
        module_globals[fixture_name] = fixture_func


__all__ = [
    "api_class",
    "get_api_registry",
    "create_api_fixture",
    "load_api_fixtures",
]
