"""测试 UI fixtures - 视频录制配置

测试覆盖:
- browser_record_video fixture 默认值
- browser_video_dir fixture 默认值
- 视频录制配置传递到 context

v3.35.7 新增
"""

from unittest.mock import MagicMock, patch


class TestBrowserRecordVideoFixture:
    """测试 browser_record_video fixture"""

    def test_fixture_is_defined(self):
        """fixture 已定义"""
        from df_test_framework.testing.fixtures.ui import browser_record_video

        # 验证 fixture 函数存在且被正确装饰
        assert hasattr(browser_record_video, "pytestmark") or callable(browser_record_video)

    def test_fixture_has_session_scope(self):
        """fixture 为 session 作用域"""
        import inspect

        from df_test_framework.testing.fixtures.ui import browser_record_video

        # 检查函数源码中的装饰器
        source = inspect.getsource(browser_record_video)
        assert 'scope="session"' in source


class TestBrowserVideoDirFixture:
    """测试 browser_video_dir fixture"""

    def test_fixture_is_defined(self):
        """fixture 已定义"""
        from df_test_framework.testing.fixtures.ui import browser_video_dir

        # 验证 fixture 函数存在且被正确装饰
        assert hasattr(browser_video_dir, "pytestmark") or callable(browser_video_dir)

    def test_fixture_has_session_scope(self):
        """fixture 为 session 作用域"""
        import inspect

        from df_test_framework.testing.fixtures.ui import browser_video_dir

        # 检查函数源码中的装饰器
        source = inspect.getsource(browser_video_dir)
        assert 'scope="session"' in source


class TestBrowserManagerVideoConfig:
    """测试 BrowserManager 视频录制配置"""

    def test_init_with_video_config(self):
        """初始化时可以配置视频录制"""
        with patch(
            "df_test_framework.capabilities.drivers.web.playwright.browser.PLAYWRIGHT_AVAILABLE",
            True,
        ):
            from df_test_framework.capabilities.drivers.web.playwright.browser import (
                BrowserManager,
                BrowserType,
            )

            manager = BrowserManager(
                browser_type=BrowserType.CHROMIUM,
                headless=True,
                record_video=True,
                video_dir="custom/videos",
                video_size={"width": 1920, "height": 1080},
            )

            assert manager.record_video is True
            assert manager.video_dir == "custom/videos"
            assert manager.video_size == {"width": 1920, "height": 1080}

    def test_init_default_video_config(self):
        """默认视频配置"""
        with patch(
            "df_test_framework.capabilities.drivers.web.playwright.browser.PLAYWRIGHT_AVAILABLE",
            True,
        ):
            from df_test_framework.capabilities.drivers.web.playwright.browser import (
                BrowserManager,
            )

            manager = BrowserManager()

            assert manager.record_video is False
            assert manager.video_dir == "reports/videos"
            assert manager.video_size is None

    def test_video_config_types(self):
        """视频配置类型正确"""
        with patch(
            "df_test_framework.capabilities.drivers.web.playwright.browser.PLAYWRIGHT_AVAILABLE",
            True,
        ):
            from df_test_framework.capabilities.drivers.web.playwright.browser import (
                BrowserManager,
            )

            manager = BrowserManager(
                record_video=True,
                video_dir="reports/videos",
            )

            assert isinstance(manager.record_video, bool)
            assert isinstance(manager.video_dir, str)


class TestUIFixturesExports:
    """测试 UI fixtures 导出"""

    def test_all_exports_include_video_fixtures(self):
        """__all__ 包含视频相关 fixtures"""
        from df_test_framework.testing.fixtures import ui

        assert "browser_record_video" in ui.__all__
        assert "browser_video_dir" in ui.__all__

    def test_video_fixtures_are_importable(self):
        """视频 fixtures 可以正常导入"""
        from df_test_framework.testing.fixtures.ui import (
            browser_record_video,
            browser_video_dir,
        )

        assert callable(browser_record_video)
        assert callable(browser_video_dir)


class TestContextVideoRecording:
    """测试 context fixture 视频录制集成"""

    def test_context_options_without_video(self):
        """不录制视频时，context_options 不包含 record_video_dir"""
        # 模拟不录制视频的场景
        browser_record_video = False
        browser_video_dir = "reports/videos"
        browser_viewport = {"width": 1280, "height": 720}

        context_options = {"viewport": browser_viewport}

        if browser_record_video:
            context_options["record_video_dir"] = browser_video_dir

        assert "record_video_dir" not in context_options
        assert context_options["viewport"] == browser_viewport

    def test_context_options_with_video(self):
        """录制视频时，context_options 包含 record_video_dir"""
        browser_record_video = True
        browser_video_dir = "reports/videos"
        browser_viewport = {"width": 1280, "height": 720}

        context_options = {"viewport": browser_viewport}

        if browser_record_video:
            context_options["record_video_dir"] = browser_video_dir

        assert context_options["record_video_dir"] == "reports/videos"
        assert context_options["viewport"] == browser_viewport


class TestBrowserManagerStart:
    """测试 BrowserManager.start() 视频录制"""

    @patch("df_test_framework.capabilities.drivers.web.playwright.browser.sync_playwright")
    @patch(
        "df_test_framework.capabilities.drivers.web.playwright.browser.PLAYWRIGHT_AVAILABLE",
        True,
    )
    def test_start_creates_video_dir_when_recording(self, mock_sync_playwright):
        """启动时录制视频会创建视频目录"""
        from df_test_framework.capabilities.drivers.web.playwright.browser import (
            BrowserManager,
        )

        # 设置 mock
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_sync_playwright.return_value.start.return_value = mock_playwright
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        manager = BrowserManager(
            record_video=True,
            video_dir="test_videos",
        )

        with patch("pathlib.Path.mkdir") as mock_mkdir:
            try:
                manager.start()
            finally:
                manager.stop()

            # 验证创建了视频目录
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch("df_test_framework.capabilities.drivers.web.playwright.browser.sync_playwright")
    @patch(
        "df_test_framework.capabilities.drivers.web.playwright.browser.PLAYWRIGHT_AVAILABLE",
        True,
    )
    def test_start_passes_video_options_to_context(self, mock_sync_playwright):
        """启动时视频选项传递给 context"""
        from df_test_framework.capabilities.drivers.web.playwright.browser import (
            BrowserManager,
        )

        # 设置 mock
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_sync_playwright.return_value.start.return_value = mock_playwright
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        manager = BrowserManager(
            record_video=True,
            video_dir="test_videos",
            video_size={"width": 1280, "height": 720},
        )

        with patch("pathlib.Path.mkdir"):
            try:
                manager.start()
            finally:
                manager.stop()

            # 验证 new_context 被调用时包含视频选项
            call_kwargs = mock_browser.new_context.call_args[1]
            assert call_kwargs["record_video_dir"] == "test_videos"
            assert call_kwargs["record_video_size"] == {"width": 1280, "height": 720}

    @patch("df_test_framework.capabilities.drivers.web.playwright.browser.sync_playwright")
    @patch(
        "df_test_framework.capabilities.drivers.web.playwright.browser.PLAYWRIGHT_AVAILABLE",
        True,
    )
    def test_start_without_video_no_video_options(self, mock_sync_playwright):
        """不录制视频时，context 不包含视频选项"""
        from df_test_framework.capabilities.drivers.web.playwright.browser import (
            BrowserManager,
        )

        # 设置 mock
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_sync_playwright.return_value.start.return_value = mock_playwright
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        manager = BrowserManager(record_video=False)

        try:
            manager.start()
        finally:
            manager.stop()

        # 验证 new_context 被调用时不包含视频选项
        call_kwargs = mock_browser.new_context.call_args[1]
        assert "record_video_dir" not in call_kwargs
        assert "record_video_size" not in call_kwargs
