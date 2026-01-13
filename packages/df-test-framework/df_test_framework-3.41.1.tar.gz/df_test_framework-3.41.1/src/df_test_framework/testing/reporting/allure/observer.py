"""Allure测试观察者

零配置自动记录HTTP请求、拦截器、数据库查询等操作到Allure报告

设计原则:
- 零配置: 通过pytest autouse fixture自动注入
- 零侵入: 测试代码无需修改
- 可视化: 生成Allure HTML报告而非终端日志
- 行业标准: 使用Allure Report（与Playwright/Selenium对齐）
- 并发安全: 支持并发请求，使用dict存储多个上下文
- 异常安全: 使用ExitStack确保上下文正确关闭

架构:
- AllureObserver: 核心观察者类，记录测试操作到Allure
- ContextVar: 线程安全的全局observer访问
- pytest fixture: 自动注入到每个测试

v3.12.0 重构:
- 修复并发请求覆盖问题（使用dict存储多个上下文）
- 修复异常安全问题（使用ExitStack）
- 新增GraphQL和gRPC协议支持
- 配置化截断长度

v3.17.0 重构:
- 使用 correlation_id 关联 Start/End 事件（替代 method:url）
- 支持 CorrelatedEvent 新事件类型
- 并发安全的事件关联（不再依赖请求路径）

v3.22.0 重构:
- 支持记录 params（GET 请求参数）
- 完整记录中间件修改后的 headers

v3.40.0 重构:
- 新增敏感数据脱敏支持（使用统一脱敏服务）
- 脱敏 HTTP headers、body、params
- 脱敏 GraphQL variables 和响应数据
- 脱敏 gRPC metadata
- 支持通过配置独立控制 allure 上下文的脱敏开关
"""

import json
import time
from contextlib import ExitStack
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

try:
    import allure

    ALLURE_AVAILABLE = True
except ImportError:
    ALLURE_AVAILABLE = False
    allure = None

if TYPE_CHECKING:
    from df_test_framework.capabilities.clients.http.core import Request, Response


# 线程安全的当前Observer
_current_observer: ContextVar["AllureObserver | None"] = ContextVar("allure_observer", default=None)


def is_allure_enabled() -> bool:
    """检查Allure集成是否启用

    优先级:
    1. Allure库是否可用 (ALLURE_AVAILABLE)
    2. FrameworkSettings.enable_allure配置
    3. 默认值: True (如果Allure可用)

    Returns:
        是否启用
    """
    if not ALLURE_AVAILABLE or allure is None:
        return False

    try:
        from df_test_framework.infrastructure.config import get_settings

        settings = get_settings()
        return settings.enable_allure
    except Exception:
        pass

    return True


@dataclass
class StepContext:
    """Step上下文状态

    存储单个请求/查询的step上下文和相关信息
    """

    exit_stack: ExitStack = field(default_factory=ExitStack)
    start_time: float = field(default_factory=time.time)
    step_context: Any = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """安全关闭所有上下文"""
        self.exit_stack.close()
        return False


class AllureObserver:
    """Allure测试观察者

    自动记录测试操作到Allure报告:
    - HTTP请求/响应详情
    - 拦截器执行过程
    - GraphQL请求（v3.12.0新增）
    - gRPC调用（v3.12.0新增）
    - 数据库查询
    - Redis缓存操作
    - 错误和异常

    特性:
    - 零配置: 通过autouse fixture自动启用
    - 终端静默: 测试通过时无额外输出
    - 详细报告: Allure HTML报告包含完整详情
    - 拦截器可见: 每个拦截器都是独立的sub-step
    - 并发安全: 支持并发请求（v3.12.0）
    - 异常安全: 使用ExitStack确保上下文正确关闭（v3.12.0）

    使用方式:
        # 完全自动，通过 autouse fixture 注入
        def test_api(http_client):
            response = http_client.post("/api/users", json={"name": "Alice"})
            assert response.status_code == 201

        # Allure报告自动包含:
        # - 🌐 POST /api/users (主step)
        #   ├─ 📤 Request Details (附件)
        #   ├─ ⚙️ SignatureInterceptor (sub-step)
        #   ├─ ⚙️ TokenInterceptor (sub-step)
        #   └─ ✅ Response (201) - 145ms (附件)

    生成报告:
        pytest --alluredir=./allure-results
        allure serve ./allure-results
    """

    # 默认截断长度配置
    DEFAULT_MAX_BODY_LENGTH = 1000
    DEFAULT_MAX_VALUE_LENGTH = 500
    DEFAULT_MAX_SQL_LENGTH = 2000

    def __init__(
        self,
        test_name: str,
        max_body_length: int | None = None,
        max_value_length: int | None = None,
        max_sql_length: int | None = None,
    ):
        """初始化Observer

        Args:
            test_name: 当前测试名称
            max_body_length: HTTP响应体最大截断长度（默认1000）
            max_value_length: 缓存值等最大截断长度（默认500）
            max_sql_length: SQL语句最大截断长度（默认2000）
        """
        self.test_name = test_name
        self.request_counter = 0
        self.query_counter = 0
        self.graphql_counter = 0
        self.grpc_counter = 0
        self.ui_counter = 0  # v3.35.7: UI 操作计数器

        # 配置化截断长度
        self.max_body_length = max_body_length or self.DEFAULT_MAX_BODY_LENGTH
        self.max_value_length = max_value_length or self.DEFAULT_MAX_VALUE_LENGTH
        self.max_sql_length = max_sql_length or self.DEFAULT_MAX_SQL_LENGTH

        # 并发安全: 使用dict存储多个请求/查询上下文
        self._http_contexts: dict[str, StepContext] = {}
        self._query_contexts: dict[str, StepContext] = {}
        self._graphql_contexts: dict[str, StepContext] = {}
        self._grpc_contexts: dict[str, StepContext] = {}

        # v3.17.0: EventBus 事件关联映射 (correlation_id → request_id)
        # 用于关联 HttpRequestStartEvent 和 HttpRequestEndEvent
        # 使用事件的 correlation_id 字段（而非 method:url）确保并发安全
        self._event_correlations: dict[str, str] = {}

        # v3.40.0: 脱敏服务缓存
        self._sanitize_service_cache = None

    @property
    def _sanitize_service(self):
        """获取脱敏服务（惰性加载）

        v3.40.0 新增：使用统一脱敏服务
        """
        if self._sanitize_service_cache is None:
            from df_test_framework.infrastructure.sanitize import get_sanitize_service

            self._sanitize_service_cache = get_sanitize_service()
        return self._sanitize_service_cache

    def _sanitize_for_allure(self, data: dict[str, Any] | None) -> dict[str, Any] | None:
        """为 Allure 报告脱敏数据

        v3.40.0 新增：使用统一脱敏服务对 headers、body 等敏感数据进行脱敏。

        Args:
            data: 要脱敏的字典数据

        Returns:
            脱敏后的数据
        """
        if data is None:
            return None

        service = self._sanitize_service
        if not service.is_context_enabled("allure"):
            return data

        return service.sanitize_dict(data, context="allure")

    def _sanitize_body_content(self, body: str | None) -> str | None:
        """为 Allure 报告脱敏 body 内容

        v3.40.0 新增：尝试将 body 解析为 JSON 并脱敏，如果解析失败则返回原始内容。

        Args:
            body: HTTP body 内容（字符串）

        Returns:
            脱敏后的 body 内容
        """
        if body is None:
            return None

        service = self._sanitize_service
        if not service.is_context_enabled("allure"):
            return body

        # 尝试解析 JSON 并脱敏
        try:
            import json as json_module

            parsed = json_module.loads(body)
            if isinstance(parsed, dict):
                sanitized = service.sanitize_dict(parsed, context="allure")
                return json_module.dumps(sanitized, ensure_ascii=False)
            elif isinstance(parsed, list):
                # 列表中的每个 dict 元素都需要脱敏
                sanitized_list = []
                for item in parsed:
                    if isinstance(item, dict):
                        sanitized_list.append(service.sanitize_dict(item, context="allure"))
                    else:
                        sanitized_list.append(item)
                return json_module.dumps(sanitized_list, ensure_ascii=False)
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

        return body

    def _truncate(self, value: str | None, max_length: int) -> str | None:
        """安全截断字符串

        Args:
            value: 要截断的字符串
            max_length: 最大长度

        Returns:
            截断后的字符串
        """
        if value is None:
            return None
        if len(value) <= max_length:
            return value
        return value[:max_length] + f"... (truncated, total {len(value)} chars)"

    # ========== HTTP 观察方法 ==========

    def on_http_request_start(self, request: "Request") -> str | None:
        """HTTP请求开始

        创建Allure step并附加请求详情。支持并发请求。

        Args:
            request: Request对象

        Returns:
            request_id - 用于关联后续事件（如拦截器、响应）
        """
        if not is_allure_enabled():
            return None

        self.request_counter += 1
        request_id = f"req-{self.request_counter:03d}"

        # 创建上下文状态
        ctx = StepContext()

        # 创建Allure step (带emoji图标)
        step_title = f"🌐 {request.method} {request.url}"
        ctx.step_context = allure.step(step_title)
        # 使用ExitStack安全管理上下文
        ctx.exit_stack.enter_context(ctx.step_context)

        # 存储上下文（支持并发）
        self._http_contexts[request_id] = ctx

        # 附加请求详情
        # v3.40.0: 应用脱敏
        request_details = {
            "request_id": request_id,
            "method": request.method,
            "url": request.url,
            "headers": self._sanitize_for_allure(dict(request.headers) if request.headers else {}),
            "params": self._sanitize_for_allure(request.params),
            "json": self._sanitize_for_allure(request.json),
            "data": request.data,
        }

        allure.attach(
            json.dumps(request_details, indent=2, ensure_ascii=False, default=str),
            name="📤 Request Details",
            attachment_type=allure.attachment_type.JSON,
        )

        return request_id

    def on_interceptor_execute(
        self, request_id: str, interceptor_name: str, changes: dict[str, Any]
    ) -> None:
        """拦截器执行记录

        在当前HTTP请求step下创建子step，展示拦截器做了什么修改

        Args:
            request_id: 请求ID（用于关联）
            interceptor_name: 拦截器名称
            changes: 拦截器做的修改（如添加的headers）
        """
        if not is_allure_enabled():
            return

        # 跳过空变化
        if not changes:
            return

        # 在当前HTTP请求step下创建sub-step
        with allure.step(f"  ⚙️ {interceptor_name}"):
            allure.attach(
                json.dumps(changes, indent=2, ensure_ascii=False),
                name="Changes",
                attachment_type=allure.attachment_type.JSON,
            )

    def on_http_request_end(
        self, request_id: str, response: "Response", duration_ms: float | None = None
    ) -> None:
        """HTTP请求结束

        附加响应详情并关闭当前step

        Args:
            request_id: 请求ID
            response: Response对象
            duration_ms: 请求耗时（毫秒），如果未提供则自动计算
        """
        if not is_allure_enabled():
            return

        # 获取上下文
        ctx = self._http_contexts.get(request_id)
        if not ctx:
            return

        try:
            # 计算耗时
            if duration_ms is None:
                duration_ms = (time.time() - ctx.start_time) * 1000

            # 响应详情（使用配置化截断长度）
            # v3.40.0: 应用脱敏
            response_body = self._truncate(response.body, self.max_body_length)
            response_details = {
                "request_id": request_id,
                "status_code": response.status_code,
                "headers": self._sanitize_for_allure(
                    dict(response.headers) if response.headers else {}
                ),
                "body": response_body,  # body 是字符串，后续可考虑解析后脱敏
                "duration_ms": round(duration_ms, 2) if duration_ms else None,
            }

            # 根据状态码选择emoji
            status_emoji = "✅" if 200 <= response.status_code < 300 else "❌"
            attachment_name = f"{status_emoji} Response ({response.status_code})"
            if duration_ms:
                attachment_name += f" - {round(duration_ms, 2)}ms"

            allure.attach(
                json.dumps(response_details, indent=2, ensure_ascii=False, default=str),
                name=attachment_name,
                attachment_type=allure.attachment_type.JSON,
            )
        finally:
            # 安全关闭上下文
            ctx.exit_stack.close()
            self._http_contexts.pop(request_id, None)

    def on_error(self, error: Exception, context: dict[str, Any]) -> None:
        """错误记录

        记录错误信息到Allure报告

        Args:
            error: 异常对象
            context: 错误上下文信息（如stage, request_id等）
        """
        if not is_allure_enabled():
            return

        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
        }

        allure.attach(
            json.dumps(error_details, indent=2, ensure_ascii=False),
            name="❌ Error",
            attachment_type=allure.attachment_type.JSON,
        )

        # 如果有request_id，关闭对应的上下文
        request_id = context.get("request_id")
        if request_id and request_id in self._http_contexts:
            ctx = self._http_contexts.pop(request_id)
            ctx.exit_stack.close()

    # ========== EventBus 事件处理器 (v3.16.0 新增, v3.17.0 重构) ==========

    async def handle_http_request_start_event(self, event) -> None:
        """处理 HTTP 请求开始事件 (来自 EventBus)

        v3.16.0: 适配 Middleware 系统的 EventBus 事件订阅机制。
        v3.17.0: 使用 event.correlation_id 进行事件关联（并发安全）。
        v3.17.0: 整合 OpenTelemetry 追踪上下文。
        v3.22.0: 支持记录 params（GET 请求参数）和完整 headers。

        直接附加 HTTP 请求详情到当前 Allure 步骤 (不创建新步骤)。

        Args:
            event: HttpRequestStartEvent（带 correlation_id、trace_id、span_id、params）
        """
        if not is_allure_enabled():
            return

        self.request_counter += 1

        # v3.17.0: 使用事件的 correlation_id 进行关联（并发安全）
        # 存储 event_id 用于 End 事件关联
        correlation_id = getattr(event, "correlation_id", None)
        event_id = getattr(event, "event_id", None)
        if correlation_id and event_id:
            self._event_correlations[correlation_id] = event_id

        # 附加请求详情
        # v3.17.0: 包含 OpenTelemetry 追踪上下文（仅在有值时显示）
        # v3.22.0: 包含 params（GET 请求参数）
        # v3.40.0: 应用脱敏
        request_details: dict[str, Any] = {
            "event_id": event_id,
            "correlation_id": correlation_id,
            "method": event.method,
            "url": event.url,
            "headers": self._sanitize_for_allure(dict(event.headers) if event.headers else {}),
            "body": self._sanitize_body_content(event.body if hasattr(event, "body") else None),
        }

        # v3.22.0: 添加 params（GET 请求参数）
        # v3.40.0: 应用脱敏
        params = getattr(event, "params", None)
        if params:
            request_details["params"] = self._sanitize_for_allure(params)

        # 仅在启用 OpenTelemetry 时添加追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            request_details["trace_id"] = trace_id
        if span_id:
            request_details["span_id"] = span_id

        allure.attach(
            json.dumps(request_details, indent=2, ensure_ascii=False, default=str),
            name=f"🌐 {event.method} {event.url} - Request",
            attachment_type=allure.attachment_type.JSON,
        )

    async def handle_http_request_end_event(self, event) -> None:
        """处理 HTTP 请求结束事件 (来自 EventBus)

        v3.16.0: 适配 Middleware 系统的 EventBus 事件订阅机制。
        v3.17.0: 使用 event.correlation_id 进行事件关联（并发安全）。
        v3.17.0: 记录响应体内容，整合 OpenTelemetry 追踪上下文。

        直接附加 HTTP 响应详情到当前 Allure 步骤 (不创建新步骤)。

        Args:
            event: HttpRequestEndEvent（带 correlation_id、trace_id、span_id）
        """
        if not is_allure_enabled():
            return

        # v3.17.0: 清理关联映射（Start 事件时存储的）
        correlation_id = getattr(event, "correlation_id", None)
        if correlation_id:
            self._event_correlations.pop(correlation_id, None)

        # 计算耗时
        duration_ms = event.duration * 1000 if event.duration else 0

        # 响应详情
        # v3.17.0: 包含 OpenTelemetry 追踪上下文（仅在有值时显示）
        # v3.40.0: 应用脱敏
        truncated_body = self._truncate(event.body, self.max_body_length) if event.body else None
        response_details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": correlation_id,
            "status_code": event.status_code,
            "headers": self._sanitize_for_allure(dict(event.headers) if event.headers else {}),
            "body": self._sanitize_body_content(truncated_body),
            "duration_ms": round(duration_ms, 2) if duration_ms else None,
        }

        # 仅在启用 OpenTelemetry 时添加追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            response_details["trace_id"] = trace_id
        if span_id:
            response_details["span_id"] = span_id

        # 根据状态码选择emoji
        status_emoji = "✅" if 200 <= event.status_code < 300 else "❌"
        attachment_name = (
            f"{status_emoji} {event.method} {event.url} - Response ({event.status_code})"
        )
        if duration_ms:
            attachment_name += f" - {round(duration_ms, 2)}ms"

        allure.attach(
            json.dumps(response_details, indent=2, ensure_ascii=False),
            name=attachment_name,
            attachment_type=allure.attachment_type.JSON,
        )

    async def handle_http_request_error_event(self, event) -> None:
        """处理 HTTP 请求错误事件 (来自 EventBus)

        v3.17.0 新增: 处理请求错误事件，整合 OpenTelemetry 追踪上下文。

        Args:
            event: HttpRequestErrorEvent（带 correlation_id、trace_id、span_id）
        """
        if not is_allure_enabled():
            return

        # v3.17.0: 清理关联映射
        correlation_id = getattr(event, "correlation_id", None)
        if correlation_id:
            self._event_correlations.pop(correlation_id, None)

        # 计算耗时
        duration_ms = event.duration * 1000 if event.duration else 0

        # 错误详情
        # v3.17.0: 包含 OpenTelemetry 追踪上下文（仅在有值时显示）
        error_details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": correlation_id,
            "method": event.method,
            "url": event.url,
            "error_type": event.error_type,
            "error_message": event.error_message,
            "duration_ms": round(duration_ms, 2) if duration_ms else None,
        }

        # 仅在启用 OpenTelemetry 时添加追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            error_details["trace_id"] = trace_id
        if span_id:
            error_details["span_id"] = span_id

        allure.attach(
            json.dumps(error_details, indent=2, ensure_ascii=False),
            name=f"❌ {event.method} {event.url} - Error ({event.error_type})",
            attachment_type=allure.attachment_type.JSON,
        )

    async def handle_middleware_execute_event(self, event) -> None:
        """处理中间件执行事件 (来自 EventBus)

        v3.17.0 新增: 记录中间件对请求的修改。

        Args:
            event: MiddlewareExecuteEvent（带 correlation_id）
        """
        if not is_allure_enabled():
            return

        # 跳过空变化
        changes = getattr(event, "changes", {})
        if not changes:
            return

        middleware_name = getattr(event, "middleware_name", "Unknown")
        phase = getattr(event, "phase", "execute")
        correlation_id = getattr(event, "correlation_id", None)

        # 中间件执行详情
        middleware_details = {
            "middleware": middleware_name,
            "phase": phase,
            "correlation_id": correlation_id,
            "changes": changes,
        }

        # 使用 sub-step 展示中间件执行
        phase_emoji = "⬆️" if phase == "before" else "⬇️"
        allure.attach(
            json.dumps(middleware_details, indent=2, ensure_ascii=False),
            name=f"  {phase_emoji} {middleware_name} ({phase})",
            attachment_type=allure.attachment_type.JSON,
        )

    # ========== GraphQL EventBus 事件处理器 (v3.33.0 新增) ==========

    async def handle_graphql_request_start_event(self, event) -> None:
        """处理 GraphQL 请求开始事件 (来自 EventBus)

        v3.33.0 新增: 支持 GraphQL 中间件系统的事件发布

        Args:
            event: GraphQLRequestStartEvent
        """
        if not is_allure_enabled():
            return

        self.graphql_counter += 1

        correlation_id = getattr(event, "correlation_id", None)
        event_id = getattr(event, "event_id", None)
        if correlation_id and event_id:
            self._event_correlations[correlation_id] = event_id

        # 附加请求详情
        # v3.40.0: 应用脱敏
        request_details: dict[str, Any] = {
            "event_id": event_id,
            "correlation_id": correlation_id,
            "url": getattr(event, "url", ""),
            "operation_type": getattr(event, "operation_type", ""),
            "operation_name": getattr(event, "operation_name", None),
        }

        # 可选字段
        query = getattr(event, "query", None)
        if query:
            request_details["query"] = self._truncate(query, self.max_sql_length)

        # v3.40.0: 变量可能包含敏感信息，需要脱敏
        variables = getattr(event, "variables", None)
        if variables:
            request_details["variables"] = self._sanitize_for_allure(variables)

        # OpenTelemetry 追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            request_details["trace_id"] = trace_id
        if span_id:
            request_details["span_id"] = span_id

        op_name = request_details["operation_name"] or "anonymous"
        op_type = request_details["operation_type"] or "query"

        allure.attach(
            json.dumps(request_details, indent=2, ensure_ascii=False, default=str),
            name=f"📊 GraphQL {op_type}: {op_name} - Request",
            attachment_type=allure.attachment_type.JSON,
        )

    async def handle_graphql_request_end_event(self, event) -> None:
        """处理 GraphQL 请求结束事件 (来自 EventBus)

        v3.33.0 新增: 支持 GraphQL 中间件系统的事件发布

        Args:
            event: GraphQLRequestEndEvent
        """
        if not is_allure_enabled():
            return

        correlation_id = getattr(event, "correlation_id", None)
        if correlation_id:
            self._event_correlations.pop(correlation_id, None)

        duration = getattr(event, "duration", 0)
        duration_ms = duration * 1000 if duration else 0
        has_errors = getattr(event, "has_errors", False)
        error_count = getattr(event, "error_count", 0)

        # 响应详情
        # v3.40.0: 应用脱敏
        response_details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": correlation_id,
            "url": getattr(event, "url", ""),
            "operation_type": getattr(event, "operation_type", ""),
            "operation_name": getattr(event, "operation_name", None),
            "has_errors": has_errors,
            "error_count": error_count,
            "duration_ms": round(duration_ms, 2) if duration_ms else None,
        }

        # 可选字段
        # v3.40.0: 响应数据可能包含敏感信息，需要脱敏
        data = getattr(event, "data", None)
        if data:
            truncated_data = self._truncate(data, self.max_body_length)
            response_details["data"] = self._sanitize_body_content(truncated_data)

        # OpenTelemetry 追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            response_details["trace_id"] = trace_id
        if span_id:
            response_details["span_id"] = span_id

        # 根据是否有错误选择 emoji
        status_emoji = "❌" if has_errors else "✅"
        op_name = response_details["operation_name"] or "anonymous"
        op_type = response_details["operation_type"] or "query"

        attachment_name = f"{status_emoji} GraphQL {op_type}: {op_name} - Response"
        if duration_ms:
            attachment_name += f" ({duration_ms:.2f}ms)"

        allure.attach(
            json.dumps(response_details, indent=2, ensure_ascii=False),
            name=attachment_name,
            attachment_type=allure.attachment_type.JSON,
        )

    async def handle_graphql_request_error_event(self, event) -> None:
        """处理 GraphQL 请求错误事件 (来自 EventBus)

        v3.33.0 新增: 支持 GraphQL 中间件系统的事件发布
        注意：此事件用于 HTTP 传输层错误，GraphQL 业务错误通过 EndEvent.has_errors 标识

        Args:
            event: GraphQLRequestErrorEvent
        """
        if not is_allure_enabled():
            return

        correlation_id = getattr(event, "correlation_id", None)
        if correlation_id:
            self._event_correlations.pop(correlation_id, None)

        duration = getattr(event, "duration", 0)
        duration_ms = duration * 1000 if duration else 0

        # 错误详情
        error_details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": correlation_id,
            "url": getattr(event, "url", ""),
            "operation_type": getattr(event, "operation_type", ""),
            "operation_name": getattr(event, "operation_name", None),
            "error_type": getattr(event, "error_type", "UnknownError"),
            "error_message": getattr(event, "error_message", ""),
            "duration_ms": round(duration_ms, 2) if duration_ms else None,
        }

        # OpenTelemetry 追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            error_details["trace_id"] = trace_id
        if span_id:
            error_details["span_id"] = span_id

        op_name = error_details["operation_name"] or "anonymous"
        op_type = error_details["operation_type"] or "query"
        error_type = error_details["error_type"]

        allure.attach(
            json.dumps(error_details, indent=2, ensure_ascii=False),
            name=f"❌ GraphQL {op_type}: {op_name} - Error ({error_type})",
            attachment_type=allure.attachment_type.JSON,
        )

    # ========== GraphQL 观察方法 (v3.12.0 新增) ==========

    def on_graphql_request_start(
        self,
        operation_name: str | None,
        operation_type: str,
        query: str,
        variables: dict[str, Any] | None = None,
    ) -> str | None:
        """GraphQL请求开始

        Args:
            operation_name: 操作名称
            operation_type: 操作类型（query/mutation/subscription）
            query: GraphQL查询字符串
            variables: 查询变量

        Returns:
            graphql_id - 用于关联后续事件
        """
        if not is_allure_enabled():
            return None

        self.graphql_counter += 1
        graphql_id = f"gql-{self.graphql_counter:03d}"

        # 创建上下文状态
        ctx = StepContext()

        # 创建Allure step
        op_name = operation_name or "anonymous"
        step_title = f"📊 GraphQL {operation_type}: {op_name}"
        ctx.step_context = allure.step(step_title)
        ctx.exit_stack.enter_context(ctx.step_context)

        # 存储上下文
        self._graphql_contexts[graphql_id] = ctx

        # 附加请求详情
        request_details = {
            "graphql_id": graphql_id,
            "operation_name": operation_name,
            "operation_type": operation_type,
            "query": self._truncate(query, self.max_sql_length),
            "variables": variables,
        }

        allure.attach(
            json.dumps(request_details, indent=2, ensure_ascii=False),
            name="📤 GraphQL Request",
            attachment_type=allure.attachment_type.JSON,
        )

        return graphql_id

    def on_graphql_request_end(
        self,
        graphql_id: str,
        data: dict[str, Any] | None = None,
        errors: list[dict[str, Any]] | None = None,
        duration_ms: float | None = None,
    ) -> None:
        """GraphQL请求结束

        Args:
            graphql_id: GraphQL请求ID
            data: 响应数据
            errors: GraphQL错误列表
            duration_ms: 请求耗时
        """
        if not is_allure_enabled():
            return

        ctx = self._graphql_contexts.get(graphql_id)
        if not ctx:
            return

        try:
            if duration_ms is None:
                duration_ms = (time.time() - ctx.start_time) * 1000

            response_details = {
                "graphql_id": graphql_id,
                "has_data": data is not None,
                "has_errors": bool(errors),
                "error_count": len(errors) if errors else 0,
                "duration_ms": round(duration_ms, 2) if duration_ms else None,
            }

            if errors:
                response_details["errors"] = errors

            # 根据是否有错误选择emoji
            status_emoji = "❌" if errors else "✅"
            attachment_name = f"{status_emoji} GraphQL Response"
            if duration_ms:
                attachment_name += f" - {round(duration_ms, 2)}ms"

            allure.attach(
                json.dumps(response_details, indent=2, ensure_ascii=False),
                name=attachment_name,
                attachment_type=allure.attachment_type.JSON,
            )
        finally:
            ctx.exit_stack.close()
            self._graphql_contexts.pop(graphql_id, None)

    # ========== gRPC 观察方法 (v3.12.0 新增) ==========

    def on_grpc_call_start(
        self,
        service: str,
        method: str,
        request_type: str,
        metadata: dict[str, str] | None = None,
    ) -> str | None:
        """gRPC调用开始

        Args:
            service: 服务名称
            method: 方法名称
            request_type: 请求类型（unary/server_streaming/client_streaming/bidi_streaming）
            metadata: gRPC元数据

        Returns:
            grpc_id - 用于关联后续事件
        """
        if not is_allure_enabled():
            return None

        self.grpc_counter += 1
        grpc_id = f"grpc-{self.grpc_counter:03d}"

        # 创建上下文状态
        ctx = StepContext()

        # 创建Allure step
        step_title = f"🔌 gRPC {service}/{method}"
        ctx.step_context = allure.step(step_title)
        ctx.exit_stack.enter_context(ctx.step_context)

        # 存储上下文
        self._grpc_contexts[grpc_id] = ctx

        # 附加请求详情
        # v3.40.0: metadata 可能包含 token 等敏感信息，需要脱敏
        request_details = {
            "grpc_id": grpc_id,
            "service": service,
            "method": method,
            "request_type": request_type,
            "metadata": self._sanitize_for_allure(metadata),
        }

        allure.attach(
            json.dumps(request_details, indent=2, ensure_ascii=False),
            name="📤 gRPC Request",
            attachment_type=allure.attachment_type.JSON,
        )

        return grpc_id

    def on_grpc_call_end(
        self,
        grpc_id: str,
        status_code: str,
        status_message: str | None = None,
        duration_ms: float | None = None,
    ) -> None:
        """gRPC调用结束

        Args:
            grpc_id: gRPC调用ID
            status_code: gRPC状态码（如 "OK", "INVALID_ARGUMENT"）
            status_message: 状态消息
            duration_ms: 调用耗时
        """
        if not is_allure_enabled():
            return

        ctx = self._grpc_contexts.get(grpc_id)
        if not ctx:
            return

        try:
            if duration_ms is None:
                duration_ms = (time.time() - ctx.start_time) * 1000

            response_details = {
                "grpc_id": grpc_id,
                "status_code": status_code,
                "status_message": status_message,
                "duration_ms": round(duration_ms, 2) if duration_ms else None,
            }

            # 根据状态码选择emoji
            status_emoji = "✅" if status_code == "OK" else "❌"
            attachment_name = f"{status_emoji} gRPC Response ({status_code})"
            if duration_ms:
                attachment_name += f" - {round(duration_ms, 2)}ms"

            allure.attach(
                json.dumps(response_details, indent=2, ensure_ascii=False),
                name=attachment_name,
                attachment_type=allure.attachment_type.JSON,
            )
        finally:
            ctx.exit_stack.close()
            self._grpc_contexts.pop(grpc_id, None)

    # ========== Database EventBus 事件处理器 (v3.18.0) ==========

    def handle_database_query_start_event(self, event) -> None:
        """处理数据库查询开始事件 (来自 EventBus)

        v3.18.0 新增: 支持 Database CorrelatedEvent
        v3.17.1 修复: 改为同步以匹配 Database.publish_sync()

        Args:
            event: DatabaseQueryStartEvent
        """
        if not is_allure_enabled():
            return

        operation = getattr(event, "operation", "QUERY")
        table = getattr(event, "table", "unknown")
        sql = getattr(event, "sql", "")
        params = getattr(event, "params", {})
        correlation_id = getattr(event, "correlation_id", None)

        # 创建上下文状态（使用 correlation_id 作为 key）
        if correlation_id:
            ctx = StepContext()
            step_title = f"🗄️ {operation} {table}"
            ctx.step_context = allure.step(step_title)
            ctx.exit_stack.enter_context(ctx.step_context)
            self._query_contexts[correlation_id] = ctx

        # 附加查询详情
        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": correlation_id,
            "operation": operation,
            "table": table,
        }
        if sql:
            details["sql"] = self._truncate(sql, self.max_sql_length)
        if params:
            details["params"] = params

        # 添加追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            details["trace_id"] = trace_id
        if span_id:
            details["span_id"] = span_id

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False, default=str),
            name=f"📜 Query Start: {operation} {table}",
            attachment_type=allure.attachment_type.JSON,
        )

    def handle_database_query_end_event(self, event) -> None:
        """处理数据库查询结束事件 (来自 EventBus)

        v3.18.0 新增: 支持 Database CorrelatedEvent
        v3.17.1 修复: 改为同步以匹配 Database.publish_sync()

        Args:
            event: DatabaseQueryEndEvent
        """
        if not is_allure_enabled():
            return

        correlation_id = getattr(event, "correlation_id", None)
        operation = getattr(event, "operation", "QUERY")
        table = getattr(event, "table", "unknown")
        row_count = getattr(event, "row_count", 0)
        duration_ms = getattr(event, "duration_ms", 0)

        # 构建结果详情
        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": correlation_id,
            "operation": operation,
            "table": table,
            "row_count": row_count,
            "duration_ms": round(duration_ms, 2) if duration_ms else None,
        }

        # 添加追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            details["trace_id"] = trace_id
        if span_id:
            details["span_id"] = span_id

        attachment_name = f"✅ Query Done: {row_count} rows"
        if duration_ms:
            attachment_name += f" ({duration_ms:.2f}ms)"

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=attachment_name,
            attachment_type=allure.attachment_type.JSON,
        )

        # 关闭 step 上下文
        if correlation_id:
            ctx = self._query_contexts.pop(correlation_id, None)
            if ctx:
                ctx.exit_stack.close()

    def handle_database_query_error_event(self, event) -> None:
        """处理数据库查询错误事件 (来自 EventBus)

        v3.18.0 新增: 支持 Database CorrelatedEvent
        v3.17.1 修复: 改为同步以匹配 Database.publish_sync()

        Args:
            event: DatabaseQueryErrorEvent
        """
        if not is_allure_enabled():
            return

        correlation_id = getattr(event, "correlation_id", None)
        operation = getattr(event, "operation", "QUERY")
        table = getattr(event, "table", "unknown")
        error_type = getattr(event, "error_type", "UnknownError")
        error_message = getattr(event, "error_message", "")
        duration_ms = getattr(event, "duration_ms", 0)

        # 构建错误详情
        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": correlation_id,
            "operation": operation,
            "table": table,
            "error_type": error_type,
            "error_message": error_message,
            "duration_ms": round(duration_ms, 2) if duration_ms else None,
        }

        # 添加追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            details["trace_id"] = trace_id
        if span_id:
            details["span_id"] = span_id

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=f"❌ Query Error: {error_type}",
            attachment_type=allure.attachment_type.JSON,
        )

        # 关闭 step 上下文
        if correlation_id:
            ctx = self._query_contexts.pop(correlation_id, None)
            if ctx:
                ctx.exit_stack.close()

    # ========== Redis EventBus 事件处理器 (v3.18.0) ==========

    async def handle_cache_operation_start_event(self, event) -> None:
        """处理缓存操作开始事件 (来自 EventBus)

        v3.18.0 新增: 支持 Cache 事件

        Args:
            event: CacheOperationStartEvent
        """
        if not is_allure_enabled():
            return

        operation = getattr(event, "operation", "UNKNOWN")
        key = getattr(event, "key", "")
        field = getattr(event, "field", None)
        correlation_id = getattr(event, "correlation_id", None)

        # 存储关联 ID
        if correlation_id:
            self._event_correlations[correlation_id] = getattr(event, "event_id", "")

        # 附加开始事件详情
        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": correlation_id,
            "operation": operation,
            "key": key,
        }
        if field:
            details["field"] = field

        # 添加追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            details["trace_id"] = trace_id
        if span_id:
            details["span_id"] = span_id

        if field:
            attachment_name = f"💾 Redis {operation}: {key}[{field}] - Start"
        else:
            attachment_name = f"💾 Redis {operation}: {key} - Start"

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=attachment_name,
            attachment_type=allure.attachment_type.JSON,
        )

    async def handle_cache_operation_end_event(self, event) -> None:
        """处理缓存操作结束事件 (来自 EventBus)

        v3.18.0 新增: 支持 Cache 事件

        Args:
            event: CacheOperationEndEvent
        """
        if not is_allure_enabled():
            return

        # 清理关联映射
        correlation_id = getattr(event, "correlation_id", None)
        if correlation_id:
            self._event_correlations.pop(correlation_id, None)

        operation = getattr(event, "operation", "UNKNOWN")
        key = getattr(event, "key", "")
        hit = getattr(event, "hit", None)
        duration_ms = getattr(event, "duration_ms", 0)

        # 构建响应详情
        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": correlation_id,
            "operation": operation,
            "key": key,
            "duration_ms": round(duration_ms, 2) if duration_ms else None,
        }
        if hit is not None:
            details["hit"] = hit

        # 添加追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            details["trace_id"] = trace_id
        if span_id:
            details["span_id"] = span_id

        # 根据操作和命中状态选择 emoji
        if operation in ("GET", "HGET", "SISMEMBER", "HEXISTS") and hit is not None:
            status_emoji = "✅" if hit else "⚠️"
            hit_text = "HIT" if hit else "MISS"
            attachment_name = f"{status_emoji} Redis {operation}: {key} - {hit_text}"
        else:
            attachment_name = f"✅ Redis {operation}: {key} - Done"

        if duration_ms:
            attachment_name += f" ({duration_ms:.2f}ms)"

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=attachment_name,
            attachment_type=allure.attachment_type.JSON,
        )

    async def handle_cache_operation_error_event(self, event) -> None:
        """处理缓存操作错误事件 (来自 EventBus)

        v3.18.0 新增: 支持 Cache 事件

        Args:
            event: CacheOperationErrorEvent
        """
        if not is_allure_enabled():
            return

        # 清理关联映射
        correlation_id = getattr(event, "correlation_id", None)
        if correlation_id:
            self._event_correlations.pop(correlation_id, None)

        operation = getattr(event, "operation", "UNKNOWN")
        key = getattr(event, "key", "")
        error_type = getattr(event, "error_type", "UnknownError")
        error_message = getattr(event, "error_message", "")
        duration_ms = getattr(event, "duration_ms", 0)

        # 构建错误详情
        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": correlation_id,
            "operation": operation,
            "key": key,
            "error_type": error_type,
            "error_message": error_message,
            "duration_ms": round(duration_ms, 2) if duration_ms else None,
        }

        # 添加追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            details["trace_id"] = trace_id
        if span_id:
            details["span_id"] = span_id

        attachment_name = f"❌ Redis {operation}: {key} - Error ({error_type})"

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=attachment_name,
            attachment_type=allure.attachment_type.JSON,
        )

    # ========== 消息队列方法 (v3.18.0) ==========

    def on_message_publish(
        self,
        queue_type: str,
        topic: str,
        message: dict[str, Any] | str | bytes,
        key: str | None = None,
        partition: int | None = None,
        headers: dict[str, str] | None = None,
        message_id: str | None = None,
        duration_ms: float | None = None,
    ) -> None:
        """记录消息发布到 Allure

        v3.18.0 新增

        Args:
            queue_type: 队列类型 (kafka, rabbitmq, rocketmq)
            topic: 主题/队列名称
            message: 消息内容
            key: 消息键（Kafka）
            partition: 分区（Kafka）
            headers: 消息头
            message_id: 消息 ID
            duration_ms: 发送耗时
        """
        if not is_allure_enabled():
            return

        # 构建 step 标题
        step_title = f"📤 {queue_type.upper()}: Publish → {topic}"
        if duration_ms is not None:
            step_title += f" ({duration_ms:.2f}ms)"

        with allure.step(step_title):
            publish_details: dict[str, Any] = {
                "queue_type": queue_type,
                "topic": topic,
            }

            if key:
                publish_details["key"] = key
            if partition is not None:
                publish_details["partition"] = partition
            if message_id:
                publish_details["message_id"] = message_id
            if headers:
                publish_details["headers"] = headers
            if duration_ms is not None:
                publish_details["duration_ms"] = round(duration_ms, 2)

            # 处理消息体
            if isinstance(message, dict):
                message_str = json.dumps(message, indent=2, ensure_ascii=False, default=str)
            elif isinstance(message, bytes):
                try:
                    message_str = message.decode("utf-8")
                except UnicodeDecodeError:
                    message_str = f"<binary: {len(message)} bytes>"
            else:
                message_str = str(message)

            publish_details["message"] = self._truncate(message_str, self.max_body_length)

            allure.attach(
                json.dumps(publish_details, indent=2, ensure_ascii=False, default=str),
                name=f"Message Published: {topic}",
                attachment_type=allure.attachment_type.JSON,
            )

    def on_message_consume(
        self,
        queue_type: str,
        topic: str,
        message: dict[str, Any] | str | bytes,
        consumer_group: str | None = None,
        partition: int | None = None,
        offset: int | None = None,
        message_id: str | None = None,
        processing_time_ms: float | None = None,
    ) -> None:
        """记录消息消费到 Allure

        v3.18.0 新增

        Args:
            queue_type: 队列类型 (kafka, rabbitmq, rocketmq)
            topic: 主题/队列名称
            message: 消息内容
            consumer_group: 消费者组
            partition: 分区（Kafka）
            offset: 偏移量（Kafka）
            message_id: 消息 ID
            processing_time_ms: 处理耗时
        """
        if not is_allure_enabled():
            return

        # 构建 step 标题
        step_title = f"📥 {queue_type.upper()}: Consume ← {topic}"
        if processing_time_ms is not None:
            step_title += f" ({processing_time_ms:.2f}ms)"

        with allure.step(step_title):
            consume_details: dict[str, Any] = {
                "queue_type": queue_type,
                "topic": topic,
            }

            if consumer_group:
                consume_details["consumer_group"] = consumer_group
            if partition is not None:
                consume_details["partition"] = partition
            if offset is not None:
                consume_details["offset"] = offset
            if message_id:
                consume_details["message_id"] = message_id
            if processing_time_ms is not None:
                consume_details["processing_time_ms"] = round(processing_time_ms, 2)

            # 处理消息体
            if isinstance(message, dict):
                message_str = json.dumps(message, indent=2, ensure_ascii=False, default=str)
            elif isinstance(message, bytes):
                try:
                    message_str = message.decode("utf-8")
                except UnicodeDecodeError:
                    message_str = f"<binary: {len(message)} bytes>"
            else:
                message_str = str(message)

            consume_details["message"] = self._truncate(message_str, self.max_body_length)

            allure.attach(
                json.dumps(consume_details, indent=2, ensure_ascii=False, default=str),
                name=f"Message Consumed: {topic}",
                attachment_type=allure.attachment_type.JSON,
            )

    async def handle_message_publish_end_event(self, event) -> None:
        """处理消息发布成功事件 (来自 EventBus)

        v3.34.1 重构（原 handle_message_publish_event）

        Args:
            event: MessagePublishEndEvent
        """
        if not is_allure_enabled():
            return

        topic = getattr(event, "topic", "")
        messenger_type = getattr(event, "messenger_type", "")
        message_id = getattr(event, "message_id", None)
        duration = getattr(event, "duration", 0)
        partition = getattr(event, "partition", None)
        offset = getattr(event, "offset", None)

        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": getattr(event, "correlation_id", None),
            "messenger_type": messenger_type,
            "topic": topic,
            "duration_ms": round(duration * 1000, 2) if duration else None,
        }

        if message_id:
            details["message_id"] = message_id
        if partition is not None:
            details["partition"] = partition
        if offset is not None:
            details["offset"] = offset

        # 添加追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            details["trace_id"] = trace_id
        if span_id:
            details["span_id"] = span_id

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=f"📤 [{messenger_type}] Published: {topic}",
            attachment_type=allure.attachment_type.JSON,
        )

    async def handle_message_publish_error_event(self, event) -> None:
        """处理消息发布错误事件 (来自 EventBus)

        v3.34.1 新增

        Args:
            event: MessagePublishErrorEvent
        """
        if not is_allure_enabled():
            return

        topic = getattr(event, "topic", "")
        messenger_type = getattr(event, "messenger_type", "")
        error_type = getattr(event, "error_type", "")
        error_message = getattr(event, "error_message", "")
        duration = getattr(event, "duration", 0)

        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": getattr(event, "correlation_id", None),
            "messenger_type": messenger_type,
            "topic": topic,
            "error_type": error_type,
            "error_message": error_message,
            "duration_ms": round(duration * 1000, 2) if duration else None,
        }

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=f"❌ [{messenger_type}] Publish Failed: {topic}",
            attachment_type=allure.attachment_type.JSON,
        )

    async def handle_message_consume_end_event(self, event) -> None:
        """处理消息消费成功事件 (来自 EventBus)

        v3.34.1 重构（原 handle_message_consume_event）

        Args:
            event: MessageConsumeEndEvent
        """
        if not is_allure_enabled():
            return

        topic = getattr(event, "topic", "")
        messenger_type = getattr(event, "messenger_type", "")
        message_id = getattr(event, "message_id", None)
        consumer_group = getattr(event, "consumer_group", None)
        processing_time = getattr(event, "processing_time", 0)
        partition = getattr(event, "partition", None)
        offset = getattr(event, "offset", None)

        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": getattr(event, "correlation_id", None),
            "messenger_type": messenger_type,
            "topic": topic,
            "processing_time_ms": round(processing_time * 1000, 2) if processing_time else None,
        }

        if message_id:
            details["message_id"] = message_id
        if consumer_group:
            details["consumer_group"] = consumer_group
        if partition is not None:
            details["partition"] = partition
        if offset is not None:
            details["offset"] = offset

        # 添加追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            details["trace_id"] = trace_id
        if span_id:
            details["span_id"] = span_id

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=f"📥 [{messenger_type}] Consumed: {topic}",
            attachment_type=allure.attachment_type.JSON,
        )

    async def handle_message_consume_error_event(self, event) -> None:
        """处理消息消费错误事件 (来自 EventBus)

        v3.34.1 新增

        Args:
            event: MessageConsumeErrorEvent
        """
        if not is_allure_enabled():
            return

        topic = getattr(event, "topic", "")
        messenger_type = getattr(event, "messenger_type", "")
        message_id = getattr(event, "message_id", None)
        consumer_group = getattr(event, "consumer_group", None)
        error_type = getattr(event, "error_type", "")
        error_message = getattr(event, "error_message", "")
        processing_time = getattr(event, "processing_time", 0)

        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": getattr(event, "correlation_id", None),
            "messenger_type": messenger_type,
            "topic": topic,
            "error_type": error_type,
            "error_message": error_message,
            "processing_time_ms": round(processing_time * 1000, 2) if processing_time else None,
        }

        if message_id:
            details["message_id"] = message_id
        if consumer_group:
            details["consumer_group"] = consumer_group

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=f"❌ [{messenger_type}] Consume Failed: {topic}",
            attachment_type=allure.attachment_type.JSON,
        )

    # ========== 存储方法 (v3.18.0) ==========

    def on_storage_operation(
        self,
        storage_type: str,
        operation: str,
        path: str,
        size: int | None = None,
        duration_ms: float | None = None,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """记录存储操作到 Allure

        v3.18.0 新增

        Args:
            storage_type: 存储类型 (local, s3, oss)
            operation: 操作类型 (upload, download, delete, copy, move, list)
            path: 文件路径或对象键
            size: 文件大小（字节）
            duration_ms: 操作耗时
            success: 是否成功
            error: 错误信息（失败时）
        """
        if not is_allure_enabled():
            return

        # 选择 emoji
        emoji_map = {
            "upload": "⬆️",
            "download": "⬇️",
            "delete": "🗑️",
            "copy": "📋",
            "move": "📦",
            "list": "📂",
        }
        emoji = emoji_map.get(operation.lower(), "📁")

        # 构建 step 标题
        step_title = f"{emoji} {storage_type.upper()}: {operation} {path}"
        if not success:
            step_title += " ❌"
        elif duration_ms is not None:
            step_title += f" ({duration_ms:.2f}ms)"

        with allure.step(step_title):
            storage_details: dict[str, Any] = {
                "storage_type": storage_type,
                "operation": operation,
                "path": path,
                "success": success,
            }

            if size is not None:
                # 格式化文件大小
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.2f} KB"
                else:
                    size_str = f"{size / (1024 * 1024):.2f} MB"
                storage_details["size"] = size_str
                storage_details["size_bytes"] = size

            if duration_ms is not None:
                storage_details["duration_ms"] = round(duration_ms, 2)

            if error:
                storage_details["error"] = error

            allure.attach(
                json.dumps(storage_details, indent=2, ensure_ascii=False, default=str),
                name=f"Storage {operation}: {path}",
                attachment_type=allure.attachment_type.JSON,
            )

    async def handle_storage_operation_start_event(self, event) -> None:
        """处理存储操作开始事件 (来自 EventBus)

        v3.18.0 新增

        Args:
            event: StorageOperationStartEvent
        """
        if not is_allure_enabled():
            return

        storage_type = getattr(event, "storage_type", "unknown")
        operation = getattr(event, "operation", "UNKNOWN")
        path = getattr(event, "path", "")
        size = getattr(event, "size", None)
        correlation_id = getattr(event, "correlation_id", None)

        # 存储关联 ID
        if correlation_id:
            self._event_correlations[correlation_id] = getattr(event, "event_id", "")

        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": correlation_id,
            "storage_type": storage_type,
            "operation": operation,
            "path": path,
        }

        if size is not None:
            details["size"] = size

        # 添加追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            details["trace_id"] = trace_id
        if span_id:
            details["span_id"] = span_id

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=f"📁 Storage {operation}: {path} - Start",
            attachment_type=allure.attachment_type.JSON,
        )

    async def handle_storage_operation_end_event(self, event) -> None:
        """处理存储操作结束事件 (来自 EventBus)

        v3.18.0 新增

        Args:
            event: StorageOperationEndEvent
        """
        if not is_allure_enabled():
            return

        # 清理关联映射
        correlation_id = getattr(event, "correlation_id", None)
        if correlation_id:
            self._event_correlations.pop(correlation_id, None)

        storage_type = getattr(event, "storage_type", "unknown")
        operation = getattr(event, "operation", "UNKNOWN")
        path = getattr(event, "path", "")
        size = getattr(event, "size", None)
        duration_ms = getattr(event, "duration_ms", 0)

        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": correlation_id,
            "storage_type": storage_type,
            "operation": operation,
            "path": path,
            "duration_ms": round(duration_ms, 2) if duration_ms else None,
        }

        if size is not None:
            details["size"] = size

        # 添加追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            details["trace_id"] = trace_id
        if span_id:
            details["span_id"] = span_id

        attachment_name = f"✅ Storage {operation}: {path} - Done"
        if duration_ms:
            attachment_name += f" ({duration_ms:.2f}ms)"

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=attachment_name,
            attachment_type=allure.attachment_type.JSON,
        )

    async def handle_storage_operation_error_event(self, event) -> None:
        """处理存储操作错误事件 (来自 EventBus)

        v3.18.0 新增

        Args:
            event: StorageOperationErrorEvent
        """
        if not is_allure_enabled():
            return

        # 清理关联映射
        correlation_id = getattr(event, "correlation_id", None)
        if correlation_id:
            self._event_correlations.pop(correlation_id, None)

        storage_type = getattr(event, "storage_type", "unknown")
        operation = getattr(event, "operation", "UNKNOWN")
        path = getattr(event, "path", "")
        error_type = getattr(event, "error_type", "UnknownError")
        error_message = getattr(event, "error_message", "")
        duration_ms = getattr(event, "duration_ms", 0)

        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": correlation_id,
            "storage_type": storage_type,
            "operation": operation,
            "path": path,
            "error_type": error_type,
            "error_message": error_message,
            "duration_ms": round(duration_ms, 2) if duration_ms else None,
        }

        # 添加追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            details["trace_id"] = trace_id
        if span_id:
            details["span_id"] = span_id

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=f"❌ Storage {operation}: {path} - Error ({error_type})",
            attachment_type=allure.attachment_type.JSON,
        )

    # ========== 事务事件处理 (v3.18.0) ==========

    def handle_transaction_commit_event(self, event) -> None:
        """处理事务提交事件（同步）

        v3.18.0: 新增

        Args:
            event: TransactionCommitEvent
        """
        if not is_allure_enabled():
            return

        repository_count = getattr(event, "repository_count", 0)
        session_id = getattr(event, "session_id", None)

        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "repository_count": repository_count,
            "session_id": session_id,
        }

        # 添加追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            details["trace_id"] = trace_id
        if span_id:
            details["span_id"] = span_id

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=f"💾 Transaction COMMIT ({repository_count} repositories)",
            attachment_type=allure.attachment_type.JSON,
        )

    def handle_transaction_rollback_event(self, event) -> None:
        """处理事务回滚事件（同步）

        v3.18.0: 新增

        Args:
            event: TransactionRollbackEvent
        """
        if not is_allure_enabled():
            return

        repository_count = getattr(event, "repository_count", 0)
        reason = getattr(event, "reason", "auto")
        session_id = getattr(event, "session_id", None)

        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "repository_count": repository_count,
            "reason": reason,
            "session_id": session_id,
        }

        # 添加追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            details["trace_id"] = trace_id
        if span_id:
            details["span_id"] = span_id

        # 根据回滚原因使用不同的emoji
        reason_icon = {
            "auto": "🔄",  # 自动回滚
            "exception": "❌",  # 异常回滚
            "manual": "↩️",  # 手动回滚
        }.get(reason, "🔄")

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=f"{reason_icon} Transaction ROLLBACK ({reason}, {repository_count} repositories)",
            attachment_type=allure.attachment_type.JSON,
        )

    # ========== UI 事件处理 (v3.35.7) ==========

    async def handle_ui_navigation_start_event(self, event) -> None:
        """处理 UI 导航开始事件

        v3.35.7: 新增

        Args:
            event: UINavigationStartEvent
        """
        if not is_allure_enabled():
            return

        self.ui_counter += 1
        page_name = getattr(event, "page_name", "Page")
        url = getattr(event, "url", "")
        correlation_id = getattr(event, "correlation_id", None)

        if correlation_id:
            self._event_correlations[correlation_id] = getattr(event, "event_id", "")

        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": correlation_id,
            "page_name": page_name,
            "url": url,
            "base_url": getattr(event, "base_url", ""),
        }

        # 添加追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            details["trace_id"] = trace_id
        if span_id:
            details["span_id"] = span_id

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=f"🌐 Navigate: {page_name} → {url}",
            attachment_type=allure.attachment_type.JSON,
        )

    async def handle_ui_navigation_end_event(self, event) -> None:
        """处理 UI 导航结束事件

        v3.35.7: 新增

        Args:
            event: UINavigationEndEvent
        """
        if not is_allure_enabled():
            return

        correlation_id = getattr(event, "correlation_id", None)
        if correlation_id:
            self._event_correlations.pop(correlation_id, None)

        page_name = getattr(event, "page_name", "Page")
        url = getattr(event, "url", "")
        title = getattr(event, "title", "")
        duration = getattr(event, "duration", 0)
        success = getattr(event, "success", True)

        duration_ms = duration * 1000 if duration else 0

        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "correlation_id": correlation_id,
            "page_name": page_name,
            "url": url,
            "title": title,
            "success": success,
            "duration_ms": round(duration_ms, 2) if duration_ms else None,
        }

        status_emoji = "✅" if success else "❌"
        display_title = title[:30] if title else page_name
        attachment_name = f"{status_emoji} Navigate: {display_title}"
        if duration_ms:
            attachment_name += f" ({duration_ms:.1f}ms)"

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=attachment_name,
            attachment_type=allure.attachment_type.JSON,
        )

    async def handle_ui_click_event(self, event) -> None:
        """处理 UI 点击事件

        v3.35.7: 新增

        Args:
            event: UIClickEvent
        """
        if not is_allure_enabled():
            return

        page_name = getattr(event, "page_name", "Page")
        selector = getattr(event, "selector", "")
        element_text = getattr(event, "element_text", "")
        duration = getattr(event, "duration", 0)

        duration_ms = duration * 1000 if duration else 0

        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "page_name": page_name,
            "selector": selector,
            "element_text": element_text,
            "duration_ms": round(duration_ms, 2) if duration_ms else None,
        }

        display_text = element_text if element_text else selector[:30]
        attachment_name = f"🖱️ Click: {display_text}"
        if duration_ms:
            attachment_name += f" ({duration_ms:.1f}ms)"

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=attachment_name,
            attachment_type=allure.attachment_type.JSON,
        )

    async def handle_ui_input_event(self, event) -> None:
        """处理 UI 输入事件

        v3.35.7: 新增

        Args:
            event: UIInputEvent
        """
        if not is_allure_enabled():
            return

        page_name = getattr(event, "page_name", "Page")
        selector = getattr(event, "selector", "")
        value = getattr(event, "value", "")
        masked = getattr(event, "masked", False)
        duration = getattr(event, "duration", 0)

        duration_ms = duration * 1000 if duration else 0
        display_value = "***" if masked else value

        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "page_name": page_name,
            "selector": selector,
            "value": display_value,
            "masked": masked,
            "duration_ms": round(duration_ms, 2) if duration_ms else None,
        }

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=f"⌨️ Input: {selector} = '{display_value}'",
            attachment_type=allure.attachment_type.JSON,
        )

    async def handle_ui_screenshot_event(self, event) -> None:
        """处理 UI 截图事件

        v3.35.7: 新增

        Args:
            event: UIScreenshotEvent
        """
        if not is_allure_enabled():
            return

        page_name = getattr(event, "page_name", "Page")
        path = getattr(event, "path", "")
        full_page = getattr(event, "full_page", False)
        size_bytes = getattr(event, "size_bytes", 0)

        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "page_name": page_name,
            "path": path,
            "full_page": full_page,
            "size_bytes": size_bytes,
            "size_kb": round(size_bytes / 1024, 2) if size_bytes else None,
        }

        scope = "full_page" if full_page else "viewport"
        attachment_name = f"📸 Screenshot: {page_name} ({scope})"

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=attachment_name,
            attachment_type=allure.attachment_type.JSON,
        )

        # 如果有路径，尝试附加实际截图
        if path:
            try:
                with open(path, "rb") as f:
                    allure.attach(
                        f.read(),
                        name=f"Screenshot: {page_name}",
                        attachment_type=allure.attachment_type.PNG,
                    )
            except Exception:
                pass

    async def handle_ui_wait_event(self, event) -> None:
        """处理 UI 等待事件

        v3.35.7: 新增

        Args:
            event: UIWaitEvent
        """
        if not is_allure_enabled():
            return

        page_name = getattr(event, "page_name", "Page")
        wait_type = getattr(event, "wait_type", "")
        condition = getattr(event, "condition", "")
        duration = getattr(event, "duration", 0)
        success = getattr(event, "success", True)

        duration_ms = duration * 1000 if duration else 0

        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "page_name": page_name,
            "wait_type": wait_type,
            "condition": condition,
            "success": success,
            "duration_ms": round(duration_ms, 2) if duration_ms else None,
        }

        status_emoji = "✅" if success else "⏰"
        attachment_name = f"{status_emoji} Wait: {wait_type} - {condition[:30]}"
        if duration_ms:
            attachment_name += f" ({duration_ms:.1f}ms)"

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=attachment_name,
            attachment_type=allure.attachment_type.JSON,
        )

    async def handle_ui_error_event(self, event) -> None:
        """处理 UI 错误事件

        v3.35.7: 新增

        Args:
            event: UIErrorEvent
        """
        if not is_allure_enabled():
            return

        page_name = getattr(event, "page_name", "Page")
        operation = getattr(event, "operation", "")
        selector = getattr(event, "selector", "")
        error_type = getattr(event, "error_type", "")
        error_message = getattr(event, "error_message", "")
        screenshot_path = getattr(event, "screenshot_path", "")

        details: dict[str, Any] = {
            "event_id": getattr(event, "event_id", None),
            "page_name": page_name,
            "operation": operation,
            "selector": selector,
            "error_type": error_type,
            "error_message": error_message,
        }

        # 添加追踪信息
        trace_id = getattr(event, "trace_id", None)
        span_id = getattr(event, "span_id", None)
        if trace_id:
            details["trace_id"] = trace_id
        if span_id:
            details["span_id"] = span_id

        allure.attach(
            json.dumps(details, indent=2, ensure_ascii=False),
            name=f"❌ UI Error: {operation} - {error_type}",
            attachment_type=allure.attachment_type.JSON,
        )

        # 如果有错误截图，附加到报告
        if screenshot_path:
            try:
                with open(screenshot_path, "rb") as f:
                    allure.attach(
                        f.read(),
                        name=f"Error Screenshot: {page_name}",
                        attachment_type=allure.attachment_type.PNG,
                    )
            except Exception:
                pass

    # ========== 清理方法 ==========

    def cleanup(self) -> None:
        """清理所有未关闭的上下文

        在测试结束时调用，确保所有step正确关闭
        """
        # 关闭所有HTTP上下文
        for ctx in self._http_contexts.values():
            ctx.exit_stack.close()
        self._http_contexts.clear()

        # 关闭所有查询上下文
        for ctx in self._query_contexts.values():
            ctx.exit_stack.close()
        self._query_contexts.clear()

        # 关闭所有GraphQL上下文
        for ctx in self._graphql_contexts.values():
            ctx.exit_stack.close()
        self._graphql_contexts.clear()

        # 关闭所有gRPC上下文
        for ctx in self._grpc_contexts.values():
            ctx.exit_stack.close()
        self._grpc_contexts.clear()


def get_current_observer() -> AllureObserver | None:
    """获取当前测试的Observer

    通过ContextVar获取，线程安全

    Returns:
        当前测试的AllureObserver实例，如果没有则返回None
    """
    return _current_observer.get()


def set_current_observer(observer: AllureObserver | None) -> None:
    """设置当前测试的Observer

    通过ContextVar设置，线程安全

    Args:
        observer: AllureObserver实例或None
    """
    _current_observer.set(observer)


__all__ = [
    "AllureObserver",
    "get_current_observer",
    "set_current_observer",
    "is_allure_enabled",
    "ALLURE_AVAILABLE",
    "StepContext",
]
