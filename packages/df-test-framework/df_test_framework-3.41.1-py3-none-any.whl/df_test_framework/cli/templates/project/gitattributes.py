""".gitattributes 模板

统一 Git 行为，避免跨平台协作时的问题（特别是行尾符号）。
确保 Python 项目在 Windows 上也使用 LF。
"""

GITATTRIBUTES_TEMPLATE = """# Git 属性配置
# 文档: https://git-scm.com/docs/gitattributes

# 自动检测文本文件并规范化行尾
* text=auto

# 源代码文件 - 强制使用 LF
*.py text eol=lf
*.sh text eol=lf
*.yml text eol=lf
*.yaml text eol=lf
*.json text eol=lf
*.toml text eol=lf
*.md text eol=lf
*.txt text eol=lf
*.sql text eol=lf

# 配置文件 - 强制使用 LF
.env* text eol=lf
.gitignore text eol=lf
.editorconfig text eol=lf
.gitattributes text eol=lf
*.cfg text eol=lf
*.ini text eol=lf

# 文档文件
*.rst text eol=lf
*.html text eol=lf
*.css text eol=lf
*.js text eol=lf

# Windows 批处理文件 - 强制使用 CRLF
*.bat text eol=crlf
*.cmd text eol=crlf
*.ps1 text eol=crlf

# 二进制文件 - 不进行任何转换
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.ico binary
*.pdf binary
*.zip binary
*.tar binary
*.gz binary
*.7z binary
*.db binary
*.sqlite binary
*.pkl binary
*.pickle binary

# Python 编译文件
*.pyc binary
*.pyo binary
*.pyd binary

# 导出时忽略（git archive）
.gitattributes export-ignore
.gitignore export-ignore
.editorconfig export-ignore
tests/ export-ignore
docs/ export-ignore
*.md export-ignore
"""

__all__ = ["GITATTRIBUTES_TEMPLATE"]
