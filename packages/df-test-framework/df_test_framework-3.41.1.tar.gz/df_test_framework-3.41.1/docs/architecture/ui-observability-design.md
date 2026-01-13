# UI 自动化可观测性技术规范

**版本**: v3.35.7
**日期**: 2025-12-20
**状态**: ✅ 已实现

---

## 1. 概述

### 1.1 模块集成状态

df-test-framework 各模块可观测性集成状态：

| 模块 | EventBus | AllureObserver | ObservabilityLogger | 完成度 |
|------|----------|----------------|---------------------|--------|
| HTTP Client | ✅ | ✅ | ✅ | 100% |
| GraphQL | ✅ | ✅ | ❌ | 90% |
| gRPC | ✅ | ✅ | ❌ | 90% |
| Database | ✅ | ✅ | ✅ | 100% |
| Redis | ✅ | ✅ | ✅ | 100% |
| Storage | ✅ | ✅ | ❌ | 90% |
| MQ | ✅ | ✅ | ❌ | 90% |
| **UI (Playwright)** | ✅ | ✅ | ✅ | **100%** |

### 1.2 实现功能

v3.35.7 为 UI 自动化添加了完整的可观测性支持：

1. **EventBus 集成**: 7 个 UI 事件类型，支持事件驱动架构
2. **Allure 报告增强**: 自动记录 UI 操作（导航、点击、输入、截图、等待）
3. **实时调试日志**: `ui_logger()` 终端实时输出
4. **OpenTelemetry 支持**: 自动注入 trace_id/span_id
5. **视频录制**: BrowserManager 和 Fixtures 支持视频录制配置
6. **敏感数据脱敏**: 自动检测并脱敏密码等敏感输入

---

## 2. 架构设计

### 2.1 分层架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Testing Layer (Layer 3)                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ pytest fixtures: page, browser_manager, event_bus               │ │
│  │                                                                   │ │
│  │  ┌─────────────────┐    ┌──────────────────────────────────────┐ │ │
│  │  │ AllureObserver  │    │ ObservabilityLogger (ui_logger)     │ │ │
│  │  │ - UI 事件处理   │    │ - 实时终端输出                        │ │ │
│  │  │ - 截图/视频附件 │    │ - 操作耗时                            │ │ │
│  │  └────────┬────────┘    └─────────────────┬────────────────────┘ │ │
│  │           │                               │                       │ │
│  │           │ 订阅事件                       │ 同步日志              │ │
│  │           ▼                               ▼                       │ │
│  │  ┌───────────────────────────────────────────────────────────────┐ │
│  │  │                     EventBus                                  │ │
│  │  │  ui.navigation.start/end, ui.click, ui.input                 │ │
│  │  │  ui.screenshot, ui.wait, ui.error                            │ │
│  │  └───────────────────────────────────────────────────────────────┘ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │ 发布事件
                                    │
┌─────────────────────────────────────────────────────────────────────┐
│                      Capabilities Layer (Layer 2)                    │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                 capabilities/drivers/web/                        │ │
│  │                                                                   │ │
│  │  ┌──────────────────────────────────────────────────────────┐    │ │
│  │  │                     BasePage                              │    │ │
│  │  │  - goto() → UINavigationStartEvent/UINavigationEndEvent  │    │ │
│  │  │  - click() → UIClickEvent                                │    │ │
│  │  │  - fill() → UIInputEvent (自动脱敏)                      │    │ │
│  │  │  - screenshot() → UIScreenshotEvent                      │    │ │
│  │  │  - wait_for_selector() → UIWaitEvent                     │    │ │
│  │  └──────────────────────────────────────────────────────────┘    │ │
│  │                                                                   │ │
│  │  ┌──────────────────────────────────────────────────────────┐    │ │
│  │  │                   BrowserManager                          │    │ │
│  │  │  - record_video: bool                                    │    │ │
│  │  │  - video_dir: str                                        │    │ │
│  │  │  - video_size: dict                                      │    │ │
│  │  └──────────────────────────────────────────────────────────┘    │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │ 使用
                                    │
┌─────────────────────────────────────────────────────────────────────┐
│                         Core Layer (Layer 0)                         │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    core/events/types.py                          │ │
│  │                                                                   │ │
│  │  - UINavigationStartEvent / UINavigationEndEvent                 │ │
│  │  - UIClickEvent                                                  │ │
│  │  - UIInputEvent                                                  │ │
│  │  - UIScreenshotEvent                                             │ │
│  │  - UIWaitEvent                                                   │ │
│  │  - UIErrorEvent                                                  │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. 事件类型

### 3.1 事件列表

| 事件类型 | 基类 | 说明 | 触发时机 |
|----------|------|------|----------|
| `UINavigationStartEvent` | CorrelatedEvent | 页面导航开始 | `BasePage.goto()` |
| `UINavigationEndEvent` | CorrelatedEvent | 页面导航结束 | 导航完成/失败 |
| `UIClickEvent` | Event | 点击操作 | `BasePage.click()` |
| `UIInputEvent` | Event | 输入操作 | `BasePage.fill()` |
| `UIScreenshotEvent` | Event | 截图操作 | `BasePage.screenshot()` |
| `UIWaitEvent` | Event | 等待操作 | `BasePage.wait_for_selector()` |
| `UIErrorEvent` | Event | UI 错误 | 操作异常时 |

### 3.2 事件属性

```python
# 导航事件（关联事件对）
UINavigationStartEvent:
    page_name: str      # 页面对象名称
    url: str            # 目标 URL
    base_url: str       # 基础 URL
    correlation_id: str # 关联 ID（与 End 事件配对）

UINavigationEndEvent:
    page_name: str
    url: str
    title: str          # 页面标题
    duration: float     # 导航耗时（秒）
    success: bool
    correlation_id: str # 关联 ID

# 操作事件
UIClickEvent:
    page_name: str
    selector: str       # CSS 选择器
    element_text: str   # 元素文本（截断到 50 字符）
    duration: float

UIInputEvent:
    page_name: str
    selector: str
    value: str          # 输入值（可能已脱敏）
    masked: bool        # 是否已脱敏
    duration: float

UIScreenshotEvent:
    page_name: str
    path: str           # 截图保存路径
    full_page: bool     # 是否全页截图
    element_selector: str
    size_bytes: int

UIWaitEvent:
    page_name: str
    wait_type: str      # selector, url, load_state
    condition: str      # 等待条件
    timeout: float
    duration: float
    success: bool

UIErrorEvent:
    page_name: str
    operation: str      # click, fill, goto 等
    selector: str
    error_type: str
    error_message: str
    screenshot_path: str
```

### 3.3 使用示例

```python
from df_test_framework.core.events import (
    UINavigationStartEvent,
    UINavigationEndEvent,
    UIClickEvent,
    UIInputEvent,
)

# 创建导航开始事件（返回事件和 correlation_id）
start_event, correlation_id = UINavigationStartEvent.create(
    page_name="LoginPage",
    url="https://example.com/login",
    base_url="https://example.com",
)

# 创建导航结束事件（复用 correlation_id）
end_event = UINavigationEndEvent.create(
    correlation_id=correlation_id,
    page_name="LoginPage",
    url="https://example.com/login",
    title="登录 - Example",
    duration=1.5,
    success=True,
)

# 创建点击事件
click_event = UIClickEvent.create(
    page_name="LoginPage",
    selector="#submit-button",
    element_text="登录",
    duration=0.2,
)

# 创建输入事件（自动注入 trace_id/span_id）
input_event = UIInputEvent.create(
    page_name="LoginPage",
    selector="#password",
    value="***",  # 已脱敏
    masked=True,
    duration=0.1,
)
```

---

## 4. BasePage 集成

### 4.1 EventBus 注入

```python
from df_test_framework.capabilities.drivers.web import BasePage
from df_test_framework.infrastructure.events import EventBus

class LoginPage(BasePage):
    def __init__(self, page, event_bus: EventBus | None = None):
        super().__init__(
            page,
            url="/login",
            base_url="https://example.com",
            event_bus=event_bus,  # 可选：注入事件总线
        )
        self.username_input = "#username"
        self.password_input = "#password"
        self.submit_button = "button[type='submit']"

    def wait_for_page_load(self):
        self.wait_for_selector(self.submit_button)

    def login(self, username: str, password: str):
        # 所有操作自动发布事件到 EventBus
        self.fill(self.username_input, username)  # → UIInputEvent
        self.fill(self.password_input, password)  # → UIInputEvent (masked)
        self.click(self.submit_button)            # → UIClickEvent
```

### 4.2 敏感数据脱敏

BasePage 自动检测以下关键词并脱敏输入值：

- `password`, `passwd`
- `secret`, `token`, `key`
- `pin`, `otp`

```python
# 选择器包含 "password" 时自动脱敏
self.fill("#password", "secret123")
# → UIInputEvent(value="***", masked=True)
```

---

## 5. 日志输出

### 5.1 ui_logger() 使用

```python
from df_test_framework.infrastructure.logging.observability import ui_logger

logger = ui_logger()

# UI 专用日志方法
logger.navigation_start("LoginPage", "https://example.com/login")
logger.navigation_end("LoginPage", "https://example.com/login", duration=1.5, success=True)
logger.ui_click("#login-button", duration=0.2)
logger.ui_fill("#username", "test_user", duration=0.1)
logger.ui_screenshot("/tmp/screenshot.png", size_bytes=102400)
logger.ui_wait_complete("selector", "#modal", duration=0.5, success=True)
logger.ui_error("click", "#missing-element", TimeoutError("Element not found"))
```

### 5.2 终端输出示例

```
[12:34:56] [UI] 🌐 LoginPage → https://example.com/login
[12:34:57] [UI] 🌐 LoginPage ← ✅ (1500.0ms)
[12:34:57] [UI] ⌨️ fill: #username = 'test_user' (100.0ms)
[12:34:57] [UI] ⌨️ fill: #password = '***' (100.0ms)
[12:34:58] [UI] 🖱️ click: #login-button (200.0ms)
[12:34:58] [UI] ⏳ wait_selector: .dashboard → ✅ (500.0ms)
```

---

## 6. Allure 报告

### 6.1 AllureObserver 事件处理

AllureObserver 自动订阅并处理 7 个 UI 事件：

```python
async def handle_ui_navigation_start_event(self, event)
async def handle_ui_navigation_end_event(self, event)
async def handle_ui_click_event(self, event)
async def handle_ui_input_event(self, event)
async def handle_ui_screenshot_event(self, event)
async def handle_ui_wait_event(self, event)
async def handle_ui_error_event(self, event)
```

### 6.2 报告效果

```
📋 Test: test_login_flow
│
├─ 🌐 Navigate: LoginPage → https://example.com/login
│  └─ ✅ Navigate: LoginPage - Login Page (245ms)
│
├─ ⌨️ Input: #username = 'test_user'
│
├─ ⌨️ Input: #password = '***'
│
├─ 🖱️ Click: Login Button (25ms)
│
├─ ✅ Wait: selector - .dashboard (visible) (1250ms)
│
└─ 📸 Screenshot: DashboardPage (viewport)
```

### 6.3 错误记录

```
├─ ❌ UI Error: wait_for_selector - TimeoutError
│  ├─ 📋 Error Details (JSON)
│  └─ 📸 Error Screenshot: LoginPage.png
```

---

## 7. 视频录制

### 7.1 BrowserManager 配置

```python
from df_test_framework.capabilities.drivers.web import BrowserManager, BrowserType

manager = BrowserManager(
    browser_type=BrowserType.CHROMIUM,
    headless=True,
    record_video=True,           # 启用视频录制
    video_dir="reports/videos",  # 视频保存目录
    video_size={"width": 1280, "height": 720},  # 可选：视频分辨率
)
```

### 7.2 Fixture 配置

```python
# conftest.py
@pytest.fixture(scope="session")
def browser_record_video(pytestconfig, settings):
    """支持 --record-video 命令行覆盖"""
    if pytestconfig.getoption("--record-video"):
        return True
    return getattr(settings, "record_video", False)

@pytest.fixture(scope="session")
def browser_video_dir(settings):
    return getattr(settings, "video_dir", "reports/videos")
```

### 7.3 命令行使用

```bash
# 启用视频录制
pytest tests/ui/ --record-video

# 组合其他选项
pytest tests/ui/ --headed --record-video --browser=firefox
```

---

## 8. 脚手架模板

### 8.1 ui_conftest.py 模板

脚手架生成的 `conftest.py` 包含：

- `browser_record_video` fixture（支持 `--record-video`）
- `browser_video_dir` fixture
- `event_bus` fixture
- `pytest_runtest_makereport` 钩子（失败时自动附加截图/视频）

### 8.2 ui_page_object.py 模板

```python
class {PageName}Page(BasePage):
    def __init__(
        self,
        page,
        base_url: str = "",
        event_bus: "EventBus | None" = None,
    ):
        super().__init__(page, url="{page_url}", base_url=base_url, event_bus=event_bus)
```

---

## 9. 文件清单

### 9.1 核心实现

| 文件 | 说明 |
|------|------|
| `core/events/types.py` | 7 个 UI 事件类型定义 |
| `core/events/__init__.py` | 事件导出 |
| `capabilities/drivers/web/playwright/page.py` | BasePage EventBus 集成 |
| `capabilities/drivers/web/playwright/browser.py` | BrowserManager 视频录制 |
| `infrastructure/logging/observability.py` | ui_logger() 和 UI 日志方法 |
| `testing/fixtures/ui.py` | 视频录制 Fixtures |
| `testing/reporting/allure/observer.py` | AllureObserver UI 事件处理器 |

### 9.2 模板文件

| 文件 | 说明 |
|------|------|
| `cli/templates/project/ui_conftest.py` | UI 项目 conftest 模板 |
| `cli/templates/project/ui_page_object.py` | 页面对象模板 |

---

## 10. 测试覆盖

- 14 个视频录制和 UI Fixtures 单元测试
- 1587 个测试全部通过

---

## 11. 未来扩展

1. **网络请求拦截**: 记录页面发起的 XHR/Fetch 请求
2. **Console 日志**: 记录浏览器控制台日志到 Allure
3. **性能指标**: 集成 Web Vitals (LCP, FID, CLS)
4. **Accessibility**: 集成 axe-core 可访问性检查
