"""测试 DataGenerator - 数据生成器

测试覆盖:
- 基础数据生成（random_string, random_int, random_float, random_decimal, random_bool）
- 个人信息生成（name, email, phone, address, company）
- 日期时间生成（date, datetime_str, future_date, past_date, timestamp）
- 业务数据生成（order_id, order_no, user_id, payment_no, chinese_phone）
- 金融数据生成（amount, decimal, currency_code）
- 类方法（test_id）
"""

import string
from datetime import datetime
from decimal import Decimal

from df_test_framework.testing.data.generators import DataGenerator


class TestDataGeneratorBasic:
    """测试基础数据生成"""

    def test_init_default_locale(self):
        """测试默认本地化设置"""
        gen = DataGenerator()
        assert gen.faker is not None

    def test_init_custom_locale(self):
        """测试自定义本地化设置"""
        gen = DataGenerator(locale="en_US")
        assert gen.faker is not None

    def test_random_string_default_length(self):
        """测试随机字符串默认长度"""
        gen = DataGenerator()
        result = gen.random_string()
        assert len(result) == 10
        assert all(c in string.ascii_letters + string.digits for c in result)

    def test_random_string_custom_length(self):
        """测试随机字符串自定义长度"""
        gen = DataGenerator()
        result = gen.random_string(length=20)
        assert len(result) == 20

    def test_random_string_custom_chars(self):
        """测试随机字符串自定义字符集"""
        gen = DataGenerator()
        result = gen.random_string(length=10, chars="ABC123")
        assert len(result) == 10
        assert all(c in "ABC123" for c in result)

    def test_random_int_default_range(self):
        """测试随机整数默认范围"""
        gen = DataGenerator()
        for _ in range(100):
            result = gen.random_int()
            assert 0 <= result <= 100

    def test_random_int_custom_range(self):
        """测试随机整数自定义范围"""
        gen = DataGenerator()
        for _ in range(100):
            result = gen.random_int(min_value=10, max_value=20)
            assert 10 <= result <= 20

    def test_random_float_default(self):
        """测试随机浮点数默认值"""
        gen = DataGenerator()
        result = gen.random_float()
        assert 0.0 <= result <= 100.0
        # 验证精度
        str_result = str(result)
        if "." in str_result:
            decimals = len(str_result.split(".")[1])
            assert decimals <= 2

    def test_random_float_custom_decimals(self):
        """测试随机浮点数自定义精度"""
        gen = DataGenerator()
        result = gen.random_float(decimals=4)
        str_result = str(result)
        if "." in str_result:
            decimals = len(str_result.split(".")[1])
            assert decimals <= 4

    def test_random_decimal_type(self):
        """测试随机 Decimal 类型"""
        gen = DataGenerator()
        result = gen.random_decimal()
        assert isinstance(result, Decimal)

    def test_random_decimal_range(self):
        """测试随机 Decimal 范围"""
        gen = DataGenerator()
        result = gen.random_decimal(min_value=10.0, max_value=20.0)
        assert Decimal("10.0") <= result <= Decimal("20.0")

    def test_random_bool(self):
        """测试随机布尔值"""
        gen = DataGenerator()
        results = [gen.random_bool() for _ in range(100)]
        # 确保有 True 和 False
        assert True in results
        assert False in results

    def test_random_choice(self):
        """测试随机选择"""
        gen = DataGenerator()
        choices = ["a", "b", "c"]
        for _ in range(100):
            result = gen.random_choice(choices)
            assert result in choices


class TestDataGeneratorPersonal:
    """测试个人信息生成"""

    def test_name(self):
        """测试姓名生成"""
        gen = DataGenerator()
        result = gen.name()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_email(self):
        """测试邮箱生成"""
        gen = DataGenerator()
        result = gen.email()
        assert isinstance(result, str)
        assert "@" in result

    def test_phone(self):
        """测试手机号生成"""
        gen = DataGenerator()
        result = gen.phone()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_address(self):
        """测试地址生成"""
        gen = DataGenerator()
        result = gen.address()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_company(self):
        """测试公司名生成"""
        gen = DataGenerator()
        result = gen.company()
        assert isinstance(result, str)
        assert len(result) > 0


class TestDataGeneratorDateTime:
    """测试日期时间生成"""

    def test_date(self):
        """测试日期生成"""
        gen = DataGenerator()
        result = gen.date()
        assert isinstance(result, datetime)

    def test_datetime_str_default_format(self):
        """测试日期时间字符串默认格式"""
        gen = DataGenerator()
        result = gen.datetime_str()
        # 验证格式 YYYY-MM-DD HH:MM:SS
        assert len(result) == 19
        datetime.strptime(result, "%Y-%m-%d %H:%M:%S")

    def test_datetime_str_custom_format(self):
        """测试日期时间字符串自定义格式"""
        gen = DataGenerator()
        result = gen.datetime_str("%Y%m%d")
        assert len(result) == 8
        datetime.strptime(result, "%Y%m%d")

    def test_future_date(self):
        """测试未来日期生成"""
        gen = DataGenerator()
        now = datetime.now()
        result = gen.future_date(days=30)
        assert result > now

    def test_past_date(self):
        """测试过去日期生成"""
        gen = DataGenerator()
        now = datetime.now()
        result = gen.past_date(days=30)
        assert result < now

    def test_timestamp_seconds(self):
        """测试秒级时间戳"""
        gen = DataGenerator()
        result = gen.timestamp()
        assert isinstance(result, int)
        assert len(str(result)) == 10

    def test_timestamp_milliseconds(self):
        """测试毫秒级时间戳"""
        gen = DataGenerator()
        result = gen.timestamp(milliseconds=True)
        assert isinstance(result, int)
        assert len(str(result)) == 13


class TestDataGeneratorBusiness:
    """测试业务数据生成"""

    def test_order_id_default_prefix(self):
        """测试订单号默认前缀"""
        gen = DataGenerator()
        result = gen.order_id()
        assert result.startswith("ORD")
        assert len(result) > 10

    def test_order_id_custom_prefix(self):
        """测试订单号自定义前缀"""
        gen = DataGenerator()
        result = gen.order_id(prefix="TEST_ORD")
        assert result.startswith("TEST_ORD")

    def test_order_no(self):
        """测试订单号别名方法"""
        gen = DataGenerator()
        result = gen.order_no()
        assert result.startswith("TEST_ORD_")

    def test_user_id(self):
        """测试用户ID生成"""
        gen = DataGenerator()
        result = gen.user_id()
        assert result.startswith("TEST_USER_")

    def test_payment_no(self):
        """测试支付订单号生成"""
        gen = DataGenerator()
        result = gen.payment_no()
        assert result.startswith("PAY_")

    def test_transaction_id(self):
        """测试交易ID生成"""
        gen = DataGenerator()
        result = gen.transaction_id()
        assert result.startswith("TXN_")

    def test_card_number_default_length(self):
        """测试卡号默认长度"""
        gen = DataGenerator()
        result = gen.card_number()
        assert len(result) == 16
        assert result.isdigit()

    def test_card_number_custom_length(self):
        """测试卡号自定义长度"""
        gen = DataGenerator()
        result = gen.card_number(length=19)
        assert len(result) == 19

    def test_uuid(self):
        """测试UUID生成"""
        gen = DataGenerator()
        result = gen.uuid()
        assert isinstance(result, str)
        assert len(result) == 36
        assert result.count("-") == 4

    def test_chinese_phone(self):
        """测试中国手机号生成"""
        gen = DataGenerator()
        result = gen.chinese_phone()
        assert len(result) == 11
        assert result.isdigit()
        # 验证前缀是有效的运营商号段
        assert result[0] == "1"
        assert result[1] in "3456789"


class TestDataGeneratorFinancial:
    """测试金融数据生成"""

    def test_amount_default(self):
        """测试金额默认范围"""
        gen = DataGenerator()
        result = gen.amount()
        assert isinstance(result, Decimal)
        assert Decimal("1.0") <= result <= Decimal("1000.0")

    def test_amount_custom_range(self):
        """测试金额自定义范围"""
        gen = DataGenerator()
        result = gen.amount(min_value=10.0, max_value=100.0)
        assert Decimal("10.0") <= result <= Decimal("100.0")

    def test_decimal_alias(self):
        """测试 decimal 别名方法"""
        gen = DataGenerator()
        result = gen.decimal(min_value=0.0, max_value=50.0)
        assert isinstance(result, Decimal)
        assert Decimal("0.0") <= result <= Decimal("50.0")

    def test_currency_code(self):
        """测试货币代码生成"""
        gen = DataGenerator()
        result = gen.currency_code()
        assert isinstance(result, str)
        assert len(result) == 3  # ISO 4217


class TestDataGeneratorNetwork:
    """测试网络数据生成"""

    def test_url(self):
        """测试URL生成"""
        gen = DataGenerator()
        result = gen.url()
        assert isinstance(result, str)
        assert result.startswith(("http://", "https://"))

    def test_ipv4(self):
        """测试IPv4地址生成"""
        gen = DataGenerator()
        result = gen.ipv4()
        parts = result.split(".")
        assert len(parts) == 4
        for part in parts:
            assert 0 <= int(part) <= 255

    def test_user_agent(self):
        """测试User-Agent生成"""
        gen = DataGenerator()
        result = gen.user_agent()
        assert isinstance(result, str)
        assert len(result) > 0


class TestDataGeneratorClassMethod:
    """测试类方法"""

    def test_test_id_default_prefix(self):
        """测试 test_id 默认前缀"""
        result = DataGenerator.test_id()
        assert result.startswith("TEST")

    def test_test_id_custom_prefix(self):
        """测试 test_id 自定义前缀"""
        result = DataGenerator.test_id("ORDER")
        assert result.startswith("ORDER")

    def test_test_id_uniqueness(self):
        """测试 test_id 唯一性"""
        ids = [DataGenerator.test_id("TEST") for _ in range(100)]
        # 所有ID应该是唯一的
        assert len(set(ids)) == 100
