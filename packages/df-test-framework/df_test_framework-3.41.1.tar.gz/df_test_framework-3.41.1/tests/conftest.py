"""pytest 配置文件

v3.37.0: 框架插件通过 pytest11 Entry Points 自动加载
- pip install df-test-framework 后，插件自动可用
- 无需手动声明 pytest_plugins

自动加载的插件:
- df_test_framework.testing.fixtures.core - 核心 fixtures
- df_test_framework.testing.fixtures.allure - Allure 报告
- df_test_framework.testing.plugins.env_plugin - 环境管理
- df_test_framework.testing.plugins.logging_plugin - 日志桥接
- df_test_framework.testing.plugins.markers - 环境标记
"""

# 插件通过 pyproject.toml [project.entry-points.pytest11] 自动加载
# 无需手动声明 pytest_plugins
