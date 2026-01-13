"""pyproject.toml配置文件模板

v3.37.0: 使用 pytest 9.0 原生 TOML 配置
v3.38.2: 移除 loguru 依赖（框架使用 structlog）
v3.38.4: 添加 freezegun 依赖（time_mock 需要）
v3.38.5: structlog + pytest 集成（ProcessorFormatter 统一格式）
v3.38.6: 添加本地调试相关注释
v3.38.7: 简化日志架构，LoggingMiddleware 使用固定级别
"""

PYPROJECT_TOML_TEMPLATE = """[project]
name = "{project_name}"
version = "1.0.0"
description = "基于 df-test-framework v3.38.7 的自动化测试项目"
requires-python = ">=3.12"
dependencies = [
    {framework_dependency},
    "pytest>=9.0.0",
    "pytest-timeout>=2.3.0",
    "pytest-asyncio>=0.24.0",
    "allure-pytest>=2.13.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    # v3.38.5: freezegun 已内置于框架（time_mock fixture）
]

[project.optional-dependencies]
dev = [
    "pytest-cov>=5.0.0",
    "ruff>=0.6.0",
    "mypy>=1.11.0",
]
# UI 测试（Playwright）
ui = [
    "pytest-playwright>=0.4.0",
]
# v3.38.5 高性能 JSON 序列化（可选，日志 JSONRenderer 自动使用）
performance = [
    "orjson>=3.9.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.metadata]
allow-direct-references = true

# v3.37.0: pytest 9.0 原生 TOML 配置
# 使用 [tool.pytest] 替代 [tool.pytest.ini_options]
[tool.pytest]
minversion = "9.0"
pythonpath = ["src"]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "--alluredir=reports/allure-results",
]
markers = [
    "smoke: 冒烟测试，核心功能验证",
    "regression: 回归测试，全量功能验证",
    "e2e: 端到端测试，完整业务流程",
    "negative: 负向测试，异常场景验证",
    "integration: 集成测试，多模块协作",
    "slow: 执行时间较长的测试",
    "api: API 接口测试",
    "ui: UI 界面测试",
    # 注意: keep_data 和 debug marker 由框架自动注册，无需在此定义
]

# v3.37.0: timeout 需要为字符串类型（pytest-timeout 兼容）
timeout = "30"
timeout_method = "thread"

# 输出模式: progress（进度条）/ classic（经典）/ count（计数）
# console_output_style = "classic"  # 如遇日志混排问题可启用

# v3.13.0: pytest-asyncio 配置（支持 async def test_xxx）
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"

# Live logging: 实时显示日志（运行时）
# 本地调试时使用: pytest --log-cli-level=DEBUG -v -s
log_cli = true
log_cli_level = "INFO"  # 默认 INFO，调试时命令行覆盖为 DEBUG

# Captured logging: 捕获日志（测试失败时显示在 "Captured log" 区域）
log_level = "DEBUG"  # 捕获 DEBUG 及以上级别，失败时可查看详细日志

# v3.38.9: 以下格式配置会被 ProcessorFormatter 覆盖（实时日志 + captured log 均生效）
# 保留配置作为备用：当框架未安装或禁用时生效
log_cli_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
log_cli_date_format = "%Y-%m-%d %H:%M:%S"
log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
log_date_format = "%Y-%m-%d %H:%M:%S"

# 本地调试快速命令（详见 docs/guides/local_debug_quickstart.md）:
#   pytest tests/ --env=local -v                           # 使用 local 环境
#   pytest tests/ --env=local --log-cli-level=DEBUG -v -s  # DEBUG 日志
#   pytest tests/ --env=local --pdb -v -s                  # 失败时进入调试器

# 过滤警告
filterwarnings = [
    "ignore::pytest.PytestAssertRewriteWarning",
]

# df_settings_class 指定框架使用的 Settings 类
df_settings_class = "{project_name}.config.{ProjectName}Settings"

[tool.ruff]
line-length = 100
target-version = "py312"
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
"""

__all__ = ["PYPROJECT_TOML_TEMPLATE"]
