"""测试 main.py - CLI主入口

测试覆盖:
- main() 函数
- 命令行参数解析
- 命令分发
"""

import shutil
from pathlib import Path

import pytest

from df_test_framework.cli.main import main


class TestCLIMain:
    """测试CLI主入口"""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """临时目录"""
        yield tmp_path
        # 清理
        for item in tmp_path.iterdir():
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            else:
                item.unlink()

    def test_init_command(self, temp_dir):
        """测试init命令"""
        project_path = str(temp_dir / "my_project")

        # 执行init命令
        main(["init", project_path, "--type", "api"])

        # 验证项目创建成功
        assert Path(project_path).exists()
        assert (Path(project_path) / "pyproject.toml").exists()

    def test_init_command_with_force(self, temp_dir):
        """测试init命令的--force选项"""
        project_path = str(temp_dir / "my_project")

        # 第一次创建
        main(["init", project_path, "--type", "api"])

        # 第二次创建（强制覆盖）
        main(["init", project_path, "--type", "api", "--force"])

        # 应该成功
        assert Path(project_path).exists()

    def test_init_command_ui_type(self, temp_dir):
        """测试init命令创建UI项目"""
        project_path = str(temp_dir / "ui_project")

        main(["init", project_path, "--type", "ui"])

        # 验证UI特定文件
        assert (Path(project_path) / "src" / "ui_project" / "pages").exists()

    def test_init_command_full_type(self, temp_dir):
        """测试init命令创建Full项目"""
        project_path = str(temp_dir / "full_project")

        main(["init", project_path, "--type", "full"])

        # 验证API和UI文件都存在
        project = Path(project_path)
        assert (project / "src" / "full_project" / "apis").exists()
        assert (project / "src" / "full_project" / "pages").exists()

    def test_gen_test_command(self, temp_dir):
        """测试gen test命令"""
        import os

        old_cwd = os.getcwd()

        # 先创建项目
        project_path = temp_dir / "test_project"
        main(["init", str(project_path), "--type", "api"])

        os.chdir(project_path)
        try:
            # 生成测试文件
            main(["gen", "test", "user_login", "--feature", "用户模块"])

            # 验证文件生成
            test_file = project_path / "tests" / "api" / "test_user_login.py"
            assert test_file.exists()
        finally:
            os.chdir(old_cwd)

    def test_gen_builder_command(self, temp_dir):
        """测试gen builder命令"""
        import os

        old_cwd = os.getcwd()

        # 先创建项目
        project_path = temp_dir / "test_project"
        main(["init", str(project_path), "--type", "api"])

        os.chdir(project_path)
        try:
            # 生成Builder
            main(["gen", "builder", "user"])

            # 验证文件生成
            builder_file = project_path / "src" / "test_project" / "builders" / "user_builder.py"
            assert builder_file.exists()
        finally:
            os.chdir(old_cwd)

    def test_gen_repository_command(self, temp_dir):
        """测试gen repo命令"""
        import os

        old_cwd = os.getcwd()

        # 先创建项目
        project_path = temp_dir / "test_project"
        main(["init", str(project_path), "--type", "api"])

        os.chdir(project_path)
        try:
            # 生成Repository
            main(["gen", "repo", "user", "--table-name", "users"])

            # 验证文件生成
            repo_file = (
                project_path / "src" / "test_project" / "repositories" / "user_repository.py"
            )
            assert repo_file.exists()
        finally:
            os.chdir(old_cwd)

    def test_gen_api_command(self, temp_dir):
        """测试gen api命令"""
        import os

        old_cwd = os.getcwd()

        # 先创建项目
        project_path = temp_dir / "test_project"
        main(["init", str(project_path), "--type", "api"])

        os.chdir(project_path)
        try:
            # 生成API客户端（使用 order 而不是 user，因为脚手架模板默认创建 user_api.py）
            main(["gen", "api", "order", "--api-path", "orders"])

            # 验证文件生成
            api_file = project_path / "src" / "test_project" / "apis" / "order_api.py"
            assert api_file.exists()
        finally:
            os.chdir(old_cwd)

    @pytest.mark.skip(reason="JSON模型生成功能需要进一步完善")
    def test_gen_models_command(self, temp_dir):
        """测试gen models命令

        TODO: 依赖于generate_models_from_json的修复
        """
        pass

    def test_generate_alias(self, temp_dir):
        """测试generate命令的别名"""
        import os

        old_cwd = os.getcwd()

        project_path = temp_dir / "test_project"
        main(["init", str(project_path), "--type", "api"])

        os.chdir(project_path)
        try:
            # 使用generate别名（而不是gen）
            main(["generate", "test", "sample_test"])

            test_file = project_path / "tests" / "api" / "test_sample_test.py"
            assert test_file.exists()
        finally:
            os.chdir(old_cwd)

    def test_repository_alias(self, temp_dir):
        """测试repository命令的别名"""
        import os

        old_cwd = os.getcwd()

        project_path = temp_dir / "test_project"
        main(["init", str(project_path), "--type", "api"])

        os.chdir(project_path)
        try:
            # 使用repository别名（而不是repo）
            main(["gen", "repository", "product"])

            repo_file = (
                project_path / "src" / "test_project" / "repositories" / "product_repository.py"
            )
            assert repo_file.exists()
        finally:
            os.chdir(old_cwd)

    def test_gen_graphql_client_command(self, temp_dir):
        """测试gen graphql-client命令（v3.35.6）"""
        import os

        old_cwd = os.getcwd()

        # 先创建项目
        project_path = temp_dir / "test_project"
        main(["init", str(project_path), "--type", "api"])

        os.chdir(project_path)
        try:
            # 生成GraphQL客户端（使用默认名称）
            main(["gen", "graphql-client"])

            # 验证文件生成（默认生成 graphql_client.py）
            client_file = project_path / "src" / "test_project" / "clients" / "graphql_client.py"
            assert client_file.exists()

            # 验证文件内容包含关键代码
            content = client_file.read_text(encoding="utf-8")
            assert "GraphQLClient" in content
            assert "TestProjectGraphQLClient" in content
        finally:
            os.chdir(old_cwd)

    def test_gen_graphql_test_command(self, temp_dir):
        """测试gen graphql-test命令（v3.35.6）"""
        import os

        old_cwd = os.getcwd()

        # 先创建项目
        project_path = temp_dir / "test_project"
        main(["init", str(project_path), "--type", "api"])

        os.chdir(project_path)
        try:
            # 生成GraphQL测试示例
            main(["gen", "graphql-test"])

            # 验证文件生成（默认生成在 tests/graphql/ 目录）
            test_file = project_path / "tests" / "graphql" / "test_graphql_example.py"
            assert test_file.exists()

            # 验证文件内容包含关键代码
            content = test_file.read_text(encoding="utf-8")
            assert "graphql" in content.lower()
            assert "def test_" in content
        finally:
            os.chdir(old_cwd)

    def test_gen_redis_fixture_command(self, temp_dir):
        """测试gen redis-fixture命令（v3.35.6）"""
        import os

        old_cwd = os.getcwd()

        # 先创建项目
        project_path = temp_dir / "test_project"
        main(["init", str(project_path), "--type", "api"])

        os.chdir(project_path)
        try:
            # 生成Redis Fixture
            main(["gen", "redis-fixture"])

            # 验证fixture文件生成（文件名是 redis_fixtures.py）
            fixture_file = project_path / "src" / "test_project" / "fixtures" / "redis_fixtures.py"
            assert fixture_file.exists()

            # 验证测试文件生成（生成在 tests/redis/ 目录）
            test_file = project_path / "tests" / "redis" / "test_redis_example.py"
            assert test_file.exists()

            # 验证fixture文件内容
            fixture_content = fixture_file.read_text(encoding="utf-8")
            assert "redis" in fixture_content.lower()
            assert "@pytest.fixture" in fixture_content

            # 验证测试文件内容
            test_content = test_file.read_text(encoding="utf-8")
            assert "def test_" in test_content
        finally:
            os.chdir(old_cwd)


__all__ = ["TestCLIMain"]
