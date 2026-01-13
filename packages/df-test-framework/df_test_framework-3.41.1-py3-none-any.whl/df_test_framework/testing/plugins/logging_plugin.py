"""pytest 日志插件 - 自动配置 structlog 与 pytest 集成

此插件自动配置 structlog 日志系统，与 pytest 原生日志系统无缝集成。

v3.38.2: 重写，使用 structlog 替代 loguru
v3.38.3: 简化 API，从 settings.logging 读取配置
v3.38.5: 修复 pytest 日志集成问题
    - 禁用 structlog 控制台输出，由 pytest 统一处理
    - 替换 pytest handlers 的 formatter 为 ProcessorFormatter
    - 解决日志重复和 dict 格式问题
v3.38.6: 两阶段初始化，确保日志格式统一
    - 模块加载时即完成 structlog 早期初始化
    - 解决 pytest_configure 阶段日志格式不统一问题
v3.38.7: 修复 YAML logging.level 配置不生效问题
    - 显式设置 df_test_framework 命名空间的日志级别
    - 防止 pytest log_level 覆盖框架日志级别
v3.38.9: 增强 captured log 支持
    - 替换 caplog_handler 和 report_handler 的 formatter
    - 统一 "Captured log setup/call/teardown" 区域的日志格式

使用方式:
    # 方式 1: 在 conftest.py 中声明插件（推荐）
    pytest_plugins = ["df_test_framework.testing.plugins.logging_plugin"]

    # 方式 2: 通过 Entry Points 自动加载（v3.37.0+）
    # pip install 后插件自动加载，无需手动配置

配置方式:
    # config/base.yaml
    logging:
      level: DEBUG
      format: text  # text（开发）或 json（生产）或 logfmt（Loki）
      file: logs/app.log  # 可选，启用文件日志
      rotation: "100 MB"
      retention: "7 days"

效果:
    - structlog 日志由 pytest 统一控制显示
    - 支持 pytest 的 --log-cli-level 等日志参数
    - 失败测试的日志集中显示在 "Captured log" 区域
    - 日志格式统一，无重复输出
"""

import logging

import pytest
from pytest import hookimpl

from df_test_framework.infrastructure.config import LoggingConfig
from df_test_framework.infrastructure.logging import (
    configure_logging,
    create_processor_formatter,
)

# 保存配置，供 sessionstart 使用
_logging_config: LoggingConfig | None = None

# 标记是否已完成早期初始化
_early_init_done: bool = False


def _early_init_logging() -> None:
    """早期初始化 structlog（使用默认配置）

    确保在任何 get_logger() 调用之前，structlog 已经正确配置。
    这样所有日志都会使用统一的格式，包括 pytest_configure 阶段的日志。

    v3.38.6: 新增两阶段初始化，解决日志格式不统一问题
    """
    global _early_init_done
    if _early_init_done:
        return

    # 使用默认配置初始化（禁用控制台，由 pytest 统一处理）
    default_config = LoggingConfig(
        level="DEBUG",
        format="text",
        sanitize=True,
        enable_console=False,
    )
    configure_logging(default_config)
    _early_init_done = True


# 模块加载时立即执行早期初始化
# 确保在任何 pytest 钩子执行之前，structlog 已配置
_early_init_logging()


@hookimpl(trylast=True)
def pytest_configure(config: pytest.Config) -> None:
    """pytest 配置阶段钩子

    使用 @hookimpl(trylast=True) 确保在 env_plugin 之后执行，
    这样可以从 config._df_settings 获取日志配置。

    重要: 在 pytest 环境下，禁用 structlog 的控制台输出，
    由 pytest 的 live log handler 统一处理日志显示。
    """
    global _logging_config

    # 尝试从 settings 获取日志配置
    logging_config = None
    if hasattr(config, "_df_settings"):
        settings = config._df_settings
        if settings and settings.logging is not None:
            logging_config = settings.logging

    # 如果没有配置，使用默认配置
    if logging_config is None:
        log_level = config.getini("log_level") or "DEBUG"
        logging_config = LoggingConfig(
            level=log_level.upper(),
            format="text",  # pytest 环境使用彩色控制台输出
            sanitize=True,
        )

    # 在 pytest 环境下，禁用 structlog 的控制台输出
    # 由 pytest 的 live log handler 统一处理
    logging_config = logging_config.model_copy(update={"enable_console": False})

    # 保存配置供 sessionstart 使用
    _logging_config = logging_config

    # 配置 structlog（不输出到控制台）
    configure_logging(logging_config)


@hookimpl(tryfirst=True)
def pytest_sessionstart(session: pytest.Session) -> None:
    """pytest session 开始钩子

    根据 structlog 官方文档推荐，通过 pluginmanager 访问 pytest 的 logging 插件，
    替换其 handlers 的 formatter 为 ProcessorFormatter。

    v3.38.7: 显式设置 df_test_framework 命名空间的日志级别，
    防止 pytest 的 log_level 配置覆盖 YAML 中的 logging.level 设置。

    参考: https://www.structlog.org/en/stable/standard-library.html
    """
    global _logging_config

    if _logging_config is None:
        return

    # 创建 ProcessorFormatter
    processor_formatter = create_processor_formatter(_logging_config)

    # 替换 root logger 所有 handlers 的 formatter
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.setFormatter(processor_formatter)

    # v3.38.7: 显式设置框架内部模块的日志级别
    # pytest 的 log_level 会覆盖 root logger 级别，导致 YAML 配置失效
    # 只设置内部模块级别，不影响用户可配置的中间件（capabilities.clients.http.middleware）
    framework_log_level = getattr(logging, _logging_config.level.upper(), logging.INFO)
    internal_namespaces = [
        "df_test_framework.infrastructure",  # 基础设施（events, plugins, telemetry 等）
        "df_test_framework.core",  # 核心模块
        "df_test_framework.bootstrap",  # 引导模块
    ]
    for namespace in internal_namespaces:
        logging.getLogger(namespace).setLevel(framework_log_level)

    # 官方推荐方式：通过 pluginmanager 访问 pytest 的 logging 插件
    # 参考: pytest 文档 _pytest.logging 模块
    plugin_manager = session.config.pluginmanager
    logging_plugin = plugin_manager.get_plugin("logging-plugin")
    if logging_plugin is not None:
        # log_cli_handler: 实时日志输出（--log-cli-level）
        if hasattr(logging_plugin, "log_cli_handler") and logging_plugin.log_cli_handler:
            logging_plugin.log_cli_handler.setFormatter(processor_formatter)
        # log_file_handler: 文件日志输出（--log-file）
        if hasattr(logging_plugin, "log_file_handler") and logging_plugin.log_file_handler:
            logging_plugin.log_file_handler.setFormatter(processor_formatter)
        # v3.38.9: caplog_handler - caplog fixture 使用的 handler
        if hasattr(logging_plugin, "caplog_handler") and logging_plugin.caplog_handler:
            logging_plugin.caplog_handler.setFormatter(processor_formatter)
        # v3.38.9: report_handler - "Captured log setup/call/teardown" 区域
        if hasattr(logging_plugin, "report_handler") and logging_plugin.report_handler:
            logging_plugin.report_handler.setFormatter(processor_formatter)


def pytest_unconfigure(config: pytest.Config) -> None:
    """pytest 退出阶段钩子"""
    global _logging_config
    _logging_config = None
