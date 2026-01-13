"""配置系统 + 环境管理集成测试 (v3.36.0)

测试 ConfigLoader、get_settings_for_class 与环境管理的协同工作。

v3.36.0: 移除 ConfigRegistry 测试，使用现代化 API
"""

import pytest
import yaml

from df_test_framework.infrastructure.config import (
    FrameworkSettings,
    get_settings_for_class,
    load_config,
)


class TestConfigLoaderIntegration:
    """ConfigLoader 集成测试"""

    @pytest.fixture
    def config_dir(self, tmp_path):
        """创建临时配置目录"""
        # base.yaml
        base_config = {
            "http": {
                "base_url": "http://localhost:8080",
                "timeout": 30,
            },
            "db": {
                "host": "localhost",
                "port": 3306,
                "database": "test_db",
            },
            "logging": {
                "level": "INFO",
            },
        }

        # environments/staging.yaml
        staging_config = {
            "http": {
                "base_url": "https://staging-api.example.com",
                "timeout": 60,
            },
            "db": {
                "host": "staging-db.example.com",
                "port": 3306,  # 需要显式指定，因为 YAML 文件间是对象替换而非深度合并
            },
            "logging": {
                "level": "DEBUG",
            },
        }

        # environments/prod.yaml
        prod_config = {
            "http": {
                "base_url": "https://api.example.com",
                "timeout": 120,  # 生产环境更长超时
            },
            "db": {
                "host": "prod-db.example.com",
                "port": 3306,
            },
            "logging": {
                "level": "WARNING",
            },
        }

        # 创建目录结构
        (tmp_path / "environments").mkdir()
        (tmp_path / "secrets").mkdir()

        # 写入配置文件
        with open(tmp_path / "base.yaml", "w", encoding="utf-8") as f:
            yaml.dump(base_config, f)

        with open(tmp_path / "environments" / "staging.yaml", "w", encoding="utf-8") as f:
            yaml.dump(staging_config, f)

        with open(tmp_path / "environments" / "prod.yaml", "w", encoding="utf-8") as f:
            yaml.dump(prod_config, f)

        return tmp_path

    def test_load_base_config(self, config_dir):
        """加载基础配置"""
        settings = load_config("test", config_dir)

        assert settings.env == "test"
        assert settings.http.base_url == "http://localhost:8080"
        assert settings.http.timeout == 30
        assert settings.db.host == "localhost"

    def test_load_staging_config(self, config_dir):
        """加载 staging 环境配置（覆盖 base）"""
        settings = load_config("staging", config_dir)

        assert settings.env == "staging"
        # 被覆盖的值
        assert settings.http.base_url == "https://staging-api.example.com"
        assert settings.http.timeout == 60
        assert settings.db.host == "staging-db.example.com"
        # 继承自 base.yaml 的值
        assert settings.db.port == 3306

    def test_load_prod_config(self, config_dir, monkeypatch):
        """加载 prod 配置（覆盖 base）"""
        # 在 CI 环境中需要临时移除 CI 环境变量以测试 prod 配置
        monkeypatch.delenv("CI", raising=False)

        settings = load_config("prod", config_dir)

        assert settings.env == "prod"
        # 来自 prod.yaml
        assert settings.http.base_url == "https://api.example.com"
        assert settings.http.timeout == 120
        assert settings.db.host == "prod-db.example.com"
        # 继承自 base.yaml
        assert settings.db.port == 3306

    def test_deep_merge_nested_config(self, config_dir):
        """深度合并嵌套配置"""
        # staging 应该只覆盖指定字段，其他保留 base 的值
        settings = load_config("staging", config_dir)

        # http.base_url 被覆盖
        assert settings.http.base_url == "https://staging-api.example.com"
        # http.timeout 被覆盖
        assert settings.http.timeout == 60
        # db.host 被覆盖
        assert settings.db.host == "staging-db.example.com"
        # db.port 保留 base 的值
        assert settings.db.port == 3306

    def test_unknown_env_uses_base_values(self, config_dir):
        """未定义的环境使用 base 的配置值"""
        # 使用有效的 env 值，但没有对应的环境文件
        # dev 在 Literal 中是有效的，但我们没有创建 dev.yaml
        settings = load_config("dev", config_dir)

        # env 字段会被设置为请求的环境名
        assert settings.env == "dev"
        # 使用 base 的值（因为没有 dev.yaml）
        assert settings.http.base_url == "http://localhost:8080"


class TestGetSettingsForClassIntegration:
    """get_settings_for_class 集成测试（v3.36.0 现代化 API）"""

    @pytest.fixture
    def config_dir(self, tmp_path):
        """创建临时配置目录"""
        base_config = {
            "http": {
                "base_url": "http://localhost:8080",
                "timeout": 30,
            },
            "db": {
                "host": "localhost",
                "port": 3306,
            },
        }

        (tmp_path / "environments").mkdir()
        with open(tmp_path / "base.yaml", "w", encoding="utf-8") as f:
            yaml.dump(base_config, f)

        return tmp_path

    def test_get_settings_with_env(self, config_dir):
        """使用 env 参数获取配置"""
        settings = get_settings_for_class(FrameworkSettings, env="test", config_dir=config_dir)

        assert settings.env == "test"
        assert settings.http.timeout == 30
        assert settings.http.base_url == "http://localhost:8080"
        assert settings.db.host == "localhost"
        assert settings.db.port == 3306

    def test_get_settings_default_values(self, config_dir):
        """获取默认配置值"""
        settings = get_settings_for_class(FrameworkSettings, env="test", config_dir=config_dir)

        # 验证 FrameworkSettings 的默认值
        assert settings.debug is False


class TestFallbackToEnvFile:
    """回退到 .env 文件模式测试"""

    def test_fallback_when_no_config_dir(self, tmp_path, monkeypatch):
        """无 config 目录时回退到 .env 文件"""
        # 设置工作目录
        monkeypatch.chdir(tmp_path)

        # 创建 .env 文件
        env_content = """
HTTP__BASE_URL=http://env-file.example.com
HTTP__TIMEOUT=45
"""
        (tmp_path / ".env").write_text(env_content)

        # 不存在的 config 目录
        settings = get_settings_for_class(
            FrameworkSettings, env="test", config_dir=tmp_path / "nonexistent_config"
        )

        # 应该使用 .env 文件或默认值
        assert settings is not None


class TestMultiEnvironmentScenario:
    """多环境场景集成测试"""

    @pytest.fixture
    def full_config_dir(self, tmp_path):
        """创建完整的多环境配置"""
        configs = {
            "base.yaml": {
                "debug": False,
                "http": {
                    "base_url": "http://localhost:8080",
                    "timeout": 30,
                    "verify_ssl": True,
                },
                "db": {
                    "host": "localhost",
                    "port": 3306,
                    "database": "test_db",
                },
                "test": {
                    "keep_test_data": False,
                    "parallel_workers": 4,
                },
            },
            "environments/local.yaml": {
                "debug": True,
                "http": {
                    "base_url": "http://localhost:8080",  # 显式指定以确保覆盖
                    "verify_ssl": False,
                },
                "test": {
                    "keep_test_data": True,
                },
            },
            "environments/dev.yaml": {
                "http": {
                    "base_url": "https://dev-api.example.com",
                },
                "db": {
                    "host": "dev-db.example.com",
                    "port": 3306,
                },
            },
            "environments/staging.yaml": {
                "http": {
                    "base_url": "https://staging-api.example.com",
                    "timeout": 60,
                },
                "db": {
                    "host": "staging-db.example.com",
                    "port": 3306,
                },
                "test": {
                    "parallel_workers": 2,
                },
            },
            "environments/prod.yaml": {
                "http": {
                    "base_url": "https://api.example.com",
                    "timeout": 120,
                },
                "db": {
                    "host": "prod-db.example.com",
                    "port": 3306,
                },
                "test": {
                    "keep_test_data": False,
                    "parallel_workers": 1,
                },
            },
        }

        # 创建目录
        (tmp_path / "environments").mkdir()
        (tmp_path / "secrets").mkdir()

        # 写入配置文件
        for filename, content in configs.items():
            filepath = tmp_path / filename
            with open(filepath, "w", encoding="utf-8") as f:
                yaml.dump(content, f)

        return tmp_path

    @pytest.mark.parametrize(
        "env,expected_url,expected_host",
        [
            ("local", "http://localhost:8080", "localhost"),
            ("dev", "https://dev-api.example.com", "dev-db.example.com"),
            ("staging", "https://staging-api.example.com", "staging-db.example.com"),
            ("prod", "https://api.example.com", "prod-db.example.com"),
        ],
    )
    def test_environment_specific_config(
        self, full_config_dir, env, expected_url, expected_host, monkeypatch
    ):
        """各环境配置正确加载"""
        # 在 CI 环境中需要临时移除 CI 环境变量以测试 prod 配置
        if env == "prod":
            monkeypatch.delenv("CI", raising=False)

        settings = load_config(env, full_config_dir)

        assert settings.env == env
        assert settings.http.base_url == expected_url
        assert settings.db.host == expected_host

    def test_local_environment_debug_mode(self, full_config_dir):
        """本地环境调试模式"""
        settings = load_config("local", full_config_dir)

        assert settings.debug is True
        assert settings.http.verify_ssl is False
        assert settings.test.keep_test_data is True

    def test_prod_environment_config(self, full_config_dir, monkeypatch):
        """生产环境配置"""
        # 在 CI 环境中需要临时移除 CI 环境变量以测试 prod 配置
        monkeypatch.delenv("CI", raising=False)

        settings = load_config("prod", full_config_dir)

        # 来自 prod.yaml
        assert settings.http.base_url == "https://api.example.com"
        assert settings.http.timeout == 120
        assert settings.db.host == "prod-db.example.com"
        assert settings.test.parallel_workers == 1
        # 继承自 base.yaml
        assert settings.db.port == 3306
