"""CLI env 命令测试模块

测试环境管理命令功能

v3.36.0 - 技术债务清理：提升测试覆盖率
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestEnvShow:
    """测试 env_show 命令"""

    def test_env_show_with_yaml_config(self, tmp_path):
        """测试使用 YAML 配置显示环境"""
        from df_test_framework.cli.commands.env import env_show

        # 创建临时配置目录
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "base.yaml").write_text("http:\n  timeout: 30", encoding="utf-8")
        (config_dir / "environments").mkdir()
        (config_dir / "environments" / "test.yaml").write_text(
            "env: test\ndebug: false", encoding="utf-8"
        )

        # Mock load_config
        with patch("df_test_framework.infrastructure.config.load_config") as mock_load:
            mock_settings = MagicMock()
            mock_settings.env = "test"
            mock_settings.debug = False
            mock_settings.http.base_url = "http://localhost:8000"
            mock_settings.http.timeout = 30
            mock_settings.http.max_retries = 3
            mock_settings.db = None
            mock_settings.redis = None
            mock_settings.observability = None
            mock_load.return_value = mock_settings

            result = env_show(env="test", config_dir=str(config_dir))

        assert result == 0

    def test_env_show_with_dotenv_config(self, tmp_path):
        """测试使用 .env 配置显示环境"""
        from df_test_framework.cli.commands.env import env_show

        # 创建不存在的配置目录
        config_dir = tmp_path / "nonexistent"

        # Mock FrameworkSettings
        with patch(
            "df_test_framework.infrastructure.config.FrameworkSettings"
        ) as mock_settings_cls:
            mock_settings = MagicMock()
            mock_settings.env = "dev"
            mock_settings.debug = True
            mock_settings.http.base_url = "http://localhost:8000"
            mock_settings.http.timeout = 30
            mock_settings.http.max_retries = 3
            mock_settings.db = None
            mock_settings.redis = None
            mock_settings.observability = None
            mock_settings_cls.return_value = mock_settings

            result = env_show(env=None, config_dir=str(config_dir))

        assert result == 0

    def test_env_show_error_handling(self, tmp_path):
        """测试错误处理"""
        from df_test_framework.cli.commands.env import env_show

        # 创建配置目录但抛出异常
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "base.yaml").write_text("http:\n  timeout: 30", encoding="utf-8")

        with patch(
            "df_test_framework.infrastructure.config.load_config",
            side_effect=Exception("Load error"),
        ):
            result = env_show(env="test", config_dir=str(config_dir))

        assert result == 1


@pytest.mark.unit
class TestEnvInit:
    """测试 env_init 命令"""

    def test_env_init_creates_directory_structure(self, tmp_path):
        """测试创建配置目录结构"""
        from df_test_framework.cli.commands.env import env_init

        config_dir = tmp_path / "config"

        result = env_init(config_dir=str(config_dir))

        assert result == 0
        assert config_dir.exists()
        assert (config_dir / "base.yaml").exists()
        assert (config_dir / "environments").exists()
        assert (config_dir / "environments" / "local.yaml").exists()
        assert (config_dir / "environments" / "dev.yaml").exists()
        assert (config_dir / "environments" / "test.yaml").exists()
        assert (config_dir / "environments" / "staging.yaml").exists()
        assert (config_dir / "environments" / "prod.yaml").exists()
        assert (config_dir / "secrets" / ".gitkeep").exists()
        assert (config_dir / "secrets" / ".gitignore").exists()

    def test_env_init_fails_if_exists(self, tmp_path):
        """测试配置目录已存在时失败"""
        from df_test_framework.cli.commands.env import env_init

        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "base.yaml").write_text("existing", encoding="utf-8")

        result = env_init(config_dir=str(config_dir))

        assert result == 1

    def test_env_init_creates_local_with_extends(self, tmp_path):
        """测试 local.yaml 使用 _extends 继承 dev"""
        from df_test_framework.cli.commands.env import env_init

        config_dir = tmp_path / "config"

        env_init(config_dir=str(config_dir))

        local_content = (config_dir / "environments" / "local.yaml").read_text(encoding="utf-8")
        assert "_extends: environments/dev.yaml" in local_content


@pytest.mark.unit
class TestEnvValidate:
    """测试 env_validate 命令"""

    def test_env_validate_missing_config_dir(self, tmp_path):
        """测试配置目录不存在时失败"""
        from df_test_framework.cli.commands.env import env_validate

        result = env_validate(env="test", config_dir=str(tmp_path / "nonexistent"))

        assert result == 1

    def test_env_validate_missing_base_yaml(self, tmp_path):
        """测试 base.yaml 不存在时失败"""
        from df_test_framework.cli.commands.env import env_validate

        config_dir = tmp_path / "config"
        config_dir.mkdir()

        result = env_validate(env="test", config_dir=str(config_dir))

        assert result == 1

    def test_env_validate_success(self, tmp_path):
        """测试配置验证成功"""
        from df_test_framework.cli.commands.env import env_validate

        # 创建配置目录
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "base.yaml").write_text("http:\n  timeout: 30", encoding="utf-8")
        (config_dir / "environments").mkdir()
        (config_dir / "environments" / "test.yaml").write_text(
            "env: test\nhttp:\n  base_url: http://api.example.com",
            encoding="utf-8",
        )

        # Mock load_config
        with patch("df_test_framework.infrastructure.config.load_config") as mock_load:
            mock_settings = MagicMock()
            mock_settings.env = "test"
            mock_settings.debug = False
            mock_settings.http.base_url = "http://api.example.com"
            mock_settings.db = None
            mock_settings.redis = None
            mock_load.return_value = mock_settings

            result = env_validate(env="test", config_dir=str(config_dir))

        assert result == 0

    def test_env_validate_with_warnings(self, tmp_path):
        """测试配置验证有警告"""
        from df_test_framework.cli.commands.env import env_validate

        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "base.yaml").write_text("http:\n  timeout: 30", encoding="utf-8")
        (config_dir / "environments").mkdir()

        # Mock load_config - 使用默认值
        with patch("df_test_framework.infrastructure.config.load_config") as mock_load:
            mock_settings = MagicMock()
            mock_settings.env = "test"
            mock_settings.debug = False
            mock_settings.http.base_url = "http://localhost:8000"  # 默认值
            mock_settings.db = MagicMock()
            mock_settings.db.host = None
            mock_settings.db.connection_string = None
            mock_settings.redis = MagicMock()
            mock_settings.redis.host = "localhost"  # 默认值
            mock_load.return_value = mock_settings

            result = env_validate(env="test", config_dir=str(config_dir))

        assert result == 0  # 警告不影响返回值

    def test_env_validate_error_handling(self, tmp_path):
        """测试验证异常处理"""
        from df_test_framework.cli.commands.env import env_validate

        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "base.yaml").write_text("http:\n  timeout: 30", encoding="utf-8")

        with patch(
            "df_test_framework.infrastructure.config.load_config",
            side_effect=Exception("Validation error"),
        ):
            result = env_validate(env="test", config_dir=str(config_dir))

        assert result == 1


@pytest.mark.unit
class TestPrintSettings:
    """测试 _print_settings 函数"""

    def test_print_settings_minimal(self, capsys):
        """测试最小配置输出"""
        from df_test_framework.cli.commands.env import _print_settings

        mock_settings = MagicMock()
        mock_settings.env = "test"
        mock_settings.debug = False
        mock_settings.http = None
        mock_settings.db = None
        mock_settings.redis = None
        mock_settings.observability = None

        _print_settings(mock_settings, ".env")

        captured = capsys.readouterr()
        assert "环境配置 - test" in captured.out
        assert ".env" in captured.out

    def test_print_settings_with_http(self, capsys):
        """测试包含 HTTP 配置的输出"""
        from df_test_framework.cli.commands.env import _print_settings

        mock_settings = MagicMock()
        mock_settings.env = "test"
        mock_settings.debug = True
        mock_settings.http.base_url = "http://api.example.com"
        mock_settings.http.timeout = 30
        mock_settings.http.max_retries = 3
        mock_settings.db = None
        mock_settings.redis = None
        mock_settings.observability = None

        _print_settings(mock_settings, "config/")

        captured = capsys.readouterr()
        assert "HTTP 配置" in captured.out
        assert "http://api.example.com" in captured.out
        assert "30s" in captured.out

    def test_print_settings_with_database(self, capsys):
        """测试包含数据库配置的输出"""
        from df_test_framework.cli.commands.env import _print_settings

        mock_settings = MagicMock()
        mock_settings.env = "test"
        mock_settings.debug = False
        mock_settings.http = None
        mock_settings.db.host = "localhost"
        mock_settings.db.port = 3306
        mock_settings.db.name = "test_db"
        mock_settings.db.pool_size = 10
        mock_settings.redis = None
        mock_settings.observability = None

        _print_settings(mock_settings, "config/")

        captured = capsys.readouterr()
        assert "数据库配置" in captured.out
        assert "localhost:3306" in captured.out
        assert "test_db" in captured.out

    def test_print_settings_with_redis(self, capsys):
        """测试包含 Redis 配置的输出"""
        from df_test_framework.cli.commands.env import _print_settings

        mock_settings = MagicMock()
        mock_settings.env = "test"
        mock_settings.debug = False
        mock_settings.http = None
        mock_settings.db = None
        mock_settings.redis.host = "localhost"
        mock_settings.redis.port = 6379
        mock_settings.redis.db = 0
        mock_settings.observability = None

        _print_settings(mock_settings, "config/")

        captured = capsys.readouterr()
        assert "Redis 配置" in captured.out
        assert "localhost:6379" in captured.out

    def test_print_settings_with_observability(self, capsys):
        """测试包含可观测性配置的输出"""
        from df_test_framework.cli.commands.env import _print_settings

        mock_settings = MagicMock()
        mock_settings.env = "test"
        mock_settings.debug = False
        mock_settings.http = None
        mock_settings.db = None
        mock_settings.redis = None
        mock_settings.observability.enabled = True
        mock_settings.observability.allure_recording = True
        mock_settings.observability.debug_output = False

        _print_settings(mock_settings, "config/")

        captured = capsys.readouterr()
        assert "可观测性配置" in captured.out
        assert "Allure" in captured.out


@pytest.mark.unit
class TestModuleExports:
    """测试模块导出"""

    def test_all_exports(self):
        """测试 __all__ 导出"""
        from df_test_framework.cli.commands import env

        expected_exports = ["env_show", "env_init", "env_validate"]

        for export in expected_exports:
            assert hasattr(env, export), f"Missing export: {export}"
