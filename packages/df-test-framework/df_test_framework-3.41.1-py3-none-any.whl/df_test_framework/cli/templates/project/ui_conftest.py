"""UI项目pytest配置模板

v3.37.0: 更新为 pytest11 Entry Points 自动加载
v3.35.7: 新增视频录制和 EventBus 集成
"""

UI_CONFTEST_TEMPLATE = '''"""Pytest全局配置 - UI测试 (v3.37.0)

UI测试专用的pytest配置和fixtures。

v3.37.0 重要变更:
- pytest11 Entry Points: pip install df-test-framework 后插件自动加载
- 无需手动声明 pytest_plugins（框架自动注册）

v3.35.7+: 支持视频录制和 EventBus 可观测性集成。
"""

import pytest
from pathlib import Path

from df_test_framework.capabilities.drivers.web import BrowserType


# ============================================================
# v3.37.0: 插件通过 pytest11 Entry Points 自动加载
# ============================================================
# pip install df-test-framework 后，核心插件自动可用，无需手动声明。
#
# 如果需要 UI 测试专用 fixtures，可以手动添加：
pytest_plugins = ["df_test_framework.testing.fixtures.ui"]


# ========== 配置fixtures ==========

@pytest.fixture(scope="session")
def settings():
    """配置对象（session级别）

    Returns:
        {ProjectName}Settings: 项目配置对象
    """
    from {project_name}.config import {ProjectName}Settings
    return {ProjectName}Settings()


@pytest.fixture(scope="session")
def browser_headless(pytestconfig, settings):
    """浏览器无头模式配置，支持 --headed 覆盖"""
    if pytestconfig.getoption("--headed"):
        return False
    return settings.headless


@pytest.fixture(scope="session")
def browser_type(pytestconfig, settings):
    """浏览器类型配置，支持 --browser 覆盖"""
    selected = pytestconfig.getoption("--browser") or settings.browser_type
    browser_map = {
        "chromium": BrowserType.CHROMIUM,
        "firefox": BrowserType.FIREFOX,
        "webkit": BrowserType.WEBKIT,
    }
    return browser_map.get(str(selected).lower(), BrowserType.CHROMIUM)


@pytest.fixture(scope="session")
def browser_timeout(settings):
    """浏览器超时配置"""
    return settings.browser_timeout


@pytest.fixture(scope="session")
def browser_viewport(settings):
    """浏览器视口配置"""
    return {
        "width": settings.viewport_width,
        "height": settings.viewport_height,
    }


@pytest.fixture(scope="session")
def browser_record_video(pytestconfig, settings):
    """视频录制配置（v3.35.7 新增）

    支持 --record-video 命令行覆盖。
    """
    if pytestconfig.getoption("--record-video"):
        return True
    return getattr(settings, "record_video", False)


@pytest.fixture(scope="session")
def browser_video_dir(settings):
    """视频保存目录（v3.35.7 新增）"""
    return getattr(settings, "video_dir", "reports/videos")


@pytest.fixture(scope="session")
def base_url(settings):
    """基础URL"""
    return settings.base_url


@pytest.fixture(scope="session")
def event_bus():
    """EventBus 实例（v3.35.7 新增）

    用于 UI 操作事件追踪和 Allure 报告集成。

    Example:
        >>> def test_login(page, event_bus, base_url):
        ...     login_page = LoginPage(page, base_url=base_url, event_bus=event_bus)
        ...     login_page.goto()  # 自动记录到 Allure
    """
    from df_test_framework.infrastructure.events import EventBus
    bus = EventBus()
    yield bus
    # EventBus 无需显式清理


# ========== 测试钩子 ==========

def pytest_addoption(parser):
    """添加命令行选项"""
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="显示浏览器窗口（非无头模式）"
    )
    parser.addoption(
        "--browser",
        action="store",
        default="chromium",
        help="浏览器类型: chromium, firefox, webkit"
    )
    parser.addoption(
        "--record-video",
        action="store_true",
        default=False,
        help="录制测试视频（v3.35.7 新增）"
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败时自动截图和保存视频"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        if "page" in item.funcargs:
            page = item.funcargs["page"]

            # 失败截图
            screenshots_dir = Path("reports/screenshots")
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = screenshots_dir / f"{item.name}_failure.png"

            try:
                page.screenshot(path=str(screenshot_path))
                print(f"\\n📸 失败截图: {screenshot_path}")

                # 尝试附加到 Allure
                try:
                    import allure
                    allure.attach.file(
                        str(screenshot_path),
                        name="失败截图",
                        attachment_type=allure.attachment_type.PNG
                    )
                except ImportError:
                    pass

            except Exception as e:
                print(f"\\n⚠️  截图失败: {e}")

            # 获取视频路径（如果录制了视频）
            try:
                video = page.video
                if video:
                    video_path = video.path()
                    print(f"\\n🎬 测试视频: {video_path}")

                    # 尝试附加到 Allure
                    try:
                        import allure
                        allure.attach.file(
                            str(video_path),
                            name="测试视频",
                            attachment_type=allure.attachment_type.WEBM
                        )
                    except ImportError:
                        pass
            except Exception:
                pass


def pytest_configure(config):
    """Pytest配置钩子"""
    # 注册自定义标记
    config.addinivalue_line("markers", "ui: mark test as ui test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
'''

__all__ = ["UI_CONFTEST_TEMPLATE"]
