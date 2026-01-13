"""统一脱敏服务测试

v3.40.0 新增：测试 SanitizeService 的各种脱敏功能。
"""

import pytest

from df_test_framework.infrastructure.config import (
    SanitizeConfig,
    SanitizeContextConfig,
    SanitizeStrategy,
)
from df_test_framework.infrastructure.sanitize import (
    SanitizeService,
    clear_sanitize_service,
    get_sanitize_service,
    set_sanitize_service,
)


class TestSanitizeService:
    """SanitizeService 单元测试"""

    @pytest.fixture
    def default_service(self) -> SanitizeService:
        """创建默认配置的脱敏服务"""
        config = SanitizeConfig()
        return SanitizeService(config)

    @pytest.fixture
    def full_mask_service(self) -> SanitizeService:
        """创建完全脱敏策略的服务"""
        config = SanitizeConfig(default_strategy=SanitizeStrategy.FULL)
        return SanitizeService(config)

    @pytest.fixture
    def hash_service(self) -> SanitizeService:
        """创建哈希脱敏策略的服务"""
        config = SanitizeConfig(default_strategy=SanitizeStrategy.HASH)
        return SanitizeService(config)

    @pytest.fixture
    def disabled_service(self) -> SanitizeService:
        """创建禁用脱敏的服务"""
        config = SanitizeConfig(enabled=False)
        return SanitizeService(config)

    # ========== is_sensitive 测试 ==========

    def test_is_sensitive_exact_match(self, default_service: SanitizeService):
        """测试精确匹配敏感字段"""
        assert default_service.is_sensitive("password") is True
        assert default_service.is_sensitive("token") is True
        assert default_service.is_sensitive("secret") is True
        assert default_service.is_sensitive("api_key") is True

    def test_is_sensitive_case_insensitive(self, default_service: SanitizeService):
        """测试大小写不敏感"""
        assert default_service.is_sensitive("PASSWORD") is True
        assert default_service.is_sensitive("Token") is True
        assert default_service.is_sensitive("SECRET") is True

    def test_is_sensitive_regex_match(self):
        """测试正则匹配"""
        # 创建带正则模式的配置
        config = SanitizeConfig(
            sensitive_keys=[
                "password",
                r".*_secret$",  # 正则模式
                r"^auth.*",  # 以 auth 开头
            ]
        )
        service = SanitizeService(config)

        assert service.is_sensitive("app_secret") is True
        assert service.is_sensitive("client_secret") is True
        assert service.is_sensitive("authentication") is True
        assert service.is_sensitive("username") is False

    def test_is_sensitive_non_sensitive(self, default_service: SanitizeService):
        """测试非敏感字段"""
        assert default_service.is_sensitive("username") is False
        assert default_service.is_sensitive("email") is False
        assert default_service.is_sensitive("name") is False

    def test_is_sensitive_disabled(self, disabled_service: SanitizeService):
        """测试禁用时返回 False"""
        assert disabled_service.is_sensitive("password") is False

    # ========== sanitize_value 测试 ==========

    def test_sanitize_value_partial_default(self, default_service: SanitizeService):
        """测试部分脱敏（默认策略）"""
        result = default_service.sanitize_value("password", "mysecretpassword")
        # 保留前4后4，中间用*号
        assert result == "myse****word"

    def test_sanitize_value_partial_short_value(self, default_service: SanitizeService):
        """测试短值完全脱敏"""
        result = default_service.sanitize_value("password", "abc")
        assert result == "****"

    def test_sanitize_value_full_mask(self, full_mask_service: SanitizeService):
        """测试完全脱敏策略"""
        result = full_mask_service.sanitize_value("password", "mysecretpassword")
        assert result == "******"

    def test_sanitize_value_hash(self, hash_service: SanitizeService):
        """测试哈希脱敏策略"""
        result = hash_service.sanitize_value("password", "mysecretpassword")
        assert result.startswith("sha256:")
        assert len(result) == len("sha256:") + 16

    def test_sanitize_value_non_sensitive(self, default_service: SanitizeService):
        """测试非敏感字段不脱敏"""
        result = default_service.sanitize_value("username", "alice")
        assert result == "alice"

    def test_sanitize_value_disabled(self, disabled_service: SanitizeService):
        """测试禁用时不脱敏"""
        result = disabled_service.sanitize_value("password", "secret123")
        assert result == "secret123"

    def test_sanitize_value_empty_string(self, default_service: SanitizeService):
        """测试空字符串"""
        result = default_service.sanitize_value("password", "")
        assert result == ""

    def test_sanitize_value_non_string(self, default_service: SanitizeService):
        """测试非字符串值"""
        # 非字符串值直接返回
        result = default_service.sanitize_value("password", 12345)  # type: ignore
        assert result == 12345

    # ========== sanitize_dict 测试 ==========

    def test_sanitize_dict_simple(self, default_service: SanitizeService):
        """测试简单字典脱敏"""
        # 使用足够长的密码（>8字符）以确保有足够的中间部分
        data = {"username": "alice", "password": "mysecretpassword"}
        result = default_service.sanitize_dict(data)
        assert result["username"] == "alice"
        # mysecretpassword (16 chars) -> myse + **** + word
        assert result["password"] == "myse****word"

    def test_sanitize_dict_nested(self, default_service: SanitizeService):
        """测试嵌套字典脱敏"""
        data = {
            "user": {
                "name": "alice",
                "credentials": {
                    "password": "mysecretpassword",  # 16 chars
                    "token": "abc123def456xyz",  # 15 chars
                },
            }
        }
        result = default_service.sanitize_dict(data)
        assert result["user"]["name"] == "alice"
        # mysecretpassword (16 chars) -> myse + **** + word
        assert result["user"]["credentials"]["password"] == "myse****word"
        # abc123def456xyz (15 chars) -> abc1 + **** + 6xyz （保留后4个字符）
        assert result["user"]["credentials"]["token"] == "abc1****6xyz"

    def test_sanitize_dict_with_list(self, default_service: SanitizeService):
        """测试包含列表的字典脱敏"""
        data = {
            "users": [
                {"name": "alice", "password": "secret1"},
                {"name": "bob", "password": "secret2"},
            ]
        }
        result = default_service.sanitize_dict(data)
        assert result["users"][0]["name"] == "alice"
        assert result["users"][0]["password"] == "****"  # 短值完全脱敏
        assert result["users"][1]["password"] == "****"

    def test_sanitize_dict_none(self, default_service: SanitizeService):
        """测试 None 值"""
        result = default_service.sanitize_dict(None)
        assert result is None

    def test_sanitize_dict_context_disabled(self):
        """测试特定上下文禁用脱敏"""
        config = SanitizeConfig(
            console=SanitizeContextConfig(enabled=False),
        )
        service = SanitizeService(config)

        data = {"password": "secret123"}
        result = service.sanitize_dict(data, context="console")
        assert result["password"] == "secret123"  # console 上下文禁用，不脱敏

    # ========== sanitize_message 测试 ==========

    def test_sanitize_message_password_pattern(self, default_service: SanitizeService):
        """测试消息中的密码模式脱敏"""
        message = 'Login with password="secret123"'
        result = default_service.sanitize_message(message)
        assert "secret123" not in result
        assert "******" in result

    def test_sanitize_message_token_pattern(self, default_service: SanitizeService):
        """测试消息中的 token 模式脱敏"""
        message = "Using token=abc123xyz"
        result = default_service.sanitize_message(message)
        assert "abc123xyz" not in result

    def test_sanitize_message_no_sensitive(self, default_service: SanitizeService):
        """测试无敏感内容的消息"""
        message = "User alice logged in successfully"
        result = default_service.sanitize_message(message)
        assert result == message

    def test_sanitize_message_logging_disabled(self):
        """测试 logging 上下文禁用"""
        config = SanitizeConfig(
            logging=SanitizeContextConfig(enabled=False),
        )
        service = SanitizeService(config)

        message = 'Login with password="secret123"'
        result = service.sanitize_message(message)
        assert result == message  # logging 禁用，不脱敏

    # ========== is_context_enabled 测试 ==========

    def test_is_context_enabled_default(self, default_service: SanitizeService):
        """测试默认上下文启用"""
        assert default_service.is_context_enabled("logging") is True
        assert default_service.is_context_enabled("console") is True
        assert default_service.is_context_enabled("allure") is True

    def test_is_context_enabled_disabled_service(self, disabled_service: SanitizeService):
        """测试禁用服务时上下文也禁用"""
        assert disabled_service.is_context_enabled("logging") is False
        assert disabled_service.is_context_enabled("console") is False
        assert disabled_service.is_context_enabled("allure") is False

    def test_is_context_enabled_partial(self):
        """测试部分上下文禁用"""
        config = SanitizeConfig(
            console=SanitizeContextConfig(enabled=False),
            allure=SanitizeContextConfig(enabled=False),
        )
        service = SanitizeService(config)

        assert service.is_context_enabled("logging") is True
        assert service.is_context_enabled("console") is False
        assert service.is_context_enabled("allure") is False

    def test_is_context_enabled_unknown_context(self, default_service: SanitizeService):
        """测试未知上下文默认启用"""
        assert default_service.is_context_enabled("unknown") is True


class TestSanitizeServiceSingleton:
    """脱敏服务单例测试"""

    def setup_method(self):
        """每个测试前清理缓存"""
        clear_sanitize_service()

    def teardown_method(self):
        """每个测试后清理缓存"""
        clear_sanitize_service()

    def test_get_sanitize_service_default(self):
        """测试获取默认服务"""
        service = get_sanitize_service()
        assert service is not None
        assert isinstance(service, SanitizeService)

    def test_get_sanitize_service_singleton(self):
        """测试单例模式"""
        service1 = get_sanitize_service()
        service2 = get_sanitize_service()
        assert service1 is service2

    def test_set_sanitize_service(self):
        """测试设置自定义服务"""
        config = SanitizeConfig(enabled=False)
        custom_service = SanitizeService(config)

        set_sanitize_service(custom_service)

        service = get_sanitize_service()
        assert service is custom_service
        assert service.config.enabled is False

    def test_clear_sanitize_service(self):
        """测试清除缓存

        v3.40.1: 脱敏服务缓存在 settings 对象上，
        需要通过 clear_settings_cache() 清除。
        """
        from df_test_framework.infrastructure.config import clear_settings_cache

        service1 = get_sanitize_service()
        clear_settings_cache()  # 清除 settings 缓存，service 随之清除
        service2 = get_sanitize_service()

        # 清除 settings 后应该创建新实例
        assert service1 is not service2


class TestSanitizeConfigCustomization:
    """脱敏配置自定义测试"""

    def test_custom_sensitive_keys(self):
        """测试自定义敏感字段"""
        config = SanitizeConfig(
            sensitive_keys=["my_secret", "custom_token"],
        )
        service = SanitizeService(config)

        assert service.is_sensitive("my_secret") is True
        assert service.is_sensitive("custom_token") is True
        assert service.is_sensitive("password") is False  # 不在列表中

    def test_custom_mask_settings(self):
        """测试自定义脱敏参数"""
        config = SanitizeConfig(
            keep_prefix=2,
            keep_suffix=2,
            mask_char="#",
        )
        service = SanitizeService(config)

        result = service.sanitize_value("password", "mysecretpassword")
        assert result == "my####rd"

    def test_custom_mask_value(self):
        """测试自定义完全脱敏值"""
        config = SanitizeConfig(
            default_strategy=SanitizeStrategy.FULL,
            mask_value="[REDACTED]",
        )
        service = SanitizeService(config)

        result = service.sanitize_value("password", "secret")
        assert result == "[REDACTED]"
