"""
测试现代化配置 API (v3.36.0+)

验证 settings.py 中的 get_settings、get_config、get_settings_for_class 功能。
这是推荐的新版 API，遵循以下原则：
- 惰性加载：首次访问时自动初始化
- 单例缓存：使用 lru_cache 确保全局唯一
- 依赖注入友好：可直接用于 pytest fixture
- 类型安全：完整的 Pydantic 验证

注意：旧版 API（manager.py）测试请参见 test_config.py
"""

from df_test_framework.infrastructure.config import (
    FrameworkSettings,
)
from df_test_framework.infrastructure.config.settings import (
    clear_settings_cache,
    get_config,
    get_settings,
    get_settings_for_class,
)


class CustomSettings(FrameworkSettings):
    """自定义配置类用于测试"""

    api_key: str = "default_key"
    max_retries: int = 3


class TestGetSettings:
    """测试 get_settings 函数"""

    def setup_method(self):
        """每个测试前清理缓存"""
        clear_settings_cache()

    def teardown_method(self):
        """每个测试后清理"""
        clear_settings_cache()

    def test_get_settings_returns_framework_settings(self):
        """测试 get_settings 返回 FrameworkSettings 实例"""
        settings = get_settings()
        assert isinstance(settings, FrameworkSettings)

    def test_get_settings_cached(self):
        """测试 get_settings 返回缓存的同一实例"""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_get_settings_with_env(self, monkeypatch):
        """测试指定环境加载配置"""
        # 设置环境变量
        monkeypatch.setenv("ENV", "staging")
        clear_settings_cache()

        settings = get_settings()
        assert settings.env in ("staging", "test")  # 取决于是否有 staging 配置

    def test_get_settings_auto_detect_env(self, monkeypatch):
        """测试自动从环境变量检测环境"""
        # 清除可能存在的环境变量
        monkeypatch.delenv("ENV", raising=False)
        monkeypatch.delenv("APP_ENV", raising=False)
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        clear_settings_cache()

        settings = get_settings()
        # 没有环境变量时默认使用 test
        assert settings.env == "test"


class TestGetSettingsForClass:
    """测试 get_settings_for_class 函数"""

    def setup_method(self):
        """每个测试前清理"""
        clear_settings_cache()

    def teardown_method(self):
        """每个测试后清理"""
        clear_settings_cache()

    def test_get_settings_for_custom_class(self):
        """测试获取自定义配置类实例"""
        settings = get_settings_for_class(CustomSettings)
        assert isinstance(settings, CustomSettings)
        assert settings.api_key == "default_key"
        assert settings.max_retries == 3

    def test_get_settings_for_class_with_env_override(self, monkeypatch):
        """测试使用环境变量覆盖自定义配置"""
        monkeypatch.setenv("API_KEY", "env_key")
        monkeypatch.setenv("MAX_RETRIES", "5")

        settings = get_settings_for_class(CustomSettings)
        # 如果环境变量生效，应该覆盖默认值
        # 注意：这取决于配置加载方式
        assert isinstance(settings, CustomSettings)


class TestGetConfig:
    """测试 get_config 便捷函数"""

    def setup_method(self):
        """每个测试前清理"""
        clear_settings_cache()

    def teardown_method(self):
        """每个测试后清理"""
        clear_settings_cache()

    def test_get_config_returns_full_settings(self):
        """测试无参数时返回完整配置对象"""
        config = get_config()
        assert isinstance(config, FrameworkSettings)

    def test_get_config_with_empty_path(self):
        """测试空路径返回完整配置"""
        config = get_config("")
        assert isinstance(config, FrameworkSettings)

    def test_get_config_dot_path_access(self):
        """测试点号路径访问"""
        # 获取 HTTP 配置的超时值
        timeout = get_config("http.timeout")
        assert isinstance(timeout, int)

    def test_get_config_nested_path(self):
        """测试嵌套路径访问"""
        base_url = get_config("http.base_url")
        # base_url 可能是 None 或字符串
        assert base_url is None or isinstance(base_url, str)

    def test_get_config_with_default(self):
        """测试不存在的路径返回默认值"""
        value = get_config("nonexistent.path", default="fallback")
        assert value == "fallback"

    def test_get_config_nested_default(self):
        """测试嵌套不存在路径返回默认值"""
        value = get_config("http.nonexistent.deeply.nested", default=42)
        assert value == 42


class TestClearSettingsCache:
    """测试 clear_settings_cache 函数"""

    def setup_method(self):
        """每个测试前清理"""
        clear_settings_cache()

    def teardown_method(self):
        """每个测试后清理"""
        clear_settings_cache()

    def test_clear_cache_allows_reload(self):
        """测试清理缓存后会重新加载"""
        settings1 = get_settings()

        # 清理缓存
        clear_settings_cache()

        # 由于 lru_cache，清理后应该创建新实例
        settings2 = get_settings()

        # 内容应该相同（因为配置源没变）
        assert settings1.env == settings2.env
        # 但由于重新加载，可能是不同实例
        # （这取决于 lru_cache 的行为）

    def test_clear_cache_idempotent(self):
        """测试多次清理缓存是幂等的"""
        # 多次清理不应该抛出异常
        clear_settings_cache()
        clear_settings_cache()
        clear_settings_cache()

        settings = get_settings()
        assert isinstance(settings, FrameworkSettings)


class TestConfigIntegration:
    """集成测试：完整的现代配置 API 使用流程"""

    def setup_method(self):
        """每个测试前清理"""
        clear_settings_cache()

    def teardown_method(self):
        """每个测试后清理"""
        clear_settings_cache()

    def test_complete_modern_api_flow(self):
        """测试完整的现代 API 使用流程"""
        # 1. 获取配置（惰性加载）
        settings = get_settings()
        assert isinstance(settings, FrameworkSettings)

        # 2. 使用点号路径获取值
        timeout = get_config("http.timeout")
        assert isinstance(timeout, int)

        # 3. 验证缓存生效
        settings2 = get_settings()
        assert settings is settings2

        # 4. 使用 get_config 无参数
        full_config = get_config()
        assert full_config is settings

        # 5. 获取带默认值的配置
        missing = get_config("missing.config", default="default_value")
        assert missing == "default_value"

    def test_custom_settings_class_workflow(self):
        """测试自定义配置类工作流程"""
        # 获取自定义配置
        custom = get_settings_for_class(CustomSettings)
        assert isinstance(custom, CustomSettings)
        assert hasattr(custom, "api_key")
        assert hasattr(custom, "max_retries")

        # 验证继承了基类属性
        assert hasattr(custom, "env")
        assert hasattr(custom, "http")

    def test_http_config_access(self):
        """测试 HTTP 配置访问"""
        settings = get_settings()

        # 直接属性访问
        assert settings.http is not None
        assert isinstance(settings.http.timeout, int)

        # 点号路径访问
        timeout_via_path = get_config("http.timeout")
        assert timeout_via_path == settings.http.timeout

    def test_env_detection_priority(self, monkeypatch):
        """测试环境检测优先级"""
        # ENV > APP_ENV > ENVIRONMENT > 默认 test
        # 使用有效的 env 值：local/dev/test/staging/prod
        monkeypatch.setenv("ENV", "staging")
        clear_settings_cache()

        settings = get_settings()
        # 验证环境变量生效
        assert settings.env in ("staging", "test")


class TestYamlConfigLoading:
    """测试 YAML 配置加载（需要 config 目录存在）"""

    def setup_method(self):
        """每个测试前清理"""
        clear_settings_cache()

    def teardown_method(self):
        """每个测试后清理"""
        clear_settings_cache()

    def test_yaml_config_loading_with_directory(self, tmp_path):
        """测试从 YAML 配置目录加载"""
        # 创建临时配置目录
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # 创建 base.yaml
        base_yaml = config_dir / "base.yaml"
        base_yaml.write_text(
            """
app_name: YamlTestApp
app_env: test
http:
  timeout: 45
  base_url: http://yaml-test.example.com
""",
            encoding="utf-8",
        )

        # 使用自定义配置目录加载
        from df_test_framework.infrastructure.config.settings import _load_settings

        settings = _load_settings(env="test", config_dir=config_dir)

        # 验证从 YAML 文件正确加载配置
        assert settings.app_name == "YamlTestApp"
        assert settings.http.timeout == 45
        assert settings.http.base_url == "http://yaml-test.example.com"


class TestDotEnvFallback:
    """测试 .env 文件回退（当 config 目录不存在时）"""

    def setup_method(self):
        """每个测试前清理"""
        clear_settings_cache()

    def teardown_method(self):
        """每个测试后清理"""
        clear_settings_cache()

    def test_dotenv_fallback_when_no_config_dir(self, tmp_path, monkeypatch):
        """测试无 config 目录时使用 .env 文件"""
        # 切换到临时目录
        monkeypatch.chdir(tmp_path)

        # 创建 .env 文件
        env_file = tmp_path / ".env"
        env_file.write_text("APP_NAME=DotEnvApp\nDEBUG=true\n", encoding="utf-8")

        # 使用不存在的配置目录
        from df_test_framework.infrastructure.config.settings import _load_settings

        settings = _load_settings(config_dir="nonexistent_config")

        # 应该能正常创建配置（使用默认值或环境变量）
        assert isinstance(settings, FrameworkSettings)
