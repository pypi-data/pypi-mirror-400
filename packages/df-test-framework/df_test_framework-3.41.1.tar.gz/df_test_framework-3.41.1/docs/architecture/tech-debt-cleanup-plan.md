# 技术债务清理计划

**版本**: v3.36.0
**日期**: 2025-12-20
**状态**: 进行中

---

## 0. 已完成的清理 (v3.35.8)

### ✅ 废弃模块删除

| 清理项 | 状态 |
|--------|------|
| 删除 `testing/factories/` 目录 | ✅ 已删除 |
| 删除 `TestPriority` 别名 | ✅ 已删除 |
| 删除 `TestType` 别名 | ✅ 已删除 |
| 更新测试导入路径 | ✅ 已更新 |
| 修复版本号 3.35.5 → 3.35.7 | ✅ 已修复 |

**迁移说明**：
- `from df_test_framework.testing.factories import ...` → `from df_test_framework.testing.data.factories import ...`
- `TestPriority` → `Priority`
- `TestType` → `CaseType`

---

## 1. 概述

基于当前框架状态分析，识别出以下技术债务需要清理：

| 债务类型 | 严重程度 | 优先级 | 预计工作量 |
|----------|----------|--------|-----------|
| 测试覆盖率不足 | 🔴 高 | P0 | 5-7天 |
| 版本号不一致 | 🟡 中 | P1 | 10分钟 |
| 废弃别名清理 | 🟡 中 | P2 | 1天 |
| 性能基准测试缺失 | 🟢 低 | P3 | 2天 |

---

## 2. P0: 测试覆盖率提升

### 2.1 目标

- **当前覆盖率**: 55.71%
- **目标覆盖率**: 80%
- **需要覆盖的代码行**: ~3,800 行

### 2.2 分阶段计划

#### 阶段 1: 删除或排除废弃模块 (Day 1)

以下模块是废弃的兼容层，可以从覆盖率统计中排除：

```python
# pyproject.toml 添加排除配置
[tool.coverage.run]
omit = [
    "src/df_test_framework/testing/factories/base.py",
    "src/df_test_framework/testing/factories/presets.py",
]
```

**预期提升**: +2-3%

#### 阶段 2: 补充核心模块测试 (Day 2-3)

| 模块 | 当前覆盖率 | 目标 | 优先级 |
|------|-----------|------|--------|
| `testing/debugging/console.py` | 15.0% | 70% | 高 |
| `testing/reporting/allure/observer.py` | 23.7% | 70% | 高 |
| `testing/fixtures/core.py` | 35.4% | 70% | 高 |
| `testing/fixtures/cleanup.py` | 63.3% | 80% | 中 |

**测试策略**:
1. ConsoleDebugObserver - Mock EventBus，测试各类事件处理
2. AllureObserver - Mock Allure API，测试事件到报告的转换
3. Fixtures - 使用 pytest 的 pytester fixture 测试

**预期提升**: +10-12%

#### 阶段 3: 补充基础设施测试 (Day 4-5)

| 模块 | 当前覆盖率 | 目标 |
|------|-----------|------|
| `infrastructure/tracing/interceptors/http.py` | 29.4% | 70% |
| `infrastructure/telemetry/facade.py` | 24.1% | 60% |
| `infrastructure/context/carriers/*` | 25-26% | 60% |

**预期提升**: +5-7%

#### 阶段 4: CLI 和插件测试 (Day 6-7)

| 模块 | 当前覆盖率 | 目标 |
|------|-----------|------|
| `cli/commands/env.py` | 4.5% | 60% |
| `cli/commands/interactive.py` | 5.1% | 40% |
| `testing/plugins/env_plugin.py` | 0% | 60% |
| `testing/plugins/api_autodiscovery.py` | 0% | 60% |

**预期提升**: +5-8%

### 2.3 预期结果

完成所有阶段后：
- 预期覆盖率: 78-82%
- 新增测试: ~150-200 个

---

## 3. P1: 版本号修复

### 3.1 问题

```
pyproject.toml:   version = "3.35.7"
__init__.py:      __version__ = "3.35.5"  # 不一致
```

### 3.2 修复

更新 `src/df_test_framework/__init__.py`:
```python
__version__ = "3.35.7"
```

---

## 4. P2: 废弃别名文档化

### 4.1 当前废弃项

| 废弃项 | 替代项 | 计划移除版本 |
|--------|--------|-------------|
| `TestPriority` | `Priority` | v4.0.0 |
| `TestType` | `CaseType` | v4.0.0 |
| `testing.factories` 模块 | `testing.data.factories` | v4.0.0 |
| `fake()` 函数 | `FakerAttribute` | v4.0.0 |

### 4.2 行动项

1. 在 CHANGELOG.md 中明确标注废弃时间线
2. 更新迁移指南文档
3. 在 v4.0.0 发布前创建迁移脚本（可选）

---

## 5. P3: 性能基准测试

### 5.1 目标

建立性能回归检测机制，确保核心模块性能不退化。

### 5.2 实施计划

#### 5.2.1 添加性能标记

```python
# tests/performance/test_http_client_perf.py
import pytest

@pytest.mark.performance
@pytest.mark.slow
class TestHttpClientPerformance:
    def test_sync_request_latency(self, http_client):
        """同步请求延迟 < 100ms"""
        ...

    def test_async_request_throughput(self, async_http_client):
        """异步请求吞吐量 > 100 req/s"""
        ...
```

#### 5.2.2 基准测试模块

```
tests/performance/
├── conftest.py           # 性能测试 fixtures
├── test_http_client.py   # HTTP 客户端性能
├── test_database.py      # 数据库操作性能
├── test_middleware.py    # 中间件链性能
└── test_event_bus.py     # 事件发布性能
```

#### 5.2.3 CI 集成

```yaml
# .github/workflows/performance.yml
name: Performance Tests
on:
  push:
    branches: [main, master]
jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - run: uv run pytest -m performance --benchmark-json=benchmark.json
      - uses: benchmark-action/github-action-benchmark@v1
```

---

## 6. 实施时间线

```
Week 1 (v3.36.0):
├── Day 1: P1 版本号修复 + 阶段1 废弃模块排除
├── Day 2-3: 阶段2 核心模块测试
├── Day 4-5: 阶段3 基础设施测试
├── Day 6-7: 阶段4 CLI/插件测试
└── 发布 v3.36.0

Week 2 (v3.37.0):
├── P2 废弃别名文档化
├── P3 性能基准测试框架
└── 发布 v3.37.0
```

---

## 7. 成功指标

| 指标 | 当前值 | 目标值 | 验收标准 |
|------|--------|--------|---------|
| 测试覆盖率 | 55.71% | ≥80% | CI 强制检查 |
| 0% 覆盖模块 | 7个 | 0个 | 全部 ≥40% |
| 版本号一致 | ❌ | ✅ | 自动化检查 |
| 性能基准 | 无 | 有 | 5个核心模块 |

---

## 8. 风险和缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|---------|
| 测试编写耗时超预期 | 中 | 中 | 优先覆盖核心模块 |
| 废弃模块有外部依赖 | 低 | 高 | 提供迁移脚本 |
| 性能测试环境不稳定 | 中 | 低 | 使用相对基准 |

---

## 9. 附录：覆盖率最低的 30 个模块

```
  0.0% cli/__main__.py
  0.0% testing/factories/base.py         # 废弃
  0.0% testing/factories/presets.py      # 废弃
  0.0% testing/fixtures/message_queue.py
  0.0% testing/fixtures/monitoring.py
  0.0% testing/plugins/api_autodiscovery.py
  0.0% testing/plugins/env_plugin.py
  4.5% cli/commands/env.py
  5.1% cli/commands/interactive.py
  6.2% plugins/builtin/reporting/allure_plugin.py
  6.6% cli/generators/openapi_generator.py
  6.9% capabilities/messengers/queue/rocketmq/client.py
 10.1% capabilities/messengers/queue/kafka/client.py
 11.2% infrastructure/metrics/decorators.py
 12.5% cli/commands/cicd.py
 14.1% capabilities/databases/query_builder.py
 15.0% testing/debugging/console.py
 16.7% cli/generators/openapi_parser.py
 17.0% capabilities/clients/graphql/middleware/logging.py
 17.2% capabilities/messengers/queue/rabbitmq/client.py
 18.8% testing/fixtures/metrics.py
 20.4% capabilities/clients/graphql/middleware/retry.py
 23.0% testing/fixtures/debugging.py
 23.7% testing/reporting/allure/observer.py
 24.1% infrastructure/telemetry/facade.py
 25.4% capabilities/clients/http/middleware/telemetry.py
 25.8% infrastructure/context/carriers/grpc.py
 26.2% infrastructure/context/carriers/mq.py
 27.4% testing/plugins/debug.py
 28.4% infrastructure/metrics/performance.py
```
