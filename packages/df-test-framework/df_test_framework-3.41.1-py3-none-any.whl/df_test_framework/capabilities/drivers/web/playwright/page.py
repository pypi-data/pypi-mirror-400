"""页面对象基类

提供UI自动化测试的页面对象模式(POM)基类
基于 Playwright 实现

v3.35.7: 集成 EventBus 和可观测性
"""

import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

from df_test_framework.core.events import (
    UIClickEvent,
    UIErrorEvent,
    UIInputEvent,
    UINavigationEndEvent,
    UINavigationStartEvent,
    UIScreenshotEvent,
    UIWaitEvent,
)

try:
    from playwright.sync_api import Locator, Page

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    Page = Any
    Locator = Any

if TYPE_CHECKING:
    from df_test_framework.infrastructure.events import EventBus


class BasePage(ABC):
    """
    页面对象基类

    提供页面对象模式(POM)的基础功能：
    - 元素定位和操作
    - 页面等待策略
    - 截图功能
    - 日志记录
    - 常用操作封装

    子类应该：
    1. 定义页面URL
    2. 定义页面元素定位器
    3. 实现wait_for_page_load()方法
    4. 提供业务操作方法

    示例:
        >>> class LoginPage(BasePage):
        ...     def __init__(self, page: Page):
        ...         super().__init__(page, url="/login")
        ...         self.username_input = "#username"
        ...         self.password_input = "#password"
        ...         self.login_button = "button[type='submit']"
        ...
        ...     def wait_for_page_load(self):
        ...         self.wait_for_selector(self.login_button)
        ...
        ...     def login(self, username: str, password: str):
        ...         self.fill(self.username_input, username)
        ...         self.fill(self.password_input, password)
        ...         self.click(self.login_button)
    """

    def __init__(
        self,
        page: Page,
        url: str | None = None,
        base_url: str = "",
        event_bus: "EventBus | None" = None,
    ):
        """
        初始化页面对象

        Args:
            page: Playwright Page实例
            url: 页面相对URL（如 "/login"）
            base_url: 基础URL（如 "https://example.com"）
            event_bus: 事件总线（可选，用于发布 UI 事件）

        Raises:
            ImportError: 如果未安装playwright

        v3.35.7: 新增 event_bus 参数支持可观测性
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright未安装。请运行: pip install playwright && playwright install"
            )

        self.page = page
        self.url = url
        self.base_url = base_url

        # 事件总线（可选）- 用于发布 UI 操作事件
        self._event_bus = event_bus or getattr(page, "_event_bus", None)
        # 页面对象名称（用于事件追踪）
        self._page_name = self.__class__.__name__

    def _publish_event(self, event: Any) -> None:
        """发布事件到 EventBus（如果已配置）

        v3.35.7: 新增
        """
        if self._event_bus:
            try:
                self._event_bus.publish_sync(event)
            except Exception:
                pass  # 静默失败，不影响 UI 操作

    def _should_mask_input(self, selector: str) -> bool:
        """判断是否需要脱敏输入

        检查选择器是否包含密码等敏感字段标识。

        v3.35.7: 新增
        """
        mask_patterns = ["password", "passwd", "secret", "token", "key", "pin", "otp"]
        selector_lower = selector.lower()
        return any(pattern in selector_lower for pattern in mask_patterns)

    @abstractmethod
    def wait_for_page_load(self) -> None:
        """
        等待页面加载完成

        子类必须实现此方法来定义页面加载完成的标志，例如：
        - 等待特定元素出现
        - 等待网络空闲
        - 等待页面标题
        """
        pass

    # ========== 页面导航 ==========

    def goto(self, url: str | None = None, **kwargs: Any) -> None:
        """
        导航到页面

        Args:
            url: 目标URL，如果为None则使用self.url
            kwargs: goto的其他参数

        Raises:
            ValueError: 如果url和self.url都为None

        v3.35.7: 新增事件发布
        """
        target_url = url or self.url
        if not target_url:
            raise ValueError("必须提供url参数或在构造函数中设置self.url")

        full_url = f"{self.base_url}{target_url}" if self.base_url else target_url

        # 发布导航开始事件
        start_event, correlation_id = UINavigationStartEvent.create(
            page_name=self._page_name,
            url=full_url,
            base_url=self.base_url,
        )
        self._publish_event(start_event)

        start_time = time.time()
        success = True

        try:
            self.page.goto(full_url, **kwargs)
            self.wait_for_page_load()
        except Exception as e:
            success = False
            # 发布错误事件
            error_event = UIErrorEvent.create(
                page_name=self._page_name,
                operation="goto",
                selector=full_url,
                error=e,
            )
            self._publish_event(error_event)
            raise
        finally:
            duration = time.time() - start_time
            # 发布导航结束事件
            end_event = UINavigationEndEvent.create(
                correlation_id=correlation_id,
                page_name=self._page_name,
                url=full_url,
                title=self.page.title() if success else "",
                duration=duration,
                success=success,
            )
            self._publish_event(end_event)

    def reload(self, **kwargs: Any) -> None:
        """刷新页面"""
        self.page.reload(**kwargs)
        self.wait_for_page_load()

    def go_back(self, **kwargs: Any) -> None:
        """返回上一页"""
        self.page.go_back(**kwargs)

    def go_forward(self, **kwargs: Any) -> None:
        """前进到下一页"""
        self.page.go_forward(**kwargs)

    # ========== 元素定位 ==========

    def locator(self, selector: str) -> Locator:
        """
        获取元素定位器

        Args:
            selector: CSS选择器、XPath或文本选择器

        Returns:
            Locator: Playwright定位器对象
        """
        return self.page.locator(selector)

    def get_by_role(self, role: str, **kwargs: Any) -> Locator:
        """通过ARIA role定位元素"""
        return self.page.get_by_role(role, **kwargs)

    def get_by_text(self, text: str, **kwargs: Any) -> Locator:
        """通过文本内容定位元素"""
        return self.page.get_by_text(text, **kwargs)

    def get_by_label(self, label: str, **kwargs: Any) -> Locator:
        """通过label定位元素"""
        return self.page.get_by_label(label, **kwargs)

    def get_by_placeholder(self, placeholder: str, **kwargs: Any) -> Locator:
        """通过placeholder定位元素"""
        return self.page.get_by_placeholder(placeholder, **kwargs)

    def get_by_test_id(self, test_id: str) -> Locator:
        """通过data-testid定位元素"""
        return self.page.get_by_test_id(test_id)

    # ========== 元素操作 ==========

    def click(self, selector: str, **kwargs: Any) -> None:
        """点击元素

        v3.35.7: 新增事件发布
        """
        start_time = time.time()
        element_text = ""

        try:
            # 尝试获取元素文本用于日志
            try:
                element_text = self.locator(selector).text_content() or ""
                element_text = element_text[:50]  # 截断
            except Exception:
                pass

            self.locator(selector).click(**kwargs)

        except Exception as e:
            # 发布错误事件
            error_event = UIErrorEvent.create(
                page_name=self._page_name,
                operation="click",
                selector=selector,
                error=e,
            )
            self._publish_event(error_event)
            raise
        finally:
            duration = time.time() - start_time
            # 发布点击事件
            click_event = UIClickEvent.create(
                page_name=self._page_name,
                selector=selector,
                element_text=element_text,
                duration=duration,
            )
            self._publish_event(click_event)

    def double_click(self, selector: str, **kwargs: Any) -> None:
        """双击元素"""
        self.locator(selector).dblclick(**kwargs)

    def fill(self, selector: str, value: str, **kwargs: Any) -> None:
        """填充输入框

        v3.35.7: 新增事件发布，自动脱敏敏感字段
        """
        start_time = time.time()

        # 检查是否需要脱敏（密码字段等）
        masked = self._should_mask_input(selector)
        display_value = "***" if masked else value[:20]

        try:
            self.locator(selector).fill(value, **kwargs)

        except Exception as e:
            # 发布错误事件
            error_event = UIErrorEvent.create(
                page_name=self._page_name,
                operation="fill",
                selector=selector,
                error=e,
            )
            self._publish_event(error_event)
            raise
        finally:
            duration = time.time() - start_time
            # 发布输入事件
            input_event = UIInputEvent.create(
                page_name=self._page_name,
                selector=selector,
                value=display_value,
                masked=masked,
                duration=duration,
            )
            self._publish_event(input_event)

    def clear(self, selector: str) -> None:
        """清空输入框"""
        self.locator(selector).clear()

    def type(self, selector: str, text: str, **kwargs: Any) -> None:
        """逐字输入文本（模拟键盘输入）"""
        self.locator(selector).type(text, **kwargs)

    def select_option(self, selector: str, value: str | list[str], **kwargs: Any) -> None:
        """选择下拉框选项"""
        self.locator(selector).select_option(value, **kwargs)

    def check(self, selector: str, **kwargs: Any) -> None:
        """勾选复选框"""
        self.locator(selector).check(**kwargs)

    def uncheck(self, selector: str, **kwargs: Any) -> None:
        """取消勾选复选框"""
        self.locator(selector).uncheck(**kwargs)

    def hover(self, selector: str, **kwargs: Any) -> None:
        """鼠标悬停"""
        self.locator(selector).hover(**kwargs)

    # ========== 元素查询 ==========

    def get_text(self, selector: str) -> str:
        """获取元素文本内容"""
        return self.locator(selector).text_content() or ""

    def get_inner_text(self, selector: str) -> str:
        """获取元素内部文本（不包含HTML标签）"""
        return self.locator(selector).inner_text()

    def get_attribute(self, selector: str, name: str) -> str | None:
        """获取元素属性值"""
        return self.locator(selector).get_attribute(name)

    def get_value(self, selector: str) -> str:
        """获取输入框的值"""
        return self.locator(selector).input_value()

    def is_visible(self, selector: str) -> bool:
        """检查元素是否可见"""
        return self.locator(selector).is_visible()

    def is_enabled(self, selector: str) -> bool:
        """检查元素是否可用"""
        return self.locator(selector).is_enabled()

    def is_checked(self, selector: str) -> bool:
        """检查复选框/单选框是否被选中"""
        return self.locator(selector).is_checked()

    def count(self, selector: str) -> int:
        """获取匹配元素的数量"""
        return self.locator(selector).count()

    # ========== 等待策略 ==========

    def wait_for_selector(
        self, selector: str, state: str = "visible", timeout: int | None = None
    ) -> None:
        """
        等待元素出现

        Args:
            selector: 选择器
            state: 状态 (visible/hidden/attached/detached)
            timeout: 超时时间（毫秒）

        v3.35.7: 新增事件发布
        """
        start_time = time.time()
        success = True
        timeout_sec = (timeout or 30000) / 1000  # 默认 30 秒

        try:
            self.page.wait_for_selector(selector, state=state, timeout=timeout)
        except Exception as e:
            success = False
            # 发布错误事件
            error_event = UIErrorEvent.create(
                page_name=self._page_name,
                operation="wait_for_selector",
                selector=selector,
                error=e,
            )
            self._publish_event(error_event)
            raise
        finally:
            duration = time.time() - start_time
            # 发布等待事件
            wait_event = UIWaitEvent.create(
                page_name=self._page_name,
                wait_type="selector",
                condition=f"{selector} ({state})",
                timeout=timeout_sec,
                duration=duration,
                success=success,
            )
            self._publish_event(wait_event)

    def wait_for_url(self, url: str | Any, **kwargs: Any) -> None:
        """等待URL匹配"""
        self.page.wait_for_url(url, **kwargs)

    def wait_for_load_state(self, state: str = "load", **kwargs: Any) -> None:
        """
        等待页面加载状态

        Args:
            state: 状态 (load/domcontentloaded/networkidle)
        """
        self.page.wait_for_load_state(state, **kwargs)

    def wait_for_timeout(self, timeout: int) -> None:
        """等待指定时间（毫秒）"""
        self.page.wait_for_timeout(timeout)

    # ========== 截图 ==========

    def screenshot(self, path: str | Path | None = None, **kwargs: Any) -> bytes:
        """
        页面截图

        Args:
            path: 保存路径，如果为None则返回字节数据
            kwargs: 其他截图参数

        Returns:
            bytes: 截图数据

        v3.35.7: 新增事件发布
        """
        full_page = kwargs.get("full_page", False)
        result = self.page.screenshot(path=path, **kwargs)

        # 发布截图事件
        screenshot_event = UIScreenshotEvent.create(
            page_name=self._page_name,
            path=str(path) if path else "",
            full_page=full_page,
            size_bytes=len(result),
        )
        self._publish_event(screenshot_event)

        return result

    def screenshot_element(
        self, selector: str, path: str | Path | None = None, **kwargs: Any
    ) -> bytes:
        """
        元素截图

        Args:
            selector: 元素选择器
            path: 保存路径
            kwargs: 其他截图参数

        Returns:
            bytes: 截图数据
        """
        return self.locator(selector).screenshot(path=path, **kwargs)

    # ========== 页面信息 ==========

    @property
    def title(self) -> str:
        """获取页面标题"""
        return self.page.title()

    @property
    def current_url(self) -> str:
        """获取当前URL"""
        return self.page.url

    def evaluate(self, expression: str, arg: Any = None) -> Any:
        """
        执行JavaScript代码

        Args:
            expression: JS表达式
            arg: 传递给JS的参数

        Returns:
            Any: JS执行结果
        """
        return self.page.evaluate(expression, arg)

    # ========== 便捷方法 ==========

    def scroll_to_element(self, selector: str) -> None:
        """滚动到元素位置"""
        self.locator(selector).scroll_into_view_if_needed()

    def scroll_to_top(self) -> None:
        """滚动到页面顶部"""
        self.evaluate("window.scrollTo(0, 0)")

    def scroll_to_bottom(self) -> None:
        """滚动到页面底部"""
        self.evaluate("window.scrollTo(0, document.body.scrollHeight)")


__all__ = ["BasePage"]
