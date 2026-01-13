"""Fixtures模块导出模板"""

FIXTURES_INIT_TEMPLATE = """\"\"\"Pytest Fixtures (v3.35.5)

导出项目自定义 fixtures。

框架自动提供（通过 pytest_plugins）:
- runtime: 运行时上下文
- http_client: HTTP客户端（支持中间件系统）
- database: 数据库连接
- redis_client: Redis客户端
- uow: Unit of Work（事务管理 + Repository）
- cleanup: 配置驱动的数据清理
- prepare_data / data_preparer: 数据准备工具
- http_mock: HTTP请求Mock
- time_mock: 时间Mock
- local_file_client / s3_client / oss_client: 存储客户端
- console_debugger / debug_mode: 调试工具
- allure_observer: Allure 事件自动记录
- metrics_manager / metrics_observer: 指标收集

项目自定义:
- 业务 API fixtures（如需要）
- 自定义清理逻辑

数据清理:
- 推荐使用配置驱动清理（CLEANUP__MAPPINGS__*）
- DataGenerator.test_id() - 生成可追溯的测试标识符
\"\"\"

# ========== 项目业务专属 Fixtures ==========
# 项目只需定义业务专属 fixtures，核心 fixtures 由框架自动提供

# from .api_fixtures import (
#     api_client,  # 示例：业务 API 客户端
# )

# from .uow_fixture import uow  # Unit of Work

# 注意: cleanup fixture 由框架自动提供（配置驱动清理）


__all__ = [
    # 注意: 框架自动提供以下 fixtures（无需在此导出）:
    # - runtime, http_client, database, redis_client, uow, cleanup
    # - http_mock, time_mock
    # - local_file_client, s3_client, oss_client
    # - console_debugger, debug_mode
    # - metrics_manager, metrics_observer

    # 项目业务 fixtures（取消注释以启用）
    # "api_client",
]
"""

__all__ = ["FIXTURES_INIT_TEMPLATE"]
