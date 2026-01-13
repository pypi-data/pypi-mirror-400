# 安装指南

本文档将指导您安装和配置 DF Test Framework v3.38.0。

## 📋 系统要求

- **Python**：3.12+（推荐 3.12+）
- **操作系统**：Windows / Linux / macOS
- **包管理器**：`uv`（推荐）或 `pip`
- **可选组件**：Allure、Playwright、数据库客户端等

## 🔧 安装步骤

### 方式 1：使用 uv（推荐）

```bash
# 安装 uv（如果尚未安装）
pip install uv

# 安装框架核心
uv pip install df-test-framework
```

### 方式 2：使用 pip

```bash
pip install df-test-framework
```

### 开发模式安装（本地调试）

#### 方式 1：框架自身开发（可编辑模式）

适用场景：贡献框架代码、调试框架问题、开发新功能

```bash
# 克隆仓库
git clone https://github.com/your-org/df-test-framework.git
cd df-test-framework

# 同步依赖（推荐 - 包含 dev 依赖组）
uv sync

# 或使用 pip 可编辑模式
uv pip install -e ".[dev]"
```

**验证开发模式安装**：

```bash
uv pip list | grep df-test-framework
# 输出: df-test-framework  3.38.0  /path/to/df-test-framework
#       ^^^^^^^^^^^^^^^^^^^^^^^^  ↑ 显示本地路径表示可编辑模式
```

✅ **开发模式特点**：
- 代码修改实时生效，无需重新安装
- 可以直接运行测试验证修改
- 适合框架本身的开发和调试

#### 方式 2：在测试项目中使用本地框架

适用场景：验证框架新功能、在实际项目中测试框架改动

**步骤 1：修改测试项目依赖**

在你的测试项目 `pyproject.toml` 中指定本地路径：

```toml
[project]
dependencies = [
    "df-test-framework @ file:///D:/Git/DF/qa/test-framework",
    # Windows: file:///D:/path/to/framework
    # Linux/Mac: file:///home/user/path/to/framework
    "pytest>=9.0.0",
    "allure-pytest>=2.13.0",
    # 其他依赖...
]
```

**步骤 2：安装依赖**

```bash
cd your-test-project
uv sync
```

**步骤 3：验证本地框架生效**

```bash
# 检查安装路径
uv pip show df-test-framework

# 输出应显示：
# Name: df-test-framework
# Version: 3.38.0
# Location: /path/to/df-test-framework  ← 本地路径
```

**开发工作流示例**：

```bash
# 1. 修改框架代码
cd /path/to/df-test-framework
# 编辑 src/df_test_framework/...

# 2. 运行框架自身测试
uv run pytest tests/ -v

# 3. 在测试项目中验证
cd /path/to/your-test-project
pytest tests/ -v  # 自动使用本地框架（无需重新安装）
```

**强制更新本地框架**：

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

#### 方式 3：使用环境变量（框架生成项目）

适用场景：使用 `df-test init` 生成新项目并自动使用本地框架

```bash
# 设置环境变量
export DF_TEST_LOCAL_DEV=1  # Linux/Mac
set DF_TEST_LOCAL_DEV=1     # Windows CMD
$env:DF_TEST_LOCAL_DEV=1    # Windows PowerShell

# 生成项目（自动使用本地路径依赖）
df-test init my-project
cd my-project

# 安装依赖（已配置 file://.. 路径）
uv sync
```

**环境变量说明**：

| 变量 | 值 | 效果 | 使用场景 |
|------|---|------|---------|
| `CI` | `true` | 使用本地路径 | CI/CD 环境 |
| `DF_TEST_LOCAL_DEV` | `1` | 使用本地路径 | 本地开发测试 |
| 未设置 | - | 使用 PyPI 版本 | 正常使用 |

详见：[框架依赖管理策略](../development/FRAMEWORK_DEPENDENCY_MANAGEMENT.md)

#### 切换回 PyPI 版本

如果不再需要使用本地框架，可以切换回 PyPI 版本：

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

## ✅ 验证安装

```python
import df_test_framework as df
print(df.__version__)
# 期望输出: 3.38.0
```

或使用命令行：

```bash
python -c "import df_test_framework; print(df_test_framework.__version__)"
```

验证 CLI 是否可用：

```bash
df-test --help
```

## 📦 依赖说明

核心依赖：
- `httpx` — 现代 HTTP 客户端
- `pydantic` / `pydantic-settings` — 类型安全配置体系
- `sqlalchemy` — 数据库访问与连接池
- `redis` — Redis 客户端
- `loguru` — 结构化日志
- `pluggy` — 扩展与 Hook 系统
- `pytest` — 测试运行器

可选依赖（按需安装）：

```bash
# Allure 报告支持
uv pip install df-test-framework[allure]

# UI 测试（Playwright）支持
uv pip install df-test-framework[ui]

# 一次性安装全部扩展
uv pip install df-test-framework[all]
```

Playwright 首次安装后需要下载浏览器内核：

```bash
playwright install
```

## 🐛 常见问题

### ImportError

检查：
1. Python 版本 ≥ 3.10。
2. 虚拟环境已激活。
3. `pip list` 或 `uv pip list` 中存在 `df-test-framework` 及依赖。
4. 若使用 VS Code / PyCharm，确保解释器指向正确的虚拟环境。

### 依赖冲突

建议始终使用虚拟环境：

```bash
# 使用 venv
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows

# 或使用 uv
uv venv
source .venv/bin/activate
```

## 🎯 下一步

- [快速入门](quickstart.md) — 使用 `df-test init` 生成项目骨架
- [30 分钟教程](tutorial.md) — 编写第一个 API 测试
- [快速参考](../user-guide/QUICK_REFERENCE.md) — Fixtures、调试、常用命令

---

返回：[快速开始目录](README.md) | [文档首页](../README.md)
