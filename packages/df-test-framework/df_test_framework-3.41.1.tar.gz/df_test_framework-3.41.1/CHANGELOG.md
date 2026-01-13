# Changelog

本文档记录df-test-framework的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [3.41.1] - 2026-01-04

### 架构优化与请求模型增强

**核心特性**: 基础模型迁移到 core 层 + BaseRequest 自动排除 null 值。

**主要功能**:
- 🏗️ 模型架构重构：`models/` → `core/models/`，符合五层架构 Layer 0 设计
- ✨ BaseRequest 默认排除 None 值（`exclude_none=True`）和使用字段别名（`by_alias=True`）
- 🔧 OpenAPI 代码生成器自动为请求模型使用 BaseRequest 基类
- 🐛 修复自动生成的请求模型发送大量 null 值导致后端问题

**详细内容**: 查看完整发布说明 [v3.41.1](docs/releases/v3.41.1.md)

### 重构
- 将 `df_test_framework.models` 迁移到 `df_test_framework.core.models`
- BaseRequest 增强：重写 `model_dump()` 和 `model_dump_json()` 方法，默认排除 None 值

### 改进
- OpenAPI 代码生成器：请求模型使用 BaseRequest 基类，自动继承排除 null 值特性
- BaseAPI：格式化代码以符合行长度限制

### 文档
- 新增 `docs/releases/v3.41.1.md` - 完整版本发布说明

### 测试
- ✅ 所有 2016 个测试通过
- ✅ 基础模型迁移后的导入兼容性验证通过

---

## [3.41.0] - 2025-12-31

### OpenAPI 代码生成智能增强（v3.41.0）

**核心特性**: 大幅增强 OpenAPI 代码生成器的智能化程度，生成的测试代码更接近"开箱即用"状态。

**主要变更**:
- ✨ **文件更新模式优化** - `--force` 更新并保留用户扩展，`--force --no-merge` 完全覆盖
- ✨ **智能请求示例生成** - 自动识别 `pagination`、`sortName` 等字段，生成有意义的默认值
- ✨ **前置查询自动生成** - 详情/更新/删除操作自动生成前置查询获取有效 ID
- ✨ **中文测试标题** - 根据 operationId 智能生成中文标题（如 `查询 Supplier List`）
- ✨ **智能 pytest.mark** - 区分 `smoke`（核心功能）和 `regression`（次要功能）测试
- ✨ **增强列表断言** - 自动验证列表结构和分页信息
- ✨ **E2E 测试自动生成** - 识别 CRUD 操作，生成完整流程测试
- ✨ **负向测试自动生成** - 生成边界条件和错误场景测试
- 🔧 **--tags 逗号分隔支持** - 同时支持 `--tags tag1,tag2` 和 `--tags tag1 tag2`

**详细内容**: 查看完整发布说明 [v3.41.0](docs/releases/v3.41.0.md)

### 新增
- `_is_detail_operation()` - 判断是否是详情查询操作
- `_is_update_operation()` - 判断是否是更新操作
- `_is_delete_operation()` - 判断是否是删除操作
- `_is_list_query_operation()` - 判断是否是列表查询操作
- `_needs_precondition_query()` - 判断是否需要前置查询
- `_find_list_endpoint()` - 查找对应的列表查询接口
- `_generate_request_example()` - 根据 schema 生成智能请求示例
- `_generate_chinese_title()` - 生成中文测试标题
- `_get_pytest_mark()` - 根据操作类型获取 pytest mark
- `_build_e2e_test_class()` - 生成 E2E 测试类
- `_build_negative_test_class()` - 生成负向测试类

### 变更
- `_build_typed_test_method_code()` - 增加 `endpoints` 和 `parser` 参数，支持前置查询
- `_build_typed_test_code()` - 新增 E2E 和负向测试类生成、请求模型导入生成
- `cli/main.py` - 参数语义调整：`--force` 保留用户扩展，`--force --no-merge` 完全覆盖
- `_generate_chinese_title()` - 改进驼峰命名拆分，生成更可读的标题

---

## [3.40.1] - 2025-12-31

### 修复

- 🐛 **脱敏配置不生效问题** - 修复 `sanitize.enabled: false` 配置无效的问题

### 重构

- ♻️ **脱敏服务与 settings 生命周期绑定** - 移除独立单例，缓存在 settings 对象上
  - `get_sanitize_service()` 现在将服务缓存在 settings 对象上
  - 当 `clear_settings_cache()` 被调用时，服务自动随 settings 一起清除
  - 无需额外的 `clear_sanitize_service()` 同步，设计更简洁
  - `ConsoleDebugObserver` 移除类级别缓存，每次从 settings 获取

### 文档

- 📝 **新增依赖管理策略文档** - `docs/architecture/DI_STRATEGY.md`
  - Provider 模式（重量级资源）设计说明
  - Settings 绑定（轻量级服务）设计说明
  - pytest fixtures（测试依赖）使用指南
  - 扩展新服务的指南和决策流程图
  - 与业界实践（Spring/NestJS/Django/FastAPI）对比

---

## [3.40.0] - 2025-12-31

### 统一脱敏服务（v3.40.0）

**核心特性**: 将日志系统、ConsoleDebugObserver、AllureObserver 的脱敏逻辑统一，实现共享规则、多策略支持、独立开关控制。

**主要变更**:
- ✨ 新增 `SanitizeService` - 统一脱敏服务，支持 partial/full/hash 三种策略
- ✨ 新增 `SanitizeConfig` - 配置驱动，支持正则匹配敏感字段
- ✨ 各组件独立开关 - logging/console/allure 可独立启用/禁用
- ✨ AllureObserver 脱敏 - 新增 HTTP headers/body/params、GraphQL variables、gRPC metadata 脱敏
- 🔧 零配置使用 - 默认配置覆盖 17 个常见敏感字段，开箱即用

**详细内容**: 查看完整发布说明 [v3.40.0](docs/releases/v3.40.0.md)

### 新增
- `SanitizeService` - 统一脱敏服务类
- `SanitizeConfig` - 脱敏配置模型
- `SanitizeStrategy` - 脱敏策略枚举 (FULL/PARTIAL/HASH)
- `get_sanitize_service()` - 获取脱敏服务单例
- `infrastructure/sanitize/` - 新增脱敏服务模块

### 变更
- `ConsoleDebugObserver` - 移除硬编码 `SENSITIVE_FIELDS`，使用统一服务
- `AllureObserver` - 新增脱敏支持
- `infrastructure/logging/config.py` - 使用统一脱敏服务

### 测试
- 新增 33 个单元测试
- 全部 1969 个测试通过

---

## [3.39.1] - 2025-12-31

### OpenAPI 智能类型推断（v3.39.1）

**核心特性**: 增强 OpenAPI 代码生成器的类型推断能力，适配 Java 后端缺少 Swagger 注解的场景。

**主要变更**:
- ✨ 智能字段类型推断 - 基于字段名推断 `dict`/`list` 类型（如 `data` → `dict`，`list` → `list`）
- ✨ 查询操作识别 - 根据 `operationId`/`summary` 生成更精确的断言模板
- ✨ `$ref` 引用处理 - 自动转换为 `dict[str, Any]`
- ✨ 响应状态兼容 - 同时支持 `ok`/`success` 两种状态格式
- 🔧 动态生成 `apis/__init__.py` - 自动导入新生成的 API 客户端
- 🔧 修复 `models/__init__.py` 合并丢失子包导入的问题

**详细内容**: 查看完整发布说明 [v3.39.1](docs/releases/v3.39.1.md)

### 新增
- `_is_query_operation()` - 查询操作识别函数
- 智能类型推断 - `_get_python_type(field_name=...)` 参数

### 修复
- `models/__init__.py` 合并时保留 `requests/responses` 子包导入
- `apis/__init__.py` 动态生成，自动导入新 API 客户端

---

## [3.39.0] - 2025-12-30

### 脚手架增量合并 + 示例文件重命名（v3.39.0）

**核心特性**: 新增脚手架增量合并功能，支持 `--merge` 选项保留用户自定义代码；将示例文件从 `user` 重命名为 `example` 避免与 OpenAPI tag 冲突。

**主要变更**:
- ✨ 新增 `--merge` 选项 - 增量合并生成代码，保留用户扩展区域
- ✨ 新增分区标记系统 - `AUTO_GENERATED_START/END` + `USER_EXTENSIONS`
- ✨ 新增 `merge_with_markers()` 工具函数 - 智能合并生成代码
- ✨ 增强 `generate_init_from_directory()` - AST 解析 `__all__` 生成显式导入
- 🔧 重命名示例文件 - `user.py` → `example.py`，`UserAPI` → `ExampleAPI`

**详细内容**: 查看完整发布说明 [v3.39.0](docs/releases/v3.39.0.md)

### 新增
- `merge_with_markers()` - 基于标记的智能合并函数
- `create_file_with_merge()` - 支持合并模式的文件创建
- `_extract_all_from_file()` - AST 解析提取 `__all__`
- `--merge` 选项 - `df-test gen from-swagger --merge`

### 变更
- `models/requests/user.py` → `models/requests/example.py`
- `models/responses/user.py` → `models/responses/example.py`
- `apis/user_api.py` → `apis/example_api.py`
- `UserAPI` → `ExampleAPI`，`user_api` fixture → `example_api`
- 所有模板添加分区标记支持

### 测试
- 新增 `test_merge_with_markers` - 合并功能测试
- 新增 `test_create_file_with_merge` - 文件创建合并测试
- 新增 `test_generate_with_explicit_all` - 显式导入生成测试
- 全部 1967 个测试通过

---

## [3.38.10] - 2025-12-30

### 两步登录支持 + Discriminated Union（v3.38.10）

**核心特性**: 新增两步登录 Token 提供器支持，并引入 Pydantic v2 Discriminated Union 类型实现中间件配置的类型安全。

**主要变更**:
- ✨ 新增 `TwoStepLoginTokenProvider` - 支持 check → login 两步登录流程
- ✨ 新增 `TokenSource.TWO_STEP_LOGIN` - 两步登录枚举值
- ✨ 扩展 `BearerTokenMiddlewareConfig` - 支持两步登录专用配置
- ✨ 新增 `MiddlewareConfigUnion` - Pydantic v2 Discriminated Union 类型

**详细内容**: 查看完整发布说明 [v3.38.10](docs/releases/v3.38.10.md)

### 新增
- `TwoStepLoginTokenProvider` - 两步登录 Token 提供器
- `TokenSource.TWO_STEP_LOGIN` - 新枚举值
- `MiddlewareConfigUnion` - 类型安全的中间件配置联合类型

### 测试
- `test_middleware_schema.py` - 新增中间件配置测试
- `test_middleware_chain.py` - 新增集成测试

---

## [3.38.9] - 2025-12-30

### 增强 captured log 支持（v3.38.9）

**核心特性**: 增强 pytest captured log 支持，统一 "Captured log setup/call/teardown" 区域的日志格式。

**主要变更**:
- 🔧 替换 `caplog_handler` 的 formatter - caplog fixture 使用 ProcessorFormatter
- 🔧 替换 `report_handler` 的 formatter - Captured log 区域使用 ProcessorFormatter
- 📝 更新脚手架模板注释 - 说明 ProcessorFormatter 覆盖范围

**详细内容**: 查看完整发布说明 [v3.38.9](docs/releases/v3.38.9.md)

### 修复
- `logging_plugin.py` - 新增替换 `caplog_handler` 和 `report_handler` 的 formatter

### 文档
- 更新脚手架模板 `pyproject_toml.py` 注释说明

### 测试
- 新增 `test_logging_plugin.py` - 10 个单元测试
- 全部 1927 个测试通过

---

## [3.38.8] - 2025-12-29

### 可观测性架构文档更新（v3.38.8）

**核心特性**: 更新可观测性架构文档，说明日志技术栈升级（Loguru → structlog）和控制台日志架构设计。

**主要变更**:
- 📝 更新日志技术栈说明 - Loguru → structlog
- 📝 新增控制台日志架构章节 - LoggingMiddleware vs ObservabilityLogger 设计
- 📝 新增双写设计说明 - 控制台 + EventBus 解耦
- 📝 更新版本演进表 - v3.35.7 ~ v3.38.8

**详细内容**: 查看完整发布说明 [v3.38.8](docs/releases/v3.38.8.md)

### 文档
- `docs/architecture/observability-architecture.md` - 全面更新可观测性架构文档

---

## [3.38.7] - 2025-12-26

### 简化日志系统架构（v3.38.7）

**核心特性**: 简化框架日志系统架构，遵循 structlog 最佳实践。日志级别由消息性质决定（debug/info/error），通过全局 `logging.level` 配置控制过滤显示。

**主要变更**:
- 🏗️ Logger Protocol 精简 - 只定义 structlog.BoundLogger 核心方法签名
- 🔧 LoggingMiddleware 简化 - 移除 `level` 参数，使用固定级别（请求/响应→DEBUG，错误→ERROR）
- 📦 get_logger() 直接返回 - structlog.get_logger()，无需包装器
- 📋 全局配置过滤 - YAML `logging.level` 控制日志显示级别

**详细内容**: 查看完整发布说明 [v3.38.7](docs/releases/v3.38.7.md)

### 变更（⚠️ 不兼容）
- `LoggingMiddleware` 移除 `level` 参数 - 使用固定日志级别
  - 请求/响应详情 → DEBUG
  - 错误 → ERROR
  - 通过 `logging.level` 配置控制显示

### 修复
- `infrastructure/events/bus.py` - 改用 `get_logger()` 替代 `logging.getLogger()`
- `infrastructure/plugins/manager.py` - 统一使用 structlog
- `infrastructure/telemetry/facade.py` - 统一使用 structlog
- `capabilities/clients/http/middleware/logging.py` - 统一使用 structlog
- `capabilities/clients/http/middleware/retry.py` - 统一使用 structlog
- `capabilities/messengers/queue/kafka/client.py` - 统一使用 structlog
- `capabilities/messengers/queue/rabbitmq/client.py` - 统一使用 structlog
- `capabilities/messengers/queue/rocketmq/client.py` - 统一使用 structlog

### 简化
- 移除 `StructLogger` 包装器 - 直接使用 structlog.BoundLogger
- 移除 `Logger.log()` 方法 - Protocol 只定义 structlog 原生方法
- 移除 LoggingMiddleware `_level` 属性 - 使用 `debug()` 和 `error()` 方法

### 测试
- 全部 1908 个测试通过
- 移除 3 个过时的 level 参数测试

---

## [3.38.5] - 2025-12-25

### structlog 25.5.0 最佳实践升级（v3.38.5）

**核心特性**: 升级 structlog 到 25.4.0+，按照官方最新最佳实践优化日志系统，更好地支持第三方库日志。

**主要变更**:
- 🔧 PositionalArgumentsFormatter - 支持第三方库 % 格式化日志
- 📦 ExtraAdder - 支持第三方库 extra 参数
- 📝 LogfmtRenderer - 新增 logfmt 输出格式（Loki/Prometheus 原生格式）
- 🎯 QUAL_NAME - Python 3.11+ 使用完整限定名显示调用位置
- 🔄 structlog >= 25.4.0 - 支持 Python 3.14

**详细内容**: 查看完整发布说明 [v3.38.5](docs/releases/v3.38.5.md)

### 新增
- `PositionalArgumentsFormatter` - 处理第三方库 % 格式化
- `ExtraAdder` - 处理第三方库 extra 参数
- `LogfmtRenderer` - Logfmt 输出格式
- `LoggingConfig.format="logfmt"` - 新增 logfmt 格式选项
- `CallsiteParameter.QUAL_NAME` - Python 3.11+ 完整限定名
- `create_processor_formatter()` - 创建 ProcessorFormatter（用于 pytest 集成）

### 修复
- pytest 日志集成 - 修复日志重复和 dict 格式显示问题
  - 禁用 structlog 控制台输出，由 pytest 统一处理
  - 替换 pytest handlers formatter 为 ProcessorFormatter

### 变更
- 升级 structlog 版本要求: `>=24.1.0` → `>=25.4.0`
- 优化 processor 链顺序，遵循官方最新推荐
- `logging_plugin.py` 重写，修复 pytest 集成问题

### 测试
- 新增 16 个日志模块测试用例
- 全部 36 个日志测试通过

---

## [3.38.4] - 2025-12-25

### structlog 最佳实践改进 + TimeMocker 修复（v3.38.4）

**核心特性**: 完善 structlog 实现，遵循官方最佳实践，统一第三方日志格式、支持高性能 JSON 序列化和异步日志接口。修复 `time_mock` fixture 的 `tick()`/`move_to()` 方法。

**主要变更**:
- 🔄 ProcessorFormatter 统一格式 - httpx、sqlalchemy 等第三方库日志格式与 structlog 一致
- ⏰ ISO 8601 + UTC 时间戳 - 生产环境使用标准格式，便于日志聚合
- ⚡ orjson 高性能序列化 - 比标准库 json 快 5-10 倍（可选依赖）
- 📍 CallsiteParameterAdder - 可选添加调用位置信息（文件名、函数名、行号）
- 🔀 AsyncLogger Protocol - 支持异步日志方法（ainfo、adebug 等）
- 🐛 TimeMocker 修复 - 修复 freezegun 1.5+ 版本 API 兼容性问题

**详细内容**: 查看完整发布说明 [v3.38.4](docs/releases/v3.38.4.md)

### 新增
- `ProcessorFormatter` - 统一格式化 structlog 和第三方日志
- `AsyncLogger` Protocol - 异步日志接口定义
- `is_orjson_available()` - 检查 orjson 是否可用
- `LoggingConfig.use_utc` - 使用 UTC 时间戳配置
- `LoggingConfig.use_orjson` - 使用 orjson 序列化配置
- `LoggingConfig.add_callsite` - 添加调用位置信息配置
- `performance` 可选依赖组 - 包含 orjson
- `freezegun>=1.5.0` 核心依赖 - time_mock fixture 需要

### 修复
- `TimeMocker.tick()` - 修复 freezegun 1.5+ 版本 API 兼容性
- `TimeMocker.move_to()` - 正确使用 `FrozenDateTimeFactory` 实例

### 变更
- 优化脱敏处理器位置 - 移至 processor 链早期
- 文件日志强制使用 JSON 格式 - 便于日志分析
- JSON 格式自动启用 ISO 8601 + UTC 时间戳
- 脚手架模板更新 - time_mock 使用 `import datetime` 导入方式

### 文档
- 新增 `docs/releases/v3.38.4.md` - 完整版本发布说明
- 新增 freezegun 使用注意事项 - `import datetime` vs `from datetime import datetime`

### 测试
- 全部测试通过

---

## [3.38.2] - 2025-12-25

### 现代化日志系统（v3.38.2）

**核心特性**: 从 loguru 迁移到 structlog，实现统一日志接口、pytest 原生支持、时间格式统一和 OpenTelemetry 自动集成。

**主要变更**:
- 🔄 日志库迁移 - 从 loguru 迁移到 structlog
- 🔌 pytest 原生支持 - 无需桥接，直接使用 stdlib logging
- ⏰ 时间格式统一 - 使用 strftime 格式，与 pytest 一致
- 🔗 OpenTelemetry 集成 - 自动注入 trace_id/span_id
- 🔒 敏感信息脱敏 - 自动过滤密码、token 等

**详细内容**: 查看完整发布说明 [v3.38.2](docs/releases/v3.38.2.md)

### 新增
- `Logger` Protocol - 类型安全的日志接口，支持依赖注入
- `configure_logging()` - 新的日志配置函数
- `bind_contextvars()` / `clear_contextvars()` - 全局上下文管理
- `_add_trace_info()` - OpenTelemetry trace 信息自动注入
- `_sanitize_sensitive_data()` - 敏感信息脱敏处理器

### 移除
- `setup_logger()` - 由 `configure_logging()` 替代
- `LoguruStructuredStrategy` - 不再需要策略模式
- `strategies.py` - 日志策略模块
- `pytest_integration.py` - pytest 桥接模块

### 变更
- 依赖: `loguru>=0.7.0` → `structlog>=24.1.0`
- 导入: `from loguru import logger` → `get_logger(__name__)`
- 配置: `{time:YYYY-MM-DD}` → `%Y-%m-%d %H:%M:%S.%f`

### 文档
- 新增 `docs/releases/v3.38.2.md` - 完整版本发布说明
- 更新 `docs/guides/modern_logging_best_practices.md` - 使用指南
- 更新 `docs/guides/logging_configuration.md` - 配置指南

---

## [3.38.1] - 2025-12-24

### 修复

- 修复 `DataGenerator.test_id()` 快速连续生成时可能重复的问题（使用微秒级时间戳）
- 修复 GitHub Actions CLI 集成测试路径检查（`.env.example` → `config/secrets/.env.local.example`）
- 修复脚手架模板更新导致的测试失败（`test_gen_api_command`、`test_generate_models_with_invalid_json`）

### 测试

- 新增 `to_ascii_identifier()` 函数的 7 个单元测试
- 测试数量: 1891 → 1898

---

## [3.38.0] - 2025-12-24

### OpenAPI 代码生成器增强（v3.38.0）

**核心特性**: 重大改进 OpenAPI 代码生成器，支持 Swagger 2.0、Java/Python 命名自动转换、Model 分类生成和强类型 API 方法。

**主要变更**:
- 🔧 Swagger 2.0 完整支持 - 兼容 Swagger 2.0 和 OpenAPI 3.0 两种格式
- 🔄 命名自动转换 - camelCase → snake_case，保留 alias 支持双向兼容
- 📁 Model 分类生成 - requests/responses/common 按 tag 组织
- 🎯 强类型 API 方法 - 方法签名使用 Pydantic 请求/响应模型
- 📝 脚手架模板增强 - 新增 VSCode、EditorConfig、GitAttributes 配置

**详细内容**: 查看完整发布说明 [v3.38.0](docs/releases/v3.38.0.md)

### 新增
- `OpenAPIParser` Swagger 2.0 支持 - 从 parameters 提取请求体、支持 responses.schema 格式
- `_resolve_ref()` 方法 - 自动解析 $ref 引用获取完整 schema
- `to_snake_case()` 命名转换 - Java camelCase → Python snake_case
- `model_config = ConfigDict(populate_by_name=True)` - 支持双向兼容
- `Result[T]`、`PageInfo[T]` 通用响应包装类
- `.vscode/settings.json` 模板 - VSCode 工作区配置
- `.editorconfig` 模板 - 跨编辑器代码风格统一
- `.gitattributes` 模板 - Git 文件处理规则
- `Environment.LOCAL` - 本地开发环境枚举值
- debugging/metrics/monitoring Entry Points - 新增插件入口点
- `scripts/fetch_swagger.py` - Swagger 文档获取脚本，自动探测常见 API 端点
- 脚手架模板新增 `models/requests/` 和 `models/responses/` 示例
- 脚手架模板新增 `user_api.py` API 客户端示例
- `to_ascii_identifier()` - 中文 tag 自动转换为 ASCII 标识符（支持 pypinyin）
- `[codegen]` 可选依赖组 - pypinyin 用于中文 tag 转拼音

### 修复
- 修复模板文件 import 路径错误（`attach_json`, `step`）
- 修复 `$ref` 引用未解析导致模型字段为空的问题
- 为 `sync_playwright` 添加 ImportError 占位符
- 修复 OpenAPI 解析器未识别 `*/*` content-type 导致响应模型未生成的问题

### 文档
- 新增 `docs/releases/v3.38.0.md` - OpenAPI 增强发布说明
- 新增 `docs/guides/openapi_guide.md` - OpenAPI 代码生成器使用指南
- 新增 `docs/guides/scaffold_cli_guide.md` - 脚手架 CLI 工具指南
- 新增 `docs/architecture/TEST_EXECUTION_LIFECYCLE.md` - 测试执行流程文档

### 测试
- 1891 个测试全部通过

---

## [3.37.0] - 2025-12-21

### 现代化插件系统（v3.37.0）

**核心特性**: 完全重写 pytest 插件系统，采用 2025 年官方最佳实践，删除约 1000 行代码，大幅简化架构。

**主要变更**:
- 🔌 pytest11 Entry Points - pip install 后插件自动加载，无需手动配置
- 📝 pytest 9.0 原生 TOML - 使用 `[tool.pytest]` 替代 `[tool.pytest.ini_options]`
- 🎯 config 属性状态管理 - pytest 官方推荐方式，使用 `config._df_*` 属性
- 🧹 删除 managers.py - 移除 RuntimeContextManager/CacheManager 等管理器类

**详细内容**: 查看完整发布说明 [v3.37.0](docs/releases/v3.37.0.md)

### 新增
- `[project.entry-points.pytest11]` - 5 个自动发现的插件入口点
- `config._df_runtime` - RuntimeContext 存储属性
- `config._df_settings` - 框架配置存储属性
- `config._df_test_buses` - 测试隔离 EventBus 字典

### 移除
- `managers.py` - RuntimeContextManager、CacheManager、ConfigSettingsManager
- `pytest_plugins` 手动声明 - 由 Entry Points 自动处理

### 变更
- `[tool.pytest]` 替代 `[tool.pytest.ini_options]`
- `timeout = "30"` 字符串类型（pytest-timeout 兼容）

### 测试
- 1891 个测试全部通过，40 个跳过

---

## [3.36.1] - 2025-12-21

### 统一管理器重构插件系统（v3.36.1）

**核心特性**: 引入统一的管理器架构重构 pytest 插件系统（注意：此架构已在 v3.37.0 中被移除）。

**主要变更**:
- 🏗️ PluginLoadOrder - 插件加载顺序验证
- 💾 CacheManager - 配置缓存一致性管理
- 🔄 RuntimeContextManager - RuntimeContext 生命周期管理
- 🧪 TestEventBusManager - EventBus 测试隔离

**详细内容**: 查看完整发布说明 [v3.36.1](docs/releases/v3.36.1.md)

### 新增
- `managers.py` - 统一管理器模块（4 个管理器类）

### 变更
- `env_plugin.py` - 使用 CacheManager 统一缓存清除
- `core.py` - 使用 RuntimeContextManager 和 TestEventBusManager

---

## [3.36.0] - 2025-12-21

### 配置 API 现代化重构（v3.36.0）

**核心特性**: 删除废弃的 ConfigRegistry 和 manager.py，统一使用 settings.py 的现代化 API，净删除约 1870 行代码。

**主要变更**:
- 🎯 `get_settings()` - 惰性加载 + 单例缓存
- 📍 `get_config()` - 点号路径访问配置值
- 🔧 `get_settings_for_class()` - 自定义配置类支持
- 🧹 `clear_settings_cache()` - 清理缓存

**详细内容**: 查看完整发布说明 [v3.36.0](docs/releases/v3.36.0.md)

### 移除
- `ConfigRegistry` 类 - 使用 `get_config()` 替代
- `manager.py` - 使用 `settings.py` 函数替代
- `InterceptorConfig` - 直接使用中间件配置

### 变更
- `env_plugin.py` - 直接使用 `get_settings_for_class()`
- `core.py` - 使用 `config._settings` 替代 ConfigRegistry
- 脚手架模板 - 更新为现代化 API

---

## [3.35.7] - 2025-12-20

### UI 自动化可观测性集成（v3.35.7）

**核心特性**: 为 UI 自动化能力（BasePage）添加完整的可观测性支持，包括 EventBus 事件发布、实时日志、Allure 报告集成和视频录制。

**主要变更**:
- ✨ 新增 7 个 UI 事件类型（UINavigationStartEvent、UINavigationEndEvent、UIClickEvent、UIInputEvent、UIScreenshotEvent、UIWaitEvent、UIErrorEvent）
- ✨ BasePage 方法自动发布事件到 EventBus（goto/click/fill/screenshot/wait_for_selector）
- ✨ 新增 ui_logger() 实时日志支持（ObservabilityLogger 扩展）
- ✨ AllureObserver 自动处理 UI 事件并附加到报告
- ✨ 新增视频录制配置支持（BrowserManager + Fixtures）
- ✨ 更新脚手架模板支持 EventBus 和视频录制
- 🔧 敏感输入自动脱敏（密码字段等）
- 🔧 自动关联 OpenTelemetry 追踪上下文（trace_id/span_id）

**详细内容**: 查看完整发布说明 [v3.35.7](docs/releases/v3.35.7.md) 和设计文档 [ui-observability-design.md](docs/architecture/ui-observability-design.md)

### 新增
- `UINavigationStartEvent`、`UINavigationEndEvent` - 页面导航事件对
- `UIClickEvent` - 点击操作事件
- `UIInputEvent` - 输入操作事件（支持脱敏）
- `UIScreenshotEvent` - 截图事件
- `UIWaitEvent` - 等待事件
- `UIErrorEvent` - UI 错误事件
- `ui_logger()` - UI 组件日志记录器
- BasePage `event_bus` 参数 - 支持事件总线注入
- AllureObserver UI 事件处理器（7 个 async handler）
- BrowserManager `record_video`/`video_dir`/`video_size` - 视频录制配置
- `browser_record_video`/`browser_video_dir` - 视频录制 Fixtures
- `--record-video` - 命令行视频录制开关
- UI 脚手架模板增强 - EventBus 集成和视频录制支持

### 测试
- 新增 14 个视频录制和 Fixtures 单元测试
- 新增 3 个 GraphQL/Redis CLI 命令测试（v3.35.6 补充）
- 1587 个测试全部通过

---

## [3.35.6] - 2025-12-20

### 脚手架模板增强：GraphQL 和 Redis 支持（v3.35.6）

**核心特性**: 完善脚手架模板，新增 GraphQL 客户端和 Redis 使用示例模板，同步模板至框架最新版本。

**主要变更**:
- ✨ 新增 GraphQL 客户端生成器模板 - 支持 Query/Mutation/中间件
- ✨ 新增 GraphQL 测试示例模板 - 包含完整测试场景
- ✨ 新增 Redis Fixture 和测试示例模板 - 包含测试隔离支持
- ✨ 新增 YAML 分层配置生成 - 脚手架自动生成 config/ 目录
- 🔧 更新所有模板版本号至 v3.35.5
- 🔧 修复 BusinessError 使用方式（改用关键字参数）
- 🔧 更新类型注解为 Python 3.12+ 风格

**详细内容**: 查看完整发布说明 [v3.35.6](docs/releases/v3.35.6.md)

### 新增
- `GEN_GRAPHQL_CLIENT_TEMPLATE` - GraphQL 客户端生成器模板
- `GEN_TEST_GRAPHQL_TEMPLATE` - GraphQL 测试示例模板
- `GEN_REDIS_FIXTURE_TEMPLATE` - Redis Fixture 模板
- `GEN_TEST_REDIS_TEMPLATE` - Redis 测试示例模板
- `generate_graphql_client()` - 生成 GraphQL 客户端命令
- `generate_graphql_test()` - 生成 GraphQL 测试示例命令
- `generate_redis_fixture()` - 生成 Redis Fixture 命令
- 脚手架自动生成 YAML 配置文件（config/base.yaml, config/environments/*.yaml）

### 修复
- 修复 `base_api.py` 模板中 BusinessError 使用方式
- 修复 `api_client.py` 模板中类型注解（使用 `dict[str, Any]` 替代 `Dict`）
- 修复 `.gitignore` 模板缺少 YAML 配置排除规则
- 修复 `ui_conftest.py` 模板中不必要的 fixture 导入

### 测试
- 60 个 CLI 测试全部通过

---

## [3.35.5] - 2025-12-19

### 恢复深度合并和 _extends 继承（v3.35.5）

**核心特性**: 恢复 v3.35.3 的 `LayeredYamlSettingsSource`，解决 v3.35.4 YAML 对象级别替换导致的配置丢失问题。

**主要变更**:
- ✅ 恢复 `LayeredYamlSettingsSource` - 实现 YAML 文件之间的深度合并
- ✅ 恢复 `_extends` 继承语法 - 支持环境间继承、多级继承链
- ✅ 恢复 `ConfigLoader` 类 - 提供面向对象的配置加载方式
- 🔒 新增循环继承检测 - 自动检测并警告循环继承

**详细内容**: 查看完整发布说明 [v3.35.5](docs/releases/v3.35.5.md)

### 恢复
- `LayeredYamlSettingsSource` - 深度合并 YAML 配置
- `ConfigLoader` 类 - 面向对象配置加载
- `_extends` 继承语法 - 环境间继承

### 新增
- 循环继承检测 - 防止配置文件循环引用
- 多级继承链支持 - base.yaml → dev.yaml → staging.yaml

### 测试
- 14 个 loader 测试全部通过
- 62 个配置测试全部通过

---

## [3.35.4] - 2025-12-19 (已废弃，请使用 v3.35.5)

### 配置加载最佳实践重构（v3.35.4）

**核心特性**: 按照 pydantic-settings 最佳实践完全重构，使用内置 `YamlConfigSettingsSource`，移除 `_extends` 继承语法。

**⚠️ 问题**: YAML 对象级别替换导致配置丢失，已在 v3.35.5 修复。

**主要变更**:
- 🎯 使用内置 `YamlConfigSettingsSource` - 零自定义配置源代码
- 🗑️ 移除 `_extends` 继承语法 - 使用 base + env 双层合并
- 🗑️ 移除 `ConfigLoader` 类 - 仅保留 `load_config()` 函数
- 📉 代码量从 ~300 行减少到 ~100 行

**详细内容**: 查看完整发布说明 [v3.35.4](docs/releases/v3.35.4.md)

### 移除
- `ConfigLoader` 类（使用 `load_config()` 函数替代）
- `LayeredYamlSettingsSource` 自定义配置源（使用内置）
- `_extends` 继承语法支持

### 测试
- 62 个测试全部通过

---

## [3.35.3] - 2025-12-19

### 方案A最佳实现：LayeredYamlSettingsSource（v3.35.3）

**核心特性**: 创建 `LayeredYamlSettingsSource` 继承 `PydanticBaseSettingsSource`，完全融入 pydantic-settings 原生配置源体系。

**主要变更**:
- 🏗️ 新增 `LayeredYamlSettingsSource` - 自定义配置源，实现分层 YAML 加载
- 🔗 完全融入 pydantic-settings 配置源体系 - 在 `settings_customise_sources` 中组合配置源
- 📦 ConfigLoader 简化 - 不再手动加载 YAML，由配置源自动处理
- 🎯 面向对象设计 - 可继承 LayeredYamlSettingsSource 扩展功能

**详细内容**: 查看完整发布说明 [v3.35.3](docs/releases/v3.35.3.md)

### 新增
- `LayeredYamlSettingsSource` - pydantic-settings 原生配置源

### 重构
- `ConfigLoader.load()` 简化，使用 `_create_settings_class()` 工厂函数
- 配置源组合移到 `settings_customise_sources`

### 移除
- `ConfigLoader._cache` 属性（缓存移到 LayeredYamlSettingsSource）
- `ConfigLoader.clear_cache()` 方法

### 测试
- 更新 TestDeepMerge 测试 LayeredYamlSettingsSource
- 移除缓存相关测试
- 67 个测试全部通过

---

## [3.35.2] - 2025-12-19

### ConfigLoader 重构（v3.35.2）

**核心特性**: 使用 pydantic-settings 内置的 `nested_model_default_partial_update` 功能，移除所有手动环境变量解析代码。

**主要变更**:
- 🔧 移除 `_NESTED_CONFIG_KEYS` 硬编码列表
- 🔧 移除手动环境变量解析方法（`_parse_env_vars`, `_env_vars_to_nested_dict`, `_parse_env_value`）
- 🔧 使用 pydantic-settings 原生深度合并功能
- 📉 代码量从 ~400 行减少到 ~287 行

**详细内容**: 查看完整发布说明 [v3.35.2](docs/releases/v3.35.2.md)

### 重构
- `ConfigLoader` 使用 `nested_model_default_partial_update=True` 实现深度合并
- 移除 `_SettingsNoEnv` 临时子类 hack

### 测试
- 移除已删除方法的测试类
- 69 个测试全部通过

---

## [3.35.1] - 2025-12-18

### 嵌套配置深度合并修复（v3.35.1）

**核心修复**: 修复 YAML 分层配置与环境变量/secrets 深度合并问题，增强自定义配置类支持。

**主要修复**:
- 🔧 嵌套配置深度合并 - `SIGNATURE__SECRET` 现在正确与 YAML 配置合并，而非完全覆盖
- 🔧 插件执行顺序 - `env_plugin` 添加 `@hookimpl(tryfirst=True)` 确保先于 `core` 执行
- 🔧 自定义配置类 - `ConfigLoader` 和 `ConfigRegistry` 支持 `settings_class` 参数

**详细内容**: 查看完整发布说明 [v3.35.1](docs/releases/v3.35.1.md)

### 修复
- `ConfigLoader` 环境变量与 YAML 配置深度合并
- `env_plugin` 插件执行顺序问题（使用 `@hookimpl(tryfirst=True)`）
- `core.pytest_configure` 正确使用 `ConfigRegistry` 中的配置

### 增强
- `ConfigLoader` 支持 `settings_class` 参数指定自定义配置类
- `ConfigRegistry.initialize()` 支持 `settings_class` 参数
- `env_plugin` 自动从 `df_settings_class` 获取项目配置类

### 测试
- 新增环境变量清理 fixture 防止测试间污染
- 框架测试 80 passed

---

## [3.35.0] - 2025-12-18

### 环境管理（v3.35.0）

**核心特性**: 完整的环境管理系统，支持 YAML 分层配置、配置继承、统一配置访问。

**主要功能**:
- 🌍 多环境配置加载 - `FrameworkSettings.for_environment("staging")` 自动加载 `.env` + `.env.staging`
- 📁 YAML 分层配置 - `config/base.yaml` + `config/environments/{env}.yaml`
- 🔗 配置继承 - `_extends: base.yaml` 支持环境配置继承
- 🎯 ConfigRegistry 单例 - 统一配置访问入口，支持点号路径访问
- 🛠️ CLI 命令 - `df-test env show/init/validate`
- ⚡ Pytest 参数 - `pytest --env=staging --config-dir=config`
- 🔙 向后兼容 - 无 config/ 目录时自动回退到 .env 模式

**详细内容**: 查看完整发布说明 [v3.35.0](docs/releases/v3.35.0.md)

### 新增

#### 多环境配置 (`infrastructure/config/schema.py`)
- `EnvLiteral` 新增 "local" 环境类型
- `FrameworkSettings.for_environment(env)` - 多环境文件加载类方法
- `is_local` 属性 - 判断是否为本地环境

#### YAML 配置加载器 (`infrastructure/config/loader.py`)
- `ConfigLoader` - YAML 分层配置加载器
- `load_config(env, config_dir)` - 便捷加载函数
- 支持 `_extends` 配置继承
- 深度合并配置（嵌套字典递归合并）
- `config/secrets/.env.local` 敏感配置支持

#### 配置注册中心 (`infrastructure/config/registry.py`)
- `ConfigRegistry` - 全局配置单例
- `ConfigRegistry.initialize(env, config_dir)` - 初始化全局单例
- `ConfigRegistry.for_environment(env, config_dir)` - 为指定环境创建实例
- `registry.get("http.timeout")` - 点号路径访问
- 快捷属性 `registry.http`, `registry.db`, `registry.redis` 等

#### CLI 命令 (`cli/commands/env.py`)
- `df-test env show` - 显示当前环境配置
- `df-test env init` - 初始化配置目录结构
- `df-test env validate --env=staging` - 验证配置完整性
- `--config-dir` 参数支持自定义配置目录

#### Pytest 插件 (`testing/plugins/env_plugin.py`)
- `--env` 命令行参数 - 指定运行环境
- `--config-dir` 命令行参数 - 指定配置目录
- `config_registry` fixture - 配置注册中心
- `settings` fixture - 框架配置
- `current_env` fixture - 当前环境名称

### 测试
- 新增 44 个单元测试，覆盖 ConfigLoader 和 ConfigRegistry

---

## [3.34.1] - 2025-12-17

### MQ 事件架构重构（Bug Fix）

**核心特性**: 修复 v3.14.0 以来 MQ 事件系统的架构缺陷，统一为 Start/End/Error 三态模式，与 HTTP/gRPC/GraphQL 架构保持一致。

**问题描述**:
- v3.14.0 的 MQ 事件实现存在严重架构问题
- 事件定义字段（message_id, body_size）从未被正确填充
- MQ 客户端传递的参数（queue_type, message）与事件定义不匹配
- 缺少 Start/End/Error 三态模式，无法进行完整的请求追踪

**修复内容**:
- ✅ 重构 MQ 事件为 Start/End/Error 三态模式
- ✅ 所有 MQ 事件继承 `CorrelatedEvent`，支持 correlation_id 关联
- ✅ 添加工厂方法 `create()` 自动注入 OpenTelemetry 追踪上下文
- ✅ 新增 `messenger_type` 字段区分 kafka/rabbitmq/rocketmq
- ✅ 统一 KafkaClient、RabbitMQClient、RocketMQClient 的事件发布

**新增事件类型**:
- `MessagePublishStartEvent` - 消息发布开始
- `MessagePublishEndEvent` - 消息发布成功
- `MessagePublishErrorEvent` - 消息发布失败
- `MessageConsumeStartEvent` - 消息消费开始
- `MessageConsumeEndEvent` - 消息消费成功
- `MessageConsumeErrorEvent` - 消息消费失败

**影响范围**:
- `core/events/types.py` - 事件类型定义
- `core/events/__init__.py` - 事件导出
- `capabilities/messengers/queue/kafka/client.py` - Kafka 客户端
- `capabilities/messengers/queue/rabbitmq/client.py` - RabbitMQ 客户端
- `capabilities/messengers/queue/rocketmq/client.py` - RocketMQ 客户端
- `testing/reporting/allure/observer.py` - Allure 报告集成
- `plugins/builtin/reporting/allure_plugin.py` - Allure 插件
- `testing/debugging/console.py` - 控制台调试器

**⚠️ 破坏性变更**: 删除了原 `MessagePublishEvent` 和 `MessageConsumeEvent`，替换为新的 Start/End/Error 事件。如果有直接订阅这些事件的代码，需要迁移到新的事件类型。

**详细内容**: 查看完整发布说明 [v3.34.1](docs/releases/v3.34.1.md)

---

## [3.34.0] - 2025-12-17

### ConsoleDebugObserver MQ 事件支持

**核心特性**: ConsoleDebugObserver 新增 MQ（消息队列）事件支持，实时显示消息发布和消费详情。

**主要功能**:
- 📤 消息发布显示 - 实时显示 topic、message_id、body_size、partition
- 📥 消息消费显示 - 实时显示 consumer_group、处理耗时、offset
- 🎛️ 独立开关 - show_mq 参数控制 MQ 调试输出
- 🎨 彩色输出 - 发布用青色(cyan)，消费用黄色(yellow)

**详细内容**: 查看完整发布说明 [v3.34.0](docs/releases/v3.34.0.md)

### 新增

#### ConsoleDebugObserver MQ 支持 (`testing/debugging/console.py`)
- `MQMessageRecord` - MQ 消息记录数据类
- `show_mq` 参数 - 控制 MQ 调试输出（默认 True）
- `_handle_mq_publish()` - 处理消息发布事件
- `_handle_mq_consume()` - 处理消息消费事件
- `_print_mq_publish()` - 打印消息发布信息
- `_print_mq_consume()` - 打印消息消费信息

#### create_console_debugger 函数
- 新增 `show_mq` 参数

### 文档
- 更新 `docs/architecture/ROADMAP_V3.29_ENHANCEMENTS.md` - v3.34.0 实施记录

---

## [3.33.0] - 2025-12-17

### GraphQL 中间件系统

**核心特性**: GraphQL 客户端集成中间件系统（洋葱模型），支持事件驱动的可观测性。与 HTTP/gRPC 客户端架构统一。

**主要功能**:
- 🧩 中间件系统 - GraphQL 专用中间件（与 HTTP/gRPC 一致的洋葱模型）
- 📊 自动事件发布 - GraphQLEventPublisherMiddleware
- 🔄 重试中间件 - GraphQLRetryMiddleware（网络错误/GraphQL 错误重试）
- 📝 日志中间件 - GraphQLLoggingMiddleware
- 🎯 Allure 报告集成 - 自动记录 GraphQL 调用
- 🖥️ 控制台调试支持 - 实时显示 GraphQL 请求/响应

**详细内容**: 查看完整发布说明 [v3.33.0](docs/releases/v3.33.0.md)

### 新增

#### GraphQL 中间件基类 (`capabilities/clients/graphql/middleware/`)
- `GraphQLMiddleware` - 继承自 `BaseMiddleware[GraphQLRequest, GraphQLResponse]`
- `GraphQLLoggingMiddleware` - 日志中间件（priority=0）
- `GraphQLRetryMiddleware` - 重试中间件（priority=10）
- `GraphQLEventPublisherMiddleware` - 事件发布中间件（priority=999，最内层）

#### GraphQL 事件类型 (`core/events/types.py`)
- `GraphQLRequestStartEvent` - 请求开始事件
- `GraphQLRequestEndEvent` - 请求结束事件（含 has_errors、error_count）
- `GraphQLRequestErrorEvent` - 请求错误事件（HTTP 传输层错误）

### 重构

#### GraphQLClient (`capabilities/clients/graphql/client.py`)
- 新增 `middlewares` 参数 - 支持自定义中间件列表
- 新增 `event_bus` 参数 - 注入 EventBus 实例
- 新增 `use()` 方法 - 链式添加中间件
- 自动添加 GraphQLEventPublisherMiddleware
- 内部使用 `MiddlewareChain` 执行中间件链

#### GraphQL 数据模型 (`capabilities/clients/graphql/models.py`)
- `GraphQLRequest` - 新增 `url`、`headers`、`operation_type`、`variables_json`、`to_payload()` 字段/方法
- `GraphQLResponse` - 新增 `has_errors`、`data_json` 属性

#### Allure 报告支持 (`testing/reporting/allure/observer.py`)
- 新增 `handle_graphql_request_start_event` - 处理请求开始事件
- 新增 `handle_graphql_request_end_event` - 处理请求结束事件
- 新增 `handle_graphql_request_error_event` - 处理请求错误事件

#### 控制台调试支持 (`testing/debugging/console.py`)
- 新增 `GraphQLCallRecord` 数据类
- 新增 GraphQL 调试选项（show_graphql、show_graphql_query、show_graphql_variables）
- 实时显示 GraphQL 请求/响应/错误信息

### 文档
- 更新 `docs/architecture/ROADMAP_V3.29_ENHANCEMENTS.md` - v3.33.0 实施记录

---

## [3.32.0] - 2025-12-17

### gRPC 中间件系统重构 + 事件系统统一

**核心特性**: gRPC 客户端从拦截器模式重构为中间件模式，与 HTTP 客户端架构统一。同时集成事件系统，支持 Allure 报告和控制台调试。

**主要功能**:
- 🔄 中间件模式 - 从 Interceptor 重构为 Middleware（与 HTTP 一致）
- 🔗 GrpcEventPublisherMiddleware - gRPC 事件发布中间件
- 📊 Allure 报告集成 - 自动记录 gRPC 调用详情
- 🖥️ 控制台调试支持 - 实时显示 gRPC 请求/响应

**详细内容**: 查看完整发布说明 [v3.32.0](docs/releases/v3.32.0.md)

### 重构

#### gRPC 中间件系统 (`capabilities/clients/grpc/middleware/`)
- **从拦截器模式重构为中间件模式**（与 HTTP 客户端架构统一）
- 新增 `GrpcMiddleware` - 中间件基类，继承自 `BaseMiddleware[GrpcRequest, GrpcResponse]`
- 新增 `GrpcLoggingMiddleware` - 日志中间件
- 新增 `GrpcMetadataMiddleware` - 元数据中间件
- 新增 `GrpcRetryMiddleware` - 重试中间件（指数退避）
- 新增 `GrpcTimingMiddleware` - 耗时统计中间件
- 新增 `GrpcEventPublisherMiddleware` - 事件发布中间件
- 新增 `GrpcRequest` 数据类 - 包装请求信息用于中间件链
- 使用 `MiddlewareChain` 执行中间件（洋葱模型）

#### GrpcClient 重构 (`capabilities/clients/grpc/client.py`)
- `interceptors` 参数更名为 `middlewares`
- 使用 `MiddlewareChain` 替代手动拦截器调用
- 新增 `use()` 方法 - 链式添加中间件
- 中间件按 priority 排序执行

#### GrpcTracingInterceptor 重构 (`infrastructure/tracing/interceptors/grpc.py`)
- 重构为 `GrpcTracingMiddleware`（保留向后兼容别名）
- 继承新的 `GrpcMiddleware` 基类

### 删除
- 删除 `capabilities/clients/grpc/interceptors.py` - 旧的拦截器模式已完全迁移到中间件

### 新增

#### gRPC 事件类型 (`core/events/types.py`)
- `GrpcRequestStartEvent` - gRPC 请求开始事件
- `GrpcRequestEndEvent` - gRPC 请求结束事件
- `GrpcRequestErrorEvent` - gRPC 请求错误事件

#### GrpcClient 增强 (`capabilities/clients/grpc/client.py`)
- 新增 `enable_events` 参数 - 控制事件发布（默认启用）
- 新增 `service_name` 参数 - 自定义服务名称
- 自动添加 GrpcEventPublisherMiddleware（当 enable_events=True）
- 新增 `_extract_service_name()` 方法 - 从 stub 类提取服务名

#### Allure 报告支持 (`plugins/builtin/reporting/allure_plugin.py`)
- 新增 gRPC 事件处理器
- 自动记录 gRPC 调用到 Allure 步骤
- 显示服务名、方法名、状态码、耗时
- 支持请求/响应数据附件

#### 控制台调试支持 (`testing/debugging/console.py`)
- 新增 `GrpcCallRecord` 数据类
- 新增 gRPC 显示选项（show_grpc、show_grpc_metadata、show_grpc_data）
- 实时显示 gRPC 请求/响应/错误信息

### 文档
- 新增 `docs/releases/v3.32.0.md` - 完整版本发布说明

### 测试
- 新增 52 个 gRPC 中间件测试（test_middleware.py）
- 更新 26 个 GrpcClient 测试以适配中间件模式
- 更新 GrpcTracingMiddleware 测试

---

## [3.31.0] - 2025-12-17

### Factory 系统重构

**核心特性**: Factory 系统重构，融合 factory_boy 和 polyfactory 最佳实践，提供声明式 API。

**主要功能**:
- 🏭 Factory 重构 - 现代化声明式 API，支持泛型类型提示
- 🎯 Trait 支持 - 预设配置组，通过布尔标志激活
- 🔗 SubFactory/PostGenerated - 嵌套工厂和后处理字段
- 📦 8 个预置工厂 - 覆盖常见业务场景

**详细内容**: 查看完整发布说明 [v3.31.0](docs/releases/v3.31.0.md)

### 新增

#### Factory 核心类 (`testing/data/factories/base.py`)
- `Factory[T]` - 泛型工厂基类，声明式字段定义
- `FactoryMeta` - 元类，自动收集声明式字段
- `Sequence` - 自增序列生成器
- `LazyAttribute` - 延迟计算属性（可访问其他字段）
- `PostGenerated` - 后处理字段（所有字段生成后计算）
- `SubFactory` - 嵌套工厂支持
- `FakerAttribute` - Faker 数据生成器
- `Use` - 直接调用函数生成值
- `Trait` - 预设配置组

#### 预置工厂 (`testing/data/factories/examples.py`)
- `UserFactory` - 用户工厂（支持 admin/vip/inactive Trait）
- `ProductFactory` - 商品工厂（支持 on_sale/out_of_stock Trait）
- `AddressFactory` - 地址工厂
- `OrderFactory` - 订单工厂（支持 pending/paid/shipped/completed Trait）
- `PaymentFactory` - 支付工厂（支持 alipay/wechat/bank_card Trait）
- `CardFactory` - 银行卡工厂（支持 visa/mastercard Trait）
- `ApiResponseFactory` - API 响应工厂（支持 error/paginated Trait）
- `PaginationFactory` - 分页工厂

### 废弃
- `df_test_framework.testing.factories` 模块 - 已迁移到 `testing.data.factories`，将在 v4.0.0 移除

### 文档
- 新增 `docs/releases/v3.31.0.md` - 完整版本发布说明
- 更新 `docs/architecture/ROADMAP_V3.29_ENHANCEMENTS.md` - 移除时间估算，更新版本规划

### 测试
- 新增 96 个 Factory 相关测试，全部通过

---

## [3.30.0] - 2025-12-16

### 断言增强

**核心特性**: 新增独立 JSON Schema 验证器和自定义匹配器，增强断言能力。

**主要功能**:
- 🔍 SchemaValidator - 独立的 JSON Schema 验证器
- 🎯 自定义匹配器 - 15+ 匹配器类，支持组合、取反、操作符重载
- 📋 预定义 Schema - 常用业务 Schema 模板

**详细内容**: 查看完整发布说明 [v3.30.0](docs/releases/v3.30.0.md)

### 新增

#### JSON Schema 验证 (`testing/assertions/json_schema.py`)
- `SchemaValidator` - 独立验证器类
- `SchemaValidationError` - 验证错误异常
- `assert_schema()` - 快捷验证函数
- `validate_response_schema()` - HTTP 响应验证
- `create_object_schema()` / `create_array_schema()` - Schema 构建器
- `COMMON_SCHEMAS` - 预定义 Schema（id、uuid、email、phone_cn、pagination、api_response）

#### 自定义匹配器 (`testing/assertions/matchers.py`)
- `RegexMatcher` - 正则匹配
- `ContainsMatcher` - 包含匹配
- `InRangeMatcher` - 范围匹配
- `TypeMatcher` - 类型匹配
- `LengthMatcher` - 长度匹配
- `AllOfMatcher` / `AnyOfMatcher` - 组合匹配
- `NotMatcher` - 取反匹配
- 快捷函数: `matches_regex()`, `contains()`, `in_range()`, `equals()`, `is_type()`, `has_length()`, `all_of()`, `any_of()`, `starts_with()`, `ends_with()`, `greater_than()`, `less_than()`
- 预定义实例: `is_none`, `is_not_none`, `is_true`, `is_false`, `is_empty`, `is_not_empty`, `is_string`, `is_int`, `is_float`, `is_number`, `is_bool`, `is_list`, `is_dict`, `is_date`

### 依赖
- 新增 `jsonpath-ng>=1.7.0` - JSONPath 查询支持

### 文档
- 新增 `docs/releases/v3.30.0.md` - 完整版本发布说明

### 测试
- 新增 85 个单元测试，全部通过

---

## [3.29.0] - 2025-12-16

### utils/ 模块重构与 Factory 模式

**核心特性**: utils/ 模块重构，功能迁移到正确的架构层级；新增 Factory 模式。

**主要功能**:
- 🏗️ utils/ 重构 - 功能迁移到正确的五层架构位置
- 🏭 Factory 模式 - 新增测试数据工厂，创建完整业务对象
- ♻️ 向后兼容 - utils 模块保留废弃导出，将在 v4.0.0 移除

**详细内容**: 查看完整发布说明 [v3.29.0](docs/releases/v3.29.0.md)

### 迁移

| 原位置 | 新位置 |
|--------|--------|
| `utils.data_generator` | `testing.data.generators` |
| `utils.assertion` | `testing.assertions` |
| `utils.resilience` | `infrastructure.resilience` |
| `utils.decorator` | `core.decorators` |
| `utils.types` | `core.types` |

### 新增

#### 测试数据工厂 (`testing/data/factories/`)
- `Factory` - 工厂基类，创建完整业务对象
- `ModelFactory` - 带类型提示的工厂基类
- `FactoryMeta` - 工厂元配置

#### 弹性工具 (`infrastructure/resilience/`)
- `CircuitBreaker` - 熔断器（从 utils 迁移）
- `CircuitOpenError` - 熔断器打开异常
- `CircuitState` - 熔断器状态枚举
- `circuit_breaker` - 熔断器装饰器

#### 通用装饰器 (`core/decorators.py`)
- `retry_on_failure` - 失败重试装饰器
- `log_execution` - 执行日志装饰器
- `deprecated` - 废弃标记装饰器
- `cache_result` - 缓存结果装饰器

#### Pydantic 序列化类型 (`core/types.py`)
- `DecimalAsFloat` - Decimal 序列化为浮点数
- `DecimalAsCurrency` - Decimal 序列化为货币格式

### 废弃
- `df_test_framework.utils` 模块 - 保留向后兼容，将在 v4.0.0 移除

### 文档
- 新增 `docs/releases/v3.29.0.md` - 完整版本发布说明

### 测试
- 所有迁移保持向后兼容，现有代码无需立即修改

---

## [3.28.1] - 2025-12-14

### Bug 修复与改进

**核心特性**: 修复 ConsoleDebugObserver 事件订阅问题，添加 `-s` 标志提示。

**主要功能**:
- 🐛 修复 ConsoleDebugObserver 使用事件类型类订阅（修复 AttributeError）
- 💡 添加 `-s` 标志提示 - 当调试启用但 stderr 被捕获时显示提示

**详细内容**: 查看完整发布说明 [v3.28.1](docs/releases/v3.28.1.md)

### 修复
- `ConsoleDebugObserver.subscribe()` - 改用事件类型类订阅，保持类型安全

### 新增
- `_show_s_flag_hint()` - 当调试启用但 stderr 被捕获时显示提示

### 文档
- 更新 `docs/architecture/observability-debugging-unification.md` - 说明 `-s` 标志要求
- 新增 `docs/releases/v3.28.1.md` - 完整版本发布说明

---

## [3.28.0] - 2025-12-14

### 调试系统重构与简化

**核心特性**: 统一调试系统，移除 HTTPDebugger/DBDebugger，新增 @pytest.mark.debug marker 支持特定测试调试。

**主要功能**:
- 🎯 调试系统统一 - 移除 HTTPDebugger/DBDebugger，统一使用 ConsoleDebugObserver
- 🏷️ @pytest.mark.debug - 新增 marker，为特定测试启用调试输出
- 🔧 显式 fixture 优先 - console_debugger 显式使用时忽略全局 DEBUG_OUTPUT 配置

**详细内容**: 查看完整发布说明 [v3.28.0](docs/releases/v3.28.0.md)

### 新增

#### 调试控制优先级（`testing/fixtures/debugging.py`）
- `@pytest.mark.debug` marker - 强制启用调试输出
- `_auto_debug_by_marker` fixture - 自动检测 marker 或全局配置
- 显式 fixture 优先 - console_debugger 显式使用时始终创建调试器

### 移除
- `HTTPDebugger` - 旧版 HTTP 调试器（v3.27.0 已废弃）
- `DBDebugger` - 旧版数据库调试器
- `http_debugger` fixture - 改用 console_debugger
- `enable_http_debug()` / `disable_http_debug()` - 全局函数
- `enable_db_debug()` / `disable_db_debug()` - 全局函数

### 文档
- 新增 `docs/releases/v3.28.0.md` - 完整版本发布说明
- 更新 `docs/architecture/observability-debugging-unification.md` - 设计文档

---

## [3.27.0] - 2025-12-14

### 调试系统统一与 pytest 集成

**核心特性**: 统一调试系统架构，ConsoleDebugObserver 增加 pytest 模式自动检测，HTTPDebugger 标记为废弃。

**主要功能**:
- 🔧 ConsoleDebugObserver pytest 集成 - 自动检测 pytest 模式，通过 loguru 桥接输出
- ⚠️ HTTPDebugger 废弃公告 - 推荐使用 ConsoleDebugObserver（事件驱动）

**详细内容**: 查看完整发布说明 [v3.27.0](docs/releases/v3.27.0.md)

### 废弃
- `HTTPDebugger` - 已废弃，推荐使用 `ConsoleDebugObserver`

### 文档
- 新增 `docs/architecture/observability-debugging-unification.md` - 可观测性与调试系统统一设计
- 新增 `docs/releases/v3.27.0.md` - 完整版本发布说明

**注意**: v3.27.0 的 `use_pytest_bridge` 参数已在 v3.28.0 中移除。

---

## [3.26.0] - 2025-12-14

### pytest 日志集成重构

**核心特性**: 重构 loguru 与 pytest 的日志集成，采用 loguru → logging 桥接模式，解决日志与测试名称混行问题。

**主要功能**:
- 📋 `logging_plugin` - pytest 插件，自动配置 loguru → logging 桥接
- ✨ `setup_pytest_logging()` - 手动配置 API
- ✅ caplog 原生支持 - loguru 日志被 pytest caplog 正确捕获

**详细内容**: 查看完整发布说明 [v3.26.0](docs/releases/v3.26.0.md)

### 新增

#### 日志集成模块（`infrastructure/logging/pytest_integration.py`）
- `setup_pytest_logging()` - 配置 loguru → logging 桥接
- `teardown_pytest_logging()` - 清理桥接，恢复默认行为

#### pytest 插件（`testing/plugins/logging_plugin.py`）
- `pytest_configure` hook - 自动配置日志桥接
- `pytest_unconfigure` hook - 自动清理

#### pytest 模式控制（`infrastructure/logging/logger.py`）
- `set_pytest_mode()` - 设置 pytest 模式标志
- `is_pytest_mode()` - 检查是否在 pytest 模式下运行

### 变更
- `setup_logger()` - 新增 pytest 模式支持，自动使用桥接 handler

### 移除
- `testing/fixtures/core.py` 中的 `caplog` fixture 覆盖

### 文档
- 新增 `docs/releases/v3.26.0.md` - 完整版本发布说明
- 新增 `docs/guides/logging_pytest_integration.md` - pytest 日志集成指南（含方案设计决策）

### 测试
- 新增 7 个测试用例，全部通过

---

## [3.25.0] - 2025-12-14

### 认证管理能力增强

**核心特性**: 增强 HttpClient 的认证管理能力，简化登出后的状态清理，新增认证状态查询和 Cookie 精细控制。

**主要功能**:
- ✨ `reset_auth_state()` - 组合方法，一次调用完全清除认证状态
- ✨ `get_auth_info()` - 查询当前认证状态，方便调试
- ✨ `clear_cookie(name)` - 精细控制，只删除指定的 Cookie
- ✨ `get_cookies()` - 获取当前所有 Cookies
- ✨ `ApiKeyMiddleware` 增强 - 支持 `skip_api_key` 和 `custom_api_key`

**详细内容**: 查看完整发布说明 [v3.25.0](docs/releases/v3.25.0.md)

### 新增

#### HttpClient 方法（`capabilities/clients/http/rest/httpx/client.py`）
- `reset_auth_state()` - 组合调用 `clear_auth_cache()` + `clear_cookies()`
- `get_auth_info()` - 返回认证状态字典（Token 缓存、Cookies 等）
- `clear_cookie(name)` - 删除指定的 Cookie，返回是否成功
- `get_cookies()` - 返回当前所有 Cookies 字典

#### ApiKeyMiddleware 增强（`middleware/auth.py`）
- `skip_api_key` metadata - 跳过 API Key 添加
- `custom_api_key` metadata - 使用自定义 API Key

### 文档
- 新增 `docs/releases/v3.25.0.md` - 完整版本发布说明
- 更新 `docs/guides/auth_session_guide.md` - 添加新方法说明

### 测试
- 新增 12 个测试用例，全部通过

---

## [3.24.0] - 2025-12-14

### Metrics 事件驱动重构

**核心特性**: MetricsObserver 订阅 EventBus 自动收集 Prometheus 指标，三大可观测性支柱全部统一到事件驱动架构。

**主要功能**:
- ✨ `MetricsObserver` - 事件驱动的 Prometheus 指标收集器
- ✨ `metrics_observer` fixture - 自动订阅 HTTP/DB/Cache 事件收集指标
- ✨ 路径规范化 - 自动将 `/users/123` 规范化为 `/users/{id}`，避免高基数
- 🗑️ 删除 `MetricsInterceptor` - 旧的拦截器模式已移除

**详细内容**: 查看完整发布说明 [v3.24.0](docs/releases/v3.24.0.md)

### 新增

#### MetricsObserver（`infrastructure/metrics/observer.py`）
- 订阅 HTTP 事件：`HttpRequestStart/End/Error`
- 订阅 Database 事件：`DatabaseQueryStart/End/Error`
- 订阅 Cache 事件：`CacheOperationStart/End/Error`
- 路径规范化：数字 ID → `{id}`，UUID → `{uuid}`
- 基数限制：防止高基数指标

#### 指标（自动收集）
- `http_requests_total` - 请求总数（method, path, status）
- `http_request_duration_seconds` - 请求耗时直方图
- `http_requests_in_flight` - 进行中请求数
- `http_errors_total` - 错误总数
- `db_queries_total` - 查询总数
- `db_query_duration_seconds` - 查询耗时
- `db_rows_affected` - 影响行数
- `cache_operations_total` - 缓存操作总数
- `cache_hits_total` / `cache_misses_total` - 命中/未命中

#### Fixtures（`testing/fixtures/metrics.py`）
- `metrics_manager` - Prometheus 指标管理器（Session 级别）
- `metrics_observer` - 事件驱动指标收集器（Session 级别）
- `test_metrics_observer` - 测试级别指标收集器（Function 级别）

### 删除
- `infrastructure/metrics/integrations/` - 整个目录已删除
- `MetricsInterceptor` - 旧的拦截器模式
- `HttpMetrics` / `DatabaseMetrics` - 旧的指标类

### 文档
- 新增 `docs/releases/v3.24.0.md` - 完整版本发布说明
- 更新 `docs/architecture/observability-architecture.md` - 添加 MetricsObserver
- 更新 `docs/architecture/eventbus-integration-analysis.md` - 标记 Metrics 重构完成

### 测试
- 新增 16 个测试用例（9 通过，7 因无 prometheus_client 跳过）

---

## [3.23.0] - 2025-12-13

### ObservabilityConfig 统一配置

**核心特性**: 统一可观测性配置，caplog fixture 集成 loguru。

**主要功能**:
- ✨ `ObservabilityConfig` - 统一控制 Allure 记录和调试输出
- ✨ `caplog` fixture - 桥接 loguru 到 pytest 日志捕获
- ⚠️ `enable_event_publisher` 废弃 - 事件始终发布

**详细内容**: 查看完整发布说明 [v3.23.0](docs/releases/v3.23.0.md)

### 新增

#### ObservabilityConfig（`infrastructure/config/schema.py`）
- `enabled` - 总开关（控制所有观察者）
- `allure_recording` - Allure 记录开关
- `debug_output` - 调试输出开关

#### Fixtures
- `caplog` - 覆盖 pytest caplog，集成 loguru 日志

### 废弃
- `enable_event_publisher` 参数 - 事件始终发布，使用 ObservabilityConfig 控制观察者

### 文档
- 新增 `docs/releases/v3.23.0.md` - 完整版本发布说明
- 更新可观测性架构文档

---

## [3.22.1] - 2025-12-13

### ConsoleDebugObserver 数据库调试

**核心特性**: ConsoleDebugObserver 支持数据库 SQL 查询的彩色调试输出。

**主要功能**:
- ✨ 数据库查询事件订阅 - DatabaseQueryStart/End/Error
- ✨ 彩色 SQL 输出 - 操作类型、表名、耗时、行数
- ✨ 新增配置选项 - show_database, show_sql, show_sql_params

**详细内容**: 查看完整发布说明 [v3.22.1](docs/releases/v3.22.1.md)

### 新增

#### ConsoleDebugObserver 配置
- `show_database` - 是否显示数据库查询
- `show_sql` - 是否显示 SQL 语句
- `show_sql_params` - 是否显示 SQL 参数
- `max_sql_length` - 最大 SQL 显示长度

#### 事件订阅
- `DatabaseQueryStartEvent` - 查询开始
- `DatabaseQueryEndEvent` - 查询完成
- `DatabaseQueryErrorEvent` - 查询错误

### 文档
- 新增 `docs/releases/v3.22.1.md` - 完整版本发布说明

---

## [3.22.0] - 2025-12-13

### HTTP 可观测性增强

**核心特性**: 重构 HTTP 事件发布机制，确保 Allure 报告记录完整的请求头和参数。

**主要功能**:
- ✨ `HttpEventPublisherMiddleware` - 在中间件链内部发布事件，记录完整 headers
- ✨ `HttpRequestStartEvent.params` - 支持记录 GET 请求参数
- ✨ `ConsoleDebugObserver` - 现代化彩色控制台调试器（事件驱动）
- ✨ `console_debugger` fixture - 自动订阅事件的调试 fixture

**详细内容**: 查看完整发布说明 [v3.22.0](docs/releases/v3.22.0.md)

### 新增

#### 事件系统
- `HttpRequestStartEvent.params` - GET 请求参数字段

#### 中间件
- `HttpEventPublisherMiddleware` - 事件发布中间件（priority=999）

#### HttpClient
- `enable_event_publisher` 参数 - 控制是否启用事件发布（默认 True）

#### 调试工具
- `ConsoleDebugObserver` - 现代化控制台调试器
- `create_console_debugger()` - 创建调试器便捷函数

#### Fixtures
- `console_debugger` - 控制台调试 fixture
- `http_debugger` - HTTP 调试 fixture
- `debug_mode` - 调试模式便捷 fixture

### 修复
- **Allure 请求头为空** - 事件发布移至中间件链内部，现在记录完整 headers
- **中间件添加的 headers 不可见** - 现在能记录 Authorization、签名等中间件添加的头

### 文档
- 新增 `docs/releases/v3.22.0.md` - 完整版本发布说明

---

## [3.21.0] - 2025-12-13

### Session 管理增强

**核心特性**: 新增 `clear_cookies()` 方法，解决认证流程测试中的 Session Token 复用问题。

**主要功能**:
- ✨ `clear_cookies()` - 清除 httpx 客户端的 Cookies，强制服务器创建新 Session

**详细内容**: 查看完整发布说明 [v3.21.0](docs/releases/v3.21.0.md)

### 新增
- 新增 `HttpClient.clear_cookies()` 方法 - 清除 httpx 客户端的 Cookies

### 文档
- 新增 `docs/releases/v3.21.0.md` - 完整版本发布说明
- 新增 `docs/guides/auth_session_guide.md` - 认证与 Session 管理指南

---

## [3.20.0] - 2025-12-12

### HTTP 能力完善

**核心特性**: 完善 HTTP 客户端能力，新增 multipart/form-data 文件上传、raw body 二进制数据支持，以及 HEAD/OPTIONS HTTP 方法。

**主要功能**:
- ✨ `files` 参数 - 支持 multipart/form-data 文件上传和混合表单
- ✨ `content` 参数 - 支持 application/octet-stream 二进制数据和 text/plain 纯文本
- ✨ `HEAD` 方法 - 检查资源存在性和获取元数据
- ✨ `OPTIONS` 方法 - CORS 预检和 API 元信息获取

**详细内容**: 查看完整发布说明 [v3.20.0](docs/releases/v3.20.0.md)

### 新增

#### Request 类
- 新增 `files` 字段 - 存储 multipart/form-data 文件数据
- 新增 `content` 字段 - 存储 raw body 数据（bytes 或 str）
- 新增 `with_file()` 方法 - 添加单个文件
- 新增 `with_files()` 方法 - 设置文件字典或列表
- 新增 `with_form_field()` 方法 - 添加表单字段
- 新增 `with_form_fields()` 方法 - 批量添加表单字段
- 新增 `with_content()` 方法 - 设置 raw body 内容

#### 类型定义
- 新增 `FileTypes` - 单文件类型定义（bytes | tuple）
- 新增 `FilesTypes` - 文件集合类型定义（dict | list）

#### HttpClient
- 新增 `head()` 方法 - HEAD 请求
- 新增 `options()` 方法 - OPTIONS 请求
- `post/put/patch` 新增 `files` 参数
- `post/put/patch` 新增 `content` 参数

#### BaseAPI
- 新增 `head()` 方法 - HEAD 请求
- 新增 `options()` 方法 - OPTIONS 请求
- `post/put/patch` 新增 `files` 参数

#### LoggingMiddleware
- 新增 `_format_files_info()` 方法 - 格式化文件元信息日志
- 新增 `_format_content_info()` 方法 - 格式化 content 日志
- 新增 `_extract_file_info()` 方法 - 提取单个文件元信息
- 支持记录 files 参数（文件名、大小、MIME 类型）
- 支持记录 content 参数（类型、大小）

### 文档
- 新增 `docs/releases/v3.20.0.md` - 完整版本发布说明
- 新增 `docs/guides/httpx_advanced_usage.md` - httpx 高级用法参考指南
- 更新 `docs/plans/RFC_MULTIPART_FORM_DATA_SUPPORT.md` - 扩展为 HTTP 能力完善 RFC

### 测试
- 新增 `tests/capabilities/clients/http/core/test_request.py` - Request 新功能单元测试（19 个测试）
- 新增 `tests/capabilities/clients/http/core/test_multipart.py` - multipart 集成测试（19 个测试）
- 扩展 `tests/capabilities/clients/http/middleware/test_logging.py` - LoggingMiddleware files/content 测试（23 个测试）

---

## [3.19.0] - 2025-12-11

### 认证控制增强

**核心特性**: 新增请求级别认证控制，支持跳过认证和自定义 Token，解决认证测试场景中的隔离问题。

**主要功能**:
- ✨ `skip_auth` 参数 - API 方法级别跳过认证中间件
- ✨ `token` 参数 - API 方法级别使用自定义 Token
- ✨ `clear_auth_cache()` - 清除 Token 缓存支持完整认证流程测试
- ✨ `Request.metadata` - 请求元数据支持中间件行为控制

**详细内容**: 查看完整发布说明 [v3.19.0](docs/releases/v3.19.0.md)

### 新增
- 新增 `Request.metadata` 字段 - 用于中间件控制（skip_auth, custom_token）
- 新增 `Request.with_metadata()` 方法 - 设置请求元数据
- 新增 `Request.get_metadata()` 方法 - 获取请求元数据
- 新增 `BearerTokenMiddleware.clear_cache()` 方法 - 清除 Token 缓存
- 新增 `HttpClient.clear_auth_cache()` 方法 - 清除所有认证中间件缓存
- 新增 `BaseAPI.get/post/put/delete/patch` 的 `skip_auth` 参数
- 新增 `BaseAPI.get/post/put/delete/patch` 的 `token` 参数

### 改进
- `BearerTokenMiddleware` 支持检查 `Request.metadata.skip_auth` 跳过认证
- `BearerTokenMiddleware` 支持检查 `Request.metadata.custom_token` 使用自定义 Token
- `HttpClient._prepare_request_object` 支持 `skip_auth` 和 `token` 参数

### 文档
- 新增 `docs/releases/v3.19.0.md` - 完整版本发布说明
- 更新 `docs/guides/middleware_guide.md` - BearerTokenMiddleware 四种模式和请求级控制

### 测试
- 新增 `tests/unit/clients/http/test_auth_control.py` - 认证控制功能单元测试

---

## [3.18.1] - 2025-12-10

### 顶层中间件配置

**核心特性**: 新增顶层中间件配置支持，允许通过环境变量配置签名和 Bearer Token 中间件，无需代码硬编码。

**主要功能**:
- ✨ 顶层签名中间件配置 - `SIGNATURE__*` 环境变量配置
- ✨ 顶层 Token 中间件配置 - `BEARER_TOKEN__*` 环境变量配置
- ✨ 自动合并到 `http.middlewares` - model_validator 自动处理

**详细内容**: 查看完整发布说明 [v3.18.1](docs/releases/v3.18.1.md)

### 新增
- 新增 `FrameworkSettings.signature` - 顶层签名中间件配置字段
- 新增 `FrameworkSettings.bearer_token` - 顶层 Token 中间件配置字段
- 新增 `_merge_toplevel_middlewares` - 自动合并中间件配置的 model_validator

### 修复
- 修复 `MiddlewareConfig.normalize_paths` - 正确解析 JSON 数组格式的环境变量（如 `["/api/**","/h5/**"]`）

### 文档
- 新增 `docs/releases/v3.18.1.md` - 完整版本发布说明

### 测试
- 所有 1234 个测试通过

---

## [3.18.0] - 2025-12-10

### 配置驱动清理与数据准备 Fixtures

**核心特性**: 统一配置前缀，新增配置驱动的数据清理系统和数据准备 fixtures，解决 UoW 测试数据提交问题。

**主要功能**:
- ✨ 配置前缀统一 - 移除 APP_ 前缀，环境变量与 .env 保持一致
- ✨ 配置驱动清理 - `CLEANUP__MAPPINGS__*` 零代码配置数据库清理映射
- ✨ `prepare_data` fixture - 回调式数据准备，自动提交事务
- ✨ `data_preparer` fixture - 上下文管理器式数据准备，支持链式清理注册
- ✨ `ConfigDrivenCleanupManager` - 配置驱动的清理管理器

**详细内容**: 查看完整发布说明 [v3.18.0](docs/releases/v3.18.0.md)

### 新增

#### 配置系统
- 新增 `CleanupMapping` - 清理映射配置类（table/field）
- 新增 `CleanupConfig` - 清理配置类（enabled/mappings）
- 新增 `FrameworkSettings.cleanup` - 清理配置字段

#### 清理系统
- 新增 `ConfigDrivenCleanupManager` - 配置驱动的清理管理器
- 新增 `cleanup` fixture - 配置驱动的清理 fixture

#### 数据准备
- 新增 `prepare_data` fixture - 回调式数据准备（自动 commit）
- 新增 `data_preparer` fixture - 上下文管理器式数据准备

### 变更
- `EnvVarSource.prefix` 从 `"APP_"` 改为 `""`
- `ArgSource.prefix` 从 `"APP_"` 改为 `""`
- `FrameworkSettings.model_config.env_prefix` 从 `"APP_"` 改为 `""`
- 配置格式：`TEST__REPOSITORY_PACKAGE`（无需 APP_ 前缀）
- 配置格式：`CLEANUP__MAPPINGS__orders__table=card_order`

### 文档
- 新增 `docs/releases/v3.18.0.md` - 完整版本发布说明

### 测试
- 所有 1229 个测试通过

---

## [3.17.2] - 2025-12-09

### 中间件架构优化

**核心特性**: 中间件系统代码质量优化，修复同步/异步兼容性问题，完善类型定义。

**主要功能**:
- ✨ 使用 Python 3.12 type 语句定义中间件类型别名
- ✨ HttpClient 同步/异步事件循环兼容性增强
- ✨ LoginTokenProvider 支持同步和异步 HTTP 客户端
- ✨ 移除未实现的中间件枚举类型，保持代码一致性

**详细内容**: 查看完整发布说明 [v3.17.2](docs/releases/v3.17.2.md)

### 修复
- 修复 `protocol.py` 类型定义注释与实现不一致的问题
- 修复 `HttpClient.request_with_middleware()` 使用已弃用的 `get_event_loop()` 问题
- 修复 `LoginTokenProvider._do_login()` 无法处理同步 httpx.Client 的问题
- 修复 `MiddlewareType` 枚举包含未实现类型导致工厂报错的问题

### 重构
- 重构 `core/middleware/protocol.py` - 使用 Python 3.12 type 语句
- 重构 `HttpClient.request_with_middleware()` - 使用 `asyncio.run()` + `nest_asyncio`
- 重构 `LoginTokenProvider._do_login()` - 增加 httpx.Client/AsyncClient 类型检查

### 变更
- `MiddlewareType` 枚举移除未实现的 `TIMEOUT`、`RATE_LIMIT`、`CIRCUIT_BREAKER` 类型
- `middleware_guide.md` 示例代码更新为推荐用法（使用 `client.get()` 而非 `request_with_middleware()`）

### 文档
- 更新 `docs/releases/v3.17.2.md` - 完整版本发布说明
- 更新 `docs/guides/middleware_guide.md` - 示例代码现代化
- 更新 `docs/ESSENTIAL_DOCS.md` - 框架版本和示例代码
- 更新 `docs/architecture/MIDDLEWARE_V3.14_DESIGN.md` - 状态从"设计草案"改为"已实现"

### 测试
- 所有现有测试通过

---

## [3.17.1] - 2025-12-08

### 能力层 Allure 集成优化与 UoW 事务事件

**核心特性**: 统一能力层 Allure 集成为纯 EventBus 驱动模式，实现 UoW 事务事件自动记录，修复同步/异步事件处理器兼容性问题。

**主要功能**:
- ✨ 能力层完全移除对 AllureObserver 的直接依赖
- ✨ 所有 Allure 报告通过 EventBus 自动生成
- ✨ EventBus 支持同步和异步两种事件处理器
- ✨ Database 事件升级为 CorrelatedEvent
- ✨ UoW 事务事件集成 - commit/rollback 自动记录到 Allure
- ✨ 回滚原因追踪（auto/exception/manual）
- ✨ AllurePlugin 标记为 DEPRECATED，规划未来纯插件模式

**详细内容**: 查看完整发布说明 [v3.17.1](docs/releases/v3.17.1.md)

### 新增

#### 事务事件
- 新增 `TransactionCommitEvent` - 事务提交事件类型
- 新增 `TransactionRollbackEvent` - 事务回滚事件类型
- 新增 `UnitOfWork.commit()` 事件发布功能
- 新增 `UnitOfWork.rollback(reason)` 事件发布功能
- 新增 `AllureObserver.handle_transaction_commit_event()` 处理器
- 新增 `AllureObserver.handle_transaction_rollback_event()` 处理器

#### Database 事件升级
- 新增 `DatabaseQueryStartEvent.operation/table` 字段
- 新增 `DatabaseQueryStartEvent/EndEvent/ErrorEvent.create()` 工厂方法
- 新增 EventBus 同步/异步处理器自动检测机制

### 修复
- 修复 EventBus 无条件 await 导致同步处理器报错的问题
- 修复 BearerTokenMiddleware LOGIN 模式未自动注入 http_client 的问题
- 修复能力层直接调用 AllureObserver 导致的紧耦合问题
- 修复 Database/Redis 事件处理器异步/同步不匹配问题
- 修复 `uow` fixture 未传递 `event_bus` 参数导致事务事件无法发布的问题
- 修复 `_publish_event()` 使用异步方法的问题，改为 `_publish_event_sync()`

### 重构
- 重构 Database 客户端事件发布逻辑（统一使用 publish_sync）
- 重构 Redis 客户端移除直接 AllureObserver 调用
- 重构 AllureObserver 删除废弃方法（on_query_start/on_query_end/on_query_error/on_cache_operation）

### 变更
- `UnitOfWork.rollback()` 现在接受 `reason` 参数（默认 "manual"）
- `UnitOfWork.__exit__()` 根据退出情况传递不同的 reason（auto/exception）
- AllurePlugin 标记为 DEPRECATED（推荐使用 EventBus + allure fixture）
- Database 事件升级为 CorrelatedEvent（向后兼容）

### 文档
- 新增 `docs/releases/v3.17.1.md` - 完整版本发布说明（含 UoW 事务事件）
- 新增 `docs/architecture/future_allure_plugin_plans.md` - 未来 Allure 插件纯插件模式规划
- 新增 `docs/architecture/ALLURE_INTEGRATION_OPTIMIZATION_SUMMARY.md` - 实施总结
- 新增 `docs/architecture/ALLURE_INTEGRATION_ANALYSIS.md` - 架构分析
- 新增 `docs/architecture/CAPABILITIES_OPTIMIZATION_PLAN.md` - 优化计划

### 测试
- 新增事务事件测试，2/2 通过
- 框架测试：1307/1307 通过

---

## [3.17.0] - 2025-12-05

### 事件系统重构与可观测性增强

**核心特性**: 完全重构事件系统，支持事件关联、OpenTelemetry 追踪整合、测试隔离，修复 Allure 报告记录问题。

**主要功能**:
- ✨ 事件唯一标识（event_id）与关联系统（correlation_id）
- ✨ OpenTelemetry 自动整合（trace_id/span_id，W3C TraceContext）
- ✨ 测试级 EventBus 隔离（ContextVar 实现）
- ✨ AllureObserver 自动集成（修复 v3.16.0 报告问题）
- ✨ 工厂方法模式（Event.create()）

**详细内容**: 查看完整发布说明 [v3.17.0](docs/releases/v3.17.0.md)

### 新增
- 新增 `Event.event_id` - 事件唯一标识
- 新增 `CorrelatedEvent.correlation_id` - 事件关联 ID
- 新增 `Event.trace_id/span_id` - OpenTelemetry 追踪上下文
- 新增 `Event.create()` 系列工厂方法
- 新增 `set_test_event_bus()` / `get_event_bus()` - 测试隔离 API
- 新增 `allure_observer` fixture - Allure 自动集成

### 修复
- 修复 v3.16.0 Allure 报告无法记录 HTTP 请求/响应的问题
- 修复 Session/Function 级 EventBus 路由失败
- 修复事件关联使用脆弱的字符串匹配

### 文档
- 新增 `docs/architecture/V3.17_EVENT_SYSTEM_REDESIGN.md` - 架构设计文档
- 更新 15 个核心文档到 v3.17.0（新增 1,280+ 行内容）

### 测试
- 新增事件系统完整测试套件，全部通过

---

## [3.16.0] - 2025-12-05

### 五层架构重构 - Layer 4 Bootstrap 引导层

**核心特性**: 解决架构依赖违规问题，引入 Layer 4 Bootstrap 引导层。

**问题背景**:
- v3.14.0 设计规定 `infrastructure/` (Layer 1) 只能依赖 `core/` (Layer 0)
- 但 `bootstrap/`、`providers/`、`runtime/` 需要创建 `capabilities/` (Layer 2) 的实例
- 这导致了 Layer 1 → Layer 2 的依赖违规

**解决方案**:
- 将 `bootstrap/`、`providers/`、`runtime/` 提升为独立的 Layer 4（引导层）
- Layer 4 作为"组装层"，可以合法依赖所有其他层

**架构变更**:

| 层级 | 目录 | 说明 |
|------|------|------|
| **Layer 0** | `core/` | 纯抽象（无第三方依赖） |
| **Layer 1** | `infrastructure/` | 基础设施（config、logging、telemetry、events、plugins） |
| **Layer 2** | `capabilities/` | 能力层（clients、databases、messengers、storages、drivers） |
| **Layer 3** | `testing/` + `cli/` | 门面层（并行） |
| **Layer 4** | `bootstrap/` | **引导层（新增）** - 框架组装和初始化 |
| **横切** | `plugins/` | 插件实现 |

**依赖规则**:
```
Layer 4 (bootstrap/)           ──► 可依赖 Layer 0-3 全部（引导层特权）
Layer 3 (testing/ + cli/)      ──► 可依赖 Layer 0-2（门面层，并行）
Layer 2 (capabilities/)        ──► 可依赖 Layer 0-1
Layer 1 (infrastructure/)      ──► 只能依赖 Layer 0
Layer 0 (core/)                ──► 无依赖（最底层）
plugins/ (横切关注点)           ──► 可依赖任意层级
```

**详细内容**: 查看完整发布说明 [v3.16.0](docs/releases/v3.16.0.md) 和架构设计 [V3.16_LAYER4_BOOTSTRAP_ARCHITECTURE.md](docs/architecture/V3.16_LAYER4_BOOTSTRAP_ARCHITECTURE.md)

### 新增

#### Bootstrap 层 (Layer 4)
- 新增 `bootstrap/` - 独立的引导层目录
- 新增 `bootstrap/bootstrap.py` - 框架初始化入口（Bootstrap 类）
- 新增 `bootstrap/providers.py` - 服务工厂注册（ProviderRegistry、Provider、SingletonProvider）
- 新增 `bootstrap/runtime.py` - 运行时上下文管理（RuntimeContext、RuntimeBuilder）
- 新增 `default_providers()` - 默认服务工厂集合

### 变更

#### 导入路径变更（破坏性变更）
```python
# v3.14.0 导入（旧，已移除）
# from df_test_framework.infrastructure.bootstrap import Bootstrap  # ❌ 不再可用
# from df_test_framework.infrastructure.providers import ProviderRegistry  # ❌ 不再可用
# from df_test_framework.infrastructure.runtime import RuntimeContext  # ❌ 不再可用

# v3.16.0 导入（新）
from df_test_framework.bootstrap import (
    Bootstrap,
    BootstrapApp,
    ProviderRegistry,
    Provider,
    SingletonProvider,
    RuntimeContext,
    RuntimeBuilder,
    default_providers,
)

# 顶层便捷导入（推荐）
from df_test_framework import (
    Bootstrap,
    BootstrapApp,
    ProviderRegistry,
    RuntimeContext,
    RuntimeBuilder,
)
```

### 移除

- ❌ `df_test_framework.infrastructure.bootstrap/` - 已迁移到 `df_test_framework.bootstrap`
- ❌ `df_test_framework.infrastructure.providers/` - 已迁移到 `df_test_framework.bootstrap`
- ❌ `df_test_framework.infrastructure.runtime/` - 已迁移到 `df_test_framework.bootstrap`

**迁移指南**: 将所有 `from df_test_framework.infrastructure.xxx` 导入改为 `from df_test_framework.bootstrap` 或 `from df_test_framework`

### 文档

- 新增 `docs/architecture/V3.16_LAYER4_BOOTSTRAP_ARCHITECTURE.md` - 五层架构完整设计文档
- 新增 `docs/releases/v3.16.0.md` - 完整版本发布说明

### 测试

- ✅ 导入路径测试（新路径可用、旧路径已移除）
- ✅ Bootstrap 功能测试（框架初始化、服务注册、运行时上下文）
- ✅ ProviderRegistry 测试（服务注册/获取、单例模式、默认 Providers）
- ✅ RuntimeContext 测试（服务访问、RuntimeBuilder、上下文管理）
- ✅ 核心测试 100% 通过

---

## [3.14.0] - 2025-12-03

### 🔧 Hotfix (2025-12-04)

**修复 AsyncHttpClient 拦截器加载失败问题**:
- 🐛 修复 `_load_interceptors_from_config()` 使用错误属性名 `config.paths` 的 bug
- ✅ 改为正确检查 `include_paths` 和 `exclude_paths` 属性（与同步 HttpClient 保持一致）
- 📝 新增详细技术文档：`docs/troubleshooting/async_http_client_interceptor_issue.md`

**影响**: 修复前所有使用配置驱动的 AsyncHttpClient 拦截器都无法工作，导致 401 签名验证失败。

**详细信息**: 查看 [AsyncHttpClient 拦截器问题排查报告](docs/troubleshooting/async_http_client_interceptor_issue.md)

---

### 企业级平台架构升级

**核心特性**: 四层架构 + 横切关注点设计，统一中间件系统，可观测性融合。

**架构变更**:

| 层级 | 目录 | 说明 |
|------|------|------|
| **Layer 0** | `core/` | 纯抽象（middleware、context、events、protocols）- 无第三方依赖 |
| **Layer 1** | `infrastructure/` | 基础设施（config、providers、runtime、bootstrap、telemetry、plugins） |
| **Layer 2** | `capabilities/` | 能力层（clients、databases、messengers、storages、drivers） |
| **Layer 3** | `testing/` + `cli/` | 接口层（并行） |
| **横切** | `plugins/` | 插件实现（不在层级中） |

**主要功能**:
- 🧅 **统一中间件系统**: `Interceptor` → `Middleware`（洋葱模型）
- 📡 **可观测性融合**: `Telemetry` = Tracing + Metrics + Logging
- 🔗 **上下文传播**: `ExecutionContext` 贯穿全链路
- 📢 **事件驱动**: `EventBus` 发布/订阅模式
- 📁 **目录重组**: 四层架构，职责清晰

**详细内容**: 查看完整发布说明 [v3.14.0](docs/releases/v3.14.0.md)

### 新增

#### Core 层 (Layer 0)
- 新增 `core/protocols/` - 协议定义（IHttpClient、ITelemetry、IEventBus、IPluginManager 等）
- 新增 `core/middleware/` - 统一中间件系统（Middleware、MiddlewareChain、BaseMiddleware）
- 新增 `core/context/` - 上下文传播（ExecutionContext、get_or_create_context）
- 新增 `core/events/` - 事件类型（HttpRequestEndEvent、DatabaseQueryEndEvent 等）
- 新增 `core/exceptions.py` - 异常体系迁移
- 新增 `core/types.py` - 类型定义迁移

#### Infrastructure 层 (Layer 1)
- 新增 `infrastructure/plugins/` - 插件系统（HookSpecs、PluggyPluginManager）
- 新增 `infrastructure/telemetry/` - 可观测性实现（Telemetry、NoopTelemetry）
- 新增 `infrastructure/events/` - 事件总线实现（EventBus）
- 新增 `infrastructure/context/carriers/` - 上下文载体（HttpContextCarrier、GrpcContextCarrier、MqContextCarrier）

#### Capabilities 层 (Layer 2)
- 新增 `capabilities/` - 能力层统一目录
- 新增 `capabilities/clients/http/middleware/` - HTTP 中间件
  - `SignatureMiddleware` - 签名中间件
  - `BearerTokenMiddleware` - Bearer Token 认证
  - `RetryMiddleware` - 重试中间件
  - `LoggingMiddleware` - 日志中间件
  - `HttpTelemetryMiddleware` - 可观测性中间件

#### Plugins (横切关注点)
- 新增 `plugins/builtin/monitoring/` - 监控插件（MonitoringPlugin）
- 新增 `plugins/builtin/reporting/` - 报告插件（AllurePlugin）

### 迁移指南

详见 [v3.13 到 v3.14 迁移指南](docs/migration/v3.13-to-v3.14.md)

**快速迁移检查清单**:
- [ ] `Interceptor` → `Middleware` 重命名
- [ ] 调整中间件优先级值（反转：priority 数字越小越先执行）
- [ ] 异步测试添加 `@pytest.mark.asyncio`
- [ ] `extensions/` → `plugins/`（插件实现）

### 文档

- 新增 `docs/architecture/V3.14_ENTERPRISE_PLATFORM_DESIGN.md` - 架构设计文档
- 新增 `docs/migration/v3.13-to-v3.14.md` - 迁移指南
- 新增 `docs/releases/v3.14.0.md` - 完整版本发布说明

### 测试

- ✅ 新增 `tests/core/test_middleware.py` - 中间件系统完整单元测试（14个测试，100%通过）
  - 测试 MiddlewareChain 基本功能
  - 测试洋葱模型执行顺序
  - 测试状态共享、异常处理、中止逻辑
  - 测试 SyncMiddleware 和 @middleware 装饰器
  - 测试重试中间件等复杂场景
- ✅ 新增 `tests/core/test_events.py` - 事件总线完整单元测试（20个测试，100%通过）
  - 测试 EventBus 订阅/发布机制
  - 测试 @bus.on() 装饰器
  - 测试全局订阅和取消订阅
  - 测试异常处理和异步并发
  - 测试框架内置事件（HttpRequestEndEvent、DatabaseQueryEndEvent）
  - 测试实际应用场景（日志记录、指标收集）
- ✅ 新增 `tests/core/test_context.py` - 上下文传播完整单元测试（22个测试，100%通过）
  - 测试 ExecutionContext 创建和子上下文
  - 测试上下文不可变性和链式调用
  - 测试 baggage、user_id、tenant_id 等属性
  - 测试上下文管理器（with_context 和 with_context_async）
  - 测试上下文传播和隔离
  - 测试嵌套上下文和流式构建

- ✅ 新增 `tests/migration/test_v3_13_to_v3_14_examples.py` - 迁移指南示例验证（20个测试，19通过，1跳过）
  - 验证所有导入路径迁移示例
  - 验证向后兼容性和废弃警告
  - 验证中间件迁移示例
  - 验证事件系统、上下文传播、插件系统迁移
- ✅ 新增 `tests/README.md` - 测试目录结构说明文档
  - 说明四层架构镜像结构
  - 测试分类和命名规范
  - 运行测试指南

**测试覆盖率**: v3.14.0 核心功能测试覆盖率显著提升
- 中间件系统: 14个测试用例（100%通过）
- 事件总线: 20个测试用例（100%通过）
- 上下文传播: 22个测试用例（100%通过）
- 迁移验证: 20个测试用例（19通过，1跳过）
- **总测试数: 1426个** (+172个新增，包括重组后的测试）
- **通过率: 100%**（排除需要外部服务的测试）

### 测试目录重组

- ✨ 创建镜像 src/ 的四层架构测试目录
  - `tests/core/` - Layer 0 核心抽象层测试
  - `tests/infrastructure/` - Layer 1 基础设施层测试
  - `tests/capabilities/` - Layer 2 能力层测试
    - `capabilities/clients/` - HTTP/GraphQL/gRPC客户端测试
    - `capabilities/databases/` - 数据库测试
    - `capabilities/messengers/` - 消息队列测试
  - `tests/plugins/` - 横切关注点插件测试
  - `tests/migration/` - 迁移验证测试
- ✅ 旧目录保留以确保向后兼容（将在 v3.16.0 清理）

### 代码集成（2025-12-04）

**核心特性**: 将新架构系统完全集成到现有代码中。

**主要功能**:
- ✨ HttpClient/AsyncHttpClient 集成 MiddlewareChain，新增 `middlewares` 参数和 `.use()` 方法
- ✨ Database/UnitOfWork 集成 EventBus，自动发布查询事件
- ✨ Kafka/RabbitMQ/RocketMQ 集成 EventBus，自动发布消息事件
- ✅ 完全向后兼容，旧 API 仍可使用但会触发废弃警告

**详细内容**: 查看完整发布说明 [v3.14.0](docs/releases/v3.14.0.md)

### 新增
- 新增 `HttpClient.use()` - 链式添加中间件
- 新增 `HttpClient.request_with_middleware()` - 使用新中间件系统发送请求
- 新增 `Database(event_bus=...)` - 支持事件总线集成
- 新增 `UnitOfWork(event_bus=...)` - 支持事务事件
- 新增 `KafkaClient(event_bus=...)` - 支持消息事件
- 新增 `RabbitMQClient(event_bus=...)` - 支持消息事件
- 新增 `RocketMQClient(event_bus=...)` - 支持消息事件

### 变更
- 变更主入口异常类导入路径（从 `common` 改为 `core`）
- 标记 `interceptors` 模块为废弃（v3.16.0 移除）

### 文档
- 新增 `docs/migration/v3.14-migration-status.md` - 迁移状态追踪文档
- 更新 `docs/releases/v3.14.0.md` - 添加代码集成说明

### 测试
- ✅ 新增集成测试，验证 MiddlewareChain 和 EventBus 集成
- ✅ 测试通过: 1464 passed, 40 skipped

### 兼容性与废弃

- ⚠️ **废弃警告**: `common/` 和 `extensions/` 模块（v3.16.0 移除）
- ⚠️ **废弃警告**: `interceptors` 模块（v3.16.0 移除）

### 文档和模板全面更新（2025-12-04）

**P0+P1+P2 文档更新完成**

#### 新增核心指南
- 新增 `docs/user-guide/QUICK_START_V3.14.md` - v3.14.0 快速开始（5分钟上手）
- 新增 `docs/guides/middleware_guide.md` - 中间件使用指南（600+行，50+示例）
- 新增 `docs/guides/event_bus_guide.md` - EventBus 使用指南
- 新增 `docs/guides/telemetry_guide.md` - Telemetry 可观测性指南
- 新增 `docs/migration/v3.14-docs-templates-audit.md` - 文档模板审计报告

#### 全面术语统一
- 更新 11 个用户指南文档（USER_MANUAL、BEST_PRACTICES 等）
- 更新 9 个脚手架模板文件
- 全局替换: "拦截器" → "中间件"、"Interceptor" → "Middleware"
- 统一版本号: v3.12.0/v3.11.0 → v3.14.0
- 更新导入路径到新架构

#### 变更统计
- 新增文档: 5 个（1650+ 行）
- 更新文档: 11 个
- 更新模板: 9 个
- 总变更: 25+ 文件，2000+ 行

---

## [3.13.0] - 2025-12-03

### UnitOfWork 配置驱动架构重构

**核心特性**: UnitOfWork 支持配置驱动，无需继承或覆盖 fixture。

**重大变更**:
- 🗑️ 移除 `BaseUnitOfWork`（直接使用 `UnitOfWork`）
- ✨ 新增 `TestExecutionConfig.repository_package` 配置
- ✨ `uow` fixture 支持配置驱动，自动读取 `TEST__REPOSITORY_PACKAGE`
- ✨ Repository 自动发现通过配置启用

**使用方式变更**:

| 版本 | 方式 | 代码量 |
|------|------|--------|
| v3.12.x | 继承 `BaseUnitOfWork` + 覆盖 `uow` fixture | ~166 行 |
| v3.13.0 | 配置 `TEST__REPOSITORY_PACKAGE` | 1 行 |

**配置示例**:
```env
# .env
TEST__REPOSITORY_PACKAGE=my_project.repositories
```

**测试代码**:
```python
def test_example(uow):
    uow.users.create({"name": "test"})  # ✅ 自动发现 Repository
    # 测试结束自动回滚
```

**详细内容**: 查看完整发布说明 [v3.13.0](docs/releases/v3.13.0.md)

---

## [3.12.1] - 2025-12-02

### 统一测试数据保留配置

**核心特性**: `should_keep_test_data()` 支持 Settings 配置，UoW 和 cleanup 共享统一配置。

**主要变更**:
- ✨ `TestExecutionConfig` 新增 `keep_test_data` 字段
- ✨ `should_keep_test_data()` 改用 `get_settings()` 读取配置
- ✨ `uow` fixture 改用 `should_keep_test_data()` 统一检查
- 🗑️ 移除直接的 `os.getenv("KEEP_TEST_DATA")` 调用

**配置方式**:

| 优先级 | 方式 | 用法 |
|-------|-----|------|
| 1 | 测试标记 | `@pytest.mark.keep_data` |
| 2 | 命令行参数 | `pytest --keep-test-data` |
| 3 | Settings 配置 | `.env` 中 `TEST__KEEP_TEST_DATA=1` |

**注意**: `.env` 文件格式为 `TEST__KEEP_TEST_DATA=1`（双下划线表示嵌套），系统环境变量需要 `APP_` 前缀。

**详细内容**: 查看完整发布说明 [v3.12.1](docs/releases/v3.12.1.md)

---

## [3.12.0] - 2025-12-02

### Testing 模块架构重构

**核心特性**: 基于 V3 架构设计优化 testing 模块组织结构。

**主要变更**:
- ✨ 创建 `testing/reporting/allure/` 子系统（非扁平设计）
- ✨ 统一 `testing/debugging/` 调试工具模块
- ✨ 迁移 `TracingInterceptor` 到 `infrastructure/tracing/interceptors/`
- ✨ AllureObserver 增强：并发请求支持、异常安全、GraphQL/gRPC 协议支持
- ✨ 新增 `GrpcTracingInterceptor` 分布式追踪拦截器
- 🗑️ 删除分散的 `testing/observers/` 目录

**详细内容**: 查看完整发布说明 [v3.12.0](docs/releases/v3.12.0.md)

### 变更

#### 模块重组
- `testing/reporting/allure/` - Allure 报告子系统（observer、helper、fixtures）
- `testing/debugging/` - 调试工具统一（http、database、pytest_plugin）
- `infrastructure/tracing/interceptors/` - 追踪拦截器归位

#### 导入路径变更
```python
# Allure（新路径）
from df_test_framework.testing.reporting.allure import AllureObserver, AllureHelper

# Debug（新路径）
from df_test_framework.testing.debugging import HTTPDebugger, DBDebugger

# Tracing（新路径）
from df_test_framework.infrastructure.tracing.interceptors import (
    TracingInterceptor,       # HTTP 追踪
    GrpcTracingInterceptor,   # gRPC 追踪（新增）
)
```

### 移除
- 移除 `testing/observers/` 目录
- 移除 `testing/plugins/allure.py`（迁移至 reporting/allure/helper.py）
- 移除 `testing/plugins/debug.py`（迁移至 debugging/pytest_plugin.py）
- 移除 `clients/http/interceptors/tracing.py`（迁移至 infrastructure/）

### 文档
- 新增 `docs/releases/v3.12.0.md` - 完整版本发布说明
- 新增 `docs/architecture/TESTING_MODULE_OPTIMIZATION.md` - 架构优化方案

### 新增
- 新增 `GrpcTracingInterceptor` - gRPC 分布式追踪拦截器
- 新增 `AllureObserver.on_graphql_request_start/end` - GraphQL 协议支持
- 新增 `AllureObserver.on_grpc_call_start/end` - gRPC 协议支持
- 新增 `AllureObserver` 可配置截断参数：`max_body_length`、`max_value_length`、`max_sql_length`

### 修复
- 修复 AllureObserver 并发请求上下文被覆盖问题（P0）
- 修复 AllureObserver 异常时上下文未正确关闭问题（P0）

### 测试
- 全部 1134 个测试通过（新增 24 个）

---

## [3.11.1] - 2025-11-28

### 测试数据清理模块重构

**核心特性**: 统一的测试数据清理机制，支持 `--keep-test-data` 配置控制。

**主要功能**:
- ✨ `should_keep_test_data()` - 统一配置检查函数（标记 > CLI参数 > 环境变量）
- ✨ `CleanupManager` - 清理管理器基类，自动检查配置
- ✨ `SimpleCleanupManager` - 回调函数模式清理器
- ✨ `ListCleanup` - 列表式清理器，继承自 list
- ✨ `DataGenerator.test_id()` - 类方法，无需实例化生成测试数据标识符

**详细内容**: 查看完整发布说明 [v3.11.1](docs/releases/v3.11.1.md)

### 新增

#### 清理模块 (`testing/fixtures/cleanup.py`)
- 新增 `should_keep_test_data(request)` - 检查是否保留测试数据
- 新增 `CleanupManager` - 抽象基类，子类实现 `_do_cleanup()`
- 新增 `SimpleCleanupManager` - 通过 `register_cleanup(type, callback)` 注册清理函数
- 新增 `ListCleanup` - 继承 list，提供 `should_keep()`/`should_do_cleanup()` 方法

#### 数据生成器增强
- 新增 `DataGenerator.test_id(prefix)` 类方法 - 无需实例化，直接生成测试标识符
- 格式: `{prefix}{timestamp14}{random6}`，如 `TEST_ORD20251128123456789012`

### 移除
- 移除旧的 `test_data_cleaner` fixture（已由新 API 替代）

### 文档
- 新增 `docs/releases/v3.11.1.md` - 完整版本发布说明
- 新增 `docs/guides/test_data_cleanup.md` - 使用指南
- 更新 `CLAUDE.md` - 数据清理示例代码

### 测试
- 新增清理模块测试：41 个（全部通过）
- 新增 `DataGenerator.test_id()` 测试：3 个（全部通过）
- 总计：78 个相关测试通过

---

## [3.11.0] - 2025-11-26

### Phase 2 完整交付 (P2.5-P2.8)

**核心特性**: 协议扩展 + Mock 工具增强 + 测试覆盖率提升

**主要功能**:
- ✨ GraphQL 客户端 (P2.5) - 支持 Query/Mutation/Subscription、QueryBuilder、批量操作、文件上传
- ✨ gRPC 客户端 (P2.6) - 支持所有 RPC 模式、拦截器、健康检查
- ✨ DatabaseMocker (P2.7) - 数据库操作 Mock，SQL 标准化、调用历史
- ✨ RedisMocker (P2.7) - Redis 操作 Mock，支持 fakeredis 或简单内存实现
- ✅ 新增 104+ 个单元测试 (P2.8)
- ✅ 测试总数达到 1078 个，通过率 98.9%

**详细内容**: 查看完整发布说明 [v3.11.0](docs/releases/v3.11.0.md)

### 新增

#### GraphQL 客户端
- 新增 `GraphQLClient` - 基于 httpx 的 GraphQL 客户端
- 新增 `QueryBuilder` - 流畅的 GraphQL 查询构建器
- 新增 `GraphQLRequest/Response/Error` 数据模型
- 支持批量查询、文件上传

#### gRPC 客户端
- 新增 `GrpcClient` - 通用 gRPC 客户端
- 新增 `LoggingInterceptor/MetadataInterceptor/RetryInterceptor/TimingInterceptor` 拦截器
- 新增 `GrpcResponse[T]/GrpcError/GrpcStatusCode` 数据模型
- 新增 `ChannelOptions` 通道配置
- 支持所有 RPC 调用模式（Unary/Server Streaming/Client Streaming/Bidirectional）

#### Mock 工具增强
- 新增 `DatabaseMocker` - 数据库操作 Mock 工具
- 新增 `RedisMocker` - Redis 操作 Mock 工具
- RedisMocker 支持 fakeredis 或降级到简单内存实现
- DatabaseMocker 支持 SQL 标准化、调用历史、断言辅助

### 测试
- 新增 GraphQL 客户端测试：37 个（全部通过）
- 新增 gRPC 客户端测试：39 个通过，1 个跳过
- 新增 Mock 工具测试：28 个通过，1 个跳过
- 总测试数：1078 个
- 测试通过率：98.9% (1036/1047)
- 测试覆盖率：57.02%

### 文档
- 新增 `docs/releases/v3.11.0.md` - 完整版本发布说明
- 更新 `CHANGELOG.md` - Phase 2 完整摘要

---

## [3.10.0] - 2025-11-26

### 存储客户端 - LocalFile + S3 + 阿里云OSS

**核心特性**: 统一的文件存储抽象，支持本地文件、AWS S3、阿里云OSS三种存储方式。

**主要功能**:
- LocalFileClient - 本地文件系统存储，支持元数据、路径安全验证
- S3Client - 基于 boto3 的 AWS S3 对象存储，支持 MinIO
- OSSClient - 基于 oss2 的阿里云 OSS 对象存储，支持 STS、CRC64、内网访问
- 统一的 CRUD API（upload/download/delete/list/copy）
- 分片上传支持（大文件自动分片）
- 预签名 URL 生成
- 完整的 pytest fixtures（local_file_client、s3_client、oss_client）

**详细内容**: 查看完整使用指南 [storage.md](docs/guides/storage.md)

### 测试覆盖
- 75个单元测试，全部通过
- LocalFileClient 测试覆盖率 95%+
- S3Client 测试覆盖率 95%+
- OSSClient 测试覆盖率 95%+

### OpenTelemetry 分布式追踪

**核心特性**: 基于 OpenTelemetry 标准的分布式追踪能力，支持 Console/OTLP/Jaeger/Zipkin 导出器。

**主要功能**:
- TracingManager 追踪管理器，支持多导出器配置
- @trace_span/@trace_async_span/@TraceClass 装饰器，零侵入式追踪
- TracingContext 和 Baggage 上下文传播机制
- HTTP 请求追踪拦截器，自动记录请求链路
- 数据库查询追踪集成，记录 SQL 执行详情
- 70个单元测试，覆盖率 95%+

**详细内容**: 查看完整发布说明 [v3.10.0](docs/releases/v3.10.0.md)

### 测试数据工具增强

**核心特性**: 数据加载器和响应断言辅助，提升测试数据处理效率。

**主要功能**:
- JSONLoader/CSVLoader/YAMLLoader 三种数据加载器
- 支持 JSONPath 查询、类型转换、环境变量替换
- ResponseAssertions 响应断言辅助（链式调用 + 静态方法）
- 支持状态码、JSON、响应头、响应时间断言
- pytest 参数化支持

**预置工厂说明**:
- UserFactory/OrderFactory 等 8 个预置工厂已标记为 **示例代码**
- 这些工厂是业务领域特定的，不同项目字段差异大
- **建议**: 项目根据自身需求继承 Factory 基类自定义工厂
- Factory 基类提供 Sequence、LazyAttribute、FakerAttribute 等通用能力

**详细内容**: 查看完整发布说明 [v3.10.0](docs/releases/v3.10.0.md)

### Prometheus 指标监控

**核心特性**: 基于 Prometheus 的应用性能监控（APM），零配置模式。

**主要功能**:
- MetricsManager 指标管理器，支持 Prometheus exporter 和 Pushgateway
- Counter/Gauge/Histogram/Summary 四种指标类型，线程安全
- @count_calls/@time_calls/@track_in_progress 等 6 个装饰器
- HttpMetrics 自动收集 HTTP 请求指标
- DatabaseMetrics 自动收集数据库查询指标
- 零配置模式（无需安装 prometheus_client 即可使用）
- 44个单元测试，全部通过

**详细内容**: 查看完整发布说明 [v3.10.0](docs/releases/v3.10.0.md)

### 文档
- 新增 `docs/guides/storage.md` - 存储客户端完整使用指南
- 新增 `docs/guides/distributed_tracing.md` - 分布式追踪完整使用指南
- 新增 `docs/guides/test_data.md` - 测试数据工具完整使用指南
- 新增 `docs/guides/prometheus_metrics.md` - Prometheus 监控完整使用指南
- 新增 `docs/releases/v3.10.0.md` - 完整版本发布说明
- 新增 `examples/01-basic/storage_usage.py` - 存储客户端使用示例

### 测试覆盖
- 257个新增测试用例，全部通过
- 存储模块: 75个测试，覆盖率 95%+
- 追踪模块: 70个测试，覆盖率 95%+
- 测试数据: 68个测试，覆盖率 90%+
- 指标模块: 44个测试，覆盖率 92%+

---

## [3.9.0] - 2025-11-25

### 消息队列客户端 - Kafka + RabbitMQ + RocketMQ

**核心特性**: 提供三大主流消息队列的统一封装,支持企业级测试场景。

**主要功能**:
- Kafka客户端 (confluent-kafka 1.9.2)，生产性能提升3倍
- RabbitMQ客户端 (pika, AMQP 0-9-1)，支持延迟队列和死信队列
- RocketMQ客户端，支持顺序消息和事务消息
- SSL/TLS 支持，完整的证书认证和 SASL 认证
- 统一的 API 设计，便于切换不同消息队列

**详细内容**: 查看完整发布说明 [v3.9.0](docs/releases/v3.9.0.md)

### 测试覆盖
- 68个单元测试和集成测试
- Kafka测试覆盖率 96.32%
- RabbitMQ测试覆盖率 94.85%
- RocketMQ测试覆盖率 91.47%

---

## [3.8.0] - 2025-11-25

### AsyncHttpClient - 异步HTTP客户端

**核心特性**: 基于 httpx.AsyncClient 实现的异步HTTP客户端，性能提升 10-50 倍。

**主要功能**:
- 并发性能提升 40 倍 (100个请求从 20秒 降至 0.5秒)
- 内存占用降低 90%，CPU占用降低 75%
- 默认启用 HTTP/2 支持，连接复用
- 完全兼容现有拦截器，无需修改
- 适用场景: 批量操作、压力测试、微服务调用、数据迁移

**详细内容**: 查看完整发布说明 [v3.8.0](docs/releases/v3.8.0.md)

### 修复
- 更新 CLI 生成模板的版本引用 (v3.7 → v3.8)
- 重构 Repository 测试从 MockDatabase 到 MockSession

### 依赖变更
- 新增 pytest-asyncio>=1.3.0 (异步测试支持)

---

## [3.7.0] - 2025-11-24

### Unit of Work 模式 - 现代化数据访问架构

**核心特性**: 统一管理事务边界和 Repository 生命周期，解决 v3.6.2 事务隔离失效问题。

**主要功能**:
- 新增 BaseUnitOfWork 类，支持 Repository 懒加载和缓存
- 新增 uow fixture，替代 db_transaction，确保所有操作在同一事务中
- 所有 Repository 共享同一个 Session，事务隔离正确
- 新增熔断器 (Circuit Breaker) 模块，防止级联失败
- 新增安全最佳实践指南 (8000+字)
- 集成 CI/CD 依赖漏洞扫描 (Safety/Bandit/pip-audit)

**详细内容**: 查看完整发布说明 [v3.7.0](docs/releases/v3.7.0.md)

### 测试覆盖
- 19个 UnitOfWork 单元测试，覆盖率 94.52%
- 26个熔断器单元测试，覆盖率 98.40%

---

## [3.6.2] - 2025-11-24

### 测试数据清理控制机制

**核心特性**: 增强 db_transaction fixture 的数据清理控制，提供灵活的清理策略。

**主要功能**:
- 默认强制回滚，确保测试数据不残留
- 支持三种控制方式：命令行参数、测试标记、环境变量
- 移除 TransactionalDatabase 包装器，直接返回 SQLAlchemy Session
- 新增框架架构说明文档

**详细内容**: 查看完整发布说明 [v3.6.2](docs/releases/v3.6.2.md)

### 测试
- 17个集成测试，覆盖所有数据清理场景

---

## [3.6.1] - 2025-11-23

### 日志系统修复 + Loguru/Pytest 深度集成

**核心特性**: 修复日志传播导致的重复输出问题，增强 Loguru 和 pytest 集成。

**主要功能**:
- 修复日志传播链导致的重复输出问题
- 新增 LoguruHandler 集成 Loguru 到 Python logging
- 新增 LoguruPytestHandler 集成到 pytest 日志系统
- 新增 pytest_configure_logging hook 自动配置

**详细内容**: 查看完整发布说明 [v3.6.1](docs/releases/v3.6.1.md)

### 测试
- 26个日志系统单元测试

---

## [3.6.0] - 2025-11-22

### Decimal 零配置序列化 + HttpClient Pydantic 支持

**核心特性**: Decimal 类型的 JSON 序列化零配置支持，HttpClient 增强 Pydantic 集成。

**主要功能**:
- 全局 Decimal JSON 编码器，自动转换为字符串
- HttpClient 原生支持 Pydantic 模型序列化/反序列化
- 新增 DecimalJSONEncoder 和 DecimalJSONProvider (Flask扩展)
- 修复 LogConfig 死循环问题

**详细内容**: 查看完整发布说明 [v3.6.0](docs/releases/v3.6.0.md)

### 测试
- 22个单元测试，全部通过

---

## [3.5.0] - 2025-11-21

### 核心特性
- Repository基类：基础的CRUD能力
- 查询构建器：支持链式调用和复杂查询
- 数据库工厂：自动管理Session生命周期
- 事务支持：上下文管理器模式
- SQLAlchemy 2.0 原生支持

### 依赖变更
- SQLAlchemy >= 2.0.0

---

## [3.4.0] - 2025-11-20

### 核心特性
- HttpClient：统一的HTTP客户端接口
- 拦截器链：支持请求/响应拦截
- 重试机制：指数退避 + 抖动
- Mock支持：MockHttpClient 测试辅助

### 依赖变更
- httpx >= 0.27.0
- tenacity >= 8.5.0

---

## [3.3.0] - 2025-11-19

### 核心特性
- Factory模式：测试数据生成
- Faker集成：真实感测试数据
- 序列和懒加载：灵活的数据生成

### 依赖变更
- Faker >= 30.8.2

---

## [3.2.0] - 2025-11-18

### 核心特性
- 日志系统：LogConfig配置化管理
- Loguru集成：更优雅的日志输出
- 多输出支持：控制台、文件、JSON、Syslog

### 依赖变更
- loguru >= 0.7.3

---

## [3.1.0] - 2025-11-17

### 核心特性
- BaseModel：统一的数据模型基类
- 配置系统：环境变量管理
- 验证器：Pydantic集成

### 依赖变更
- pydantic >= 2.10.3
- pydantic-settings >= 2.7.0

---

## [3.0.0] - 2025-11-16

### 重大变更
- 项目重构：模块化架构
- Python 3.12+：现代化类型注解
- pytest 8.0+：最新测试框架

### 核心特性
- clients/：HTTP、数据库客户端
- infrastructure/：基础设施层
- testing/：测试工具集

---

## [2.x.x] - Legacy 版本

早期版本的变更记录已归档。详见: [CHANGELOG_V2.md](CHANGELOG_V2.md)
