"""UI页面对象模板

v3.35.7: 新增 EventBus 集成支持
"""

UI_PAGE_OBJECT_TEMPLATE = '''"""页面对象: {page_name}

使用页面对象模式(POM)封装页面元素和操作。

v3.35.7+: 支持 EventBus 集成，自动发布 UI 操作事件到 Allure 报告。
"""

from typing import TYPE_CHECKING

from df_test_framework.capabilities.drivers.web import BasePage

if TYPE_CHECKING:
    from df_test_framework.infrastructure.events import EventBus


class {PageName}Page(BasePage):
    """{page_name}页面对象

    页面URL: {page_url}

    使用示例:
        >>> # 基础用法（无事件追踪）
        >>> page_obj = {PageName}Page(page, base_url="https://example.com")
        >>> page_obj.goto()
        >>>
        >>> # 启用事件追踪（推荐）
        >>> page_obj = {PageName}Page(page, base_url="https://example.com", event_bus=event_bus)
        >>> page_obj.goto()  # 自动记录到 Allure 报告
    """

    def __init__(
        self,
        page,
        base_url: str = "",
        event_bus: "EventBus | None" = None,
    ):
        """初始化页面对象

        Args:
            page: Playwright Page 实例
            base_url: 基础 URL
            event_bus: 事件总线（可选，用于 Allure 报告集成）
        """
        super().__init__(page, url="{page_url}", base_url=base_url, event_bus=event_bus)

        # 定义页面元素定位器
        self.heading = "h1"
        # TODO: 添加更多元素定位器
        # self.username_input = "#username"
        # self.password_input = "#password"
        # self.submit_button = "button[type=\'submit\']"

    def wait_for_page_load(self):
        """等待页面加载完成"""
        self.wait_for_selector(self.heading, state="visible")

    # TODO: 添加页面操作方法
    # def login(self, username: str, password: str):
    #     """执行登录操作
    #
    #     所有操作会自动记录到 Allure 报告（如果启用 event_bus）:
    #     - 🖱️ Click: button[type=\'submit\']
    #     - ⌨️ Input: #username = \'xxx\'
    #     - ⌨️ Input: #password = \'***\' (自动脱敏)
    #     """
    #     self.fill(self.username_input, username)
    #     self.fill(self.password_input, password)
    #     self.click(self.submit_button)

    # def get_heading_text(self) -> str:
    #     """获取标题文本"""
    #     return self.get_text(self.heading)


__all__ = ["{PageName}Page"]
'''

__all__ = ["UI_PAGE_OBJECT_TEMPLATE"]
