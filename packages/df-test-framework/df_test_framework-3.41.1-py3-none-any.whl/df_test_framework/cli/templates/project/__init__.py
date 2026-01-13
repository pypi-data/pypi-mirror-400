"""项目初始化模板

包含创建测试项目时使用的所有文件模板。
"""

# 基础配置文件模板
from .base_api import BASE_API_TEMPLATE
from .conftest import CONFTEST_TEMPLATE
from .constants import CONSTANTS_ERROR_CODES_TEMPLATE
from .data_cleaners import DATA_CLEANERS_TEMPLATE
from .docs_api import DOCS_API_TEMPLATE
from .editorconfig import EDITORCONFIG_TEMPLATE
from .enhanced_gitignore import ENHANCED_GITIGNORE_TEMPLATE
from .fixtures_init import FIXTURES_INIT_TEMPLATE
from .gitattributes import GITATTRIBUTES_TEMPLATE
from .gitignore import GITIGNORE_TEMPLATE
from .models_requests_example import MODELS_REQUESTS_EXAMPLE_TEMPLATE
from .models_responses_example import MODELS_RESPONSES_EXAMPLE_TEMPLATE
from .pyproject_toml import PYPROJECT_TOML_TEMPLATE
from .readme import README_API_TEMPLATE, README_FULL_TEMPLATE, README_UI_TEMPLATE
from .script_fetch_swagger import SCRIPT_FETCH_SWAGGER_TEMPLATE
from .script_run_tests import SCRIPT_RUN_TESTS_TEMPLATE

# API项目专用模板
from .settings import SETTINGS_TEMPLATE
from .test_example import TEST_EXAMPLE_TEMPLATE
from .ui_conftest import UI_CONFTEST_TEMPLATE
from .ui_fixtures_init import UI_FIXTURES_INIT_TEMPLATE
from .ui_page_object import UI_PAGE_OBJECT_TEMPLATE

# UI项目专用模板
from .ui_settings import UI_SETTINGS_TEMPLATE
from .ui_test_example import UI_TEST_EXAMPLE_TEMPLATE
from .user_api_example import EXAMPLE_API_TEMPLATE
from .utils_converters import UTILS_CONVERTERS_TEMPLATE

# 增强功能模板
from .utils_validators import UTILS_VALIDATORS_TEMPLATE
from .vscode_settings import VSCODE_EXTENSIONS_TEMPLATE, VSCODE_SETTINGS_TEMPLATE

__all__ = [
    # 基础配置文件
    "GITIGNORE_TEMPLATE",
    "GITATTRIBUTES_TEMPLATE",
    "EDITORCONFIG_TEMPLATE",
    "README_API_TEMPLATE",
    "README_UI_TEMPLATE",
    "README_FULL_TEMPLATE",
    "PYPROJECT_TOML_TEMPLATE",
    "VSCODE_SETTINGS_TEMPLATE",
    "VSCODE_EXTENSIONS_TEMPLATE",
    # API项目模板
    "SETTINGS_TEMPLATE",
    "CONFTEST_TEMPLATE",
    "FIXTURES_INIT_TEMPLATE",
    "BASE_API_TEMPLATE",
    "DATA_CLEANERS_TEMPLATE",
    "TEST_EXAMPLE_TEMPLATE",
    "MODELS_REQUESTS_EXAMPLE_TEMPLATE",
    "MODELS_RESPONSES_EXAMPLE_TEMPLATE",
    "EXAMPLE_API_TEMPLATE",
    # UI项目模板
    "UI_SETTINGS_TEMPLATE",
    "UI_CONFTEST_TEMPLATE",
    "UI_PAGE_OBJECT_TEMPLATE",
    "UI_TEST_EXAMPLE_TEMPLATE",
    "UI_FIXTURES_INIT_TEMPLATE",
    # 增强功能模板
    "UTILS_VALIDATORS_TEMPLATE",
    "UTILS_CONVERTERS_TEMPLATE",
    "CONSTANTS_ERROR_CODES_TEMPLATE",
    "ENHANCED_GITIGNORE_TEMPLATE",
    "SCRIPT_RUN_TESTS_TEMPLATE",
    "SCRIPT_FETCH_SWAGGER_TEMPLATE",
    "DOCS_API_TEMPLATE",
]
