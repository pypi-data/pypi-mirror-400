"""测试 utils.py - CLI工具函数

测试覆盖:
- to_snake_case() - 名称转换为蛇形
- to_pascal_case() - 名称转换为帕斯卡
- create_file() - 文件创建
- replace_template_vars() - 模板变量替换
- detect_project_name() - 项目名称检测
- merge_with_markers() - 增量合并（v3.39.0）
- create_file_with_merge() - 带合并的文件创建（v3.39.0）
- generate_init_from_directory() - 动态生成 __init__.py（v3.39.0）
"""

import shutil

import pytest

from df_test_framework.cli.utils import (
    AUTO_GENERATED_END,
    AUTO_GENERATED_START,
    AUTO_GENERATED_WARNING,
    USER_EXTENSIONS_HINT,
    USER_EXTENSIONS_START,
    create_file,
    create_file_with_merge,
    detect_project_name,
    generate_init_from_directory,
    merge_with_markers,
    replace_template_vars,
    to_ascii_identifier,
    to_pascal_case,
    to_snake_case,
)


class TestNameConversion:
    """测试名称转换函数"""

    def test_to_snake_case_with_hyphens(self):
        """测试横杠分隔转蛇形"""
        assert to_snake_case("my-test-project") == "my_test_project"
        assert to_snake_case("gift-card-api") == "gift_card_api"

    def test_to_snake_case_with_spaces(self):
        """测试空格分隔转蛇形"""
        assert to_snake_case("my test project") == "my_test_project"
        assert to_snake_case("user login test") == "user_login_test"

    def test_to_snake_case_with_camel_case(self):
        """测试驼峰命名转蛇形"""
        assert to_snake_case("MyTestProject") == "my_test_project"
        assert to_snake_case("UserLogin") == "user_login"
        assert to_snake_case("HTTPClient") == "http_client"
        assert to_snake_case("XMLParser") == "xml_parser"

    def test_to_snake_case_already_snake(self):
        """测试已经是蛇形的名称"""
        assert to_snake_case("my_test_project") == "my_test_project"
        assert to_snake_case("user_login") == "user_login"

    def test_to_snake_case_mixed_format(self):
        """测试混合格式"""
        assert to_snake_case("my-TestProject") == "my_test_project"
        assert to_snake_case("User-Login_Test") == "user_login_test"

    def test_to_pascal_case_with_hyphens(self):
        """测试横杠分隔转帕斯卡"""
        assert to_pascal_case("my-test-project") == "MyTestProject"
        assert to_pascal_case("gift-card-api") == "GiftCardApi"

    def test_to_pascal_case_with_underscores(self):
        """测试下划线分隔转帕斯卡"""
        assert to_pascal_case("my_test_project") == "MyTestProject"
        assert to_pascal_case("user_login") == "UserLogin"

    def test_to_pascal_case_with_camel_case(self):
        """测试驼峰命名转帕斯卡"""
        assert to_pascal_case("UserLogin") == "UserLogin"
        assert to_pascal_case("myTestProject") == "MyTestProject"

    def test_to_pascal_case_with_spaces(self):
        """测试空格分隔转帕斯卡"""
        assert to_pascal_case("my test project") == "MyTestProject"


class TestAsciiIdentifier:
    """测试 ASCII 标识符转换函数（v3.38.0）"""

    def test_ascii_string_unchanged(self):
        """测试纯 ASCII 字符串转换为 snake_case"""
        assert to_ascii_identifier("user-controller") == "user_controller"
        assert to_ascii_identifier("UserAPI") == "user_api"
        assert to_ascii_identifier("my_test") == "my_test"

    def test_chinese_with_pypinyin(self):
        """测试中文转换（有 pypinyin 时转拼音）"""
        try:
            import pypinyin  # noqa: F401

            # 有 pypinyin 时应该转换为拼音
            result = to_ascii_identifier("用户管理")
            assert result.isascii()
            assert "_" in result or result.isalpha()
            # 拼音结果应该是 yong_hu_guan_li
            assert "yong" in result or "tag_" in result
        except ImportError:
            # 没有 pypinyin 时跳过此测试
            pytest.skip("pypinyin 未安装")

    def test_chinese_without_pypinyin_fallback(self):
        """测试中文转换（无 pypinyin 时使用哈希）"""
        # 模拟无 pypinyin 的情况
        import sys

        # 临时移除 pypinyin
        pypinyin_module = sys.modules.get("pypinyin")
        if pypinyin_module:
            sys.modules["pypinyin"] = None

        try:
            # 重新导入以触发 ImportError
            from df_test_framework.cli.utils import _generate_tag_id

            result = _generate_tag_id("用户管理")
            assert result.startswith("tag_")
            assert len(result) == 10  # tag_ + 6位哈希
            assert result.isascii()
        finally:
            # 恢复 pypinyin
            if pypinyin_module:
                sys.modules["pypinyin"] = pypinyin_module

    def test_mixed_ascii_chinese(self):
        """测试混合 ASCII 和中文"""
        result = to_ascii_identifier("API用户")
        assert result.isascii()
        # 结果应该是合法的 Python 标识符
        assert result.replace("_", "").isalnum()

    def test_empty_string(self):
        """测试空字符串"""
        result = to_ascii_identifier("")
        assert result == ""

    def test_hash_consistency(self):
        """测试哈希一致性（相同输入相同输出）"""
        from df_test_framework.cli.utils import _generate_tag_id

        result1 = _generate_tag_id("测试标签")
        result2 = _generate_tag_id("测试标签")
        assert result1 == result2

    def test_hash_uniqueness(self):
        """测试哈希唯一性（不同输入不同输出）"""
        from df_test_framework.cli.utils import _generate_tag_id

        result1 = _generate_tag_id("标签一")
        result2 = _generate_tag_id("标签二")
        assert result1 != result2


class TestCreateFile:
    """测试文件创建函数"""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """临时目录"""
        yield tmp_path
        # 清理
        for item in tmp_path.iterdir():
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            else:
                item.unlink()

    def test_create_file_simple(self, temp_dir):
        """测试创建简单文件"""
        file_path = temp_dir / "test.txt"
        content = "Hello World"

        create_file(file_path, content)

        assert file_path.exists()
        assert file_path.read_text(encoding="utf-8") == content

    def test_create_file_with_directory(self, temp_dir):
        """测试创建带目录的文件"""
        file_path = temp_dir / "subdir" / "nested" / "test.txt"
        content = "Nested file"

        create_file(file_path, content)

        assert file_path.exists()
        assert file_path.read_text(encoding="utf-8") == content

    def test_create_file_already_exists_without_force(self, temp_dir):
        """测试文件已存在且不强制覆盖"""
        file_path = temp_dir / "existing.txt"
        file_path.write_text("Original content", encoding="utf-8")

        with pytest.raises(FileExistsError, match="already exists"):
            create_file(file_path, "New content", force=False)

        # 验证文件内容未被修改
        assert file_path.read_text(encoding="utf-8") == "Original content"

    def test_create_file_already_exists_with_force(self, temp_dir):
        """测试文件已存在且强制覆盖"""
        file_path = temp_dir / "existing.txt"
        file_path.write_text("Original content", encoding="utf-8")

        create_file(file_path, "New content", force=True)

        assert file_path.read_text(encoding="utf-8") == "New content"

    def test_create_file_with_chinese_content(self, temp_dir):
        """测试创建包含中文的文件"""
        file_path = temp_dir / "chinese.txt"
        content = "你好，世界！"

        create_file(file_path, content)

        assert file_path.read_text(encoding="utf-8") == content


class TestReplaceTemplateVars:
    """测试模板变量替换函数"""

    def test_replace_single_variable(self):
        """测试替换单个变量"""
        template = "Hello {name}!"
        result = replace_template_vars(template, {"{name}": "World"})
        assert result == "Hello World!"

    def test_replace_multiple_variables(self):
        """测试替换多个变量"""
        template = "Project: {project_name}, Type: {project_type}"
        replacements = {"{project_name}": "my-project", "{project_type}": "api"}
        result = replace_template_vars(template, replacements)
        assert result == "Project: my-project, Type: api"

    def test_replace_with_empty_dict(self):
        """测试空替换字典"""
        template = "No changes here"
        result = replace_template_vars(template, {})
        assert result == "No changes here"

    def test_replace_variable_multiple_times(self):
        """测试变量出现多次"""
        template = "{name} loves {name}"
        result = replace_template_vars(template, {"{name}": "Alice"})
        assert result == "Alice loves Alice"

    def test_replace_with_chinese(self):
        """测试替换中文变量"""
        template = "欢迎使用 {framework_name}"
        result = replace_template_vars(template, {"{framework_name}": "DF测试框架"})
        assert result == "欢迎使用 DF测试框架"


class TestDetectProjectName:
    """测试项目名称检测函数"""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """创建临时项目目录"""
        import os

        old_cwd = os.getcwd()
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        os.chdir(project_dir)

        yield project_dir

        os.chdir(old_cwd)
        if project_dir.exists():
            shutil.rmtree(project_dir, ignore_errors=True)

    def test_detect_from_pyproject_toml(self, temp_project):
        """测试从pyproject.toml检测项目名"""
        pyproject = temp_project / "pyproject.toml"
        pyproject.write_text(
            '[project]\nname = "my-awesome-project"\nversion = "1.0.0"', encoding="utf-8"
        )

        name = detect_project_name()
        assert name == "my-awesome-project"

    def test_detect_from_pyproject_toml_with_quotes(self, temp_project):
        """测试从pyproject.toml检测项目名（不同引号）"""
        pyproject = temp_project / "pyproject.toml"
        pyproject.write_text(
            "[project]\nname = 'single-quote-project'\nversion = '1.0.0'", encoding="utf-8"
        )

        name = detect_project_name()
        assert name == "single-quote-project"

    def test_detect_from_pyproject_toml_with_spaces(self, temp_project):
        """测试从pyproject.toml检测项目名（带空格）"""
        pyproject = temp_project / "pyproject.toml"
        pyproject.write_text(
            '[project]\n  name  =  "spaced-project"  \nversion = "1.0.0"', encoding="utf-8"
        )

        name = detect_project_name()
        assert name == "spaced-project"

    def test_detect_fallback_to_directory_name(self, temp_project):
        """测试无pyproject.toml时回退到目录名"""
        name = detect_project_name()
        assert name == "test_project"

    def test_detect_from_pyproject_toml_malformed(self, temp_project):
        """测试pyproject.toml格式错误时回退到目录名"""
        pyproject = temp_project / "pyproject.toml"
        pyproject.write_text(
            "[project]\nversion = '1.0.0'",  # 没有name字段
            encoding="utf-8",
        )

        name = detect_project_name()
        assert name == "test_project"


class TestMergeWithMarkers:
    """测试增量合并函数（v3.39.0）"""

    def test_merge_preserves_user_content(self):
        """测试合并时保留用户扩展区域内容"""
        existing_content = f'''"""模块"""

{AUTO_GENERATED_START}
{AUTO_GENERATED_WARNING}

class OldClass:
    pass

{AUTO_GENERATED_END}


{USER_EXTENSIONS_START}
{USER_EXTENSIONS_HINT}

class MyCustomClass:
    """用户自定义类"""
    pass
'''

        new_content = f'''"""模块"""

{AUTO_GENERATED_START}
{AUTO_GENERATED_WARNING}

class NewClass:
    pass

{AUTO_GENERATED_END}


{USER_EXTENSIONS_START}
{USER_EXTENSIONS_HINT}
'''

        result = merge_with_markers(existing_content, new_content)

        # 验证新的自动生成内容
        assert "class NewClass:" in result
        assert "class OldClass:" not in result

        # 验证用户内容被保留
        assert "class MyCustomClass:" in result
        assert "用户自定义类" in result

    def test_merge_without_user_content(self):
        """测试用户区域为空时的合并"""
        existing_content = f'''"""模块"""

{AUTO_GENERATED_START}
class OldClass:
    pass
{AUTO_GENERATED_END}

{USER_EXTENSIONS_START}
{USER_EXTENSIONS_HINT}
'''

        new_content = f'''"""模块"""

{AUTO_GENERATED_START}
class NewClass:
    pass
{AUTO_GENERATED_END}

{USER_EXTENSIONS_START}
{USER_EXTENSIONS_HINT}
'''

        result = merge_with_markers(existing_content, new_content)

        # 验证新内容
        assert "class NewClass:" in result
        assert "class OldClass:" not in result

    def test_merge_with_multiline_user_content(self):
        """测试多行用户内容的合并"""
        existing_content = f'''"""模块"""

{AUTO_GENERATED_START}
pass
{AUTO_GENERATED_END}

{USER_EXTENSIONS_START}
{USER_EXTENSIONS_HINT}

# 用户添加的注释
def custom_function():
    return "custom"

class AnotherCustomClass:
    pass
'''

        new_content = f'''"""模块"""

{AUTO_GENERATED_START}
class UpdatedClass:
    pass
{AUTO_GENERATED_END}

{USER_EXTENSIONS_START}
{USER_EXTENSIONS_HINT}
'''

        result = merge_with_markers(existing_content, new_content)

        # 验证用户内容被保留
        assert "用户添加的注释" in result
        assert "def custom_function():" in result
        assert "class AnotherCustomClass:" in result


class TestCreateFileWithMerge:
    """测试带合并的文件创建（v3.39.0）"""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """临时目录"""
        yield tmp_path
        for item in tmp_path.iterdir():
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            else:
                item.unlink()

    def test_create_new_file(self, temp_dir):
        """测试创建新文件"""
        file_path = temp_dir / "new_file.py"
        content = "# New file content"

        success, action = create_file_with_merge(file_path, content)

        assert success is True
        assert action == "created"
        assert file_path.exists()
        assert file_path.read_text(encoding="utf-8") == content

    def test_merge_mode_with_markers(self, temp_dir):
        """测试合并模式（有分区标记）"""
        file_path = temp_dir / "mergeable.py"

        # 创建初始文件
        initial_content = f'''"""模块"""

{AUTO_GENERATED_START}
{AUTO_GENERATED_WARNING}

class InitialClass:
    pass

{AUTO_GENERATED_END}


{USER_EXTENSIONS_START}
{USER_EXTENSIONS_HINT}

class UserClass:
    pass
'''
        file_path.write_text(initial_content, encoding="utf-8")

        # 尝试合并新内容
        new_content = f'''"""模块"""

{AUTO_GENERATED_START}
{AUTO_GENERATED_WARNING}

class UpdatedClass:
    pass

{AUTO_GENERATED_END}


{USER_EXTENSIONS_START}
{USER_EXTENSIONS_HINT}
'''
        success, action = create_file_with_merge(file_path, new_content, merge=True)

        assert success is True
        assert action == "merged"

        result = file_path.read_text(encoding="utf-8")
        assert "class UpdatedClass:" in result
        assert "class UserClass:" in result
        assert "class InitialClass:" not in result

    def test_merge_mode_without_markers(self, temp_dir):
        """测试合并模式（无分区标记，应跳过）"""
        file_path = temp_dir / "no_markers.py"
        file_path.write_text("# Old content without markers", encoding="utf-8")

        new_content = f"""# New content
{AUTO_GENERATED_START}
{AUTO_GENERATED_END}
"""
        success, action = create_file_with_merge(file_path, new_content, merge=True)

        assert success is False
        assert "skipped" in action

    def test_force_mode_overwrites(self, temp_dir):
        """测试强制覆盖模式"""
        file_path = temp_dir / "force_test.py"
        file_path.write_text("# Old content", encoding="utf-8")

        new_content = "# New content"
        success, action = create_file_with_merge(file_path, new_content, force=True)

        assert success is True
        assert action == "overwritten"
        assert file_path.read_text(encoding="utf-8") == new_content

    def test_skip_existing_file(self, temp_dir):
        """测试默认跳过已存在的文件"""
        file_path = temp_dir / "existing.py"
        file_path.write_text("# Original", encoding="utf-8")

        success, action = create_file_with_merge(file_path, "# New")

        assert success is False
        assert action == "skipped"
        assert file_path.read_text(encoding="utf-8") == "# Original"


class TestGenerateInitFromDirectory:
    """测试动态生成 __init__.py（v3.39.0）"""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """临时目录"""
        module_dir = tmp_path / "mymodule"
        module_dir.mkdir()
        yield module_dir
        shutil.rmtree(tmp_path, ignore_errors=True)

    def test_generate_with_modules_no_all(self, temp_dir):
        """测试无 __all__ 时使用 * 导入"""
        # 创建没有 __all__ 的模块文件
        (temp_dir / "user.py").write_text("class User: pass", encoding="utf-8")
        (temp_dir / "order.py").write_text("class Order: pass", encoding="utf-8")

        result = generate_init_from_directory(temp_dir, docstring="测试模块")

        assert '"""测试模块"""' in result
        assert "from .user import *" in result
        assert "from .order import *" in result
        assert AUTO_GENERATED_START in result
        assert USER_EXTENSIONS_START in result

    def test_generate_with_explicit_all(self, temp_dir):
        """测试有 __all__ 时生成显式导入"""
        # 创建有 __all__ 的模块文件
        (temp_dir / "user.py").write_text(
            'class CreateUser: pass\nclass UpdateUser: pass\n\n__all__ = ["CreateUser", "UpdateUser"]',
            encoding="utf-8",
        )
        (temp_dir / "order.py").write_text(
            'class Order: pass\n\n__all__ = ["Order"]',
            encoding="utf-8",
        )

        result = generate_init_from_directory(temp_dir, docstring="测试模块")

        # 验证显式导入
        assert "from .user import CreateUser, UpdateUser" in result
        assert "from .order import Order" in result
        # 验证生成 __all__
        assert "__all__ = [" in result
        assert '"CreateUser"' in result
        assert '"Order"' in result
        assert '"UpdateUser"' in result

    def test_generate_empty_directory(self, temp_dir):
        """测试空目录时生成"""
        result = generate_init_from_directory(temp_dir, docstring="空模块")

        assert '"""空模块"""' in result
        assert "# 暂无模块" in result
        assert USER_EXTENSIONS_START in result

    def test_generate_ignores_init_and_private(self, temp_dir):
        """测试忽略 __init__.py 和私有模块"""
        (temp_dir / "__init__.py").write_text("# init", encoding="utf-8")
        (temp_dir / "_private.py").write_text("# private", encoding="utf-8")
        (temp_dir / "public.py").write_text("# public", encoding="utf-8")

        result = generate_init_from_directory(temp_dir)

        assert "from .public import *" in result
        assert "__init__" not in result
        assert "_private" not in result

    def test_generate_sorted_imports(self, temp_dir):
        """测试导入按字母顺序排序"""
        (temp_dir / "zebra.py").write_text("", encoding="utf-8")
        (temp_dir / "apple.py").write_text("", encoding="utf-8")
        (temp_dir / "mango.py").write_text("", encoding="utf-8")

        result = generate_init_from_directory(temp_dir)

        # 验证排序
        apple_pos = result.find("from .apple")
        mango_pos = result.find("from .mango")
        zebra_pos = result.find("from .zebra")

        assert apple_pos < mango_pos < zebra_pos


__all__ = [
    "TestNameConversion",
    "TestAsciiIdentifier",
    "TestCreateFile",
    "TestReplaceTemplateVars",
    "TestDetectProjectName",
    "TestMergeWithMarkers",
    "TestCreateFileWithMerge",
    "TestGenerateInitFromDirectory",
]
