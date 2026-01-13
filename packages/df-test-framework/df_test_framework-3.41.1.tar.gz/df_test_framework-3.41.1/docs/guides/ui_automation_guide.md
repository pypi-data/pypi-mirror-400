# UI 自动化测试指南

> **版本要求**: df-test-framework >= 3.0.0
> **更新日期**: 2025-12-24
> **最新版本**: v3.38.0

---

## 概述

本指南介绍如何使用 df-test-framework 进行 UI 自动化测试。框架基于 **Playwright** 实现，提供：

- **页面对象模式 (POM)** - 结构化页面元素管理
- **多浏览器支持** - Chromium、Firefox、WebKit
- **可观测性集成** (v3.35.7) - EventBus 事件发布、日志记录、Allure 报告
- **视频录制** (v3.35.7) - 自动记录测试过程
- **等待策略** - 智能元素等待机制
- **截图功能** - 失败时自动截图

### 核心组件

| 组件 | 职责 |
|------|------|
| `BrowserManager` | 浏览器启动和管理 |
| `BasePage` | 页面对象基类 |
| `ElementLocator` | 元素定位器 |
| `WaitHelper` | 等待策略辅助类 |

---

## 快速开始

### 1. 安装依赖

```bash
# 安装 Playwright
pip install playwright

# 安装浏览器驱动
playwright install
```

或在 pyproject.toml 中：

```toml
dependencies = [
    "df-test-framework[ui]>=3.38.0",
]
```

### 2. 创建页面对象

```python
from df_test_framework.capabilities.drivers.web.playwright import BasePage
from playwright.sync_api import Page

class LoginPage(BasePage):
    """登录页面对象"""

    def __init__(self, page: Page):
        super().__init__(page, url="/login")

        # 元素定位器
        self.username_input = "#username"
        self.password_input = "#password"
        self.login_button = "button[type='submit']"
        self.error_message = ".error-message"

    def wait_for_page_load(self):
        """等待页面加载完成"""
        self.wait_for_selector(self.login_button)

    def login(self, username: str, password: str):
        """执行登录操作"""
        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        self.click(self.login_button)

    def get_error_message(self) -> str:
        """获取错误信息"""
        return self.get_text(self.error_message)
```

### 3. 编写测试

```python
import pytest
import allure
from assertpy import assert_that
from df_test_framework import step

@allure.feature("用户认证")
class TestLogin:
    """登录功能测试"""

    @allure.title("测试登录成功")
    @pytest.mark.smoke
    def test_login_success(self, browser_page, login_page):
        """测试正确的用户名和密码登录"""
        with step("访问登录页"):
            login_page.goto()

        with step("输入凭据并登录"):
            login_page.login("admin", "password123")

        with step("验证登录成功"):
            # 验证跳转到首页
            assert_that(browser_page.url).contains("/dashboard")

    @allure.title("测试登录失败")
    def test_login_failure(self, login_page):
        """测试错误的密码"""
        with step("访问登录页"):
            login_page.goto()

        with step("输入错误凭据"):
            login_page.login("admin", "wrong_password")

        with step("验证错误提示"):
            error = login_page.get_error_message()
            assert_that(error).is_equal_to("用户名或密码错误")
```

### 4. 配置 Fixtures

```python
# conftest.py
import pytest
from df_test_framework.capabilities.drivers.web.playwright import (
    BrowserManager,
    BrowserType,
)
from my_project.pages.login_page import LoginPage

@pytest.fixture(scope="session")
def browser_manager():
    """浏览器管理器"""
    manager = BrowserManager(
        browser_type=BrowserType.CHROMIUM,
        headless=True,
        timeout=30000,
        viewport={"width": 1280, "height": 720}
    )
    yield manager
    manager.stop()

@pytest.fixture
def browser_page(browser_manager):
    """浏览器页面"""
    browser, context, page = browser_manager.start()
    yield page
    browser_manager.stop()

@pytest.fixture
def login_page(browser_page, event_bus):
    """登录页面对象"""
    return LoginPage(browser_page, event_bus=event_bus)
```

---

## BrowserManager 详解

### 基本用法

```python
from df_test_framework.capabilities.drivers.web.playwright import (
    BrowserManager,
    BrowserType,
)

# 创建浏览器管理器
manager = BrowserManager(
    browser_type=BrowserType.CHROMIUM,
    headless=True,  # 无头模式
    slow_mo=100,    # 每步延迟100ms（调试用）
    timeout=30000,  # 默认超时30秒
    viewport={"width": 1920, "height": 1080}
)

# 启动浏览器
browser, context, page = manager.start()

# 使用页面
page.goto("https://example.com")

# 关闭浏览器
manager.stop()
```

### 作为上下文管理器

```python
with BrowserManager(headless=False) as (browser, context, page):
    page.goto("https://example.com")
    # 自动关闭
```

### 视频录制 (v3.35.7)

```python
manager = BrowserManager(
    browser_type=BrowserType.CHROMIUM,
    headless=True,
    record_video=True,              # 启用视频录制
    video_dir="reports/videos",     # 视频保存目录
    video_size={"width": 1280, "height": 720}  # 视频分辨率
)

browser, context, page = manager.start()
page.goto("https://example.com")
# ... 执行测试
manager.stop()
# 视频保存在 reports/videos/ 目录
```

---

## BasePage 详解

### 核心方法

#### 导航方法

```python
# 访问页面
page.goto()  # 使用初始化时指定的 URL
page.goto("https://custom.com")  # 自定义 URL

# 刷新页面
page.refresh()

# 后退/前进
page.go_back()
page.go_forward()
```

#### 元素交互

```python
# 点击
page.click("#submit-button")
page.click("text=登录")  # 文本定位
page.double_click("#item")

# 输入
page.fill("#username", "admin")
page.type("#search", "关键词", delay=100)  # 模拟打字

# 选择
page.select_option("#country", "CN")
page.select_option("#country", label="中国")

# 勾选
page.check("#agree")
page.uncheck("#agree")

# 上传文件
page.upload_file("#file-input", "path/to/file.pdf")
```

#### 元素查询

```python
# 获取文本
text = page.get_text(".message")

# 获取属性
value = page.get_attribute("#input", "value")
href = page.get_attribute("a.link", "href")

# 检查可见性
is_visible = page.is_visible("#popup")
is_hidden = page.is_hidden("#loading")

# 检查启用状态
is_enabled = page.is_enabled("#submit")
is_disabled = page.is_disabled("#submit")
```

#### 等待策略

```python
# 等待元素出现
page.wait_for_selector("#result", timeout=5000)

# 等待元素消失
page.wait_for_selector("#loading", state="hidden")

# 等待 URL
page.wait_for_url("**/dashboard")

# 等待加载完成
page.wait_for_load_state("networkidle")

# 自定义等待
page.wait_for_function("() => document.title === 'Dashboard'")
```

#### 截图

```python
# 页面截图
page.screenshot("screenshot.png")

# 元素截图
page.screenshot("#element", path="element.png")

# 全页截图
page.screenshot("full.png", full_page=True)
```

---

## 可观测性集成 (v3.35.7)

### EventBus 集成

BasePage 自动发布 UI 事件到 EventBus：

```python
from df_test_framework.infrastructure.events import EventBus

event_bus = EventBus()

# 监听 UI 事件
@event_bus.subscribe("ui.navigation.start")
def on_navigation(event):
    print(f"导航到: {event.url}")

@event_bus.subscribe("ui.click")
def on_click(event):
    print(f"点击元素: {event.selector}")

# 创建页面（注入 EventBus）
page_obj = LoginPage(page, event_bus=event_bus)

# 操作会自动触发事件
page_obj.goto()  # 触发 ui.navigation.start + ui.navigation.end
page_obj.click("#button")  # 触发 ui.click
page_obj.fill("#input", "text")  # 触发 ui.input
```

### UI 事件类型

| 事件类型 | 说明 | 字段 |
|---------|------|------|
| `ui.navigation.start` | 页面导航开始 | url |
| `ui.navigation.end` | 页面导航结束 | url, duration |
| `ui.click` | 点击操作 | selector |
| `ui.input` | 输入操作 | selector, value（脱敏） |
| `ui.screenshot` | 截图操作 | path |
| `ui.wait` | 等待操作 | selector, state |
| `ui.error` | UI 错误 | message, selector |

### Allure 报告集成

使用 `allure_observer` fixture 自动记录 UI 操作到 Allure：

```python
@pytest.fixture
def login_page(browser_page, event_bus, allure_observer):
    """带 Allure 记录的登录页"""
    # allure_observer 自动订阅 EventBus
    return LoginPage(browser_page, event_bus=event_bus)

def test_login(login_page):
    login_page.goto()
    login_page.fill("#username", "admin")
    login_page.click("#submit")

    # ✅ Allure 报告中自动包含：
    # - 页面导航记录
    # - 元素交互日志
    # - 截图（如有）
    # - OpenTelemetry trace_id
```

### 敏感数据脱敏

密码字段自动脱敏：

```python
# 输入密码
page.fill("#password", "secret123")

# EventBus 事件中显示
# UIInputEvent(selector="#password", value="***")

# Allure 报告中显示
# "输入 #password: ***"
```

---

## 高级用法

### 1. 多浏览器测试

```python
@pytest.fixture(params=[
    BrowserType.CHROMIUM,
    BrowserType.FIREFOX,
    BrowserType.WEBKIT
])
def browser_manager(request):
    """参数化浏览器类型"""
    manager = BrowserManager(browser_type=request.param)
    yield manager
    manager.stop()
```

### 2. 页面工厂模式

```python
class PageFactory:
    """页面工厂"""

    def __init__(self, page: Page, event_bus=None):
        self.page = page
        self.event_bus = event_bus

    def login_page(self) -> LoginPage:
        return LoginPage(self.page, event_bus=self.event_bus)

    def dashboard_page(self) -> DashboardPage:
        return DashboardPage(self.page, event_bus=self.event_bus)

@pytest.fixture
def pages(browser_page, event_bus):
    """页面工厂"""
    return PageFactory(browser_page, event_bus)

def test_flow(pages):
    """测试完整流程"""
    pages.login_page().login("admin", "pass")
    pages.dashboard_page().click_menu("设置")
```

### 3. 元素封装

```python
class Button:
    """按钮元素封装"""

    def __init__(self, page: BasePage, selector: str):
        self.page = page
        self.selector = selector

    def click(self):
        self.page.click(self.selector)

    def is_enabled(self) -> bool:
        return self.page.is_enabled(self.selector)

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.submit_button = Button(self, "#submit")

    def login(self, username, password):
        # ...
        self.submit_button.click()
```

### 4. 自定义等待条件

```python
class CustomPage(BasePage):
    def wait_for_ajax_complete(self):
        """等待 AJAX 请求完成"""
        self.wait_for_function(
            "() => window.jQuery && jQuery.active === 0"
        )

    def wait_for_element_count(self, selector: str, count: int):
        """等待元素数量"""
        self.wait_for_function(
            f"() => document.querySelectorAll('{selector}').length === {count}"
        )
```

---

## pytest 集成

### conftest.py 配置

```python
import pytest
from df_test_framework.capabilities.drivers.web.playwright import (
    BrowserManager,
    BrowserType,
)

@pytest.fixture(scope="session")
def browser_type(pytestconfig):
    """从命令行获取浏览器类型"""
    browser = pytestconfig.getoption("--browser", default="chromium")
    return BrowserType(browser)

@pytest.fixture(scope="session")
def headless(pytestconfig):
    """从命令行获取是否无头模式"""
    return pytestconfig.getoption("--headless", default=True)

@pytest.fixture(scope="session")
def browser_manager(browser_type, headless):
    """浏览器管理器"""
    manager = BrowserManager(
        browser_type=browser_type,
        headless=headless,
        timeout=30000,
        viewport={"width": 1280, "height": 720},
        record_video=True,
        video_dir="reports/videos"
    )
    yield manager
    manager.stop()

@pytest.fixture
def page(browser_manager):
    """浏览器页面"""
    browser, context, page = browser_manager.start()
    yield page
    # 失败时自动截图
    browser_manager.stop()
```

### pytest 命令行选项

```python
# conftest.py
def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        action="store",
        default="chromium",
        help="浏览器类型: chromium, firefox, webkit"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="启用无头模式"
    )
```

运行测试：

```bash
# 使用 Firefox
pytest tests/ui/ --browser=firefox

# 显示浏览器窗口
pytest tests/ui/ --headless=false

# 录制视频
pytest tests/ui/ --record-video
```

---

## 最佳实践

### 1. 使用页面对象模式

```python
# ✅ 好的实践 - 页面对象封装
class LoginPage(BasePage):
    def login(self, username, password):
        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        self.click(self.login_button)

def test_login(login_page):
    login_page.login("admin", "password")

# ❌ 不好的实践 - 直接操作元素
def test_login(page):
    page.fill("#username", "admin")
    page.fill("#password", "password")
    page.click("#submit")
```

### 2. 显式等待

```python
# ✅ 好的实践 - 显式等待
page.wait_for_selector("#result")
text = page.get_text("#result")

# ❌ 不好的实践 - 硬编码延迟
import time
time.sleep(2)
text = page.get_text("#result")
```

### 3. 有意义的断言

```python
# ✅ 好的实践 - 清晰的断言
assert_that(error_msg).is_equal_to("用户名或密码错误")

# ❌ 不好的实践 - 模糊的断言
assert len(error_msg) > 0
```

---

## 常见问题

### Q: 如何处理动态元素？

使用等待策略：

```python
page.wait_for_selector("#dynamic-element")
page.click("#dynamic-element")
```

### Q: 如何处理 iframe？

```python
# 切换到 iframe
frame = page.frame("iframe-name")
frame.click("#button")

# 返回主页面
page.main_frame().click("#button")
```

### Q: 如何处理弹窗？

```python
# 监听对话框
page.page.on("dialog", lambda dialog: dialog.accept())

# 触发弹窗
page.click("#trigger-alert")
```

---

## 相关文档

- [EventBus 使用指南](event_bus_guide.md)
- [分布式追踪指南](distributed_tracing.md)
- [脚手架 CLI 工具指南](scaffold_cli_guide.md)
