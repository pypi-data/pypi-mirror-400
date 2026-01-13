"""测试文件生成模板"""

GEN_TEST_TEMPLATE = """\"\"\"测试文件: {test_name}

使用 df-test-framework v3.38.7 进行 API 测试。

v3.38.7 最佳实践:
- ✅ allure_observer: 自动记录 HTTP 请求/响应到 Allure 报告
- ✅ cleanup fixture: 配置驱动的数据清理（v3.18.0+）
- ✅ skip_auth/token: 请求级认证控制（v3.19.0+）
- ✅ DataGenerator.test_id(): 生成测试标识符
- ✅ 强类型 API 方法: Pydantic Model 参数和返回值
- ✅ EventBus 事件关联: correlation_id 追踪请求链路
- ✅ structlog 日志系统: 日志级别由消息性质决定，全局配置控制过滤
\"\"\"

import pytest
import allure
from df_test_framework import DataGenerator, attach_json, step


@allure.feature("{feature_name}")
@allure.story("{story_name}")
class Test{TestName}:
    \"\"\"{TestName} 测试类

    使用 allure_observer fixture 自动记录所有 HTTP 请求到 Allure 报告。
    使用 cleanup fixture 进行配置驱动的数据清理。
    \"\"\"

    @allure.title("测试{test_description}")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_{method_name}(self, http_client, cleanup, allure_observer):
        \"\"\"测试{test_description}

        Fixtures:
        - http_client: HTTP 客户端（自动添加签名/Token）
        - cleanup: 配置驱动的数据清理
        - allure_observer: 自动记录请求/响应到 Allure

        数据清理说明:
        - cleanup.add("type", id): 注册清理项
        - 测试结束后自动清理（除非 --keep-test-data）
        - 需在 config/base.yaml 配置 cleanup.mappings
        \"\"\"
        with step("准备测试数据"):
            # 使用 DataGenerator 生成测试标识符（推荐）
            order_no = DataGenerator.test_id("TEST_ORD")

            # 或使用 Builder 模式
            # from {{project_name}}.builders import UserBuilder
            # user_data = UserBuilder().with_name("test_user").build()
            pass

        with step("调用API"):
            # 中间件自动添加签名/Token
            # response = http_client.post("/api/orders", json={"order_no": order_no})

            # 注册数据清理（配置驱动，需在 YAML 配置 cleanup.mappings）
            # cleanup.add("orders", order_no)
            pass

        with step("验证响应"):
            # data = response.json()
            # attach_json(data, name="响应数据")
            # assert data["code"] == 200
            pass

        # ✅ 测试结束后:
        # - allure_observer 已自动记录所有请求/响应
        # - cleanup 自动清理数据（除非 --keep-test-data）

    @allure.title("测试{test_description} - 认证场景")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_{method_name}_auth_scenarios(self, http_client, allure_observer):
        \"\"\"测试{test_description} - 认证控制场景

        v3.19.0+ 请求级认证控制:
        - skip_auth=True: 跳过认证（测试未登录场景）
        - token="xxx": 使用自定义 Token
        - clear_auth_cache(): 清除 Token 缓存
        \"\"\"
        with step("测试未登录场景"):
            # 跳过认证，测试接口返回 401
            # response = http_client.get("/api/protected", skip_auth=True)
            # assert response.status_code == 401
            pass

        with step("测试自定义Token"):
            # 使用指定 Token（不影响中间件缓存）
            # response = http_client.get("/api/me", token="custom_token")
            pass

        with step("测试完整认证流程"):
            # 1. 登录获取 Token
            # login_resp = http_client.post("/auth/login", json={{...}}, skip_auth=True)
            # token = login_resp.json()["data"]["token"]

            # 2. 用 Token 访问
            # response = http_client.get("/api/me", token=token)

            # 3. 登出
            # http_client.post("/auth/logout", token=token)

            # 4. 验证 Token 已失效
            # response = http_client.get("/api/me", token=token)
            # assert response.status_code == 401
            pass

    @allure.title("测试{test_description} - Mock模式")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_{method_name}_with_mock(self, http_mock, http_client):
        \"\"\"测试{test_description}（使用 HTTP Mock）

        使用 http_mock 隔离外部依赖，无需真实服务。
        \"\"\"
        with step("配置Mock响应"):
            # http_mock.get("/api/external", json={{
            #     "code": 200,
            #     "data": {{"mock": "data"}},
            # }})
            pass

        with step("调用API（返回Mock数据）"):
            # response = http_client.get("/api/external")
            # data = response.json()
            # assert data["code"] == 200
            pass

        with step("验证Mock调用"):
            # http_mock.assert_called("/api/external", "GET", times=1)
            pass


__all__ = ["Test{TestName}"]
"""

__all__ = ["GEN_TEST_TEMPLATE"]
