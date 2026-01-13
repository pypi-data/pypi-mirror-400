# 依赖管理策略 (DI Strategy)

> **版本**: v3.40.1
> **作者**: Claude Code
> **日期**: 2025-12-31

---

## 概述

DF Test Framework 采用**混合依赖管理策略**（Hybrid DI），根据服务特性选择不同的管理模式：

| 服务类型 | 管理模式 | 适用场景 |
|---------|---------|---------|
| **重量级资源** | Provider 模式 | 连接池、外部资源、需显式关闭 |
| **轻量级服务** | Settings 绑定 | 纯配置驱动、无外部依赖 |
| **测试依赖** | pytest fixtures | 测试生命周期管理 |

---

## 1. Provider 模式（重量级资源）

### 适用场景

- 持有外部连接（TCP/Socket/HTTP）
- 需要连接池管理
- 需要显式关闭释放资源
- 需要线程安全的单例

### 实现位置

```
bootstrap/providers.py
├── SingletonProvider[T]    # 泛型单例提供者（双重检查锁）
├── ProviderRegistry        # 提供者注册表
└── default_providers()     # 默认资源工厂
```

### 使用示例

```python
# 注册 Provider
providers = ProviderRegistry(
    providers={
        "http_client": SingletonProvider(http_factory),
        "database": SingletonProvider(db_factory),
        "redis": SingletonProvider(redis_factory),
    }
)

# 获取资源（通过 RuntimeContext）
http_client = runtime.http_client()
database = runtime.database()
```

### 当前注册的 Provider

| Key | 类型 | 说明 |
|-----|------|------|
| `http_client` | HttpClient | HTTP 连接池 |
| `database` | Database | SQLAlchemy 数据库连接池 |
| `redis` | RedisClient | Redis 连接池 |
| `local_file` | LocalFileClient | 本地文件存储 |
| `s3` | S3Client | AWS S3 对象存储 |
| `oss` | OSSClient | 阿里云 OSS 对象存储 |

### 生命周期

```
Bootstrap.build()
    └── ProviderRegistry 创建
            └── SingletonProvider 注册（惰性，未实例化）
                    │
                    ▼
            runtime.http_client()  ──► 首次访问时实例化
                    │
                    ▼
            RuntimeContext.close()
                    └── ProviderRegistry.shutdown()
                            └── 调用 close()/shutdown() 释放资源
```

### 线程安全

`SingletonProvider` 使用双重检查锁定模式：

```python
def get(self, context: TRuntime):
    # 第一次检查（无锁，快速路径）
    if self._instance is None:
        with self._lock:
            # 第二次检查（有锁，防止竞态）
            if self._instance is None:
                self._instance = self._factory(context)
    return self._instance
```

---

## 2. Settings 绑定模式（轻量级服务）

### 适用场景

- 纯配置驱动的服务
- 无外部资源依赖
- 生命周期跟随配置
- 不需要显式关闭

### 实现位置

```
infrastructure/config/settings.py
├── get_settings()           # lru_cache 单例
└── clear_settings_cache()   # 清除缓存

infrastructure/sanitize/service.py
├── get_sanitize_service()   # 绑定 settings 生命周期
└── SanitizeService          # 脱敏服务
```

### 使用示例

```python
# 获取配置（自动缓存）
from df_test_framework import get_settings
settings = get_settings()

# 获取脱敏服务（绑定 settings 生命周期）
from df_test_framework.infrastructure.sanitize import get_sanitize_service
service = get_sanitize_service()
```

### 当前的轻量级服务

| 服务 | 获取方式 | 说明 |
|------|---------|------|
| `FrameworkSettings` | `get_settings()` | 框架配置 |
| `SanitizeService` | `get_sanitize_service()` | 脱敏服务 |

### 生命周期

```
get_settings()  ──► lru_cache 缓存
        │
        ▼
get_sanitize_service()
        │
        └── 检查 settings 对象上是否有缓存
                │
                ├── 有 ──► 返回缓存实例
                │
                └── 无 ──► 创建并缓存到 settings 对象
                                │
                                ▼
                        clear_settings_cache()
                                └── settings 清除，service 随之清除
```

### 为什么不用 Provider？

| 对比项 | Provider 模式 | Settings 绑定 |
|-------|--------------|--------------|
| 依赖 | 需要 RuntimeContext | 仅需 settings |
| 锁开销 | 双重检查锁 | 无锁（lru_cache 线程安全） |
| 关闭方法 | 需要 shutdown() | 无需（GC 自动回收） |
| 复杂度 | 高（Factory + Provider + Registry） | 低（直接绑定） |
| 适用 | 连接池、外部资源 | 纯内存计算 |

**结论**：轻量级服务使用 Provider 是过度设计。

---

## 3. pytest fixtures（测试依赖）

### 适用场景

- 测试生命周期管理
- 测试隔离
- 依赖注入到测试函数

### 实现位置

```
testing/fixtures/
├── core.py      # runtime, http_client, database, redis_client
├── cleanup.py   # cleanup_manager, test_data_cleaner
├── ui.py        # browser_manager, page
└── mq.py        # kafka_producer, rabbitmq_channel
```

### 使用示例

```python
# conftest.py
@pytest.fixture(scope="session")
def http_client(runtime):
    return runtime.http_client()

@pytest.fixture
def cleanup(runtime):
    manager = CleanupManager(runtime)
    yield manager
    manager.cleanup()

# test_example.py
def test_api(http_client, cleanup):
    response = http_client.post("/users", json={"name": "test"})
    cleanup.add("users", response.json()["id"])
    assert response.status_code == 201
```

### Fixture 作用域

| 作用域 | 资源类型 | 示例 |
|-------|---------|------|
| `session` | 重量级（连接池） | runtime, http_client, database |
| `function` | 轻量级（测试隔离） | cleanup, test_context |
| `module` | 中等（模块共享） | test_data |

---

## 4. 选择指南

### 决策流程图

```
需要管理的服务/资源
        │
        ▼
    持有外部连接？
        │
    ┌───┴───┐
    是      否
    │       │
    ▼       ▼
需要连接池？   纯配置驱动？
    │           │
┌───┴───┐   ┌───┴───┐
是      否  是      否
│       │   │       │
▼       ▼   ▼       ▼
Provider  Provider  Settings  评估具体情况
模式      模式      绑定
```

### 快速判断

**使用 Provider 模式**：
- ✅ HTTP 客户端（连接池）
- ✅ 数据库（连接池）
- ✅ Redis（连接池）
- ✅ 对象存储客户端（外部连接）
- ✅ 消息队列客户端（外部连接）

**使用 Settings 绑定**：
- ✅ 配置服务
- ✅ 脱敏服务
- ✅ 日志配置
- ✅ 其他纯内存计算服务

**使用 pytest fixtures**：
- ✅ 测试级别的资源管理
- ✅ 测试数据清理
- ✅ 测试隔离

---

## 5. 与业界实践对比

| 框架 | 重量级资源 | 轻量级服务 | 测试 |
|------|-----------|-----------|------|
| **Spring Boot** | Bean + IoC Container | `@Value` / Environment | @SpringBootTest |
| **NestJS** | Provider + Module | ConfigService | @nestjs/testing |
| **Django** | ORM Manager | settings.py | TestCase |
| **FastAPI** | Depends() | Pydantic Settings | pytest + fixtures |
| **DF Test Framework** | Provider + Registry | Settings 绑定 | pytest fixtures |

---

## 6. 扩展新服务的指南

### 添加重量级资源

```python
# 1. 定义工厂函数
def my_client_factory(context: TRuntime) -> MyClient:
    config = context.settings.my_service
    return MyClient(host=config.host, port=config.port)

# 2. 注册到 ProviderRegistry
providers["my_client"] = SingletonProvider(my_client_factory)

# 3. 在 RuntimeContext 添加便捷方法
def my_client(self) -> MyClient:
    return self.providers.get("my_client", self)
```

### 添加轻量级服务

```python
# 1. 定义服务类
class MyService:
    def __init__(self, config: MyConfig):
        self.config = config

# 2. 定义获取函数（绑定 settings）
_SETTINGS_ATTR = "_my_service_instance"

def get_my_service() -> MyService:
    from df_test_framework import get_settings
    settings = get_settings()

    if not hasattr(settings, _SETTINGS_ATTR):
        config = settings.my_config or MyConfig()
        setattr(settings, _SETTINGS_ATTR, MyService(config))

    return getattr(settings, _SETTINGS_ATTR)
```

---

## 7. 常见问题

### Q: 为什么 SanitizeService 不用 Provider？

A: SanitizeService 是纯内存计算服务，不持有外部连接，不需要：
- 连接池管理
- 显式关闭
- 双重检查锁

绑定到 settings 生命周期是最简洁的实现。

### Q: 什么时候应该新增 Provider？

A: 当服务满足以下任一条件时：
1. 需要 TCP/Socket 连接
2. 需要连接池管理
3. 需要显式释放资源
4. 需要 RuntimeContext 上下文

### Q: 如何确保配置变更后服务刷新？

A: 调用 `clear_settings_cache()` 会：
1. 清除 `get_settings()` 的 lru_cache
2. 绑定在 settings 对象上的服务（如 SanitizeService）随之失效
3. 下次调用 `get_xxx_service()` 时自动创建新实例

---

## 相关文档

- [V3.16 Bootstrap 架构](V3.16_LAYER4_BOOTSTRAP_ARCHITECTURE.md) - Provider 系统详细设计
- [v3.40.1 发布说明](../releases/v3.40.1.md) - SanitizeService 生命周期绑定
- [配置管理指南](../user-guide/configuration.md) - Settings 使用说明

---

**返回**: [架构文档](README.md) | [文档首页](../README.md)
