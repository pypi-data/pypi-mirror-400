"""VSCode 工作区配置模板

为团队提供统一的 VSCode 配置，包括：
- Python 解释器和路径配置
- 测试框架配置（pytest）
- 代码格式化工具（Ruff）
- 类型检查工具（Mypy）
"""

VSCODE_SETTINGS_TEMPLATE = """{
  // Python 配置
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.autoImportCompletions": true,

  // 测试配置
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": [
    "tests",
    "-v"
  ],

  // 格式化配置（使用 Ruff）
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit",
      "source.fixAll": "explicit"
    }
  },

  // Ruff 配置
  "ruff.enable": true,
  "ruff.lint.run": "onType",
  "ruff.organizeImports": true,

  // 编辑器配置
  "editor.rulers": [100],
  "editor.tabSize": 4,
  "editor.insertSpaces": true,
  "editor.trimAutoWhitespace": true,
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "files.encoding": "utf8",
  "files.eol": "\\n",

  // 文件排除（不在侧边栏显示）
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true,
    "**/.ruff_cache": true,
    "**/.mypy_cache": true,
    "**/*.egg-info": true
  },

  // 搜索排除
  "search.exclude": {
    "**/.venv": true,
    "**/node_modules": true,
    "**/.pytest_cache": true,
    "**/.ruff_cache": true,
    "**/.mypy_cache": true,
    "**/reports": true
  },

  // 终端配置
  "terminal.integrated.env.linux": {
    "PYTHONPATH": "${workspaceFolder}/src:${env:PYTHONPATH}"
  },
  "terminal.integrated.env.osx": {
    "PYTHONPATH": "${workspaceFolder}/src:${env:PYTHONPATH}"
  },
  "terminal.integrated.env.windows": {
    "PYTHONPATH": "${workspaceFolder}/src;${env:PYTHONPATH}"
  }
}
"""

VSCODE_EXTENSIONS_TEMPLATE = """{
  "recommendations": [
    // Python 核心
    "ms-python.python",
    "ms-python.vscode-pylance",

    // 代码质量
    "charliermarsh.ruff",

    // 测试
    "littlefoxteam.vscode-python-test-adapter",

    // YAML 支持
    "redhat.vscode-yaml",

    // EditorConfig 支持
    "editorconfig.editorconfig",

    // Git 增强
    "eamodio.gitlens",

    // Markdown 支持
    "yzhang.markdown-all-in-one"
  ]
}
"""

__all__ = ["VSCODE_SETTINGS_TEMPLATE", "VSCODE_EXTENSIONS_TEMPLATE"]
