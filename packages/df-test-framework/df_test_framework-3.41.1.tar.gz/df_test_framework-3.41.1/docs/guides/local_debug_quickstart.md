# 本地开发调试快速指南

> **版本**: v3.38.6
> **更新日期**: 2025-12-26
> **适用场景**: 使用 df-test-framework 的测试项目本地开发调试

---

## 快速开始

### 一分钟配置

```yaml
# config/environments/local.yaml
_extends: environments/dev.yaml
env: local
debug: true

logging:
  level: DEBUG
  format: text
  sanitize: false  # 本地可关闭脱敏

observability:
  debug_output: true

test:
  keep_test_data: true
```

```bash
# 运行测试
uv run pytest tests/ --env=local --log-cli-level=DEBUG -v
```

---

## 配置方式

### 方式 1：YAML 配置文件（推荐）

创建 `config/environments/local.yaml`：

```yaml
# 继承 dev 环境配置
_extends: environments/dev.yaml
env: local
debug: true

# 日志配置
logging:
  level: DEBUG        # DEBUG/INFO/WARNING/ERROR/CRITICAL
  format: text        # text（彩色）/ json / logfmt
  sanitize: false     # 本地开发关闭脱敏，方便查看完整数据

# HTTP 客户端配置
http:
  base_url: "http://localhost:8080"
  timeout: 120        # 调试时延长超时

# 可观测性
observability:
  debug_output: true  # 启用调试输出
  enable_tracing: false

# 测试配置
test:
  keep_test_data: true   # 保留测试数据便于调试
  screenshot_on_failure: true
```

### 方式 2：环境变量

```bash
# Windows PowerShell
$env:ENV = "local"
$env:LOGGING__LEVEL = "DEBUG"
$env:OBSERVABILITY__DEBUG_OUTPUT = "true"

# Windows CMD
set ENV=local
set LOGGING__LEVEL=DEBUG
set OBSERVABILITY__DEBUG_OUTPUT=true

# Linux/Mac
export ENV=local
export LOGGING__LEVEL=DEBUG
export OBSERVABILITY__DEBUG_OUTPUT=true
```

### 方式 3：pyproject.toml

```toml
[tool.pytest.ini_options]
# 实时日志显示
log_cli = true
log_cli_level = "DEBUG"

# 捕获日志（测试失败时显示）
log_level = "DEBUG"

# 默认参数
addopts = "-v --env=local"
```

---

## 常用命令

### 基本调试命令

```bash
# 使用 local 环境运行所有测试
uv run pytest tests/ --env=local -v

# 显示 DEBUG 日志
uv run pytest tests/ --env=local --log-cli-level=DEBUG -v

# 显示 print 输出（不捕获）
uv run pytest tests/ --env=local -v -s

# 组合使用
uv run pytest tests/ --env=local --log-cli-level=DEBUG -v -s
```

### 运行特定测试

```bash
# 运行单个文件
uv run pytest tests/api/test_user.py --env=local -v

# 运行单个测试类
uv run pytest tests/api/test_user.py::TestUserAPI --env=local -v

# 运行单个测试函数
uv run pytest tests/api/test_user.py::TestUserAPI::test_login --env=local -v

# 按关键词筛选
uv run pytest tests/ -k "login or register" --env=local -v
```

### 失败调试

```bash
# 首次失败即停止
uv run pytest tests/ --env=local -x -v

# 失败时进入 pdb 调试器
uv run pytest tests/ --env=local --pdb -v

# 失败时进入 pdb，并显示局部变量
uv run pytest tests/ --env=local --pdb -l -v

# 只运行上次失败的测试
uv run pytest tests/ --env=local --lf -v

# 先运行失败的测试
uv run pytest tests/ --env=local --ff -v
```

### 性能分析

```bash
# 显示最慢的 10 个测试
uv run pytest tests/ --env=local --durations=10 -v

# 显示所有测试耗时
uv run pytest tests/ --env=local --durations=0 -v
```

---

## 命令参数速查表

| 参数 | 作用 | 示例 |
|------|------|------|
| `--env=local` | 使用本地环境配置 | `--env=local` |
| `--log-cli-level=DEBUG` | 实时显示 DEBUG 日志 | `--log-cli-level=DEBUG` |
| `-v` / `-vv` | 详细输出 | `-vv` |
| `-s` | 显示 print 输出 | `-s` |
| `-x` | 首次失败即停止 | `-x` |
| `--pdb` | 失败时进入调试器 | `--pdb` |
| `-l` / `--showlocals` | 显示局部变量 | `-l` |
| `-k "关键词"` | 按名称筛选测试 | `-k "login"` |
| `--lf` | 只运行上次失败的 | `--lf` |
| `--ff` | 先运行失败的 | `--ff` |
| `--tb=short` | 简短错误追踪 | `--tb=short` |
| `--tb=long` | 详细错误追踪 | `--tb=long` |
| `--durations=N` | 显示最慢 N 个测试 | `--durations=10` |

---

## 调试模式

### 使用 @pytest.mark.debug

```python
import pytest

@pytest.mark.debug
def test_api(http_client):
    """标记为调试模式，自动输出请求/响应详情"""
    response = http_client.get("/users/1")
    assert response.status_code == 200
```

运行时需要 `-v -s`：

```bash
uv run pytest tests/test_example.py -v -s --env=local
```

### 使用 debug_mode fixture

```python
def test_with_debug(http_client, debug_mode):
    """debug_mode fixture 自动启用调试输出"""
    response = http_client.post("/orders", json={"product": "Phone"})
    # 终端会显示彩色的请求/响应详情
```

### 使用环境变量全局启用

```bash
# 全局启用调试输出
OBSERVABILITY__DEBUG_OUTPUT=true uv run pytest tests/ -v -s --env=local
```

---

## IDE 集成

### VS Code

创建 `.vscode/launch.json`：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Tests (Local)",
      "type": "debugpy",
      "request": "launch",
      "module": "pytest",
      "args": [
        "${file}",
        "--env=local",
        "--log-cli-level=DEBUG",
        "-v",
        "-s"
      ],
      "console": "integratedTerminal",
      "justMyCode": false,
      "env": {
        "ENV": "local",
        "OBSERVABILITY__DEBUG_OUTPUT": "true"
      }
    },
    {
      "name": "Debug Current Test",
      "type": "debugpy",
      "request": "launch",
      "module": "pytest",
      "args": [
        "${file}::${selectedText}",
        "--env=local",
        "-v",
        "-s"
      ],
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}
```

### PyCharm

1. **Edit Configurations** → **+** → **pytest**
2. 设置参数：
   - **Additional Arguments**: `--env=local --log-cli-level=DEBUG -v -s`
   - **Environment variables**: `ENV=local;OBSERVABILITY__DEBUG_OUTPUT=true`

---

## 日志级别说明

| 级别 | 使用场景 | 示例 |
|------|----------|------|
| `DEBUG` | 详细诊断信息 | SQL 查询、请求/响应体、变量值 |
| `INFO` | 关键操作确认 | 用户登录、订单创建、测试步骤 |
| `WARNING` | 警告但不影响运行 | 缓存未命中、重试操作 |
| `ERROR` | 错误但可恢复 | API 超时重试、连接失败 |
| `CRITICAL` | 严重错误 | 数据库连接失败、配置缺失 |

**推荐配置**：

```yaml
# 本地开发
logging:
  level: DEBUG

# CI 环境
logging:
  level: INFO

# 生产环境
logging:
  level: WARNING
```

---

## 常见问题

### Q1: 日志没有显示？

检查以下配置：

```toml
# pyproject.toml
[tool.pytest.ini_options]
log_cli = true           # 必须启用
log_cli_level = "DEBUG"  # 级别足够低
```

或使用命令行参数：

```bash
uv run pytest tests/ --log-cli-level=DEBUG -v
```

### Q2: 想看到完整的请求/响应体？

```bash
# 方式 1：环境变量
OBSERVABILITY__DEBUG_OUTPUT=true uv run pytest tests/ -v -s

# 方式 2：使用 @pytest.mark.debug
@pytest.mark.debug
def test_api(http_client):
    pass
```

### Q3: 如何在测试中打断点？

```python
def test_with_breakpoint(http_client):
    response = http_client.get("/users")

    # Python 3.7+ 内置断点
    breakpoint()

    # 或使用 pdb
    import pdb; pdb.set_trace()

    assert response.status_code == 200
```

然后运行：

```bash
uv run pytest tests/test_example.py -v -s --env=local
```

### Q4: 如何查看 SQL 查询？

```yaml
# config/environments/local.yaml
logging:
  level: DEBUG  # SQLAlchemy 会输出 SQL

# 或单独配置 SQLAlchemy 日志级别
# 在代码中：
# import logging
# logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)
```

### Q5: 调试时想保留测试数据？

```yaml
# config/environments/local.yaml
test:
  keep_test_data: true
```

或使用命令行：

```bash
uv run pytest tests/ --env=local --keep-test-data -v
```

---

## 推荐的本地开发工作流

```bash
# 1. 使用 local 环境开发
uv run pytest tests/api/test_user.py --env=local -v

# 2. 遇到问题，开启 DEBUG 日志
uv run pytest tests/api/test_user.py --env=local --log-cli-level=DEBUG -v -s

# 3. 需要断点调试
uv run pytest tests/api/test_user.py::test_login --env=local --pdb -v -s

# 4. 修复后，运行完整测试验证
uv run pytest tests/ --env=local -v

# 5. 切换到 CI 环境验证
uv run pytest tests/ --env=test -v
```

---

## 相关文档

- [环境配置指南](env_config_guide.md) - 完整的环境配置说明
- [日志配置指南](logging_configuration.md) - 日志系统详细配置
- [pytest 日志集成](logging_pytest_integration.md) - pytest 与 structlog 集成
- [调试工具指南](../user-guide/debugging.md) - HTTP/DB 调试工具
- [本地开发指南](../development/local-development.md) - 框架开发者指南

---

**文档版本**: v1.0.0
**最后更新**: 2025-12-26
