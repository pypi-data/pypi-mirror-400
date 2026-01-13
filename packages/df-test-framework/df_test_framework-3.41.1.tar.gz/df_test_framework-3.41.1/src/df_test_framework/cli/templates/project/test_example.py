"""API测试示例模板"""

TEST_EXAMPLE_TEMPLATE = """\"\"\"示例测试

演示如何使用 df-test-framework v3.38.7 编写测试用例。

本文件展示两种测试编写模式:
1. 直接使用 http_client（适合简单场景、快速探索）
2. 使用 BaseAPI 封装（适合复杂项目、团队协作）

v3.38.7 最佳实践:
- ✅ allure_observer: 自动记录请求/响应到 Allure 报告
- ✅ cleanup fixture: 配置驱动的数据清理
- ✅ skip_auth/token: 请求级认证控制（v3.19.0+）
- ✅ with_overrides(): 运行时配置覆盖
- ✅ http_mock/time_mock: 测试隔离
- ✅ EventBus 事件关联: correlation_id 追踪请求链路
- ✅ structlog 日志系统: 日志级别由消息性质决定（v3.38.7）

v3.39.0 新增:
- ✅ 支持增量合并（--merge 选项）
- ✅ 用户扩展区域保留自定义测试

如何选择测试模式:
- 简单测试/临时调试/快速验证 → 直接使用 http_client
- 大型项目/接口自动化/回归测试 → 使用 BaseAPI 封装或 OpenAPI 生成

相关文件:
- 请求模型: src/{project_name}/models/requests/example.py
- 响应模型: src/{project_name}/models/responses/example.py
- 示例 API 客户端: src/{project_name}/apis/example_api.py
\"\"\"

import pytest
import allure
from df_test_framework import attach_json, step


# ========== AUTO-GENERATED START ==========
# 此区域由脚手架自动生成，重新生成时会被更新


# ============================================================================
# 模式 1: 直接使用 http_client（适合简单场景）
# ============================================================================


@allure.feature("示例功能")
@allure.story("基础测试")
class TestExample:
    \"\"\"示例测试类

    演示框架核心功能的使用方式。
    \"\"\"

    @allure.title("测试框架初始化")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_framework_init(self, runtime, settings):
        \"\"\"测试框架初始化

        验证框架和配置加载正常。
        \"\"\"
        with step("验证 Runtime 初始化"):
            assert runtime is not None
            assert runtime.settings is not None

        with step("验证配置加载"):
            assert settings is not None
            assert settings.http is not None
            attach_json({"api_base_url": settings.http.base_url}, name="HTTP配置")

    @allure.title("测试 HTTP 客户端")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_http_client(self, http_client):
        \"\"\"测试 HTTP 客户端基本功能

        Fixtures:
        - http_client: HTTP 客户端（中间件自动添加签名/Token）

        注意：
        - 中间件会自动添加签名/Token 等认证信息
        - Allure 记录自动生效（autouse fixture），无需显式声明
        \"\"\"
        with step("发送 GET 请求"):
            # 注意：需要配置有效的 API 地址
            # response = http_client.get("/api/health")
            # assert response.status_code == 200
            pass  # 替换为实际的 API 调用

        # ✅ allure_observer 自动记录:
        #    - 完整请求体和响应体
        #    - OpenTelemetry trace_id/span_id
        #    - 响应时间

    @allure.title("测试认证控制")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_auth_control(self, http_client):
        \"\"\"测试请求级认证控制

        v3.19.0+ 新增:
        - skip_auth=True: 跳过认证（测试未登录场景）
        - token="xxx": 使用自定义 Token
        - clear_auth_cache(): 清除 Token 缓存
        \"\"\"
        with step("测试未登录场景 (skip_auth)"):
            # 跳过认证，测试接口返回 401
            # response = http_client.get("/api/protected", skip_auth=True)
            # assert response.status_code == 401
            pass

        with step("测试自定义 Token"):
            # 使用指定 Token（不影响中间件缓存）
            # response = http_client.get("/api/me", token="custom_token")
            pass

        with step("测试清除认证缓存"):
            # 登出后清除缓存，下次请求会重新登录
            # http_client.post("/auth/logout")
            # http_client.clear_auth_cache()
            pass

    @allure.title("测试运行时配置覆盖")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_runtime_override(self, runtime):
        \"\"\"测试运行时配置覆盖

        使用 with_overrides() 动态修改配置
        \"\"\"
        with step("创建带覆盖配置的 RuntimeContext"):
            # 临时修改超时时间
            new_runtime = runtime.with_overrides({
                "http.timeout": 60,  # 覆盖超时时间
            })

            assert new_runtime.settings.http.timeout == 60
            assert runtime.settings.http.timeout != 60  # 原配置不变

        with step("验证配置隔离"):
            # with_overrides() 创建新实例，不影响原配置
            assert runtime.settings.http.timeout == runtime.settings.http.timeout

    @allure.title("测试 Unit of Work 模式")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.integration
    def test_uow_pattern(self, uow):
        \"\"\"测试 Unit of Work 模式

        使用 uow fixture 管理事务和 Repository

        注意：需要在项目中配置数据库和 Repository
        \"\"\"
        with step("使用 Repository 查询"):
            # uow.users.find_by_id(1)
            # uow.orders.find_by_order_no("ORDER_001")
            pass  # 替换为实际的 Repository 操作

        with step("执行 SQL 查询"):
            # from sqlalchemy import text
            # result = uow.session.execute(text("SELECT 1"))
            pass  # 替换为实际的 SQL 操作

        # ✅ 测试结束后自动回滚，数据不会保留
        # 如需持久化数据，调用 uow.commit()

    @allure.title("测试数据清理")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_data_cleanup(self, http_client, cleanup):
        \"\"\"测试配置驱动的数据清理

        v3.18.0+ cleanup fixture:
        - 需在 config/base.yaml 配置 cleanup.mappings
        - 测试结束后自动清理（除非 --keep-test-data）
        \"\"\"
        from df_test_framework import DataGenerator

        with step("创建测试数据"):
            # 生成唯一标识符
            order_no = DataGenerator.test_id("TEST_ORD")

            # 调用 API 创建数据
            # response = http_client.post("/api/orders", json={"order_no": order_no})
            # order_id = response.json()["data"]["id"]

            # 注册清理
            # cleanup.add("orders", order_no)
            pass

        # ✅ 测试结束后自动清理（除非 --keep-test-data 或 @pytest.mark.keep_data）

    @allure.title("测试 HTTP Mock 功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_http_mock(self, http_mock, http_client):
        \"\"\"测试 HTTP Mock 功能

        使用 http_mock 进行接口 Mock，无需真实服务
        \"\"\"
        with step("配置 Mock 响应"):
            # Mock GET /api/users 接口
            http_mock.get("/api/users", json={
                "code": 200,
                "data": [{"id": 1, "name": "Mock User"}],
                "message": "success"
            })

        with step("调用被 Mock 的接口"):
            # 发送请求，会返回 Mock 数据
            response = http_client.get("/api/users")
            data = response.json()
            attach_json(data, name="Mock响应数据")

        with step("验证 Mock 响应"):
            assert data["code"] == 200
            assert len(data["data"]) == 1
            assert data["data"][0]["name"] == "Mock User"

        with step("验证接口被调用"):
            # 验证 Mock 接口被调用了 1 次
            http_mock.assert_called("/api/users", "GET", times=1)

    @allure.title("测试时间 Mock 功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_time_mock(self, time_mock):
        \"\"\"测试时间 Mock 功能

        使用 time_mock 进行时间控制，测试时间敏感逻辑

        注意: freezegun 要求使用 `import datetime` 而非 `from datetime import datetime`
        \"\"\"
        import datetime

        with step("冻结时间到指定时刻"):
            # 冻结时间到 2024-01-01 12:00:00
            time_mock.freeze("2024-01-01 12:00:00")
            now = datetime.datetime.now()
            assert now.year == 2024
            assert now.month == 1
            assert now.hour == 12

        with step("时间前进 1 小时"):
            # 将时间移动到 2024-01-01 13:00:00
            time_mock.move_to("2024-01-01 13:00:00")
            now = datetime.datetime.now()
            assert now.hour == 13

        with step("使用增量前进时间"):
            # 使用 tick 前进指定秒数
            time_mock.tick(seconds=3600)  # 前进 1 小时
            now = datetime.datetime.now()
            assert now.hour == 14

        # ✅ 测试结束后自动恢复真实时间


# ============================================================================
# 模式 2: 使用 BaseAPI 封装（适合复杂项目）
# ============================================================================

# 导入示例模型和 API 客户端
# 这些文件已经由脚手架自动生成：
# - src/{project_name}/models/requests/example.py  - 请求模型
# - src/{project_name}/models/responses/example.py - 响应模型
# - src/{project_name}/apis/example_api.py         - API 客户端封装
from {project_name}.models.requests.example import CreateExampleRequest
from {project_name}.models.responses.example import ExampleResponse
from {project_name}.apis.example_api import ExampleAPI


@allure.feature("示例功能")
@allure.story("API 客户端模式")
class TestAPIClientPattern:
    \"\"\"演示使用 BaseAPI 封装的测试模式

    适用场景:
    - 大型项目（多人协作）
    - 接口自动化测试
    - 需要代码复用
    - 需要 IDE 智能提示

    优势:
    - 强类型：Pydantic 模型提供类型安全
    - 可复用：API 方法可在多个测试中复用
    - 易维护：接口变更只需修改 API 类
    - IDE 友好：完整的代码补全和类型提示

    相关文件:
    - 请求模型: src/{project_name}/models/requests/example.py
    - 响应模型: src/{project_name}/models/responses/example.py
    - API 客户端: src/{project_name}/apis/example_api.py
    \"\"\"

    @allure.title("使用 API 客户端创建示例")
    @pytest.mark.smoke
    def test_create_example_with_api_client(self, http_client, cleanup):
        \"\"\"演示使用 API 客户端创建示例

        对比直接使用 http_client:
        - 直接方式: http_client.post("/api/v1/examples", json={"name": "Alice", ...})
        - 封装方式: example_api.create_example(CreateExampleRequest(name="Alice", ...))
        \"\"\"
        from df_test_framework import DataGenerator

        # 实例化 API 客户端（也可以使用 example_api fixture）
        example_api = ExampleAPI(http_client)

        with step("构造请求数据"):
            # 使用 Pydantic 模型，获得 IDE 智能提示
            test_id = DataGenerator.test_id("TEST_EXAMPLE")
            request = CreateExampleRequest(
                name=f"测试示例_{test_id}",
                email=f"{test_id}@example.com",
                phone="13800138000"
            )
            attach_json(request.model_dump(), name="请求数据")

        with step("调用 API"):
            # 方法签名明确，IDE 可以提示参数
            # response = example_api.create_example(request)
            # attach_json(response, name="响应数据")
            pass  # 替换为实际调用

        with step("注册数据清理"):
            # 测试结束后自动清理
            # cleanup.add("examples", test_id)
            pass

        with step("验证响应"):
            # assert response["code"] == 200
            # assert response["data"]["name"] == request.name
            pass

    @allure.title("使用 fixture 注入 API 客户端")
    @pytest.mark.smoke
    def test_with_api_fixture(self, example_api):
        \"\"\"演示使用 @api_class 自动注册的 fixture

        example_api fixture 由 @api_class 装饰器自动注册。
        无需手动导入每个 API 类，框架会自动发现 apis 包下所有模块。

        前置条件（已在 conftest.py 中配置）:
            from df_test_framework.testing.decorators import load_api_fixtures
            load_api_fixtures(globals(), apis_package="{project_name}.apis")
        \"\"\"
        with step("直接使用 fixture"):
            # example_api 由 @api_class 装饰器自动注册
            # 无需手动实例化
            # response = example_api.list_examples(page=1, size=10)
            pass

        with step("测试跳过认证"):
            # 使用 skip_auth 参数测试公开接口
            # response = example_api.get_example(example_id=1, skip_auth=True)
            pass

    @allure.title("两种模式对比")
    @pytest.mark.smoke
    def test_compare_two_patterns(self, http_client):
        \"\"\"直观对比两种测试模式\"\"\"

        with step("模式 1: 直接使用 http_client"):
            # 优点：简单直接，无需额外定义
            # 缺点：URL 硬编码，无类型提示，不易复用
            # response = http_client.post(
            #     "/api/v1/users",
            #     json={"name": "Alice", "email": "alice@example.com"}
            # )
            pass

        with step("模式 2: 使用 API 客户端封装"):
            # 优点：强类型，IDE 提示，易复用，易维护
            # 缺点：需要额外定义 API 类（但可用 OpenAPI 生成器自动生成）
            example_api = ExampleAPI(http_client)
            request = CreateExampleRequest(name="Alice", email="alice@example.com")
            # response = example_api.create_example(request)
            pass

        # 建议:
        # - 简单场景（快速验证、临时测试）→ 模式 1
        # - 复杂项目（团队协作、长期维护）→ 模式 2
        # - 使用 `df-test gen from-swagger` 可自动生成模式 2 的代码


# ========== AUTO-GENERATED END ==========


# ========== USER EXTENSIONS ==========
# 在此区域添加自定义测试用例，重新生成时会保留


__all__ = ["TestExample", "TestAPIClientPattern"]
"""

__all__ = ["TEST_EXAMPLE_TEMPLATE"]
