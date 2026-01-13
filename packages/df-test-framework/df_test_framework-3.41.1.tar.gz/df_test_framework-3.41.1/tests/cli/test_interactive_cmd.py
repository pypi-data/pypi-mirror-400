"""CLI interactive 命令测试模块

测试交互式代码生成命令功能

v3.36.0 - 技术债务清理：提升测试覆盖率
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestQuestionaryAvailability:
    """测试 questionary 可用性检查"""

    def test_questionary_available_constant(self):
        """测试 QUESTIONARY_AVAILABLE 常量"""
        from df_test_framework.cli.commands import interactive

        # 根据是否安装 questionary 来判断
        assert isinstance(interactive.QUESTIONARY_AVAILABLE, bool)

    def test_custom_style_defined_when_available(self):
        """测试自定义样式（当 questionary 可用时）"""
        from df_test_framework.cli.commands import interactive

        if interactive.QUESTIONARY_AVAILABLE:
            assert interactive.CUSTOM_STYLE is not None
        else:
            assert interactive.CUSTOM_STYLE is None


@pytest.mark.unit
class TestInteractiveGenerate:
    """测试 interactive_generate 函数"""

    def test_interactive_generate_without_questionary(self, capsys):
        """测试没有 questionary 时的错误处理"""
        from df_test_framework.cli.commands import interactive

        # Mock QUESTIONARY_AVAILABLE 为 False
        with patch.object(interactive, "QUESTIONARY_AVAILABLE", False):
            interactive.interactive_generate()

        captured = capsys.readouterr()
        assert "questionary" in captured.out
        assert "pip install questionary" in captured.out

    def test_interactive_generate_exit_choice(self, capsys):
        """测试选择退出"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with patch.object(interactive, "questionary") as mock_q:
            mock_q.Choice = MagicMock(side_effect=lambda label, value: MagicMock(value=value))
            mock_q.select.return_value.ask.return_value = "exit"

            interactive.interactive_generate()

        captured = capsys.readouterr()
        assert "再见" in captured.out

    def test_interactive_generate_none_choice(self, capsys):
        """测试取消选择（返回 None）"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with patch.object(interactive, "questionary") as mock_q:
            mock_q.Choice = MagicMock(side_effect=lambda label, value: MagicMock(value=value))
            mock_q.select.return_value.ask.return_value = None

            interactive.interactive_generate()

        captured = capsys.readouterr()
        assert "再见" in captured.out

    def test_interactive_generate_test_choice(self):
        """测试选择生成测试用例"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with (
            patch.object(interactive, "questionary") as mock_q,
            patch.object(interactive, "_interactive_test") as mock_test,
        ):
            mock_q.Choice = MagicMock(side_effect=lambda label, value: MagicMock(value=value))
            mock_q.select.return_value.ask.return_value = "test"

            interactive.interactive_generate()

            mock_test.assert_called_once()

    def test_interactive_generate_suite_choice(self):
        """测试选择生成测试套件"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with (
            patch.object(interactive, "questionary") as mock_q,
            patch.object(interactive, "_interactive_suite") as mock_suite,
        ):
            mock_q.Choice = MagicMock(side_effect=lambda label, value: MagicMock(value=value))
            mock_q.select.return_value.ask.return_value = "suite"

            interactive.interactive_generate()

            mock_suite.assert_called_once()

    def test_interactive_generate_settings_choice(self):
        """测试选择生成配置文件"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with (
            patch.object(interactive, "questionary") as mock_q,
            patch.object(interactive, "_interactive_settings") as mock_settings,
        ):
            mock_q.Choice = MagicMock(side_effect=lambda label, value: MagicMock(value=value))
            mock_q.select.return_value.ask.return_value = "settings"

            interactive.interactive_generate()

            mock_settings.assert_called_once()

    def test_interactive_generate_builder_choice(self):
        """测试选择生成 Builder"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with (
            patch.object(interactive, "questionary") as mock_q,
            patch.object(interactive, "_interactive_builder") as mock_builder,
        ):
            mock_q.Choice = MagicMock(side_effect=lambda label, value: MagicMock(value=value))
            mock_q.select.return_value.ask.return_value = "builder"

            interactive.interactive_generate()

            mock_builder.assert_called_once()

    def test_interactive_generate_repository_choice(self):
        """测试选择生成 Repository"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with (
            patch.object(interactive, "questionary") as mock_q,
            patch.object(interactive, "_interactive_repository") as mock_repository,
        ):
            mock_q.Choice = MagicMock(side_effect=lambda label, value: MagicMock(value=value))
            mock_q.select.return_value.ask.return_value = "repository"

            interactive.interactive_generate()

            mock_repository.assert_called_once()

    def test_interactive_generate_api_choice(self):
        """测试选择生成 API 客户端"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with (
            patch.object(interactive, "questionary") as mock_q,
            patch.object(interactive, "_interactive_api") as mock_api,
        ):
            mock_q.Choice = MagicMock(side_effect=lambda label, value: MagicMock(value=value))
            mock_q.select.return_value.ask.return_value = "api"

            interactive.interactive_generate()

            mock_api.assert_called_once()


@pytest.mark.unit
class TestInteractiveTest:
    """测试 _interactive_test 函数"""

    def test_interactive_test_cancel_name(self, capsys):
        """测试取消输入测试名称"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with patch.object(interactive, "questionary") as mock_q:
            mock_q.text.return_value.ask.return_value = None

            interactive._interactive_test()

        captured = capsys.readouterr()
        assert "已取消" in captured.out

    def test_interactive_test_cancel_template(self, capsys):
        """测试取消选择模板"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with patch.object(interactive, "questionary") as mock_q:
            mock_q.text.return_value.ask.return_value = "user_login"
            mock_q.select.return_value.ask.return_value = None
            mock_q.Choice = MagicMock(side_effect=lambda label, value: MagicMock(value=value))

            interactive._interactive_test()

        captured = capsys.readouterr()
        assert "已取消" in captured.out

    def test_interactive_test_not_confirmed(self, capsys):
        """测试不确认生成"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with patch.object(interactive, "questionary") as mock_q:
            mock_q.text.return_value.ask.side_effect = [
                "user_login",  # test_name
                "/api/users",  # api_path
                "用户管理",  # feature
                "用户登录",  # story
                "tests/api",  # output_dir
            ]
            mock_q.select.return_value.ask.return_value = "complete"
            mock_q.confirm.return_value.ask.return_value = False
            mock_q.Choice = MagicMock(side_effect=lambda label, value: MagicMock(value=value))

            interactive._interactive_test()

        captured = capsys.readouterr()
        assert "已取消" in captured.out

    def test_interactive_test_success(self, capsys):
        """测试成功生成测试"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with (
            patch.object(interactive, "questionary") as mock_q,
            patch.object(interactive, "generate_test") as mock_gen,
        ):
            mock_q.text.return_value.ask.side_effect = [
                "user_login",  # test_name
                "/api/users",  # api_path
                "用户管理",  # feature
                "用户登录",  # story
                "tests/api",  # output_dir
            ]
            mock_q.select.return_value.ask.return_value = "complete"
            mock_q.confirm.return_value.ask.return_value = True
            mock_q.Choice = MagicMock(side_effect=lambda label, value: MagicMock(value=value))

            interactive._interactive_test()

            mock_gen.assert_called_once()

        captured = capsys.readouterr()
        assert "生成完成" in captured.out

    def test_interactive_test_failure(self, capsys):
        """测试生成失败"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with (
            patch.object(interactive, "questionary") as mock_q,
            patch.object(interactive, "generate_test", side_effect=Exception("生成错误")),
        ):
            mock_q.text.return_value.ask.side_effect = [
                "user_login",
                "/api/users",
                "",
                "",
                "tests/api",
            ]
            mock_q.select.return_value.ask.return_value = "complete"
            mock_q.confirm.return_value.ask.return_value = True
            mock_q.Choice = MagicMock(side_effect=lambda label, value: MagicMock(value=value))

            interactive._interactive_test()

        captured = capsys.readouterr()
        assert "生成失败" in captured.out


@pytest.mark.unit
class TestInteractiveSuite:
    """测试 _interactive_suite 函数"""

    def test_interactive_suite_cancel_name(self, capsys):
        """测试取消输入实体名称"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with patch.object(interactive, "questionary") as mock_q:
            mock_q.text.return_value.ask.return_value = None

            interactive._interactive_suite()

        captured = capsys.readouterr()
        assert "已取消" in captured.out

    def test_interactive_suite_not_confirmed(self, capsys):
        """测试不确认生成"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with patch.object(interactive, "questionary") as mock_q:
            mock_q.text.return_value.ask.side_effect = [
                "user",  # entity_name
                "users",  # table_name
                "users",  # api_path
            ]
            mock_q.confirm.return_value.ask.return_value = False

            interactive._interactive_suite()

        captured = capsys.readouterr()
        assert "已取消" in captured.out

    def test_interactive_suite_success(self, capsys):
        """测试成功生成套件"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with (
            patch.object(interactive, "questionary") as mock_q,
            patch.object(interactive, "generate_builder") as mock_builder,
            patch.object(interactive, "generate_repository") as mock_repo,
            patch.object(interactive, "generate_api_client") as mock_api,
            patch.object(interactive, "generate_test") as mock_test,
        ):
            mock_q.text.return_value.ask.side_effect = [
                "user",
                "users",
                "users",
            ]
            mock_q.confirm.return_value.ask.return_value = True

            interactive._interactive_suite()

            mock_builder.assert_called_once()
            mock_repo.assert_called_once()
            mock_api.assert_called_once()
            mock_test.assert_called_once()

        captured = capsys.readouterr()
        assert "完整套件生成完成" in captured.out


@pytest.mark.unit
class TestInteractiveSettings:
    """测试 _interactive_settings 函数"""

    def test_interactive_settings_not_confirmed(self, capsys):
        """测试不确认生成"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with patch.object(interactive, "questionary") as mock_q:
            mock_q.confirm.return_value.ask.side_effect = [
                True,  # with_interceptors
                True,  # with_profile
                False,  # confirm
            ]

            interactive._interactive_settings()

        captured = capsys.readouterr()
        assert "已取消" in captured.out

    def test_interactive_settings_success(self, capsys):
        """测试成功生成配置"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with (
            patch.object(interactive, "questionary") as mock_q,
            patch.object(interactive, "generate_settings") as mock_gen,
        ):
            mock_q.confirm.return_value.ask.side_effect = [
                True,  # with_interceptors
                True,  # with_profile
                True,  # confirm
            ]

            interactive._interactive_settings()

            mock_gen.assert_called_once()

        captured = capsys.readouterr()
        assert "配置文件生成完成" in captured.out


@pytest.mark.unit
class TestInteractiveBuilder:
    """测试 _interactive_builder 函数"""

    def test_interactive_builder_cancel(self, capsys):
        """测试取消输入"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with patch.object(interactive, "questionary") as mock_q:
            mock_q.text.return_value.ask.return_value = None

            interactive._interactive_builder()

        captured = capsys.readouterr()
        assert "已取消" in captured.out

    def test_interactive_builder_success(self, capsys):
        """测试成功生成"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with (
            patch.object(interactive, "questionary") as mock_q,
            patch.object(interactive, "generate_builder") as mock_gen,
        ):
            mock_q.text.return_value.ask.return_value = "user"

            interactive._interactive_builder()

            mock_gen.assert_called_once_with("user", force=False)

        captured = capsys.readouterr()
        assert "生成完成" in captured.out


@pytest.mark.unit
class TestInteractiveRepository:
    """测试 _interactive_repository 函数"""

    def test_interactive_repository_cancel(self, capsys):
        """测试取消输入"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with patch.object(interactive, "questionary") as mock_q:
            mock_q.text.return_value.ask.return_value = None

            interactive._interactive_repository()

        captured = capsys.readouterr()
        assert "已取消" in captured.out

    def test_interactive_repository_success(self, capsys):
        """测试成功生成"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with (
            patch.object(interactive, "questionary") as mock_q,
            patch.object(interactive, "generate_repository") as mock_gen,
        ):
            mock_q.text.return_value.ask.side_effect = ["user", "users"]

            interactive._interactive_repository()

            mock_gen.assert_called_once_with("user", table_name="users", force=False)

        captured = capsys.readouterr()
        assert "生成完成" in captured.out


@pytest.mark.unit
class TestInteractiveApi:
    """测试 _interactive_api 函数"""

    def test_interactive_api_cancel(self, capsys):
        """测试取消输入"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with patch.object(interactive, "questionary") as mock_q:
            mock_q.text.return_value.ask.return_value = None

            interactive._interactive_api()

        captured = capsys.readouterr()
        assert "已取消" in captured.out

    def test_interactive_api_success(self, capsys):
        """测试成功生成"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with (
            patch.object(interactive, "questionary") as mock_q,
            patch.object(interactive, "generate_api_client") as mock_gen,
        ):
            mock_q.text.return_value.ask.side_effect = ["user", "users"]

            interactive._interactive_api()

            mock_gen.assert_called_once_with("user", api_path="users", force=False)

        captured = capsys.readouterr()
        assert "生成完成" in captured.out


@pytest.mark.unit
class TestInteractiveSwagger:
    """测试 _interactive_swagger 函数"""

    def test_interactive_swagger_cancel_spec(self, capsys):
        """测试取消输入规范文件"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with patch.object(interactive, "questionary") as mock_q:
            mock_q.text.return_value.ask.return_value = None

            interactive._interactive_swagger()

        captured = capsys.readouterr()
        assert "已取消" in captured.out

    def test_interactive_swagger_no_options(self, capsys):
        """测试没有选择生成选项"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with patch.object(interactive, "questionary") as mock_q:
            mock_q.text.return_value.ask.return_value = "swagger.json"
            mock_q.checkbox.return_value.ask.return_value = None
            mock_q.Choice = MagicMock(
                side_effect=lambda label, value, checked=False: MagicMock(value=value)
            )

            interactive._interactive_swagger()

        captured = capsys.readouterr()
        assert "至少需要选择一项" in captured.out

    def test_interactive_swagger_not_confirmed(self, capsys):
        """测试不确认生成"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with patch.object(interactive, "questionary") as mock_q:
            mock_q.text.return_value.ask.return_value = "swagger.json"
            mock_q.checkbox.return_value.ask.return_value = ["tests"]
            mock_q.confirm.return_value.ask.side_effect = [False, False]  # use_tags, confirm
            mock_q.Choice = MagicMock(
                side_effect=lambda label, value, checked=False: MagicMock(value=value)
            )

            interactive._interactive_swagger()

        captured = capsys.readouterr()
        assert "已取消" in captured.out

    def test_interactive_swagger_success(self, capsys):
        """测试成功生成"""
        from df_test_framework.cli.commands import interactive

        if not interactive.QUESTIONARY_AVAILABLE:
            pytest.skip("questionary 未安装")

        with (
            patch.object(interactive, "questionary") as mock_q,
            patch(
                "df_test_framework.cli.generators.openapi_generator.generate_from_openapi"
            ) as mock_gen,
        ):
            mock_q.text.return_value.ask.return_value = "swagger.json"
            mock_q.checkbox.return_value.ask.return_value = ["tests", "clients"]
            mock_q.confirm.return_value.ask.side_effect = [False, True]  # use_tags, confirm
            mock_q.Choice = MagicMock(
                side_effect=lambda label, value, checked=False: MagicMock(value=value)
            )

            interactive._interactive_swagger()

            mock_gen.assert_called_once()

        captured = capsys.readouterr()
        assert "生成完成" in captured.out


@pytest.mark.unit
class TestModuleExports:
    """测试模块导出"""

    def test_all_exports(self):
        """测试 __all__ 导出"""
        from df_test_framework.cli.commands import interactive

        assert "interactive_generate" in interactive.__all__
        assert hasattr(interactive, "interactive_generate")
        assert callable(interactive.interactive_generate)
