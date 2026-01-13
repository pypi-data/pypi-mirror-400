# 本地开发指南

本文档介绍如何在本地环境中开发和调试 df-test-framework，以及如何在测试项目中使用本地版本的框架。

**适用版本**: v3.38.6+
**更新时间**: 2025-12-26

> **测试项目开发者？** 如果你是使用框架的测试项目开发者，请先阅读 [本地开发调试快速指南](../guides/local_debug_quickstart.md)，了解如何配置 DEBUG 日志和调试模式。

---

## 📋 目录

- [框架开发模式](#框架开发模式)
- [在测试项目中使用本地框架](#在测试项目中使用本地框架)
- [开发工作流](#开发工作流)
- [常见问题](#常见问题)

---

## 🔧 框架开发模式

### 1. 环境准备

**系统要求**：
- Python 3.12+
- uv 包管理器（推荐）或 pip
- Git

**克隆仓库**：

```bash
git clone https://github.com/your-org/df-test-framework.git
cd df-test-framework
```

### 2. 安装开发依赖

#### 方式 A：使用 uv（推荐）

```bash
# 同步所有依赖（包含 dev 依赖组）
uv sync

# 或同步所有可选依赖
uv sync --all-extras
```

#### 方式 B：使用 pip

```bash
# 可编辑模式安装
pip install -e ".[dev]"

# 或安装所有可选依赖
pip install -e ".[dev,ui,mq,all]"
```

### 3. 验证安装

```bash
# 检查安装状态
uv pip list | grep df-test-framework

# 输出示例：
# df-test-framework  3.38.0  /path/to/df-test-framework
#                    ↑       ↑ 显示本地路径表示可编辑模式

# 验证 CLI 可用
df-test --help

# 运行测试
uv run pytest tests/ -v --ignore=tests/test_messengers/
```

### 4. 开发环境特点

✅ **可编辑模式优势**：
- 代码修改实时生效，无需重新安装
- 可以直接调试和测试修改
- 支持 IDE 跳转和代码补全

⚠️ **注意事项**：
- 修改 `pyproject.toml` 后需要重新同步：`uv sync`
- 添加新依赖后需要更新锁文件：`uv lock`

---

## 📦 在测试项目中使用本地框架

### 方式 1：修改项目依赖（推荐）

适用场景：在现有测试项目中验证框架新功能

#### 步骤 1：修改 `pyproject.toml`

在测试项目中修改框架依赖为本地路径：

```toml
[project]
name = "my-test-project"
dependencies = [
    "df-test-framework @ file:///D:/Git/DF/qa/test-framework",
    # Windows 路径格式：file:///D:/path/to/framework
    # Linux/Mac 路径格式：file:///home/user/path/to/framework
    "pytest>=9.0.0",
    "allure-pytest>=2.13.0",
]
```

#### 步骤 2：重新安装依赖

```bash
cd your-test-project
uv sync
```

#### 步骤 3：验证本地框架生效

```bash
# 检查框架安装路径
uv pip show df-test-framework

# 期望输出：
# Name: df-test-framework
# Version: 3.38.0
# Location: D:\Git\DF\qa\test-framework  ← 本地路径
```

#### 步骤 4：强制更新本地框架

使用 `file://` 路径时，uv/pip 会缓存已安装的包。修改框架代码后需要强制重新安装：

```bash
# 方法 1：强制重新安装指定包（推荐）
uv sync --reinstall-package df-test-framework

# 方法 2：直接使用 pip 安装本地路径
uv run pip install D:/Git/DF/qa/test-framework

# 方法 3：使用 --no-cache-dir 跳过缓存
uv pip install --no-cache-dir "df-test-framework @ file:///D:/Git/DF/qa/test-framework"

# 方法 4：清除 uv 缓存后重装
uv cache clean
uv sync
```

> 💡 **提示**：如果频繁修改框架代码，建议使用**可编辑模式**安装：
> ```bash
> uv pip install -e D:/Git/DF/qa/test-framework
> ```
> 可编辑模式下，代码修改立即生效，无需重新安装。

### 方式 2：使用环境变量（框架生成项目）

适用场景：使用 `df-test init` 生成新项目并自动使用本地框架

#### 设置环境变量

```bash
# Linux/Mac
export DF_TEST_LOCAL_DEV=1

# Windows CMD
set DF_TEST_LOCAL_DEV=1

# Windows PowerShell
$env:DF_TEST_LOCAL_DEV=1
```

#### 生成项目

```bash
# 生成的项目会自动使用本地路径依赖
df-test init my-new-project
cd my-new-project

# 查看生成的 pyproject.toml
cat pyproject.toml | grep df-test-framework
# 输出: "df-test-framework @ file://..",

# 安装依赖
uv sync
```

#### 环境变量说明

| 变量 | 值 | 效果 | 使用场景 |
|------|---|------|---------|
| `CI` | `true` | 使用本地路径 | CI/CD 环境自动检测 |
| `DF_TEST_LOCAL_DEV` | `1` | 使用本地路径 | 本地开发测试 |
| 未设置 | - | 使用 PyPI 版本 | 正常使用（生产环境） |

详见：[框架依赖管理策略](./FRAMEWORK_DEPENDENCY_MANAGEMENT.md)

---

## 🚀 开发工作流

### 典型开发流程

```bash
# 1. 在框架项目中开发新功能
cd /path/to/df-test-framework

# 编辑代码
vim src/df_test_framework/capabilities/clients/http/client.py

# 2. 运行框架自身测试
uv run pytest tests/capabilities/clients/http/ -v

# 3. 在测试项目中验证
cd /path/to/your-test-project

# 直接运行测试（自动使用本地框架代码）
pytest tests/ -v

# 4. 如果一切正常，提交代码
cd /path/to/df-test-framework
git add .
git commit -m "feat(http): 添加新功能"
```

### 调试技巧

#### 1. 使用 IDE 调试

VS Code 配置示例 (`.vscode/launch.json`)：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Tests",
      "type": "debugpy",
      "request": "launch",
      "module": "pytest",
      "args": [
        "tests/capabilities/clients/http/test_client.py",
        "-v",
        "-s"
      ],
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}
```

#### 2. 使用调试输出

```python
# 方式 1：使用 debug_mode fixture（便捷方式）
def test_http_client(http_client, debug_mode):
    response = http_client.get("/api/users")
    # 控制台会输出彩色的请求/响应详情

# 方式 2：使用 console_debugger fixture（可自定义配置）
def test_with_custom_debug(http_client, console_debugger):
    console_debugger.show_headers = False  # 不显示 headers
    console_debugger.max_body_length = 1000  # 增大 body 长度
    response = http_client.get("/api/users")

# 方式 3：使用 @pytest.mark.debug marker
@pytest.mark.debug
def test_problematic_feature(http_client):
    # 自动启用调试输出
    pass

# 方式 4：环境变量全局启用
# OBSERVABILITY__DEBUG_OUTPUT=true pytest tests/ -v -s
```

> **注意**：调试输出需要 `-s` 参数才能实时显示彩色输出。

#### 3. 实时日志

```bash
# 运行测试时显示实时日志
pytest tests/ -v -s --log-cli-level=DEBUG

# 使用 local 环境配置（包含 DEBUG 日志设置）
pytest tests/ --env=local --log-cli-level=DEBUG -v -s
```

> 详细的日志和调试配置请参考 [本地开发调试快速指南](../guides/local_debug_quickstart.md)

### 代码质量检查

```bash
# 运行 Ruff 检查
uv run ruff check src/ tests/ --fix

# 格式化代码
uv run ruff format src/ tests/

# 类型检查（可选）
uv run mypy src/
```

---

## 🔄 切换版本

### 切换回 PyPI 版本

当不再需要本地框架时，切换回 PyPI 版本：

```bash
# 方法 1：修改 pyproject.toml
# 将 file://... 改为版本号
dependencies = [
    "df-test-framework>=3.38.0",  # 使用 PyPI 版本
]

# 重新安装
uv sync --reinstall-package df-test-framework

# 方法 2：直接卸载并重装
uv pip uninstall df-test-framework
uv pip install df-test-framework>=3.38.0
```

### 验证版本切换

```bash
uv pip show df-test-framework

# PyPI 版本输出：
# Location: /path/to/.venv/lib/python3.12/site-packages

# 本地版本输出：
# Location: /path/to/df-test-framework
```

---

## 🛠️ 常见问题

### Q1: 修改代码后没有生效

**原因**：可能使用的是 PyPI 版本而不是本地版本

**解决**：
```bash
# 检查当前使用的版本
uv pip show df-test-framework

# 如果 Location 不是本地路径，重新安装
cd /path/to/df-test-framework
uv pip install -e .
```

### Q2: 导入错误或模块找不到

**原因**：可能是依赖未同步或缓存问题

**解决**：
```bash
# 清除缓存并重新同步
uv cache clean
uv sync --reinstall

# 或使用 pip
pip install -e . --force-reinstall --no-cache-dir
```

### Q3: pytest 找不到测试

**原因**：可能是项目结构或配置问题

**解决**：
```bash
# 检查 pytest 配置
cat pyproject.toml | grep -A 10 "\[tool.pytest\]"

# 验证 Python 路径
uv run python -c "import sys; print(sys.path)"

# 指定测试路径
pytest -v tests/
```

### Q4: CI 环境如何使用本地框架

**解决**：CI 环境会自动检测 `CI=true` 环境变量并使用本地路径

GitHub Actions 示例：
```yaml
- name: 测试框架
  run: |
    cd df-test-framework
    uv run pytest tests/ -v

- name: 生成测试项目
  run: |
    # CI=true 自动设置，框架会使用 file://.. 依赖
    uv run df-test init test-project
    cd test-project
    uv sync
    pytest tests/ -v
```

详见：[CI/CD 配置指南](../user-guide/ci-cd.md)

### Q5: 如何在多个测试项目间共享本地框架

**推荐方案**：使用软链接或统一的路径引用

```toml
# 项目 A
dependencies = ["df-test-framework @ file:///D:/workspace/df-test-framework"]

# 项目 B
dependencies = ["df-test-framework @ file:///D:/workspace/df-test-framework"]
```

所有项目都指向同一个本地框架路径，修改框架代码后所有项目自动生效。

---

## 📚 相关文档

- [本地开发调试快速指南](../guides/local_debug_quickstart.md) - DEBUG 日志和调试配置
- [安装指南](../getting-started/installation.md)
- [框架依赖管理策略](./FRAMEWORK_DEPENDENCY_MANAGEMENT.md)
- [发布流程](./RELEASE.md)
- [贡献指南](../../CONTRIBUTING.md)
- [调试工具指南](../user-guide/debugging.md) - HTTP/DB 调试工具

---

## 🤝 贡献

如果你在本地开发过程中遇到问题或有改进建议，欢迎：

1. 提交 Issue: https://github.com/your-org/df-test-framework/issues
2. 提交 PR: https://github.com/your-org/df-test-framework/pulls
3. 参与讨论: https://github.com/your-org/df-test-framework/discussions

---

**文档版本**: v1.1.0
**最后更新**: 2025-12-26
**维护者**: 框架核心团队
