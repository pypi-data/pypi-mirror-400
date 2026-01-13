"""CLI工具函数

提供命令行工具的通用工具函数，包括字符串转换、文件操作等。

v3.39.0 新增:
- 增量合并支持（分区标记系统）
- 动态 __init__.py 生成
"""

from __future__ import annotations

import re
from pathlib import Path

# ==================== 分区标记常量 ====================
# 用于增量合并时识别自动生成区域和用户扩展区域

AUTO_GENERATED_START = "# ========== AUTO-GENERATED START =========="
AUTO_GENERATED_END = "# ========== AUTO-GENERATED END =========="
USER_EXTENSIONS_START = "# ========== USER EXTENSIONS =========="
AUTO_GENERATED_WARNING = "# 此区域由脚手架自动生成，重新生成时会被更新"
USER_EXTENSIONS_HINT = "# 在此区域添加自定义代码，重新生成时会保留"


def to_snake_case(name: str) -> str:
    """将项目名转换为snake_case

    支持多种输入格式：
    - 横杠分隔: my-test-project -> my_test_project
    - 空格分隔: my test project -> my_test_project
    - 驼峰命名: MyTestProject -> my_test_project
    - 已经是蛇形: my_test_project -> my_test_project

    Args:
        name: 项目名

    Returns:
        snake_case名称

    Example:
        >>> to_snake_case("my-test-project")
        'my_test_project'
        >>> to_snake_case("MyTestProject")
        'my_test_project'
        >>> to_snake_case("UserLogin")
        'user_login'
    """
    import re

    # 首先处理横杠和空格
    name = name.replace("-", "_").replace(" ", "_")

    # 处理驼峰命名：在大写字母前插入下划线
    # UserLogin -> User_Login -> user_login
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)

    # 处理连续大写字母的情况
    # HTTPClient -> HTTP_Client -> http_client
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)

    # 转小写并去除多余的下划线
    return re.sub(r"_+", "_", name).lower().strip("_")


def to_pascal_case(name: str) -> str:
    """将项目名转换为PascalCase

    支持多种输入格式：
    - 横杠分隔: my-test-project -> MyTestProject
    - 下划线分隔: my_test_project -> MyTestProject
    - 驼峰命名: UserLogin -> UserLogin (保持不变)
    - 空格分隔: my test project -> MyTestProject

    Args:
        name: 项目名

    Returns:
        PascalCase名称

    Example:
        >>> to_pascal_case("my-test-project")
        'MyTestProject'
        >>> to_pascal_case("gift_card_test")
        'GiftCardTest'
        >>> to_pascal_case("UserLogin")
        'UserLogin'
    """
    # 先转为蛇形，然后再转为Pascal（确保一致性）
    snake = to_snake_case(name)
    return "".join(word.capitalize() for word in snake.split("_") if word)


def create_file(file_path: Path, content: str, *, force: bool = False) -> None:
    """创建文件

    Args:
        file_path: 文件路径
        content: 文件内容
        force: 是否强制覆盖

    Raises:
        FileExistsError: 文件已存在且force=False
    """
    if file_path.exists() and not force:
        raise FileExistsError(f"{file_path} already exists. Use --force to overwrite.")

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


def merge_with_markers(existing_content: str, new_auto_content: str) -> str:
    """增量合并：保留用户扩展区域，替换自动生成区域

    文件结构:
        [文件头部注释和导入]
        # ========== AUTO-GENERATED START ==========
        # 此区域由脚手架自动生成，重新生成时会被更新
        [自动生成的代码]
        # ========== AUTO-GENERATED END ==========

        # ========== USER EXTENSIONS ==========
        # 在此区域添加自定义代码，重新生成时会保留
        [用户自定义代码]

    Args:
        existing_content: 现有文件内容
        new_auto_content: 新的自动生成内容（包含完整文件结构）

    Returns:
        合并后的文件内容

    Example:
        >>> existing = '''...
        ... # ========== AUTO-GENERATED START ==========
        ... class OldModel: pass
        ... # ========== AUTO-GENERATED END ==========
        ...
        ... # ========== USER EXTENSIONS ==========
        ... class MyCustomModel: pass
        ... '''
        >>> new_content = '''...
        ... # ========== AUTO-GENERATED START ==========
        ... class NewModel: pass
        ... # ========== AUTO-GENERATED END ==========
        ...
        ... # ========== USER EXTENSIONS ==========
        ... '''
        >>> merged = merge_with_markers(existing, new_content)
        >>> # merged 包含 NewModel 和 MyCustomModel
    """
    # 提取现有文件的用户扩展区域
    user_pattern = rf"{re.escape(USER_EXTENSIONS_START)}(.*?)$"
    user_match = re.search(user_pattern, existing_content, re.DOTALL)

    if user_match:
        # 获取用户扩展区域的内容（不包含标记本身）
        user_content = user_match.group(1).strip()

        # v3.41.0: 清理用户内容中的重复提示行
        # 移除所有 USER_EXTENSIONS_HINT 行和 USER_EXTENSIONS_START 行
        lines = user_content.split("\n")
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            # 跳过提示行和标记行
            if stripped == USER_EXTENSIONS_HINT.strip():
                continue
            if stripped == USER_EXTENSIONS_START.strip():
                continue
            if stripped == "# 在此添加自定义测试用例，重新生成时会保留":
                continue
            cleaned_lines.append(line)

        user_content = "\n".join(cleaned_lines).strip()

        # 如果清理后为空，视为无用户内容
        if not user_content:
            user_content = ""
    else:
        user_content = ""

    # 在新内容中找到用户扩展区域的位置并替换
    new_user_pattern = (
        rf"({re.escape(USER_EXTENSIONS_START)}\n{re.escape(USER_EXTENSIONS_HINT)}\n)(.*?)$"
    )
    new_user_match = re.search(new_user_pattern, new_auto_content, re.DOTALL)

    if new_user_match and user_content:
        # 替换用户区域内容
        result = new_auto_content[: new_user_match.end(1)] + "\n" + user_content
    elif user_content:
        # 新内容没有用户区域标记，追加到末尾
        result = (
            new_auto_content.rstrip()
            + f"\n\n\n{USER_EXTENSIONS_START}\n{USER_EXTENSIONS_HINT}\n\n"
            + user_content
        )
    else:
        # 没有用户内容，直接使用新内容
        result = new_auto_content

    return result


def create_file_with_merge(
    file_path: Path,
    content: str,
    *,
    force: bool = False,
    merge: bool = False,
) -> tuple[bool, str]:
    """创建或合并文件

    v3.39.0 新增：支持增量合并模式

    Args:
        file_path: 文件路径
        content: 新的文件内容（应包含分区标记）
        force: 是否强制覆盖（与 merge 互斥）
        merge: 是否使用增量合并模式

    Returns:
        (是否成功, 操作类型描述)
        - (True, "created") - 新建文件
        - (True, "merged") - 合并成功
        - (True, "overwritten") - 强制覆盖
        - (False, "skipped") - 文件已存在且未指定 force/merge

    Example:
        >>> success, action = create_file_with_merge(
        ...     Path("models/user.py"),
        ...     new_content,
        ...     merge=True
        ... )
        >>> if success:
        ...     print(f"文件已{action}")
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if not file_path.exists():
        # 文件不存在，直接创建
        file_path.write_text(content, encoding="utf-8")
        return True, "created"

    if merge:
        # 增量合并模式
        existing_content = file_path.read_text(encoding="utf-8")

        # 检查现有文件是否有分区标记
        if AUTO_GENERATED_START in existing_content:
            merged_content = merge_with_markers(existing_content, content)
            file_path.write_text(merged_content, encoding="utf-8")
            return True, "merged"
        else:
            # 现有文件没有标记，无法合并，跳过
            return False, "skipped (no markers)"

    if force:
        # 强制覆盖模式
        file_path.write_text(content, encoding="utf-8")
        return True, "overwritten"

    # 默认：文件已存在，跳过
    return False, "skipped"


def _extract_all_from_file(file_path: Path) -> list[str]:
    """从 Python 文件中提取 __all__ 定义的导出名称

    使用 AST 解析，安全可靠。

    Args:
        file_path: Python 文件路径

    Returns:
        __all__ 中定义的名称列表，如果没有 __all__ 则返回空列表
    """
    import ast

    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        for node in ast.walk(tree):
            # 查找 __all__ = [...] 赋值语句
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            return [
                                elt.value
                                for elt in node.value.elts
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                            ]
        return []
    except Exception:
        return []


def generate_init_from_directory(
    directory: Path,
    *,
    docstring: str = "",
    extra_imports: list[str] | None = None,
) -> str:
    """扫描目录生成 __init__.py 内容

    v3.39.0 新增：动态生成 __init__.py，解决分阶段生成导出不累积的问题

    功能特性：
    - 扫描目录下所有 .py 文件（排除 __init__.py 和 _ 开头的私有模块）
    - 解析每个模块的 __all__ 定义，生成显式导入
    - 自动生成 __all__ 列表，提供完整的 IDE 智能提示

    Args:
        directory: 要扫描的目录
        docstring: 模块文档字符串
        extra_imports: 额外的导入语句（保留用户添加的导入）

    Returns:
        生成的 __init__.py 内容

    Example:
        >>> content = generate_init_from_directory(
        ...     Path("src/myproject/models/requests"),
        ...     docstring="请求模型模块"
        ... )
        >>> # 自动生成:
        >>> # from .user import CreateUserRequest, UpdateUserRequest
        >>> # __all__ = ["CreateUserRequest", "UpdateUserRequest"]
    """
    # 扫描目录下所有 .py 文件（除 __init__.py 和私有模块）
    module_files = sorted(
        f for f in directory.glob("*.py") if f.stem != "__init__" and not f.stem.startswith("_")
    )

    # 构建内容
    lines = []

    # 文档字符串
    if docstring:
        lines.append(f'"""{docstring}"""')
        lines.append("")

    # 自动生成的导入
    if module_files:
        lines.append(AUTO_GENERATED_START)
        lines.append(AUTO_GENERATED_WARNING)
        lines.append("")

        all_exports: list[str] = []

        for mod_file in module_files:
            mod_name = mod_file.stem
            exports = _extract_all_from_file(mod_file)

            if exports:
                # 有 __all__，生成显式导入
                exports_str = ", ".join(sorted(exports))
                lines.append(f"from .{mod_name} import {exports_str}")
                all_exports.extend(exports)
            else:
                # 没有 __all__，使用 * 导入
                lines.append(f"from .{mod_name} import *")

        # 生成 __all__
        if all_exports:
            lines.append("")
            all_exports_str = ", ".join(f'"{name}"' for name in sorted(all_exports))
            lines.append(f"__all__ = [{all_exports_str}]")

        lines.append("")
        lines.append(AUTO_GENERATED_END)
    else:
        lines.append(AUTO_GENERATED_START)
        lines.append(AUTO_GENERATED_WARNING)
        lines.append("")
        lines.append("# 暂无模块")
        lines.append("")
        lines.append(AUTO_GENERATED_END)

    # 用户扩展区域
    lines.append("")
    lines.append("")
    lines.append(USER_EXTENSIONS_START)
    lines.append(USER_EXTENSIONS_HINT)

    # 额外导入（来自用户）
    if extra_imports:
        lines.append("")
        lines.extend(extra_imports)

    lines.append("")

    return "\n".join(lines)


def replace_template_vars(template: str, replacements: dict[str, str]) -> str:
    """替换模板中的变量

    Args:
        template: 模板字符串
        replacements: 变量替换字典

    Returns:
        替换后的字符串

    Example:
        >>> replace_template_vars("Hello {name}!", {"name": "World"})
        'Hello World!'
    """
    result = template
    for key, value in replacements.items():
        result = result.replace(key, value)
    return result


def detect_project_name() -> str:
    """检测当前项目名称

    从当前工作目录的pyproject.toml或setup.py中检测项目名称。
    如果无法检测，返回当前目录名。

    Returns:
        项目名称
    """
    cwd = Path.cwd()

    # 尝试从pyproject.toml读取
    pyproject_file = cwd / "pyproject.toml"
    if pyproject_file.exists():
        content = pyproject_file.read_text(encoding="utf-8")
        for line in content.splitlines():
            if line.strip().startswith("name"):
                # name = "project-name"
                parts = line.split("=", 1)
                if len(parts) == 2:
                    name = parts[1].strip().strip('"').strip("'")
                    return name

    # 回退到目录名
    return cwd.name


def to_ascii_identifier(name: str) -> str:
    """将名称转换为合法的 ASCII 标识符

    用于处理中文 tag 等非 ASCII 字符的场景。

    转换策略：
    1. 纯 ASCII 字符串：直接返回 snake_case
    2. 包含中文：尝试使用 pypinyin 转换为拼音
    3. 无 pypinyin：生成基于内容的短标识符

    Args:
        name: 原始名称（可能包含中文）

    Returns:
        合法的 ASCII 标识符

    Example:
        >>> to_ascii_identifier("user-controller")
        'user_controller'
        >>> to_ascii_identifier("用户管理")  # 有 pypinyin
        'yong_hu_guan_li'
        >>> to_ascii_identifier("用户管理")  # 无 pypinyin
        'tag_a1b2c3'
    """
    # 检查是否为纯 ASCII
    if name.isascii():
        return to_snake_case(name)

    # 尝试使用 pypinyin 转换中文
    try:
        from pypinyin import lazy_pinyin

        # 转换为拼音列表
        pinyin_list = lazy_pinyin(name)
        # 过滤空字符串并连接
        result = "_".join(p for p in pinyin_list if p.strip())
        # 确保结果是合法标识符
        return to_snake_case(result) if result else _generate_tag_id(name)
    except ImportError:
        # 没有 pypinyin，生成基于内容的标识符
        return _generate_tag_id(name)


def _generate_tag_id(name: str) -> str:
    """生成基于内容的短标识符

    使用内容的哈希值生成一个简短的标识符。

    Args:
        name: 原始名称

    Returns:
        格式为 tag_xxxxxx 的标识符
    """
    import hashlib

    # 使用 MD5 的前 6 位作为标识符
    hash_value = hashlib.md5(name.encode("utf-8")).hexdigest()[:6]
    return f"tag_{hash_value}"


__all__ = [
    # 字符串转换
    "to_pascal_case",
    "to_snake_case",
    "to_ascii_identifier",
    # 文件操作
    "create_file",
    "create_file_with_merge",
    "replace_template_vars",
    # 项目检测
    "detect_project_name",
    # 增量合并 (v3.39.0+)
    "merge_with_markers",
    "generate_init_from_directory",
    # 分区标记常量 (v3.39.0+)
    "AUTO_GENERATED_START",
    "AUTO_GENERATED_END",
    "USER_EXTENSIONS_START",
    "AUTO_GENERATED_WARNING",
    "USER_EXTENSIONS_HINT",
]
