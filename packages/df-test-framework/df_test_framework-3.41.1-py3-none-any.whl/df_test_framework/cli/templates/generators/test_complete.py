"""完整测试文件生成模板

包含实际实现示例，减少TODO占位符。
"""

GEN_TEST_COMPLETE_TEMPLATE = """\"\"\"测试文件: {test_name}

使用 df-test-framework v3.38.7 进行 API 测试。

测试覆盖:
- ✅ 正常场景：成功调用 API
- ✅ 参数校验：参数化测试
- ✅ 异常场景：错误处理
- ✅ 认证场景：skip_auth/token 控制
- ✅ Mock 场景：外部依赖隔离

v3.38.7 最佳实践:
- ✅ allure_observer: 自动记录请求/响应到 Allure
- ✅ cleanup fixture: 配置驱动的数据清理
- ✅ skip_auth/token: 请求级认证控制（v3.19.0+）
- ✅ 强类型 API: Pydantic Model 参数和返回值
- ✅ structlog 日志系统: 日志级别由消息性质决定
\"\"\"

import pytest
import allure
from assertpy import assert_that
from df_test_framework import DataGenerator, attach_json, step


@allure.feature("{feature_name}")
@allure.story("{story_name}")
class Test{TestName}:
    \"\"\"{TestName} 测试类

    测试场景:
    1. test_{method_name}_success - 成功场景
    2. test_{method_name}_validation - 参数校验场景
    3. test_{method_name}_auth - 认证控制场景
    4. test_{method_name}_with_mock - Mock 场景
    \"\"\"

    # ========== 正常场景 ==========

    @allure.title("测试{test_description} - 成功场景")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_{method_name}_success(
        self,
        http_client,
        cleanup,
    ):
        \"\"\"测试{test_description} - 成功场景

        Fixtures:
        - http_client: HTTP 客户端（中间件自动添加签名/Token）
        - cleanup: 配置驱动的数据清理
        - Allure 记录自动生效（autouse fixture）

        前置条件: 数据准备完成
        预期结果: API 调用成功，返回预期数据
        \"\"\"
        with step("1. 准备测试数据"):
            # 使用 DataGenerator 生成唯一标识符
            test_id = DataGenerator.test_id("TEST")

            test_data = {
                "name": f"测试用户_{test_id[-8:]}",
                "email": f"test_{test_id[-8:]}@example.com",
                "phone": "13800138000",
            }

            attach_json(test_data, name="请求数据")

        with step("2. 调用 API"):
            # 中间件自动添加签名/Token
            response = http_client.post("/api/{api_path}", json=test_data)

            # 验证 HTTP 状态码
            assert_that(response.status_code).is_equal_to(200)

            # 解析响应
            result = response.json()
            attach_json(result, name="响应数据")

        with step("3. 验证响应数据"):
            # 验证响应结构
            assert_that(result).contains_key("code", "data", "message")
            assert_that(result["code"]).is_equal_to(200)
            assert_that(result["message"]).is_equal_to("success")

            # 验证业务数据
            data = result["data"]
            assert_that(data).is_not_none()

        with step("4. 注册数据清理"):
            # 配置驱动清理（需在 config/base.yaml 配置 cleanup.mappings）
            if "id" in data:
                cleanup.add("{entity_name}s", data["id"])

        # ✅ allure_observer 已自动记录请求/响应
        # ✅ cleanup 测试结束后自动清理（除非 --keep-test-data）

    # ========== 参数校验场景 ==========

    @allure.title("测试{test_description} - 参数校验")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("invalid_field,invalid_value,expected_error", [
        ("name", "", "名称不能为空"),
        ("name", "a" * 101, "名称长度不能超过100"),
        ("email", "invalid_email", "邮箱格式错误"),
        ("phone", "123", "手机号格式错误"),
    ], ids=["空名称", "名称过长", "邮箱格式错误", "手机号格式错误"])
    def test_{method_name}_validation(
        self,
        http_client,
        invalid_field,
        invalid_value,
        expected_error
    ):
        \"\"\"测试{test_description} - 参数校验

        前置条件: 发送无效参数
        预期结果: 返回 400 错误，包含错误信息
        \"\"\"
        with step("构建无效请求数据"):
            test_data = {
                "name": "测试用户",
                "email": "test@example.com",
                "phone": "13800138000",
            }
            test_data[invalid_field] = invalid_value
            attach_json(test_data, name="无效请求数据")

        with step("调用 API 并验证错误"):
            response = http_client.post("/api/{api_path}", json=test_data)

            # 验证返回 400 错误
            assert_that(response.status_code).is_equal_to(400)

            result = response.json()
            attach_json(result, name="错误响应")

            # 验证错误码
            assert_that(result["code"]).is_equal_to(400)

    # ========== 认证场景 ==========

    @allure.title("测试{test_description} - 未登录访问")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_{method_name}_unauthorized(self, http_client):
        \"\"\"测试{test_description} - 未登录场景

        v3.19.0+ 请求级认证控制:
        - skip_auth=True 跳过认证中间件
        \"\"\"
        with step("跳过认证访问受保护接口"):
            # skip_auth=True 不添加 Token
            response = http_client.get("/api/{api_path}", skip_auth=True)
            attach_json(response.json(), name="未授权响应")

        with step("验证返回 401"):
            assert_that(response.status_code).is_equal_to(401)

    @allure.title("测试{test_description} - 完整认证流程")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_{method_name}_auth_flow(self, http_client):
        \"\"\"测试{test_description} - 完整认证流程

        v3.19.0+ 认证控制:
        1. 登录获取 Token
        2. 用 Token 访问
        3. 登出
        4. 验证 Token 失效
        \"\"\"
        with step("1. 登录获取 Token"):
            login_data = {"username": "test", "password": "test123"}
            # skip_auth=True 登录接口不需要认证
            login_resp = http_client.post("/auth/login", json=login_data, skip_auth=True)

            if login_resp.status_code == 200:
                token = login_resp.json().get("data", {}).get("token")
            else:
                pytest.skip("登录接口不可用")
                return

        with step("2. 用 Token 访问"):
            # token="xxx" 使用指定 Token
            response = http_client.get("/api/{api_path}", token=token)
            assert_that(response.status_code).is_equal_to(200)

        with step("3. 登出"):
            http_client.post("/auth/logout", token=token)

        with step("4. 验证 Token 失效"):
            response = http_client.get("/api/{api_path}", token=token)
            assert_that(response.status_code).is_in(401, 403)

    # ========== Mock 场景 ==========

    @allure.title("测试{test_description} - Mock外部依赖")
    @allure.severity(allure.severity_level.NORMAL)
    def test_{method_name}_with_mock(self, http_mock, http_client):
        \"\"\"测试{test_description} - 使用 HTTP Mock 隔离外部依赖

        场景: 当 API 需要调用外部服务时，使用 Mock 隔离
        示例: 创建用户时需要调用短信服务发送验证码
        \"\"\"
        with step("1. 配置 Mock 响应"):
            # Mock 外部短信服务
            http_mock.post("/api/sms/send", json={
                "code": 200,
                "data": {"message_id": "mock_123"}
            })

        with step("2. 调用 API（触发外部调用）"):
            test_data = {
                "name": "测试用户",
                "phone": "13800138000",
            }

            response = http_client.post("/api/{api_path}", json=test_data)
            assert_that(response.status_code).is_equal_to(200)

        with step("3. 验证 Mock 被正确调用"):
            http_mock.assert_called("/api/sms/send", "POST", times=1)


__all__ = ["Test{TestName}"]
"""

__all__ = ["GEN_TEST_COMPLETE_TEMPLATE"]
