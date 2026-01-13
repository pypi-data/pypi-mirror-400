"""load_config 函数单元测试 (v3.35.4)

测试 YAML 分层配置加载功能:
- base.yaml 加载
- environments/{env}.yaml 加载
- 环境变量深度合并（nested_model_default_partial_update）
- secrets 加载
- 环境变量覆盖

v3.35.4 变更:
- 使用内置 YamlConfigSettingsSource
- 移除 _extends 继承语法
- 移除 ConfigLoader 类（只保留 load_config 函数）
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from df_test_framework.infrastructure.config.loader import load_config

if TYPE_CHECKING:
    pass


@pytest.fixture(autouse=True)
def clean_env_vars():
    """清理测试可能设置的环境变量"""
    env_vars_to_clean = ["HTTP__BASE_URL", "SIGNATURE__SECRET", "DB__PASSWORD"]
    original_values = {k: os.environ.get(k) for k in env_vars_to_clean}

    yield

    for key, original in original_values.items():
        if original is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    """创建测试配置目录结构"""
    config_path = tmp_path / "config"
    config_path.mkdir()
    (config_path / "environments").mkdir()
    (config_path / "secrets").mkdir()
    return config_path


@pytest.fixture
def base_yaml(config_dir: Path) -> Path:
    """创建 base.yaml"""
    content = """
http:
  timeout: 30
  max_retries: 3
  verify_ssl: true

logging:
  level: INFO
  format: text

observability:
  enabled: true
  allure_recording: true
  debug_output: false
"""
    file_path = config_dir / "base.yaml"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def test_env_yaml(config_dir: Path) -> Path:
    """创建 environments/test.yaml（无 _extends，由 ConfigLoader 自动合并 base.yaml）"""
    content = """
env: test
debug: false

http:
  base_url: "http://test-api.example.com"
  timeout: 60

logging:
  level: DEBUG
"""
    file_path = config_dir / "environments" / "test.yaml"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def staging_env_yaml(config_dir: Path) -> Path:
    """创建 environments/staging.yaml"""
    content = """
env: staging
debug: false

http:
  base_url: "https://staging-api.example.com"
"""
    file_path = config_dir / "environments" / "staging.yaml"
    file_path.write_text(content, encoding="utf-8")
    return file_path


class TestLoadConfig:
    """load_config 测试"""

    def test_load_base_yaml_only(self, config_dir: Path, base_yaml: Path) -> None:
        """测试只加载 base.yaml（无环境配置）"""
        settings = load_config("dev", config_dir)

        assert settings.http.timeout == 30
        assert settings.http.max_retries == 3
        assert settings.logging.level == "INFO"
        assert settings.observability.enabled is True

    def test_load_with_environment(
        self, config_dir: Path, base_yaml: Path, test_env_yaml: Path
    ) -> None:
        """测试加载环境配置（自动合并 base.yaml + env.yaml）"""
        settings = load_config("test", config_dir)

        # 环境配置覆盖
        assert settings.env == "test"
        assert settings.debug is False
        assert settings.http.base_url == "http://test-api.example.com"
        assert settings.http.timeout == 60

        # 继承自 base.yaml（YamlConfigSettingsSource 自动合并）
        assert settings.http.max_retries == 3
        assert settings.observability.enabled is True

    def test_deep_merge(self, config_dir: Path) -> None:
        """测试深度合并（YamlConfigSettingsSource 内置功能）"""
        base_content = """
http:
  timeout: 30
  max_retries: 3
  verify_ssl: true

logging:
  level: INFO
  format: text
"""
        (config_dir / "base.yaml").write_text(base_content, encoding="utf-8")

        env_content = """
env: test
http:
  base_url: "http://example.com"
  timeout: 60

logging:
  level: DEBUG
"""
        (config_dir / "environments" / "test.yaml").write_text(env_content, encoding="utf-8")

        settings = load_config("test", config_dir)

        # http 配置应该合并
        assert settings.http.timeout == 60  # 覆盖
        assert settings.http.max_retries == 3  # 保留
        assert settings.http.base_url == "http://example.com"  # 新增
        assert settings.http.verify_ssl is True  # 保留

        # logging 配置应该合并
        assert settings.logging.level == "DEBUG"  # 覆盖
        assert settings.logging.format == "text"  # 保留

    def test_load_with_yml_extension(self, config_dir: Path, base_yaml: Path) -> None:
        """测试 .yml 扩展名"""
        env_content = """
env: dev
debug: true
"""
        (config_dir / "environments" / "dev.yml").write_text(env_content, encoding="utf-8")

        settings = load_config("dev", config_dir)

        assert settings.env == "dev"
        assert settings.debug is True

    def test_load_secrets(
        self, config_dir: Path, base_yaml: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """测试 secrets 加载"""
        secrets_content = """
HTTP__BASE_URL=http://secret-api.example.com
"""
        (config_dir / "secrets" / ".env.local").write_text(secrets_content, encoding="utf-8")

        monkeypatch.delenv("HTTP__BASE_URL", raising=False)

        settings = load_config("test", config_dir)

        assert settings.http.base_url == "http://secret-api.example.com"

        (config_dir / "secrets" / ".env.local").unlink(missing_ok=True)

    def test_env_from_environment_variable(
        self,
        config_dir: Path,
        base_yaml: Path,
        test_env_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """测试从 ENV 环境变量读取环境名"""
        monkeypatch.setenv("ENV", "test")

        settings = load_config(config_dir=config_dir)

        assert settings.env == "test"

    def test_default_env_is_test(
        self,
        config_dir: Path,
        base_yaml: Path,
        test_env_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """测试默认环境为 test"""
        monkeypatch.delenv("ENV", raising=False)

        settings = load_config(config_dir=config_dir)

        assert settings.env == "test"

    def test_load_nonexistent_base_yaml(self, tmp_path: Path) -> None:
        """测试 base.yaml 不存在的情况"""
        empty_config_dir = tmp_path / "empty_config"
        empty_config_dir.mkdir()

        settings = load_config("test", empty_config_dir)

        assert settings.env == "test"
        assert settings.http.timeout == 30


class TestLoadConfigFunction:
    """load_config 便捷函数测试"""

    def test_load_config_basic(
        self, config_dir: Path, base_yaml: Path, test_env_yaml: Path
    ) -> None:
        """测试基本使用"""
        settings = load_config("test", config_dir)

        assert settings.env == "test"
        assert settings.http.base_url == "http://test-api.example.com"

    def test_load_config_with_default_dir(
        self, config_dir: Path, base_yaml: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """测试使用默认配置目录"""
        monkeypatch.chdir(config_dir.parent)

        settings = load_config("test", "config")

        assert settings.env == "test"


class TestEnvVarsDeepMerge:
    """环境变量深度合并测试

    验证环境变量与 YAML 配置的深度合并功能（nested_model_default_partial_update）。
    """

    def test_env_var_deep_merge_with_yaml(
        self, config_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """测试环境变量与 YAML 配置的深度合并"""
        base_content = """
http:
  timeout: 30

signature:
  enabled: true
  algorithm: md5
  header: X-Sign
  include_paths:
    - "/api/**"
"""
        (config_dir / "base.yaml").write_text(base_content, encoding="utf-8")

        monkeypatch.setenv("SIGNATURE__SECRET", "my_secret_key")

        settings = load_config("test", config_dir)

        assert settings.signature.enabled is True
        assert settings.signature.algorithm.value == "md5"
        assert settings.signature.header == "X-Sign"
        secret = settings.signature.secret
        secret_value = secret.get_secret_value() if hasattr(secret, "get_secret_value") else secret
        assert secret_value == "my_secret_key"
        assert settings.signature.include_paths == ["/api/**"]

    def test_secrets_file_deep_merge_with_yaml(
        self, config_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """测试 secrets/.env.local 与 YAML 配置的深度合并"""
        base_content = """
http:
  timeout: 30
  max_retries: 3

db:
  host: localhost
  port: 3306
  pool_size: 10
"""
        (config_dir / "base.yaml").write_text(base_content, encoding="utf-8")

        secrets_content = """
DB__PASSWORD=secret_password
DB__USER=admin
"""
        (config_dir / "secrets" / ".env.local").write_text(secrets_content, encoding="utf-8")

        monkeypatch.delenv("DB__PASSWORD", raising=False)
        monkeypatch.delenv("DB__USER", raising=False)
        monkeypatch.delenv("DB__HOST", raising=False)

        settings = load_config("test", config_dir)

        assert settings.db.host == "localhost"
        assert settings.db.port == 3306
        assert settings.db.pool_size == 10
        pwd = settings.db.password
        pwd_value = pwd.get_secret_value() if hasattr(pwd, "get_secret_value") else pwd
        assert pwd_value == "secret_password"
        assert settings.db.user == "admin"

    def test_multiple_nested_configs_merge(
        self, config_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """测试多个嵌套配置同时合并"""
        base_content = """
http:
  timeout: 30

signature:
  enabled: true
  algorithm: md5

bearer_token:
  enabled: true
  source: login
  login_url: /auth/login
"""
        (config_dir / "base.yaml").write_text(base_content, encoding="utf-8")

        monkeypatch.setenv("SIGNATURE__SECRET", "sig_secret")
        monkeypatch.setenv("BEARER_TOKEN__TOKEN", "bearer_token_value")
        monkeypatch.setenv("HTTP__BASE_URL", "http://api.example.com")

        settings = load_config("test", config_dir)

        assert settings.http.timeout == 30
        assert settings.http.base_url == "http://api.example.com"

        assert settings.signature.enabled is True
        assert settings.signature.algorithm.value == "md5"
        sig_secret = settings.signature.secret
        sig_secret_value = (
            sig_secret.get_secret_value() if hasattr(sig_secret, "get_secret_value") else sig_secret
        )
        assert sig_secret_value == "sig_secret"

        assert settings.bearer_token.enabled is True
        assert settings.bearer_token.source.value == "login"
        assert settings.bearer_token.login_url == "/auth/login"

    def test_env_vars_priority_over_secrets(
        self, config_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """测试环境变量优先级高于 secrets 文件"""
        base_content = """
db:
  host: localhost
"""
        (config_dir / "base.yaml").write_text(base_content, encoding="utf-8")

        secrets_content = """
DB__PASSWORD=secrets_password
"""
        (config_dir / "secrets" / ".env.local").write_text(secrets_content, encoding="utf-8")

        monkeypatch.setenv("DB__PASSWORD", "env_password")

        settings = load_config("test", config_dir)

        pwd = settings.db.password
        pwd_value = pwd.get_secret_value() if hasattr(pwd, "get_secret_value") else pwd
        assert pwd_value == "env_password"


__all__ = [
    "TestLoadConfig",
    "TestLoadConfigFunction",
    "TestEnvVarsDeepMerge",
]
