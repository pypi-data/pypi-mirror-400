# DF Test Framework v3.29+ 功能增强路线图

> **版本**: v3.35.0+
> **创建日期**: 2025-12-16
> **最后更新**: 2025-12-18
> **状态**: ✅ v3.35.0 环境管理已完成

## ✅ v3.34.1 实施记录（2025-12-17）

**MQ 事件架构重构（Bug Fix）**:

### 问题发现

分析 v3.14.0 的 MQ 事件实现时发现严重架构问题：
- 事件定义字段（`message_id`, `body_size`）从未被正确填充
- MQ 客户端传递的参数（`queue_type`, `message`）与事件定义不匹配
- 缺少 Start/End/Error 三态模式，无法进行完整的请求追踪
- MQ 事件继承 `Event` 而非 `CorrelatedEvent`，缺少关联追踪能力

### 重构内容

1. **MQ 事件类型重构** (`core/events/types.py`)
   - 删除 `MessagePublishEvent` 和 `MessageConsumeEvent`
   - 新增 6 个事件类型，统一为 Start/End/Error 三态模式：
     - `MessagePublishStartEvent` - 发布开始
     - `MessagePublishEndEvent` - 发布成功
     - `MessagePublishErrorEvent` - 发布失败
     - `MessageConsumeStartEvent` - 消费开始
     - `MessageConsumeEndEvent` - 消费成功
     - `MessageConsumeErrorEvent` - 消费失败
   - 所有事件继承 `CorrelatedEvent`，支持 `correlation_id` 关联
   - 添加工厂方法 `create()` 自动注入 OpenTelemetry 追踪上下文
   - 新增 `messenger_type` 字段区分 kafka/rabbitmq/rocketmq

2. **MQ 客户端更新**
   - `KafkaClient`: 重构 `send()` 和 `consume()` 方法
   - `RabbitMQClient`: 重构 `publish()` 和 `consume()` 方法
   - `RocketMQClient`: 重构 `send()` 和 `subscribe()` 方法

3. **观察者更新**
   - `AllureObserver`: 新增 `handle_message_publish_end_event` 等 4 个方法
   - `AllurePlugin`: 订阅新的事件类型
   - `ConsoleDebugObserver`: 显示 `messenger_type` 和耗时信息

4. **Fixture 更新**
   - `testing/fixtures/allure.py`: 更新事件订阅

### 设计决策

- **与 HTTP/gRPC/GraphQL 架构统一**：所有通信类事件使用 Start/End/Error 三态模式
- **完整追踪能力**：通过 `correlation_id` 关联同一操作的所有事件
- **破坏性变更**：删除旧事件类型，不提供向后兼容（此为修复架构缺陷）

---

## ✅ v3.34.0 实施记录（2025-12-17）

**ConsoleDebugObserver MQ 事件支持已完成**:

### 背景分析

对 MQ（消息队列）客户端是否需要中间件系统进行了分析：
- HTTP/gRPC/GraphQL 使用请求/响应模式 → 适合中间件（洋葱模型）
- MQ 使用发布/订阅模式 → 不适合中间件
- MQ 客户端已有 EventBus 集成（v3.14.0），发布 `MessagePublishEvent` 和 `MessageConsumeEvent`

### 发现问题

- AllureObserver: ✅ 已支持 MQ 事件
- AllurePlugin: ✅ 已支持 MQ 事件
- ConsoleDebugObserver: ❌ 缺少 MQ 事件支持

### 实现内容

1. **MQMessageRecord 数据类** (`testing/debugging/console.py`)
   - topic、message_id、body_size、partition
   - consumer_group、offset（仅消费事件）
   - timestamp

2. **ConsoleDebugObserver MQ 支持**
   - `show_mq` 参数（默认 True）
   - `_handle_mq_publish()` - 处理消息发布事件
   - `_handle_mq_consume()` - 处理消息消费事件
   - `_print_mq_publish()` - 打印发布信息（📤 青色）
   - `_print_mq_consume()` - 打印消费信息（📥 黄色）

3. **create_console_debugger 函数**
   - 新增 `show_mq` 参数

### 设计决策

- **不为 MQ 添加中间件系统**：MQ 是发布/订阅模式，与请求/响应的中间件模式不匹配
- **复用现有事件**：使用 v3.14.0 已定义的 `MessagePublishEvent` 和 `MessageConsumeEvent`
- **统一调试体验**：ConsoleDebugObserver 现在支持 HTTP/DB/gRPC/GraphQL/MQ 全部五种调试

---

## ✅ v3.33.0 实施记录（2025-12-17）

**GraphQL 中间件系统已完成**:

### 实现内容

1. **GraphQL 中间件基类** (`capabilities/clients/graphql/middleware/base.py`)
   - `GraphQLMiddleware` - 继承自 `BaseMiddleware[GraphQLRequest, GraphQLResponse]`
   - 复用 core/middleware 的洋葱模型

2. **内置中间件** (`capabilities/clients/graphql/middleware/`)
   - `GraphQLLoggingMiddleware` - 日志记录（priority=0）
   - `GraphQLRetryMiddleware` - 重试逻辑（priority=10）
   - `GraphQLEventPublisherMiddleware` - 事件发布（priority=999，最内层）

3. **GraphQL 事件类型** (`core/events/types.py`)
   - `GraphQLRequestStartEvent` - 请求开始事件
   - `GraphQLRequestEndEvent` - 请求结束事件
   - `GraphQLRequestErrorEvent` - 请求错误事件

4. **GraphQLClient 重构** (`capabilities/clients/graphql/client.py`)
   - 支持 `middlewares=[]` 构造参数
   - 支持 `.use(middleware)` 链式调用
   - 自动添加 `GraphQLEventPublisherMiddleware`

5. **观察者支持**
   - AllureObserver: 新增 `handle_graphql_request_*_event` 方法
   - ConsoleDebugObserver: 新增 GraphQL 调试支持（`show_graphql` 选项）

### 设计决策

- **不复用 HttpClient**：GraphQL 使用独立的中间件系统，与 gRPC 保持一致
- **命名一致性**：使用 `Middleware` 而非 `Extension`，与 HTTP/gRPC 统一
- **洋葱模型**：EventPublisher 在最内层（priority=999），能记录完整请求信息

### 测试结果
- 核心测试全部通过：56 passed
- 导入验证成功

---

## ✅ v3.32.0 实施记录（2025-12-17）

**gRPC 事件系统统一已完成**:

### 实现内容

1. **gRPC 事件类型** (`core/events/types.py`)
   - `GrpcRequestStartEvent` - 请求开始事件
   - `GrpcRequestEndEvent` - 请求结束事件
   - `GrpcRequestErrorEvent` - 请求错误事件

2. **EventPublisherInterceptor** (`capabilities/clients/grpc/interceptors.py`)
   - 自动发布事件到 EventBus
   - 支持 correlation_id 关联
   - 可配置数据记录和截断

3. **GrpcClient 增强** (`capabilities/clients/grpc/client.py`)
   - 新增 `enable_events` 参数（默认 True）
   - 新增 `service_name` 参数
   - 自动添加 EventPublisherInterceptor

4. **Allure 报告集成** (`plugins/builtin/reporting/allure_plugin.py`)
   - gRPC 调用自动记录到 Allure 步骤
   - 显示服务名、方法名、状态码、耗时

5. **控制台调试支持** (`testing/debugging/console.py`)
   - 新增 `GrpcCallRecord` 数据类
   - 实时显示 gRPC 请求/响应/错误

### 测试结果
- 新增 13 个 gRPC 事件相关测试
- 全部测试通过：1489 passed, 40 skipped

---

## ✅ v3.31.0 实施记录（2025-12-16）

**Factory 系统重构已完成**:

### 问题背景
发现两套 Factory 系统重复实现：
- `testing/factories/` (v3.5.0 + v3.10.0) - 声明式元类设计
- `testing/data/factories/` (v3.29.0) - 类方法设计

### 解决方案
采用**方案 B**：合并到 `testing/data/factories/`，融合 factory_boy 和 polyfactory 最佳实践。

### 新 Factory 特性
- ✅ **Sequence** - 自增序列（从 factory_boy）
- ✅ **LazyAttribute** - 延迟计算（从 factory_boy）
- ✅ **PostGenerated** - 后处理字段（从 polyfactory）
- ✅ **Trait** - 预设配置组合（从 factory_boy）
- ✅ **SubFactory** - 嵌套工厂（从 factory_boy）
- ✅ **Use** - 延迟执行包装器
- ✅ **FakerAttribute** - Faker 集成
- ✅ **泛型支持** - `Factory[T]`（从 polyfactory）
- ✅ **Pydantic 原生支持**

### 迁移说明
```python
# 旧路径（已废弃，将在 v4.0.0 移除）
from df_test_framework.testing.factories import UserFactory

# 新路径（推荐）
from df_test_framework.testing.data.factories import UserFactory
```

### API 变更
```python
# 新 API 示例
user = UserFactory.build()                    # 构建单个
users = UserFactory.build_batch(10)           # 批量构建
admin = UserFactory.build(admin=True)         # 使用 Trait
order = OrderFactory.build(paid=True)         # 订单预设
```

### 预置工厂（8 个）
- UserFactory（含 vip/admin/inactive Traits）
- ProductFactory（含 out_of_stock/off_sale Traits）
- OrderFactory（含 paid/shipped/completed/cancelled Traits）
- AddressFactory（含 default Trait）
- PaymentFactory（含 success/failed/refunded Traits）
- CardFactory（含 active/used/expired Traits）
- ApiResponseFactory（含 error/not_found Traits）
- PaginationFactory

### 参考来源
- [factory_boy](https://factoryboy.readthedocs.io/) - Sequence、LazyAttribute、Trait
- [polyfactory](https://polyfactory.litestar.dev/) - 泛型支持、PostGenerated

---

## ✅ v3.30.0 实施记录（2025-12-16）

**断言增强已完成**:
- ✅ 添加 `jsonpath-ng` 到依赖
- ✅ `ResponseAssertions` 已存在（v3.10.0 已实现）
- ✅ `SchemaValidator` 独立验证器类
- ✅ `SchemaValidationError` 详细错误
- ✅ `create_object_schema()` / `create_array_schema()` 构建器
- ✅ `COMMON_SCHEMAS` 预定义 Schema
- ✅ 自定义匹配器（15+ 匹配器类）
- ✅ 匹配器操作符重载（&, |, ~）
- ✅ 预定义匹配器实例（is_none, is_string 等）
- ✅ 单元测试 85 个全部通过

**测试结果**: 1472 passed, 40 skipped, 33 warnings

---

## ✅ v3.29.0 实施记录（2025-12-16）

**Phase 1 已完成**:
- ✅ DataGenerator → testing/data/generators/
- ✅ AssertHelper → testing/assertions/
- ✅ CircuitBreaker → infrastructure/resilience/
- ✅ 装饰器 → core/decorators.py
- ✅ 类型 → core/types.py（含 DecimalAsFloat/DecimalAsCurrency）
- ✅ Factory 基类 → testing/data/factories/（使用类方法设计）
- ✅ utils/__init__.py 向后兼容 + DeprecationWarning

**Phase 2 已完成**:
- ✅ performance.py → infrastructure/metrics/performance.py
- ✅ common.py 废弃警告（random_*, load_json, load_excel）
- ✅ 具体 Factory 实现（UserFactory/OrderFactory/ProductFactory/AddressFactory）
- ✅ Factory 单元测试（33 个测试全部通过）

**测试结果**: 1387 passed, 40 skipped, 33 warnings

**设计变更**:
- Factory 采用类方法设计（`UserFactory.create()`）而非实例方法（更简洁，符合 factory_boy 模式）
- Loaders 已存在，无需新增（JSONLoader/CSVLoader/YAMLLoader 已完整）

---

## 📋 概述

本文档基于 v3.28.1 的架构分析，规划未来版本的功能增强。所有增强均遵循 v3 架构核心原则：

1. **五层架构** - Layer 0-4 职责清晰，依赖单向
2. **事件驱动** - EventBus 发布/订阅模式，组件解耦
3. **统一可观测性** - Logging/Tracing/Metrics 三大支柱
4. **testing/ 按功能职责组织** - 不按测试类型，而按工具职责

---

## 🎯 版本规划总览

| 版本 | 主题 | 特性 | 优先级 | 状态 |
|------|------|------|--------|------|
| **v3.5.0** | Mock 基础 | HTTP Mock、Time Mock | P1 | ✅ 已完成 |
| **v3.11.0** | Mock 增强 | Database Mock、Redis Mock | P1 | ✅ 已完成 |
| **v3.29.0** | 测试数据增强 | utils/ 重构、Factory 初版 | P2 | ✅ 已完成 |
| **v3.30.0** | 断言增强 | Schema 验证、匹配器 | P2 | ✅ 已完成 |
| **v3.31.0** | Factory 重构 | 合并两套 Factory、现代化设计 | P1 | ✅ 已完成 |
| **v3.32.0** | gRPC 事件统一 | gRPC EventBus 集成 | P2 | ✅ 已完成 |
| **v3.33.0** | GraphQL 中间件系统 | GraphQL 中间件 + EventBus 集成 | P2 | ✅ 已完成 |
| **v3.34.0** | 消息队列事件 | MQ 事件 Start/End/Error 三态模式 | P3 | ✅ 已完成 |
| **v3.35.0** | 环境管理 | YAML 分层配置、ConfigRegistry | P3 | ✅ 已完成 |
| **v3.36.0+** | 高级特性 | 契约测试、安全测试、计算引擎 | P3 | |

---

## 🧹 v3.29.0 前置任务 - utils/ 目录清理

### 问题分析

`utils/` 目录存在以下架构问题：

1. **游离在五层架构之外** - 没有明确的层级归属
2. **功能重复严重** - 多处实现相同功能
3. **职责混乱** - 测试工具、基础设施、核心类型混在一起

### 重复功能对照表

| 功能 | utils/ 位置 | 重复/应归属位置 | 处理方式 |
|------|-------------|-----------------|----------|
| `random_string()` | `common.py` | `DataGenerator.random_string()` | 废弃，用 DataGenerator |
| `random_email()` | `common.py` | `DataGenerator.email()` | 废弃，用 DataGenerator |
| `random_phone()` | `common.py` | `DataGenerator.phone()` | 废弃，用 DataGenerator |
| `load_json()` | `common.py` | `testing/data/loaders/JSONLoader` | 废弃，用 Loader |
| `load_excel()` | `common.py` | `testing/data/loaders/` | 迁移到 Loader |
| `DataGenerator` | `data_generator.py` | `testing/data/generators/` | 迁移 |
| `AssertHelper` | `assertion.py` | `testing/assertions/` | 迁移 |
| `decorator.py` | `utils/` | `core/decorators.py` | 迁移 |
| `performance.py` | `utils/` | `infrastructure/metrics/` | 迁移 |
| `resilience.py` | `utils/` | `infrastructure/resilience/` | 迁移 |
| `types.py` | `utils/` | `core/types.py` | 合并 |

### 目标架构

```
utils/                          # 废弃（仅保留向后兼容导出）
    └── __init__.py             # 从新位置重新导出，标记 DeprecationWarning

testing/data/                   # Layer 3
    ├── generators/             # 数据生成器（从 utils/ 迁移）
    │   ├── __init__.py
    │   └── data_generator.py   # DataGenerator 类
    ├── factories/              # 业务对象工厂（新增）
    ├── loaders/                # 数据加载器（已有 + 增强）
    └── builders/               # 数据构建器（已有）

testing/assertions/             # Layer 3
    ├── __init__.py
    ├── helper.py               # AssertHelper（从 utils/ 迁移）
    ├── response.py             # ResponseAssertion（新增）
    └── matchers.py             # 匹配器（新增）

core/                           # Layer 0
    ├── decorators.py           # 装饰器（从 utils/ 迁移）
    └── types.py                # 类型定义（合并 utils/types.py）

infrastructure/                 # Layer 1
    ├── metrics/
    │   └── performance.py      # 性能监控（从 utils/ 迁移）
    └── resilience/             # 新增目录
        └── circuit_breaker.py  # 熔断器（从 utils/ 迁移）
```

### 迁移策略

**Phase 1**: 迁移文件到新位置
**Phase 2**: 在 `utils/__init__.py` 添加向后兼容导出 + DeprecationWarning
**Phase 3**: 文档更新，引导用户使用新路径
**Phase 4**: (未来版本) 移除 utils/ 目录

### 向后兼容示例

```python
# utils/__init__.py（迁移后）
import warnings
from df_test_framework.testing.data.generators import DataGenerator
from df_test_framework.testing.assertions import AssertHelper
# ... 其他导出

def __getattr__(name):
    warnings.warn(
        f"从 'df_test_framework.utils' 导入 '{name}' 已废弃，"
        f"请使用新路径导入。详见迁移指南。",
        DeprecationWarning,
        stacklevel=2,
    )
    # 返回对应的对象
```

### 实施检查清单

```markdown
## utils/ 清理检查清单

### Phase 1: 文件迁移
- [x] 创建 `testing/data/generators/` 目录
- [x] 迁移 `DataGenerator` 到 `testing/data/generators/`
- [x] 创建 `testing/assertions/` 目录（已存在，添加 helper.py）
- [x] 迁移 `AssertHelper` 到 `testing/assertions/helper.py`
- [x] 创建 `infrastructure/resilience/` 目录
- [x] 迁移 `CircuitBreaker` 到 `infrastructure/resilience/`
- [x] 迁移 `performance.py` 到 `infrastructure/metrics/performance.py`
- [x] 合并 `utils/types.py` 到 `core/types.py`
- [x] 迁移装饰器到 `core/decorators.py`

### Phase 2: 向后兼容
- [x] 更新 `utils/__init__.py` 添加 DeprecationWarning
- [x] 确保旧导入路径仍可用（带警告）
- [x] 编写迁移指南文档（docs/releases/v3.29.0.md）

### Phase 3: 清理重复
- [x] 废弃 `common.py` 中的 `random_*` 函数
- [x] 废弃 `common.py` 中的 `load_json`
- [x] 废弃 `common.py` 中的 `load_excel`
- [x] 更新所有内部引用使用新路径

### Phase 4: 测试
- [x] 确保所有测试通过（1387 passed）
- [x] 添加废弃警告测试
- [x] 验证向后兼容性
```

---

## 📦 v3.29.0 - 测试数据增强

### 目标

增强测试数据生成和加载能力，提升测试编写效率。**同时完成 utils/ 清理重构**。

### 特性清单

#### 1. 测试数据工厂 (`testing/data/factories/`)

**需求**: 基于现有 `DataGenerator` 构建完整的业务对象

> **重要**: 框架已有 `utils/data_generator.py`（原子数据生成），Factory 是其**上层封装**，
> 用于组装完整的业务对象。Factory 内部复用 DataGenerator，避免重复实现。

**架构关系**:
```
testing/data/factories/          # 业务对象工厂（新增）
         │
         │ 内部使用
         ▼
utils/data_generator.py          # 原子数据生成（已有）
         │
         │ 内部使用
         ▼
      Faker 库
```

**目录结构**:
```
testing/data/factories/
├── __init__.py
├── base.py              # BaseFactory 抽象类（复用 DataGenerator）
├── user_factory.py      # 用户数据工厂
├── order_factory.py     # 订单数据工厂
└── product_factory.py   # 商品数据工厂
```

**核心接口**:
```python
# testing/data/factories/base.py
from abc import ABC, abstractmethod
from df_test_framework.utils.data_generator import DataGenerator

class BaseFactory(ABC):
    """测试数据工厂基类

    复用 DataGenerator 生成原子数据，组装为完整业务对象。
    """

    def __init__(self, locale: str = "zh_CN"):
        self.gen = DataGenerator(locale)  # 复用已有的 DataGenerator

    @abstractmethod
    def create(self, **overrides) -> dict:
        """创建单个数据对象"""
        pass

    def create_batch(self, count: int, **overrides) -> list[dict]:
        """批量创建数据对象"""
        return [self.create(**overrides) for _ in range(count)]

    def create_minimal(self, **overrides) -> dict:
        """创建最小必填字段对象"""
        return self.create(**overrides)
```

**示例实现**:
```python
# testing/data/factories/user_factory.py
from .base import BaseFactory

class UserFactory(BaseFactory):
    """用户数据工厂

    生成完整的用户业务对象，复用 DataGenerator 生成字段值。
    """

    def create(self, **overrides) -> dict:
        """创建完整用户对象"""
        data = {
            # 使用 DataGenerator 生成字段
            "user_id": self.gen.user_id(),
            "name": self.gen.name(),
            "email": self.gen.email(),
            "phone": self.gen.chinese_phone(),
            "address": self.gen.address(),
            # 业务字段
            "role": "user",
            "status": "active",
            "created_at": self.gen.datetime_str(),
        }
        data.update(overrides)
        return data

    def create_admin(self, **overrides) -> dict:
        """创建管理员用户"""
        return self.create(role="admin", **overrides)

    def create_minimal(self, **overrides) -> dict:
        """创建最小用户（只有必填字段）"""
        data = {
            "name": self.gen.name(),
            "email": self.gen.email(),
        }
        data.update(overrides)
        return data
```

**使用方式**:
```python
from df_test_framework.testing.data.factories import UserFactory

def test_create_user(http_client):
    factory = UserFactory()

    # 创建完整用户
    user_data = factory.create(role="admin")

    # 批量创建
    users = factory.create_batch(10)

    response = http_client.post("/users", json=user_data)
    assert response.status_code == 201
```

**与 DataGenerator 的区别**:

| 特性 | DataGenerator | Factory |
|------|---------------|---------|
| **位置** | `utils/` | `testing/data/factories/` |
| **职责** | 生成单个字段值 | 组装完整业务对象 |
| **返回值** | 字符串、数字等 | dict（完整对象） |
| **使用场景** | 需要单个随机值 | 需要完整测试数据 |
| **示例** | `gen.email()` → `"a@b.com"` | `factory.create()` → `{...}` |

#### 2. 数据加载器 (`testing/data/loaders/`)

**需求**: 从外部文件加载测试数据

**目录结构**:
```
testing/data/loaders/
├── __init__.py
├── base.py              # BaseLoader 抽象类
├── json_loader.py       # JSON 文件加载器
├── csv_loader.py        # CSV 文件加载器
├── yaml_loader.py       # YAML 文件加载器
└── excel_loader.py      # Excel 文件加载器（可选）
```

**核心接口**:
```python
# testing/data/loaders/base.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

class BaseLoader(ABC):
    """数据加载器基类"""

    @abstractmethod
    def load(self, file_path: str | Path) -> Any:
        """从文件加载数据"""
        pass

    @abstractmethod
    def load_all(self, directory: str | Path, pattern: str = "*") -> list[Any]:
        """从目录加载所有匹配文件"""
        pass
```

**示例实现**:
```python
# testing/data/loaders/json_loader.py
import json
from pathlib import Path
from .base import BaseLoader

class JsonLoader(BaseLoader):
    """JSON 数据加载器"""

    def load(self, file_path: str | Path) -> dict | list:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_all(self, directory: str | Path, pattern: str = "*.json") -> list:
        dir_path = Path(directory)
        return [self.load(f) for f in dir_path.glob(pattern)]
```

**使用方式**:
```python
from df_test_framework.testing.data.loaders import JsonLoader, CsvLoader

def test_with_json_data(http_client):
    loader = JsonLoader()
    test_cases = loader.load("testdata/users.json")

    for case in test_cases:
        response = http_client.post("/users", json=case["input"])
        assert response.status_code == case["expected_status"]

def test_with_csv_data(http_client):
    loader = CsvLoader()
    rows = loader.load("testdata/products.csv")

    for row in rows:
        response = http_client.get(f"/products/{row['id']}")
        assert response.json()["name"] == row["name"]
```

### 任务分解

| 任务 | 依赖 | 说明 |
|------|------|------|
| T1: 创建 `testing/data/factories/base.py` | - | 复用 DataGenerator |
| T2: 实现 `UserFactory` | T1 | 用户对象工厂 |
| T3: 实现 `OrderFactory` | T1 | 订单对象工厂 |
| T4: 实现 `ProductFactory` | T1 | 商品对象工厂 |
| T5: 编写 Factory 单元测试 | T2-T4 | 覆盖率 ≥80% |
| T6: 创建 `testing/data/loaders/base.py` | - | 加载器基类 |
| T7: 实现 `JsonLoader` | T6 | JSON 文件加载 |
| T8: 实现 `CsvLoader` | T6 | CSV 文件加载 |
| T9: 实现 `YamlLoader` | T6 | YAML 文件加载 |
| T10: 编写 Loader 单元测试 | T7-T9 | 覆盖率 ≥80% |
| T11: 更新 `__init__.py` 导出 | T1-T10 | 统一导出 |
| T12: 编写使用指南文档 | T1-T11 | guides/ |
| T13: 更新 CHANGELOG | T12 | 版本发布 |

> **注意**: 无需添加 Faker 依赖，框架已有（`utils/data_generator.py` 已使用）。
> Factory 层只需复用 DataGenerator 即可。

### 实施检查清单

```markdown
## v3.29.0 实施检查清单

### 测试数据工厂（复用 DataGenerator）
- [x] 创建 `testing/data/factories/` 目录
- [x] 实现 `Factory` 基类（类方法设计，复用 DataGenerator）
- [x] 实现 `ModelFactory` 带类型提示的基类
- [x] 实现 `UserFactory`（含 create_vip, create_inactive）
- [x] 实现 `OrderFactory`（含 create_paid, create_shipped, create_cancelled）
- [x] 实现 `ProductFactory`（含 create_out_of_stock, create_off_sale）
- [x] 实现 `AddressFactory`（含 create_default）
- [x] 更新 `testing/data/__init__.py` 导出
- [x] 编写单元测试（33 个测试全部通过）

### 数据加载器
- [x] `testing/data/loaders/` 目录已存在
- [x] `pyyaml` 已是依赖
- [x] `BaseLoader` 已存在（DataLoader）
- [x] `JsonLoader` 已存在
- [x] `CsvLoader` 已存在
- [x] `YamlLoader` 已存在
- [x] 导出已完成
- 备注：v3.10.0 已实现完整的 Loader 系统，无需新增

### 文档与发布
- [ ] 编写 `docs/guides/test_data_factory.md` (可选，后续版本)
- [ ] 更新 `docs/ESSENTIAL_DOCS.md` (可选，后续版本)
- [x] 更新 `CHANGELOG.md`
- [x] 创建 `docs/releases/v3.29.0.md`
- [x] 更新版本号（pyproject.toml + __init__.py）
- [x] 运行完整测试套件（1387 passed）
- [x] 代码检查通过（ruff check + ruff format）
```

---

## 📦 v3.30.0 - 断言增强

### 目标

增强断言能力，提供 HTTP 响应专用断言、JSON Schema 验证和自定义匹配器。

### 特性清单

#### 1. HTTP 响应断言 (`testing/assertions/response.py`)

**核心接口**:
```python
# testing/assertions/response.py
from typing import Any
from df_test_framework.capabilities.clients.http.core import Response

class ResponseAssertion:
    """HTTP 响应断言 - Fluent API"""

    def __init__(self, response: Response):
        self._response = response

    def has_status(self, expected: int) -> "ResponseAssertion":
        """断言状态码"""
        assert self._response.status_code == expected, \
            f"期望状态码 {expected}，实际 {self._response.status_code}"
        return self

    def has_json_path(self, path: str, value: Any = None) -> "ResponseAssertion":
        """断言 JSON 路径存在（可选值匹配）"""
        # 使用 jsonpath-ng 库
        pass

    def has_header(self, name: str, value: str | None = None) -> "ResponseAssertion":
        """断言响应头"""
        pass

    def body_contains(self, text: str) -> "ResponseAssertion":
        """断言响应体包含文本"""
        pass

    def matches_schema(self, schema: dict) -> "ResponseAssertion":
        """断言响应匹配 JSON Schema"""
        pass

def assert_response(response: Response) -> ResponseAssertion:
    """创建响应断言对象"""
    return ResponseAssertion(response)
```

**使用方式**:
```python
from df_test_framework.testing.assertions import assert_response

def test_get_user(http_client):
    response = http_client.get("/users/123")

    assert_response(response) \
        .has_status(200) \
        .has_json_path("$.data.id", 123) \
        .has_json_path("$.data.name") \
        .has_header("Content-Type", "application/json")
```

#### 2. JSON Schema 验证 (`testing/assertions/json_schema.py`)

**核心接口**:
```python
# testing/assertions/json_schema.py
from jsonschema import validate, ValidationError

class SchemaValidator:
    """JSON Schema 验证器"""

    def __init__(self, schema: dict):
        self._schema = schema

    def validate(self, data: dict) -> bool:
        """验证数据是否符合 Schema"""
        try:
            validate(instance=data, schema=self._schema)
            return True
        except ValidationError as e:
            raise AssertionError(f"Schema 验证失败: {e.message}")

    @classmethod
    def from_file(cls, file_path: str) -> "SchemaValidator":
        """从文件加载 Schema"""
        pass

def assert_schema(data: dict, schema: dict) -> None:
    """快捷断言函数"""
    SchemaValidator(schema).validate(data)
```

#### 3. 自定义匹配器 (`testing/assertions/matchers.py`)

**核心接口**:
```python
# testing/assertions/matchers.py
from abc import ABC, abstractmethod
from typing import Any
import re

class BaseMatcher(ABC):
    """匹配器基类"""

    @abstractmethod
    def matches(self, actual: Any) -> bool:
        pass

    @abstractmethod
    def describe(self) -> str:
        pass

class RegexMatcher(BaseMatcher):
    """正则匹配器"""

    def __init__(self, pattern: str):
        self._pattern = re.compile(pattern)

    def matches(self, actual: Any) -> bool:
        return bool(self._pattern.match(str(actual)))

    def describe(self) -> str:
        return f"matches regex '{self._pattern.pattern}'"

class ContainsMatcher(BaseMatcher):
    """包含匹配器"""
    pass

class InRangeMatcher(BaseMatcher):
    """范围匹配器"""
    pass

# 快捷函数
def matches_regex(pattern: str) -> RegexMatcher:
    return RegexMatcher(pattern)

def contains(value: Any) -> ContainsMatcher:
    return ContainsMatcher(value)

def in_range(min_val: Any, max_val: Any) -> InRangeMatcher:
    return InRangeMatcher(min_val, max_val)
```

### 任务分解

| 任务 | 依赖 |
|------|------|
| T1: 实现 `ResponseAssertion` 类 | - |
| T2: 集成 jsonpath-ng 库 | T1 |
| T3: 实现 `SchemaValidator` 类 | - |
| T4: 实现基础匹配器 | - |
| T5: 编写单元测试 | T1-T4 |
| T6: 更新导出和文档 | T1-T5 |

### 实施检查清单

```markdown
## v3.30.0 实施检查清单

### 响应断言
- [x] 添加 `jsonpath-ng` 到依赖
- [x] 实现 `ResponseAssertion` 类（已在 v3.10.0 实现）
- [x] 实现 Fluent API 方法链（已有）
- [x] 编写单元测试

### JSON Schema 验证
- [x] 添加 `jsonschema` 到依赖（已有）
- [x] 实现 `SchemaValidator` 类
- [x] 支持从文件加载 Schema
- [x] 编写单元测试（27 个）

### 自定义匹配器
- [x] 实现 `BaseMatcher` 抽象类
- [x] 实现 `RegexMatcher`
- [x] 实现 `ContainsMatcher`
- [x] 实现 `InRangeMatcher`
- [x] 实现 15+ 匹配器类
- [x] 编写单元测试（58 个）

### 文档与发布
- [ ] 编写 `docs/guides/assertions_guide.md`（可选，后续版本）
- [x] 更新 CHANGELOG
- [x] 创建 `docs/releases/v3.30.0.md`
```

---

## ✅ Mock 支持（已完成）

> **注意**: Mock 功能早在 v3.5.0 和 v3.11.0 已完整实现，详见 `testing/mocking/` 模块和 `docs/guides/mocking.md`。

### 已实现功能

| 模块 | 版本 | 功能 |
|------|------|------|
| **HttpMocker** | v3.5.0 / v3.16.0 | 基于 Middleware 的 HTTP Mock，支持规则匹配、链式 API |
| **TimeMocker** | v3.5.0 | 基于 freezegun，支持时间冻结/推进 |
| **DatabaseMocker** | v3.11.0 | 数据库操作 Mock，SQL 标准化匹配 |
| **RedisMocker** | v3.11.0 | 支持 fakeredis + 内存后备，完整数据结构支持 |

### 原规划内容（仅供参考）

以下是原先的规划内容，已无需实施：

### 特性清单

#### 1. HTTP Mock (`testing/mocks/http/`)

**目录结构**:
```
testing/mocks/http/
├── __init__.py
├── mock_server.py       # HTTP Mock 服务器
└── respx_adapter.py     # respx 库适配器（异步）
```

**核心接口**:
```python
# testing/mocks/http/mock_server.py
import responses
from contextlib import contextmanager

class HttpMock:
    """HTTP 请求 Mock（同步）"""

    def __init__(self):
        self._mock = responses.RequestsMock()
        self._responses: list[dict] = []

    def add(
        self,
        method: str,
        url: str,
        json: dict | None = None,
        body: str | None = None,
        status: int = 200,
        headers: dict | None = None,
    ) -> "HttpMock":
        """添加 Mock 响应"""
        self._mock.add(
            method=method,
            url=url,
            json=json,
            body=body,
            status=status,
            headers=headers or {},
        )
        return self

    def get(self, url: str, **kwargs) -> "HttpMock":
        """快捷方法: GET"""
        return self.add("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> "HttpMock":
        """快捷方法: POST"""
        return self.add("POST", url, **kwargs)

    @contextmanager
    def activate(self):
        """激活 Mock（上下文管理器）"""
        with self._mock:
            yield self

    def start(self) -> None:
        """手动启动 Mock"""
        self._mock.start()

    def stop(self) -> None:
        """手动停止 Mock"""
        self._mock.stop()
        self._mock.reset()
```

**Fixture**:
```python
# testing/fixtures/mocks.py
import pytest
from df_test_framework.testing.mocks.http import HttpMock

@pytest.fixture
def http_mock():
    """HTTP Mock fixture"""
    mock = HttpMock()
    mock.start()
    yield mock
    mock.stop()
```

**使用方式**:
```python
def test_with_mock(http_mock, http_client):
    # 设置 Mock 响应
    http_mock.get(
        "https://api.example.com/users/123",
        json={"id": 123, "name": "Mock User"},
        status=200,
    )

    # 发送请求（被 Mock 拦截）
    response = http_client.get("https://api.example.com/users/123")

    assert response.status_code == 200
    assert response.json()["name"] == "Mock User"
```

#### 2. 时间 Mock (`testing/mocks/time/`)

**核心接口**:
```python
# testing/mocks/time/time_mock.py
from freezegun import freeze_time
from contextlib import contextmanager
from datetime import datetime

class TimeMock:
    """时间 Mock（基于 freezegun）"""

    def __init__(self, freeze_datetime: str | datetime):
        """
        Args:
            freeze_datetime: 冻结时间，如 "2025-01-01 12:00:00"
        """
        self._freeze_datetime = freeze_datetime
        self._freezer = None

    @contextmanager
    def freeze(self):
        """冻结时间（上下文管理器）"""
        with freeze_time(self._freeze_datetime):
            yield

    def start(self) -> None:
        """手动启动时间冻结"""
        self._freezer = freeze_time(self._freeze_datetime)
        self._freezer.start()

    def stop(self) -> None:
        """手动停止时间冻结"""
        if self._freezer:
            self._freezer.stop()
```

**Fixture**:
```python
@pytest.fixture
def frozen_time():
    """返回 TimeMock 工厂"""
    def _create(freeze_datetime: str):
        return TimeMock(freeze_datetime)
    return _create
```

**使用方式**:
```python
def test_with_frozen_time(frozen_time):
    mock = frozen_time("2025-01-01 12:00:00")

    with mock.freeze():
        from datetime import datetime
        assert datetime.now().year == 2025
        assert datetime.now().month == 1
```

#### 3. 数据库 Mock (`testing/mocks/database/`)

**核心接口**:
```python
# testing/mocks/database/sqlite_mock.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class SQLiteMock:
    """SQLite 内存数据库 Mock"""

    def __init__(self):
        self._engine = create_engine("sqlite:///:memory:")
        self._session_factory = sessionmaker(bind=self._engine)

    def create_tables(self, base) -> None:
        """根据 SQLAlchemy Base 创建表"""
        base.metadata.create_all(self._engine)

    def session(self):
        """获取数据库 Session"""
        return self._session_factory()

    def execute(self, sql: str, params: dict | None = None):
        """执行 SQL"""
        with self._engine.connect() as conn:
            return conn.execute(sql, params or {})
```

### 任务分解

| 任务 | 依赖 |
|------|------|
| T1: 创建 `testing/mocks/` 目录结构 | - |
| T2: 添加 `responses` `freezegun` 依赖 | - |
| T3: 实现 `HttpMock` | T1, T2 |
| T4: 实现 `TimeMock` | T1, T2 |
| T5: 实现 `SQLiteMock` | T1 |
| T6: 创建 Mock Fixtures | T3-T5 |
| T7: 编写单元测试 | T3-T6 |
| T8: 更新导出和文档 | T1-T7 |

### 实施检查清单

```markdown
## v3.32.0 实施检查清单

### HTTP Mock
- [ ] 添加 `responses` 到依赖
- [ ] 添加 `respx` 到依赖（异步）
- [ ] 实现 `HttpMock` 类
- [ ] 实现 `AsyncHttpMock` 类
- [ ] 创建 `http_mock` fixture
- [ ] 编写单元测试

### 时间 Mock
- [ ] 添加 `freezegun` 到依赖
- [ ] 实现 `TimeMock` 类
- [ ] 创建 `frozen_time` fixture
- [ ] 编写单元测试

### 数据库 Mock
- [ ] 实现 `SQLiteMock` 类
- [ ] 创建 `sqlite_mock` fixture
- [ ] 编写单元测试

### 文档与发布
- [ ] 编写 `docs/guides/mock_guide.md`
- [ ] 更新 CHANGELOG
- [ ] 创建 `docs/releases/v3.32.0.md`
```

---

## 📦 v3.32.0 - gRPC 事件系统统一

### 目标

将 gRPC 客户端集成到 EventBus 事件驱动架构，统一可观测性。

### 特性清单

#### 1. gRPC 事件定义 (`core/events/grpc.py`)

**核心接口**:
```python
# core/events/grpc.py
from dataclasses import dataclass, field
from .types import CorrelatedEvent, generate_event_id

@dataclass(frozen=True)
class GrpcRequestStartEvent(CorrelatedEvent):
    """gRPC 请求开始事件"""
    event_type: str = field(default="grpc.request.start", init=False)

    service: str = ""
    method: str = ""
    metadata: dict = field(default_factory=dict)
    request_data: dict | None = None

    @classmethod
    def create(
        cls,
        service: str,
        method: str,
        metadata: dict | None = None,
        request_data: dict | None = None,
    ) -> tuple["GrpcRequestStartEvent", str]:
        """工厂方法，返回 (事件, correlation_id)"""
        correlation_id = generate_event_id()
        trace_id, span_id = _get_current_trace_context()

        event = cls(
            correlation_id=correlation_id,
            trace_id=trace_id,
            span_id=span_id,
            service=service,
            method=method,
            metadata=metadata or {},
            request_data=request_data,
        )
        return event, correlation_id

@dataclass(frozen=True)
class GrpcRequestEndEvent(CorrelatedEvent):
    """gRPC 请求结束事件"""
    event_type: str = field(default="grpc.request.end", init=False)

    service: str = ""
    method: str = ""
    status_code: int = 0
    duration: float = 0.0
    response_data: dict | None = None

    @classmethod
    def create(
        cls,
        correlation_id: str,
        service: str,
        method: str,
        status_code: int,
        duration: float,
        response_data: dict | None = None,
    ) -> "GrpcRequestEndEvent":
        """工厂方法"""
        pass

@dataclass(frozen=True)
class GrpcRequestErrorEvent(CorrelatedEvent):
    """gRPC 请求错误事件"""
    event_type: str = field(default="grpc.request.error", init=False)

    service: str = ""
    method: str = ""
    error_code: int = 0
    error_message: str = ""
    duration: float = 0.0
```

#### 2. gRPC 事件发布拦截器

**核心接口**:
```python
# capabilities/clients/grpc/interceptors/event_publisher.py
from df_test_framework.core.events.grpc import (
    GrpcRequestStartEvent,
    GrpcRequestEndEvent,
    GrpcRequestErrorEvent,
)
from df_test_framework.infrastructure.events import get_event_bus

class GrpcEventPublisherInterceptor(BaseInterceptor):
    """gRPC 事件发布拦截器"""

    def intercept_unary(self, method, request, metadata):
        # 发布 Start 事件
        event, self._correlation_id = GrpcRequestStartEvent.create(
            service=self._extract_service(method),
            method=self._extract_method(method),
            metadata=dict(metadata),
            request_data=self._serialize_request(request),
        )
        get_event_bus().publish_sync(event)

        self._start_time = time.perf_counter()
        return request, metadata

    def intercept_response(self, method, response, metadata):
        duration = time.perf_counter() - self._start_time

        # 发布 End 事件
        event = GrpcRequestEndEvent.create(
            correlation_id=self._correlation_id,
            service=self._extract_service(method),
            method=self._extract_method(method),
            status_code=0,  # OK
            duration=duration,
            response_data=self._serialize_response(response),
        )
        get_event_bus().publish_sync(event)

        return response
```

#### 3. 更新 AllureObserver 和 ConsoleDebugObserver

```python
# 在 AllureObserver 中添加 gRPC 事件处理
class AllureObserver:
    def subscribe(self, event_bus: EventBus) -> None:
        # 现有 HTTP 订阅...

        # 新增 gRPC 订阅
        event_bus.subscribe(GrpcRequestStartEvent, self._handle_grpc_start)
        event_bus.subscribe(GrpcRequestEndEvent, self._handle_grpc_end)
        event_bus.subscribe(GrpcRequestErrorEvent, self._handle_grpc_error)

    def _handle_grpc_start(self, event: GrpcRequestStartEvent) -> None:
        """处理 gRPC 请求开始"""
        allure.attach(
            json.dumps(event.request_data, indent=2, ensure_ascii=False),
            name=f"gRPC Request: {event.service}/{event.method}",
            attachment_type=allure.attachment_type.JSON,
        )
```

### 任务分解

| 任务 | 依赖 |
|------|------|
| T1: 定义 gRPC 事件类型 | - |
| T2: 实现 `GrpcEventPublisherInterceptor` | T1 |
| T3: 更新 `AllureObserver` | T1 |
| T4: 更新 `ConsoleDebugObserver` | T1 |
| T5: 更新 `MetricsObserver` | T1 |
| T6: 更新 gRPC 客户端默认拦截器 | T2 |
| T7: 编写单元测试 | T1-T6 |
| T8: 更新文档 | T1-T7 |

### 实施检查清单

```markdown
## v3.32.0 实施检查清单

### gRPC 事件系统
- [x] 在 `core/events/types.py` 添加 gRPC 事件（统一管理）
- [x] 定义 `GrpcRequestStartEvent`
- [x] 定义 `GrpcRequestEndEvent`
- [x] 定义 `GrpcRequestErrorEvent`
- [x] 实现 `GrpcEventPublisherMiddleware`（使用中间件而非拦截器）
- [x] 更新 `core/events/__init__.py` 导出

### 观察者更新
- [x] 更新 `AllurePlugin` 支持 gRPC 事件
- [x] 更新 `ConsoleDebugObserver` 支持 gRPC 事件
- [x] 更新 `MetricsObserver` 支持 gRPC 事件

### 客户端集成
- [x] 重构 `GrpcClient` 为中间件模式
- [x] 默认启用事件发布（enable_events=True）
- [x] 编写中间件和集成测试（52 个测试）

### 文档与发布
- [x] 更新 CHANGELOG
- [x] 创建 `docs/releases/v3.32.0.md`
```

---

## 📦 v3.33.0 - GraphQL 中间件系统 + 事件系统统一

### 目标

为 GraphQL 客户端引入中间件系统（Middleware System），与 HTTP/gRPC 客户端保持一致的架构设计，参考 2025 年最新趋势，实现灵活的功能扩展机制。

### 背景分析

**2025 年 GraphQL 客户端趋势**（来源：Apollo Client 4.0、Graffle）：
- **模块化架构** - 核心精简，功能按需加载
- **插件/中间件系统** - `.use()` 链式添加功能
- **OpenTelemetry 原生支持** - 可观测性内置

**设计决策**：
- ❌ 不复用 HttpClient（避免耦合，保持 GraphQL 独立控制）
- ✅ 采用中间件系统（与 HTTP/gRPC 客户端命名一致）

**目标架构**：
```
GraphQLClient
    ├── httpx.Client（直接使用，保持控制）
    └── Middleware Chain（中间件链）
            ├── GraphQLEventPublisherMiddleware（事件发布）
            ├── GraphQLRetryMiddleware（重试）
            ├── GraphQLLoggingMiddleware（日志）
            └── 自定义中间件...
```

**框架命名一致性**：
| 客户端 | 中间件基类 | 目录 |
|--------|-----------|------|
| HTTP | `HttpMiddleware` | `clients/http/middleware/` |
| gRPC | `GrpcMiddleware` | `clients/grpc/middleware/` |
| GraphQL | `GraphQLMiddleware` | `clients/graphql/middleware/` |

### 特性清单

#### 1. GraphQL 中间件基类 (`capabilities/clients/graphql/middleware/base.py`)

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from typing import Any

from df_test_framework.capabilities.clients.graphql.models import (
    GraphQLRequest,
    GraphQLResponse,
)


class GraphQLMiddleware(ABC):
    """GraphQL 中间件基类

    v3.33.0 新增

    与 HttpMiddleware、GrpcMiddleware 保持一致的设计。

    中间件执行顺序（洋葱模型）：
        Middleware1.before → Middleware2.before → execute → Middleware2.after → Middleware1.after
    """

    def __init__(self, name: str = "", priority: int = 0) -> None:
        """初始化中间件

        Args:
            name: 中间件名称
            priority: 优先级（数字越小越先执行 before，越后执行 after）
        """
        self.name = name or self.__class__.__name__
        self.priority = priority

    @abstractmethod
    async def __call__(
        self,
        request: GraphQLRequest,
        call_next: Callable[[GraphQLRequest], Coroutine[None, None, GraphQLResponse]],
    ) -> GraphQLResponse:
        """执行中间件逻辑

        Args:
            request: GraphQL 请求
            call_next: 调用下一个中间件或实际执行

        Returns:
            GraphQL 响应
        """
        ...
```

#### 2. GraphQL 客户端重构 (`capabilities/clients/graphql/client.py`)

```python
class GraphQLClient:
    """GraphQL 客户端（v3.33.0 重构）

    采用中间件系统，支持 .use() 链式添加功能。

    示例：
        # 基础用法
        client = GraphQLClient("https://api.example.com/graphql")

        # 使用中间件
        client = (
            GraphQLClient("https://api.example.com/graphql")
            .use(GraphQLLoggingMiddleware())
            .use(GraphQLRetryMiddleware(max_retries=3))
        )

        # 禁用默认事件中间件
        client = GraphQLClient(
            "https://api.example.com/graphql",
            enable_events=False,
        )
    """

    def __init__(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        timeout: int = 30,
        verify_ssl: bool = True,
        middlewares: list[GraphQLMiddleware] | None = None,
        enable_events: bool = True,
    ) -> None:
        """初始化 GraphQL 客户端

        Args:
            url: GraphQL 端点 URL
            headers: 默认请求头
            timeout: 请求超时时间（秒）
            verify_ssl: 是否验证 SSL 证书
            middlewares: 中间件列表
            enable_events: 是否启用事件发布（默认 True，自动添加 EventPublisherMiddleware）
        """
        self.url = url
        self.headers = headers or {}
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # 初始化 httpx 客户端（直接使用，不复用 HttpClient）
        self._client = httpx.Client(
            timeout=timeout,
            verify=verify_ssl,
            headers=self.headers,
        )

        # 初始化中间件链
        self._middlewares: list[GraphQLMiddleware] = list(middlewares) if middlewares else []

        # 自动添加事件发布中间件
        if enable_events:
            self._middlewares.append(GraphQLEventPublisherMiddleware())

    def use(self, middleware: GraphQLMiddleware) -> GraphQLClient:
        """添加中间件（链式调用）

        Args:
            middleware: 中间件实例

        Returns:
            self，支持链式调用

        示例：
            client = (
                GraphQLClient(url)
                .use(GraphQLLoggingMiddleware())
                .use(GraphQLRetryMiddleware())
            )
        """
        self._middlewares.append(middleware)
        return self

    @property
    def middlewares(self) -> list[GraphQLMiddleware]:
        """已注册的中间件列表（只读副本）"""
        return self._middlewares.copy()
```

#### 3. 内置中间件

**事件发布中间件** (`middleware/event_publisher.py`)：
```python
class GraphQLEventPublisherMiddleware(GraphQLMiddleware):
    """GraphQL 事件发布中间件

    v3.33.0 新增

    在中间件链最内层发布事件，确保能记录完整的请求信息。
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
        log_query: bool = True,
        log_variables: bool = True,
        log_response: bool = True,
        max_data_length: int = 1000,
    ) -> None:
        super().__init__(name="GraphQLEventPublisherMiddleware", priority=999)
        self._event_bus = event_bus
        self._log_query = log_query
        self._log_variables = log_variables
        self._log_response = log_response
        self._max_data_length = max_data_length

    async def __call__(
        self,
        request: GraphQLRequest,
        call_next: Callable[[GraphQLRequest], Coroutine[None, None, GraphQLResponse]],
    ) -> GraphQLResponse:
        event_bus = self._event_bus or get_event_bus()
        if not event_bus:
            return await call_next(request)

        # 发布开始事件
        start_event, correlation_id = GraphQLRequestStartEvent.create(
            url=request.url,
            operation_type=request.operation_type,
            operation_name=request.operation_name,
            query=request.query if self._log_query else None,
            variables=request.variables_json if self._log_variables else None,
        )
        await event_bus.publish(start_event)

        start_time = time.time()

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # 发布结束事件
            end_event = GraphQLRequestEndEvent.create(
                correlation_id=correlation_id,
                url=request.url,
                operation_type=request.operation_type,
                operation_name=request.operation_name,
                duration=duration,
                has_errors=response.has_errors,
                error_count=len(response.errors) if response.errors else 0,
                data=response.data_json if self._log_response else None,
            )
            await event_bus.publish(end_event)

            return response

        except Exception as e:
            duration = time.time() - start_time

            # 发布错误事件
            error_event = GraphQLRequestErrorEvent.create(
                correlation_id=correlation_id,
                url=request.url,
                operation_type=request.operation_type,
                operation_name=request.operation_name,
                error=e,
                duration=duration,
            )
            await event_bus.publish(error_event)
            raise
```

**重试中间件** (`middleware/retry.py`)：
```python
class GraphQLRetryMiddleware(GraphQLMiddleware):
    """GraphQL 重试中间件

    v3.33.0 新增
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_on_network_error: bool = True,
        retry_on_graphql_error: bool = False,
    ) -> None:
        super().__init__(name="GraphQLRetryMiddleware", priority=10)
        self.max_retries = max_retries
        self.retry_on_network_error = retry_on_network_error
        self.retry_on_graphql_error = retry_on_graphql_error

    async def __call__(
        self,
        request: GraphQLRequest,
        call_next: Callable[[GraphQLRequest], Coroutine[None, None, GraphQLResponse]],
    ) -> GraphQLResponse:
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await call_next(request)

                # 检查是否需要重试 GraphQL 错误
                if self.retry_on_graphql_error and response.has_errors:
                    if attempt < self.max_retries:
                        continue

                return response

            except httpx.HTTPError as e:
                last_error = e
                if not self.retry_on_network_error or attempt >= self.max_retries:
                    raise

        raise last_error  # type: ignore
```

**日志中间件** (`middleware/logging.py`)：
```python
class GraphQLLoggingMiddleware(GraphQLMiddleware):
    """GraphQL 日志中间件

    v3.33.0 新增
    """

    def __init__(self, log_query: bool = True, log_variables: bool = False) -> None:
        super().__init__(name="GraphQLLoggingMiddleware", priority=0)
        self.log_query = log_query
        self.log_variables = log_variables

    async def __call__(
        self,
        request: GraphQLRequest,
        call_next: Callable[[GraphQLRequest], Coroutine[None, None, GraphQLResponse]],
    ) -> GraphQLResponse:
        logger.info(f"GraphQL {request.operation_type}: {request.operation_name or 'anonymous'}")
        if self.log_query:
            logger.debug(f"Query: {request.query[:200]}...")
        if self.log_variables and request.variables:
            logger.debug(f"Variables: {request.variables}")

        response = await call_next(request)

        logger.info(f"GraphQL response: has_errors={response.has_errors}")
        return response
```

#### 4. 向后兼容

```python
# 旧代码继续工作
client = GraphQLClient("https://api.example.com/graphql")
response = client.execute(query)

# 新功能：使用中间件
client = (
    GraphQLClient("https://api.example.com/graphql")
    .use(GraphQLLoggingMiddleware())
    .use(GraphQLRetryMiddleware(max_retries=3))
)
```

#### 5. GraphQL 事件定义 (`core/events/types.py`)

**注意**：事件定义在 `types.py` 中统一管理，不创建单独文件。

```python
# core/events/types.py 中添加

@dataclass(frozen=True)
class GraphQLRequestStartEvent(CorrelatedEvent):
    """GraphQL 请求开始事件

    v3.33.0: 新增
    """
    url: str = ""
    operation_type: str = ""  # query, mutation, subscription
    operation_name: str | None = None
    query: str | None = None
    variables: str | None = None  # JSON 字符串（避免序列化问题）

    @classmethod
    def create(
        cls,
        url: str,
        operation_type: str,
        operation_name: str | None = None,
        query: str | None = None,
        variables: str | None = None,
        context: ExecutionContext | None = None,
    ) -> tuple["GraphQLRequestStartEvent", str]:
        """工厂方法：创建事件并返回 correlation_id"""
        correlation_id = generate_correlation_id()
        trace_id, span_id = _get_current_trace_context()
        event = cls(
            url=url,
            operation_type=operation_type,
            operation_name=operation_name,
            query=query,
            variables=variables,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )
        return event, correlation_id


@dataclass(frozen=True)
class GraphQLRequestEndEvent(CorrelatedEvent):
    """GraphQL 请求结束事件

    v3.33.0: 新增
    """
    url: str = ""
    operation_type: str = ""
    operation_name: str | None = None
    duration: float = 0.0
    has_errors: bool = False
    error_count: int = 0
    data: str | None = None  # JSON 字符串

    @classmethod
    def create(
        cls,
        correlation_id: str,
        url: str,
        operation_type: str,
        duration: float,
        operation_name: str | None = None,
        has_errors: bool = False,
        error_count: int = 0,
        data: str | None = None,
        context: ExecutionContext | None = None,
    ) -> "GraphQLRequestEndEvent":
        """工厂方法：创建事件（复用 correlation_id）"""
        trace_id, span_id = _get_current_trace_context()
        return cls(
            url=url,
            operation_type=operation_type,
            operation_name=operation_name,
            duration=duration,
            has_errors=has_errors,
            error_count=error_count,
            data=data,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )


@dataclass(frozen=True)
class GraphQLRequestErrorEvent(CorrelatedEvent):
    """GraphQL 请求错误事件（HTTP 层面的错误）

    v3.33.0: 新增

    注意：GraphQL 业务错误（response.errors）通过 EndEvent.has_errors 标识，
    此事件仅用于 HTTP 传输层错误（网络超时、连接失败等）。
    """
    url: str = ""
    operation_type: str = ""
    operation_name: str | None = None
    error_type: str = ""
    error_message: str = ""
    duration: float = 0.0

    @classmethod
    def create(
        cls,
        correlation_id: str,
        url: str,
        operation_type: str,
        error: Exception,
        duration: float,
        operation_name: str | None = None,
        context: ExecutionContext | None = None,
    ) -> "GraphQLRequestErrorEvent":
        """工厂方法：创建错误事件"""
        trace_id, span_id = _get_current_trace_context()
        return cls(
            url=url,
            operation_type=operation_type,
            operation_name=operation_name,
            error_type=type(error).__name__,
            error_message=str(error),
            duration=duration,
            correlation_id=correlation_id,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
        )
```

#### 6. 观察者更新

**AllurePlugin** (`plugins/builtin/reporting/allure_plugin.py`):
```python
# 订阅 GraphQL 事件
event_bus.subscribe(GraphQLRequestStartEvent, self._handle_graphql_start)
event_bus.subscribe(GraphQLRequestEndEvent, self._handle_graphql_end)
event_bus.subscribe(GraphQLRequestErrorEvent, self._handle_graphql_error)

def _handle_graphql_start(self, event: GraphQLRequestStartEvent) -> None:
    """记录 GraphQL 请求到 Allure"""
    if event.query:
        allure.attach(
            event.query,
            name=f"GraphQL {event.operation_type}: {event.operation_name or 'anonymous'}",
            attachment_type=allure.attachment_type.TEXT,
        )
```

**ConsoleDebugObserver** (`testing/debugging/console.py`):
```python
# 新增 GraphQLCallRecord 数据类
@dataclass
class GraphQLCallRecord:
    url: str
    operation_type: str
    operation_name: str | None
    query: str | None
    variables: str | None
    duration: float | None = None
    has_errors: bool = False
    error_count: int = 0
```

### 实施检查清单

```markdown
## v3.33.0 实施检查清单

### GraphQL 中间件系统
- [ ] 创建 `capabilities/clients/graphql/middleware/` 目录
- [ ] 实现 `GraphQLMiddleware` 基类
- [ ] 实现 `GraphQLEventPublisherMiddleware`
- [ ] 实现 `GraphQLRetryMiddleware`
- [ ] 实现 `GraphQLLoggingMiddleware`
- [ ] 更新 `__init__.py` 导出中间件

### GraphQL 客户端重构
- [ ] 添加 `middlewares` 参数
- [ ] 添加 `enable_events` 参数
- [ ] 实现 `.use()` 链式方法
- [ ] 实现中间件链执行逻辑
- [ ] 更新 `execute()` 方法
- [ ] 更新 `execute_batch()` 方法
- [ ] 更新 `upload_file()` 方法
- [ ] 保持向后兼容

### GraphQL 事件系统
- [ ] 在 `core/events/types.py` 添加 GraphQL 事件
- [ ] 定义 `GraphQLRequestStartEvent`
- [ ] 定义 `GraphQLRequestEndEvent`
- [ ] 定义 `GraphQLRequestErrorEvent`
- [ ] 更新 `core/events/__init__.py` 导出

### 观察者更新
- [ ] 更新 `AllurePlugin` 支持 GraphQL 事件
- [ ] 更新 `ConsoleDebugObserver` 支持 GraphQL 事件
- [ ] 新增 `GraphQLCallRecord` 数据类

### 测试
- [ ] 新增 GraphQL 中间件测试
- [ ] 更新 GraphQL 客户端测试
- [ ] 新增 GraphQL 事件测试
- [ ] 确保向后兼容性测试通过

### 文档与发布
- [ ] 更新 `docs/guides/graphql_client.md`
- [ ] 更新 CHANGELOG
- [ ] 创建 `docs/releases/v3.33.0.md`
```

---

## 📦 v3.34.0 - 消息队列事件系统

### 目标

将 Kafka/RabbitMQ/RocketMQ 客户端集成到 EventBus。

### 特性清单

#### 1. 消息队列事件定义

```python
# core/events/messenger.py
@dataclass(frozen=True)
class MessagePublishedEvent(CorrelatedEvent):
    """消息发布事件"""
    event_type: str = field(default="messenger.published", init=False)

    messenger_type: str = ""  # kafka, rabbitmq, rocketmq
    topic: str = ""
    partition: int | None = None
    key: str | None = None
    message_size: int = 0

@dataclass(frozen=True)
class MessageConsumedEvent(CorrelatedEvent):
    """消息消费事件"""
    event_type: str = field(default="messenger.consumed", init=False)

    messenger_type: str = ""
    topic: str = ""
    partition: int | None = None
    offset: int | None = None
    processing_time: float = 0.0
```

### 实施检查清单

```markdown
## v3.34.0 实施检查清单

### 消息队列事件系统
- [ ] 定义消息队列事件类型
- [ ] Kafka 客户端发布事件
- [ ] RabbitMQ 客户端发布事件
- [ ] RocketMQ 客户端发布事件
- [ ] 更新观察者
- [ ] 编写单元测试
- [ ] 更新文档
```

---

## ✅ v3.35.0 实施记录（2025-12-18）

**环境管理增强已完成**:

### 实现内容

#### 1. YAML 分层配置系统 (`infrastructure/config/loader.py`)

**核心特性**:
- 支持 `config/base.yaml` + `config/environments/{env}.yaml` 分层配置
- `_extends` 字段支持配置继承
- 深度合并（deep merge）配置对象
- 向后兼容 `.env` 文件模式（自动回退）

**ConfigLoader 类**:
```python
from df_test_framework.infrastructure.config import ConfigLoader, load_config

# 方式1: 使用 ConfigLoader 类
loader = ConfigLoader("config")
settings = loader.load("staging")

# 方式2: 使用便捷函数
settings = load_config("staging", "config")
```

**配置加载优先级**（从高到低）:
1. 环境变量
2. `config/secrets/.env.local`
3. `config/environments/{env}.yaml`
4. `config/base.yaml`
5. `.env` + `.env.{env}`（回退模式）
6. 代码默认值

#### 2. ConfigRegistry 统一配置访问 (`infrastructure/config/registry.py`)

**核心特性**:
- 全局单例模式
- 点号路径访问配置（`registry.get("http.timeout")`）
- 类型安全的属性访问
- 快捷属性（`http`、`db`、`redis`、`logging`、`observability`）

**使用方式**:
```python
from df_test_framework.infrastructure.config import ConfigRegistry

# 方式1: 全局单例
ConfigRegistry.initialize("staging", "config")
registry = ConfigRegistry.get_instance()

# 方式2: 为指定环境创建
registry = ConfigRegistry.for_environment("staging", "config")

# 方式3: 直接传入配置对象
settings = FrameworkSettings(env="test")
registry = ConfigRegistry(settings)

# 访问配置
timeout = registry.get("http.timeout")  # 点号路径
base_url = registry.settings.http.base_url  # 类型安全
is_debug = registry.is_debug  # 快捷属性
```

#### 3. CLI 环境管理命令 (`cli/commands/env.py`)

**新增命令**:
```bash
# 显示当前环境配置
df-test env show
df-test env show --env=staging

# 初始化配置目录结构
df-test env init
df-test env init --config-dir=my_config

# 验证配置完整性
df-test env validate --env=staging
```

**`env init` 创建的目录结构**:
```
config/
├── base.yaml              # 基础配置（所有环境共享）
├── environments/
│   ├── local.yaml         # 本地开发环境
│   ├── dev.yaml           # 开发环境
│   ├── test.yaml          # 测试环境
│   ├── staging.yaml       # 预发布环境
│   └── prod.yaml          # 生产环境
└── secrets/               # 敏感配置（已添加 .gitignore）
```

#### 4. pytest 插件增强 (`testing/plugins/env_plugin.py`)

**新增命令行参数**:
- `--env=staging` - 指定运行环境
- `--config-dir=config` - 指定配置目录

**新增 Fixtures**:
```python
@pytest.fixture(scope="session")
def config_registry(request) -> ConfigRegistry:
    """配置注册中心"""

@pytest.fixture(scope="session")
def settings(config_registry) -> FrameworkSettings:
    """框架配置"""

@pytest.fixture(scope="session")
def current_env(config_registry) -> str:
    """当前环境名称"""
```

**使用方式**:
```bash
# 在 staging 环境运行测试
pytest tests/ --env=staging

# 使用自定义配置目录
pytest tests/ --env=staging --config-dir=my_config

# 在 prod 环境运行冒烟测试
pytest tests/ --env=prod -m smoke
```

**测试中使用**:
```python
def test_example(settings, current_env):
    if current_env == "prod":
        pytest.skip("跳过生产环境")

    assert settings.http.base_url is not None
```

### 设计决策

- **向后兼容**：如果 `config/` 目录不存在，自动回退到 `.env` 文件模式
- **配置继承**：通过 `_extends` 字段支持配置继承，减少重复
- **深度合并**：嵌套配置对象深度合并，而非简单覆盖
- **全局单例**：ConfigRegistry 提供全局单例模式，便于跨模块访问
- **类型安全**：保持 FrameworkSettings Pydantic 模型的类型安全

### 测试结果

- 新增 ConfigLoader 测试：17 个
- 新增 ConfigRegistry 测试：27 个
- 全部测试通过：1534 passed, 40 skipped

### 实施检查清单

```markdown
## v3.35.0 实施检查清单

### YAML 分层配置
- [x] 创建 `infrastructure/config/loader.py`
- [x] 实现 `ConfigLoader` 类（支持继承、深度合并）
- [x] 实现 `load_config()` 便捷函数
- [x] 更新 `config/__init__.py` 导出

### ConfigRegistry 统一访问
- [x] 创建 `infrastructure/config/registry.py`
- [x] 实现全局单例模式
- [x] 实现点号路径访问 `get(path, default)`
- [x] 添加快捷属性（http、db、redis 等）
- [x] 更新 `config/__init__.py` 导出

### CLI 环境管理
- [x] 实现 `env_show()` 命令
- [x] 实现 `env_init()` 命令
- [x] 实现 `env_validate()` 命令
- [x] 更新 CLI 主入口

### pytest 插件
- [x] 添加 `--env` 命令行参数
- [x] 添加 `--config-dir` 命令行参数
- [x] 实现 `config_registry` fixture
- [x] 实现 `settings` fixture
- [x] 实现 `current_env` fixture
- [x] 在报告头部显示环境信息

### 测试
- [x] 新增 ConfigLoader 单元测试（17 个）
- [x] 新增 ConfigRegistry 单元测试（27 个）
- [x] 全部测试通过（1534 passed）

### 文档与发布
- [x] 更新 CHANGELOG.md
- [x] 创建 `docs/releases/v3.35.0.md`
- [x] 更新版本号（已是 3.35.0）
```

---

## 📦 v3.36.0+ - 高级特性（长期规划）

### 1. 契约测试

```
testing/contracts/
├── pact/                # Pact 消费者契约
└── openapi/             # OpenAPI 验证
```

### 2. 安全测试

```
testing/security/
├── owasp/               # OWASP ZAP 集成
└── sensitive_data.py    # 敏感数据检测
```

### 3. 计算引擎

```
capabilities/engines/
├── batch/
│   └── spark/           # Spark 作业测试
└── stream/
    └── flink/           # Flink 流测试
```

### 4. 性能测试集成

```
testing/performance/
├── locust/              # Locust 集成
└── k6/                  # k6 集成
```

---

## 📊 实施优先级总览

### 已完成

| 版本 | 特性 | 价值 | 状态 |
|------|------|------|------|
| **v3.5.0** | HTTP Mock、Time Mock | ⭐⭐⭐⭐⭐ | ✅ 已完成 |
| **v3.11.0** | Database Mock、Redis Mock | ⭐⭐⭐⭐⭐ | ✅ 已完成 |
| **v3.29.0** | 测试数据工厂 + 加载器 | ⭐⭐⭐⭐⭐ | ✅ 已完成 |
| **v3.30.0** | 断言增强 | ⭐⭐⭐⭐ | ✅ 已完成 |
| **v3.31.0** | Factory 重构 | ⭐⭐⭐⭐⭐ | ✅ 已完成 |
| **v3.32.0** | gRPC 事件统一 | ⭐⭐⭐⭐ | ✅ 已完成 |
| **v3.33.0** | GraphQL 中间件系统 | ⭐⭐⭐⭐ | ✅ 已完成 |
| **v3.34.0** | MQ 事件三态模式 | ⭐⭐⭐⭐ | ✅ 已完成 |
| **v3.35.0** | YAML 分层配置 + ConfigRegistry | ⭐⭐⭐⭐⭐ | ✅ 已完成 |

### 长期规划

| 版本 | 特性 | 说明 |
|------|------|------|
| v3.36.0+ | 契约测试 | Pact/OpenAPI |
| v3.36.0+ | 安全测试 | OWASP ZAP |
| v3.36.0+ | 计算引擎 | Spark/Flink |
| v3.36.0+ | 性能测试 | Locust/k6 |

---

## 📝 附录：依赖清单

### v3.29.0 新增依赖

```toml
# pyproject.toml
[project.optional-dependencies]
data = [
    # faker 已存在（utils/data_generator.py 使用）
    "pyyaml>=6.0",  # YAML 加载器需要
]
```

> **注意**: `faker` 已是现有依赖，无需新增。Factory 复用 `utils/data_generator.py`。

### v3.30.0 新增依赖

```toml
assertions = [
    "jsonpath-ng>=1.6.0",
    "jsonschema>=4.20.0",
]
```

### Mock 依赖（已安装）

> Mock 功能已在 v3.5.0 和 v3.11.0 实现，以下依赖已安装。

```toml
# 已安装的 Mock 依赖
# freezegun - TimeMocker
# fakeredis - RedisMocker（可选，有内存后备）
# pytest-httpx - HttpMocker（可选集成）
```

---

## 📚 相关文档

- [FUTURE_ENHANCEMENTS.md](./FUTURE_ENHANCEMENTS.md) - 早期规划（v3.11 时期）
- [eventbus-integration-analysis.md](./eventbus-integration-analysis.md) - EventBus 集成状态
- [observability-architecture.md](./observability-architecture.md) - 可观测性架构
- [OVERVIEW_V3.17.md](./OVERVIEW_V3.17.md) - 架构总览

---

**文档创建日期**: 2025-12-16
**最后更新**: 2025-12-18
**基于版本**: v3.35.0
**状态**: ✅ v3.29.0 ~ v3.35.0 已完成
