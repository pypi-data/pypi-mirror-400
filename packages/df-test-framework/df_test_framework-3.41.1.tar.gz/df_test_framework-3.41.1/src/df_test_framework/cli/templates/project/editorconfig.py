""".editorconfig 模板

统一团队成员的编辑器配置，确保代码风格一致。
支持几乎所有主流编辑器（VSCode、PyCharm、Sublime、Vim 等）。
"""

EDITORCONFIG_TEMPLATE = """# EditorConfig 配置
# 文档: https://editorconfig.org

# 根配置文件，停止向上查找
root = true

# 所有文件的默认配置
[*]
charset = utf-8                  # 文件编码
end_of_line = lf                 # 行尾符号（统一使用 LF）
insert_final_newline = true      # 文件末尾添加空行
trim_trailing_whitespace = true  # 去除行尾空格
indent_style = space             # 使用空格缩进
indent_size = 4                  # 缩进大小

# Python 文件
[*.py]
indent_size = 4
max_line_length = 100            # 与 Ruff 配置保持一致

# YAML 文件（配置文件）
[*.{yml,yaml}]
indent_size = 2

# JSON 文件
[*.json]
indent_size = 2

# Markdown 文件
[*.md]
trim_trailing_whitespace = false  # Markdown 中两个空格表示换行
max_line_length = off

# Shell 脚本
[*.sh]
indent_size = 2
end_of_line = lf                  # Shell 脚本必须使用 LF

# Makefile（必须使用 Tab）
[Makefile]
indent_style = tab

# TOML 配置文件
[*.toml]
indent_size = 2
"""

__all__ = ["EDITORCONFIG_TEMPLATE"]
