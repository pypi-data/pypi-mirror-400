"""示例01: 配置化HTTP中间件

v3.36.0: InterceptorConfig 已废弃，使用 MiddlewareConfig 替代

演示内容:
1. 签名中间件 (SignatureMiddleware) - MD5/SHA256/HMAC-SHA256算法
2. Bearer Token中间件 - 自动登录和Token管理
3. 路径模式匹配 - 通配符和正则表达式
4. 中间件优先级控制
5. 中间件启用/禁用

运行方式:
    python examples/07-v35-features/01_configurable_interceptors.py
"""

from typing import Self

from pydantic import model_validator

from df_test_framework import Bootstrap, FrameworkSettings, HTTPConfig
from df_test_framework.infrastructure.config import (
    BearerTokenMiddlewareConfig,
    SignatureMiddlewareConfig,
    TokenSource,
)

# ============================================================
# 示例1: 签名中间件配置
# ============================================================


def create_signature_http_config() -> HTTPConfig:
    """创建带签名中间件的HTTP配置

    签名中间件会自动为请求生成签名并添加到请求头。
    """
    return HTTPConfig(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=30,
        middlewares=[
            SignatureMiddlewareConfig(
                # 基础配置
                enabled=True,
                priority=10,  # 优先级（数字越小越先执行）
                # 签名算法配置
                algorithm="md5",  # 可选: md5, sha256, hmac-sha256
                secret="my_secret_key_12345",
                # 签名参数配置
                header="X-Sign",  # 签名头名称
                timestamp_header="X-Timestamp",  # 时间戳头名称
                nonce_header="X-Nonce",  # 随机数头名称
                # 签名内容配置
                include_query_params=True,  # 包含URL查询参数
                include_json_body=True,  # 包含JSON请求体
                # 路径匹配配置
                include_paths=[
                    "/posts/**",  # 匹配/posts/及其所有子路径
                    "/users/**",  # 匹配/users/及其所有子路径
                    "/api/**",  # 匹配/api/及其所有子路径
                ],
                exclude_paths=[
                    "/health",  # 排除健康检查
                    "/*/public/**",  # 排除公开接口
                ],
            ),
        ],
    )


class SignatureSettings(FrameworkSettings):
    """带签名中间件的Settings"""

    @model_validator(mode="after")
    def _setup_middlewares(self) -> Self:
        """设置HTTP中间件"""
        self.http = create_signature_http_config()
        return self


def demo_signature_middleware():
    """演示签名中间件"""
    print("\n" + "=" * 60)
    print("示例1: 签名中间件")
    print("=" * 60)

    # 创建运行时上下文
    runtime = Bootstrap().with_settings(SignatureSettings).build().run()

    # 获取HTTP客户端
    client = runtime.http_client()

    # 发送请求（会自动添加签名）
    print("\n发送GET请求到 /posts/1 (会自动添加签名)...")
    response = client.get("/posts/1")
    print(f"响应状态码: {response.status_code}")
    print(f"响应数据: {response.json()}")

    # 发送POST请求（会自动签名请求体）
    print("\n发送POST请求到 /posts (会自动签名请求体)...")
    new_post = {"title": "Test Post", "body": "This is a test post", "userId": 1}
    response = client.post("/posts", json=new_post)
    print(f"响应状态码: {response.status_code}")
    print(f"创建的文章ID: {response.json().get('id')}")

    print("\n✅ 签名中间件演示完成")


# ============================================================
# 示例2: Bearer Token中间件配置
# ============================================================


def create_bearer_token_http_config() -> HTTPConfig:
    """创建带Bearer Token中间件的HTTP配置

    Bearer Token中间件支持两种模式:
    1. source="static" - 使用固定Token
    2. source="login" - 自动登录获取Token
    """
    return HTTPConfig(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=30,
        middlewares=[
            BearerTokenMiddlewareConfig(
                # 基础配置
                enabled=True,
                priority=20,
                # Token源配置 - 使用静态Token
                source=TokenSource.STATIC,
                token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                # Header配置
                header="Authorization",
                token_prefix="Bearer",  # 最终格式: "Bearer {token}"
                # 路径匹配配置
                include_paths=[
                    "/posts/**",
                    "/users/**",
                ],
                exclude_paths=[
                    "/posts/public/**",
                ],
            ),
        ],
    )


class BearerTokenSettings(FrameworkSettings):
    """带Bearer Token中间件的Settings"""

    @model_validator(mode="after")
    def _setup_middlewares(self) -> Self:
        """设置HTTP中间件"""
        self.http = create_bearer_token_http_config()
        return self


def demo_bearer_token_middleware():
    """演示Bearer Token中间件"""
    print("\n" + "=" * 60)
    print("示例2: Bearer Token中间件")
    print("=" * 60)

    # 创建运行时上下文
    runtime = Bootstrap().with_settings(BearerTokenSettings).build().run()

    # 获取HTTP客户端
    client = runtime.http_client()

    # 发送请求（会自动添加Authorization头）
    print("\n发送GET请求到 /posts/1 (会自动添加Bearer Token)...")
    response = client.get("/posts/1")
    print(f"响应状态码: {response.status_code}")
    print(f"响应数据: {response.json()}")

    print("\n✅ Bearer Token中间件演示完成")


# ============================================================
# 示例3: 多个中间件组合使用
# ============================================================


def create_multi_middleware_http_config() -> HTTPConfig:
    """创建带多个中间件的HTTP配置

    演示如何组合使用多个中间件:
    - 签名中间件 (优先级10)
    - Bearer Token中间件 (优先级20)

    中间件按优先级从小到大执行。
    """
    return HTTPConfig(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=30,
        middlewares=[
            # 中间件1: 签名（优先级10，先执行）
            SignatureMiddlewareConfig(
                enabled=True,
                priority=10,
                algorithm="sha256",
                secret="my_secret",
                header="X-Sign",
                include_paths=["/api/**"],
                include_query_params=True,
                include_json_body=True,
            ),
            # 中间件2: Bearer Token（优先级20，后执行）
            BearerTokenMiddlewareConfig(
                enabled=True,
                priority=20,
                source=TokenSource.STATIC,
                token="demo_token_12345",
                header="Authorization",
                token_prefix="Bearer",
                include_paths=["/api/**"],
            ),
        ],
    )


class MultiMiddlewareSettings(FrameworkSettings):
    """带多个中间件的Settings"""

    @model_validator(mode="after")
    def _setup_middlewares(self) -> Self:
        """设置HTTP中间件"""
        self.http = create_multi_middleware_http_config()
        return self


def demo_multi_middlewares():
    """演示多个中间件组合使用"""
    print("\n" + "=" * 60)
    print("示例3: 多个中间件组合")
    print("=" * 60)

    # 创建运行时上下文
    runtime = Bootstrap().with_settings(MultiMiddlewareSettings).build().run()

    # 获取HTTP客户端
    client = runtime.http_client()

    print("\n发送请求到 /posts/1...")
    print("中间件执行顺序:")
    print("  1. SignatureMiddleware (优先级10) - 添加签名")
    print("  2. BearerTokenMiddleware (优先级20) - 添加Token")

    response = client.get("/posts/1")
    print(f"\n响应状态码: {response.status_code}")

    print("\n✅ 多中间件组合演示完成")


# ============================================================
# 示例4: 路径模式匹配演示
# ============================================================


def create_path_matching_http_config() -> HTTPConfig:
    """创建演示路径匹配的HTTP配置

    路径匹配支持:
    1. 通配符: /api/** 匹配/api/及其所有子路径
    2. 单层通配符: /api/* 只匹配/api/下一层
    3. 精确匹配: /api/users 只匹配该路径
    """
    return HTTPConfig(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=30,
        middlewares=[
            SignatureMiddlewareConfig(
                enabled=True,
                priority=10,
                algorithm="md5",
                secret="secret",
                header="X-Sign",
                # 包含路径：使用通配符
                include_paths=[
                    "/posts/**",  # 匹配 /posts, /posts/1, /posts/1/comments
                    "/users/*",  # 匹配 /users/1, /users/2 (仅一层)
                    "/comments",  # 精确匹配 /comments
                ],
                # 排除路径：优先级高于include
                exclude_paths=[
                    "/posts/public/**",  # 排除公开文章
                    "/users/*/avatar",  # 排除头像接口
                ],
            ),
        ],
    )


class PathMatchingSettings(FrameworkSettings):
    """路径匹配演示Settings"""

    @model_validator(mode="after")
    def _setup_middlewares(self) -> Self:
        """设置HTTP中间件"""
        self.http = create_path_matching_http_config()
        return self


def demo_path_matching():
    """演示路径匹配规则"""
    print("\n" + "=" * 60)
    print("示例4: 路径模式匹配")
    print("=" * 60)

    # 创建运行时上下文
    runtime = Bootstrap().with_settings(PathMatchingSettings).build().run()

    # 获取HTTP客户端
    client = runtime.http_client()

    # 测试不同路径
    test_paths = [
        ("/posts/1", True, "匹配 /posts/**"),
        ("/users/1", True, "匹配 /users/*"),
        ("/users/1/posts", False, "/users/* 只匹配一层"),
        ("/comments", True, "精确匹配 /comments"),
    ]

    print("\n路径匹配测试:")
    for path, should_match, reason in test_paths:
        print(f"\n路径: {path}")
        print(f"  预期: {'✅ 添加签名' if should_match else '❌ 不添加签名'}")
        print(f"  原因: {reason}")

        # 实际发送请求
        try:
            response = client.get(path)
            print(f"  结果: 状态码 {response.status_code}")
        except Exception as e:
            print(f"  结果: {e}")

    print("\n✅ 路径匹配演示完成")


# ============================================================
# 示例5: 中间件启用/禁用
# ============================================================


def create_toggle_http_config(signature_enabled: bool = True) -> HTTPConfig:
    """创建可切换中间件的HTTP配置"""
    return HTTPConfig(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=30,
        middlewares=[
            SignatureMiddlewareConfig(
                enabled=signature_enabled,  # 可动态控制
                priority=10,
                algorithm="md5",
                secret="secret",
                header="X-Sign",
                include_paths=["/**"],
            ),
        ],
    )


def demo_toggle_middleware():
    """演示中间件启用/禁用"""
    print("\n" + "=" * 60)
    print("示例5: 中间件启用/禁用")
    print("=" * 60)

    # 场景1: 启用中间件
    print("\n场景1: 中间件启用")

    class EnabledSettings(FrameworkSettings):
        @model_validator(mode="after")
        def _setup_middlewares(self) -> Self:
            self.http = create_toggle_http_config(signature_enabled=True)
            return self

    runtime = Bootstrap().with_settings(EnabledSettings).build().run()
    client = runtime.http_client()
    response = client.get("/posts/1")
    print(f"响应状态码: {response.status_code} (签名已添加)")

    # 场景2: 禁用中间件
    print("\n场景2: 中间件禁用")

    class DisabledSettings(FrameworkSettings):
        @model_validator(mode="after")
        def _setup_middlewares(self) -> Self:
            self.http = create_toggle_http_config(signature_enabled=False)
            return self

    runtime = Bootstrap().with_settings(DisabledSettings).build().run()
    client = runtime.http_client()
    response = client.get("/posts/1")
    print(f"响应状态码: {response.status_code} (签名未添加)")

    print("\n✅ 中间件启用/禁用演示完成")


# ============================================================
# 主函数
# ============================================================


def main():
    """运行所有示例"""
    print("\n" + "🚀 v3.36.0 配置化中间件示例".center(60, "="))

    try:
        # 示例1: 签名中间件
        demo_signature_middleware()

        # 示例2: Bearer Token中间件
        demo_bearer_token_middleware()

        # 示例3: 多个中间件组合
        demo_multi_middlewares()

        # 示例4: 路径模式匹配
        demo_path_matching()

        # 示例5: 中间件启用/禁用
        demo_toggle_middleware()

        print("\n" + "✅ 所有示例运行完成！".center(60, "="))

        print("\n💡 关键要点:")
        print("  1. 中间件配置完全声明式，无需手写拦截逻辑")
        print("  2. 使用辅助函数 + model_validator模式避免Pydantic继承问题")
        print("  3. 中间件按优先级从小到大执行")
        print("  4. 路径匹配支持通配符（**、*）和精确匹配")
        print("  5. exclude_paths优先级高于include_paths")

        print("\n📚 下一步:")
        print("  - 查看 02_profile_configuration.py 学习环境配置")
        print("  - 查看 docs/guides/middleware-configuration.md 了解最佳实践")

    except Exception as e:
        print(f"\n❌ 示例运行失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
