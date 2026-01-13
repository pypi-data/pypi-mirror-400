"""测试 core.types - 核心类型定义

测试覆盖:
- 枚举类型（Environment, LogLevel, HttpMethod, HttpStatus 等）
- Pydantic 序列化类型（DecimalAsFloat, DecimalAsCurrency）
- 类型别名（JsonDict, Headers, QueryParams）
"""

from decimal import Decimal

import pytest
from pydantic import BaseModel

from df_test_framework.core.types import (
    CaseType,
    DatabaseDialect,
    DatabaseOperation,
    DecimalAsCurrency,
    DecimalAsFloat,
    Environment,
    Headers,
    HttpMethod,
    HttpStatus,
    HttpStatusGroup,
    JsonDict,
    LogLevel,
    MessageQueueType,
    Priority,
    QueryParams,
    StorageType,
)


class TestEnvironmentEnum:
    """测试环境枚举"""

    def test_environment_values(self):
        """测试环境枚举值"""
        assert Environment.DEV.value == "dev"
        assert Environment.TEST.value == "test"
        assert Environment.STAGING.value == "staging"
        assert Environment.PRODUCTION.value == "production"
        assert Environment.PROD.value == "prod"

    def test_from_string_valid(self):
        """测试从字符串创建环境"""
        assert Environment.from_string("dev") == Environment.DEV
        assert Environment.from_string("test") == Environment.TEST
        assert Environment.from_string("staging") == Environment.STAGING
        assert Environment.from_string("production") == Environment.PRODUCTION
        assert Environment.from_string("prod") == Environment.PROD

    def test_from_string_case_insensitive(self):
        """测试大小写不敏感"""
        assert Environment.from_string("DEV") == Environment.DEV
        assert Environment.from_string("Test") == Environment.TEST

    def test_from_string_invalid(self):
        """测试无效字符串"""
        with pytest.raises(ValueError, match="Unknown environment"):
            Environment.from_string("invalid")


class TestLogLevelEnum:
    """测试日志级别枚举"""

    def test_log_level_values(self):
        """测试日志级别枚举值"""
        assert LogLevel.DEBUG.value == "DEBUG"
        assert LogLevel.INFO.value == "INFO"
        assert LogLevel.WARNING.value == "WARNING"
        assert LogLevel.ERROR.value == "ERROR"
        assert LogLevel.CRITICAL.value == "CRITICAL"


class TestHttpMethodEnum:
    """测试 HTTP 方法枚举"""

    def test_http_method_values(self):
        """测试 HTTP 方法枚举值"""
        assert HttpMethod.GET.value == "GET"
        assert HttpMethod.POST.value == "POST"
        assert HttpMethod.PUT.value == "PUT"
        assert HttpMethod.PATCH.value == "PATCH"
        assert HttpMethod.DELETE.value == "DELETE"
        assert HttpMethod.HEAD.value == "HEAD"
        assert HttpMethod.OPTIONS.value == "OPTIONS"


class TestHttpStatusEnum:
    """测试 HTTP 状态码枚举"""

    def test_success_status_codes(self):
        """测试成功状态码"""
        assert HttpStatus.OK.value == 200
        assert HttpStatus.CREATED.value == 201
        assert HttpStatus.ACCEPTED.value == 202
        assert HttpStatus.NO_CONTENT.value == 204

    def test_redirect_status_codes(self):
        """测试重定向状态码"""
        assert HttpStatus.MOVED_PERMANENTLY.value == 301
        assert HttpStatus.FOUND.value == 302
        assert HttpStatus.NOT_MODIFIED.value == 304

    def test_client_error_status_codes(self):
        """测试客户端错误状态码"""
        assert HttpStatus.BAD_REQUEST.value == 400
        assert HttpStatus.UNAUTHORIZED.value == 401
        assert HttpStatus.FORBIDDEN.value == 403
        assert HttpStatus.NOT_FOUND.value == 404
        assert HttpStatus.TOO_MANY_REQUESTS.value == 429

    def test_server_error_status_codes(self):
        """测试服务器错误状态码"""
        assert HttpStatus.INTERNAL_SERVER_ERROR.value == 500
        assert HttpStatus.BAD_GATEWAY.value == 502
        assert HttpStatus.SERVICE_UNAVAILABLE.value == 503
        assert HttpStatus.GATEWAY_TIMEOUT.value == 504


class TestHttpStatusGroupEnum:
    """测试 HTTP 状态码分组枚举"""

    def test_status_group_values(self):
        """测试状态码分组枚举值"""
        assert HttpStatusGroup.INFORMATIONAL.value == "1xx"
        assert HttpStatusGroup.SUCCESS.value == "2xx"
        assert HttpStatusGroup.REDIRECTION.value == "3xx"
        assert HttpStatusGroup.CLIENT_ERROR.value == "4xx"
        assert HttpStatusGroup.SERVER_ERROR.value == "5xx"


class TestDatabaseDialectEnum:
    """测试数据库方言枚举"""

    def test_database_dialect_values(self):
        """测试数据库方言枚举值"""
        assert DatabaseDialect.MYSQL.value == "mysql"
        assert DatabaseDialect.POSTGRESQL.value == "postgresql"
        assert DatabaseDialect.SQLITE.value == "sqlite"
        assert DatabaseDialect.ORACLE.value == "oracle"
        assert DatabaseDialect.MSSQL.value == "mssql"


class TestDatabaseOperationEnum:
    """测试数据库操作枚举"""

    def test_database_operation_values(self):
        """测试数据库操作枚举值"""
        assert DatabaseOperation.SELECT.value == "SELECT"
        assert DatabaseOperation.INSERT.value == "INSERT"
        assert DatabaseOperation.UPDATE.value == "UPDATE"
        assert DatabaseOperation.DELETE.value == "DELETE"


class TestMessageQueueTypeEnum:
    """测试消息队列类型枚举"""

    def test_mq_type_values(self):
        """测试消息队列类型枚举值"""
        assert MessageQueueType.KAFKA.value == "kafka"
        assert MessageQueueType.RABBITMQ.value == "rabbitmq"
        assert MessageQueueType.ROCKETMQ.value == "rocketmq"


class TestStorageTypeEnum:
    """测试存储类型枚举"""

    def test_storage_type_values(self):
        """测试存储类型枚举值"""
        assert StorageType.S3.value == "s3"
        assert StorageType.OSS.value == "oss"
        assert StorageType.MINIO.value == "minio"
        assert StorageType.LOCAL.value == "local"


class TestPriorityEnum:
    """测试用例优先级枚举"""

    def test_priority_values(self):
        """测试优先级枚举值"""
        assert Priority.CRITICAL.value == "critical"
        assert Priority.HIGH.value == "high"
        assert Priority.MEDIUM.value == "medium"
        assert Priority.LOW.value == "low"


class TestCaseTypeEnum:
    """测试类型枚举"""

    def test_case_type_values(self):
        """测试类型枚举值"""
        assert CaseType.SMOKE.value == "smoke"
        assert CaseType.REGRESSION.value == "regression"
        assert CaseType.INTEGRATION.value == "integration"
        assert CaseType.E2E.value == "e2e"
        assert CaseType.PERFORMANCE.value == "performance"
        assert CaseType.SECURITY.value == "security"


class TestDecimalAsFloat:
    """测试 DecimalAsFloat 序列化类型"""

    def test_decimal_serializes_to_float(self):
        """测试 Decimal 序列化为浮点数"""

        class PriceModel(BaseModel):
            price: DecimalAsFloat

        model = PriceModel(price=Decimal("99.99"))
        json_str = model.model_dump_json()

        # 验证序列化为数字而非字符串
        assert '"price":99.99' in json_str or '"price": 99.99' in json_str

    def test_decimal_as_float_precision(self):
        """测试浮点数精度"""

        class AmountModel(BaseModel):
            amount: DecimalAsFloat

        model = AmountModel(amount=Decimal("123.456789"))
        data = model.model_dump(mode="json")

        # 浮点数可能有精度损失
        assert isinstance(data["amount"], float)

    def test_decimal_as_float_with_zero(self):
        """测试零值"""

        class Model(BaseModel):
            value: DecimalAsFloat

        model = Model(value=Decimal("0"))
        data = model.model_dump(mode="json")
        assert data["value"] == 0.0


class TestDecimalAsCurrency:
    """测试 DecimalAsCurrency 序列化类型"""

    def test_decimal_serializes_to_currency(self):
        """测试 Decimal 序列化为货币格式"""

        class DisplayModel(BaseModel):
            amount: DecimalAsCurrency

        model = DisplayModel(amount=Decimal("123.45"))
        json_str = model.model_dump_json()

        # 验证序列化为货币格式字符串
        assert "$123.45" in json_str

    def test_currency_format_two_decimals(self):
        """测试货币格式保留两位小数"""

        class Model(BaseModel):
            amount: DecimalAsCurrency

        model = Model(amount=Decimal("100"))
        data = model.model_dump(mode="json")
        assert data["amount"] == "$100.00"

    def test_currency_format_with_cents(self):
        """测试带分的货币格式"""

        class Model(BaseModel):
            amount: DecimalAsCurrency

        model = Model(amount=Decimal("99.9"))
        data = model.model_dump(mode="json")
        assert data["amount"] == "$99.90"


class TestTypeAliases:
    """测试类型别名"""

    def test_json_dict_type(self):
        """测试 JsonDict 类型"""
        data: JsonDict = {"key": "value", "number": 123}
        assert isinstance(data, dict)
        assert data["key"] == "value"

    def test_headers_type(self):
        """测试 Headers 类型"""
        headers: Headers = {"Content-Type": "application/json", "Authorization": "Bearer token"}
        assert isinstance(headers, dict)
        assert headers["Content-Type"] == "application/json"

    def test_query_params_type(self):
        """测试 QueryParams 类型"""
        params: QueryParams = {"page": 1, "limit": 10, "q": "search"}
        assert isinstance(params, dict)
        assert params["page"] == 1
