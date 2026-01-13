"""环境管理命令 (v3.35.5)

提供环境配置管理命令:
- df-test env show: 显示当前环境配置
- df-test env init: 初始化配置目录结构
- df-test env validate: 验证配置完整性

Example:
    >>> # 显示当前配置
    >>> df-test env show

    >>> # 显示指定环境配置
    >>> df-test env show --env=staging

    >>> # 初始化配置目录
    >>> df-test env init

    >>> # 验证配置
    >>> df-test env validate --env=staging
"""

from __future__ import annotations

from pathlib import Path


def env_show(env: str | None = None, config_dir: str = "config") -> int:
    """显示当前环境配置

    优先使用 YAML 配置（如果 config_dir 存在），
    否则回退到 .env 文件模式。

    Args:
        env: 环境名称（如: staging）。如果为 None，使用 .env 配置
        config_dir: 配置目录路径

    Returns:
        0 表示成功
    """
    try:
        config_path = Path(config_dir)

        if config_path.exists() and (config_path / "base.yaml").exists():
            # 使用 YAML 配置
            from df_test_framework.infrastructure.config import load_config

            settings = load_config(env, config_dir)
            source = f"{config_dir}/environments/{env or 'test'}.yaml"
        else:
            # 回退到 .env 文件
            from df_test_framework.infrastructure.config import FrameworkSettings

            if env:
                settings = FrameworkSettings.for_environment(env)
                source = f".env + .env.{env}"
            else:
                settings = FrameworkSettings()
                source = ".env"

        _print_settings(settings, source)
        return 0

    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1


def env_init(config_dir: str = "config") -> int:
    """初始化配置目录结构

    创建:
    - config/base.yaml
    - config/environments/local.yaml
    - config/environments/dev.yaml
    - config/environments/test.yaml
    - config/environments/staging.yaml
    - config/environments/prod.yaml
    - config/secrets/.gitkeep

    Args:
        config_dir: 配置目录路径

    Returns:
        0 表示成功
    """
    config_path = Path(config_dir)

    # 检查是否已存在
    if config_path.exists() and (config_path / "base.yaml").exists():
        print(f"⚠️  配置目录已存在: {config_path}")
        print("   如需重新初始化，请先删除该目录")
        return 1

    # 创建目录
    (config_path / "environments").mkdir(parents=True, exist_ok=True)
    (config_path / "secrets").mkdir(parents=True, exist_ok=True)

    # 创建 base.yaml
    base_content = """# 基础配置（所有环境共享）
# v3.35.5 - YAML 分层配置（深度合并 + _extends 继承）

http:
  timeout: 30
  max_retries: 3
  verify_ssl: true

database:
  pool_size: 10
  pool_timeout: 30
  charset: utf8mb4

redis:
  db: 0
  decode_responses: true

logging:
  level: INFO
  format: text

observability:
  enabled: true
  allure_recording: true
  debug_output: false
"""
    (config_path / "base.yaml").write_text(base_content, encoding="utf-8")

    # 创建环境配置
    env_configs = {
        "local": {
            "description": "本地开发环境",
            "debug": True,
            "logging_level": "DEBUG",
        },
        "dev": {
            "description": "开发环境",
            "debug": True,
            "logging_level": "DEBUG",
        },
        "test": {
            "description": "测试环境",
            "debug": False,
            "logging_level": "INFO",
        },
        "staging": {
            "description": "预发布环境",
            "debug": False,
            "logging_level": "INFO",
        },
        "prod": {
            "description": "生产环境（只读测试）",
            "debug": False,
            "logging_level": "WARNING",
        },
    }

    for env_name, env_info in env_configs.items():
        # local 环境使用 _extends 继承 dev 配置
        if env_name == "local":
            env_content = f"""# {env_info["description"]}
# v3.35.5: 使用 _extends 继承 dev 环境配置

_extends: environments/dev.yaml

env: {env_name}
debug: {str(env_info["debug"]).lower()}

# 本地开发启用调试输出
observability:
  debug_output: true

# 本地开发保留测试数据（便于调试）
test:
  keep_test_data: true"""
        else:
            env_content = f"""# {env_info["description"]}
# v3.35.5: 深度合并 - 只需覆盖差异配置，其他继承自 base.yaml

env: {env_name}
debug: {str(env_info["debug"]).lower()}

http:
  base_url: "http://localhost:8000"  # TODO: 修改为实际地址
  # timeout: 60  # 可覆盖 base.yaml 中的配置

# database:
#   host: localhost
#   port: 3306
#   name: test_db
#   user: root
#   password: ""  # 敏感信息建议放在 secrets/ 或环境变量

# redis:
#   host: localhost
#   port: 6379

logging:
  level: {env_info["logging_level"]}
"""
        (config_path / "environments" / f"{env_name}.yaml").write_text(
            env_content, encoding="utf-8"
        )

    # 创建 secrets/.gitkeep
    (config_path / "secrets" / ".gitkeep").touch()

    # 创建 secrets/.gitignore
    gitignore_content = """# 忽略所有敏感配置文件
*
!.gitkeep
!.gitignore
"""
    (config_path / "secrets" / ".gitignore").write_text(gitignore_content, encoding="utf-8")

    print(f"✅ 配置目录已创建: {config_path}")
    print("")
    print("📁 目录结构:")
    print(f"   {config_path}/")
    print("   ├── base.yaml              # 基础配置（所有环境共享）")
    print("   ├── environments/")
    print("   │   ├── local.yaml         # 本地开发环境")
    print("   │   ├── dev.yaml           # 开发环境")
    print("   │   ├── test.yaml          # 测试环境")
    print("   │   ├── staging.yaml       # 预发布环境")
    print("   │   └── prod.yaml          # 生产环境")
    print("   └── secrets/               # 敏感配置（已添加 .gitignore）")
    print("")
    print("📝 下一步:")
    print("   1. 编辑 config/environments/*.yaml 配置各环境")
    print("   2. 运行 `df-test env validate --env=test` 验证配置")
    print("   3. 使用 `pytest --env=staging` 指定环境运行测试")

    return 0


def env_validate(env: str | None = None, config_dir: str = "config") -> int:
    """验证配置完整性

    检查:
    - 配置文件是否存在
    - 必填字段是否配置
    - 配置值是否合法

    Args:
        env: 环境名称
        config_dir: 配置目录路径

    Returns:
        0 表示成功，1 表示失败
    """
    try:
        config_path = Path(config_dir)

        # 检查配置目录
        if not config_path.exists():
            print(f"❌ 配置目录不存在: {config_path}")
            print("   请运行 `df-test env init` 初始化配置目录")
            return 1

        if not (config_path / "base.yaml").exists():
            print(f"❌ 基础配置文件不存在: {config_path}/base.yaml")
            print("   请运行 `df-test env init` 初始化配置目录")
            return 1

        # 加载配置
        from df_test_framework.infrastructure.config import load_config

        env = env or "test"
        settings = load_config(env, config_dir)

        errors: list[str] = []
        warnings: list[str] = []

        # 检查环境配置文件
        env_file = config_path / "environments" / f"{env}.yaml"
        if not env_file.exists():
            warnings.append(f"环境配置文件不存在: {env_file}")

        # 检查 HTTP 配置
        if not settings.http.base_url or settings.http.base_url == "http://localhost:8000":
            warnings.append("http.base_url 未配置或使用默认值")

        # 检查数据库配置
        if settings.db:
            if not settings.db.host and not settings.db.connection_string:
                warnings.append("database 未配置（host 或 connection_string）")

        # 检查 Redis 配置
        if settings.redis:
            if not settings.redis.host or settings.redis.host == "localhost":
                warnings.append("redis.host 未配置或使用默认值")

        # 输出结果
        if errors:
            print(f"❌ 配置验证失败（{len(errors)} 个错误）:")
            for err in errors:
                print(f"   ✗ {err}")
            return 1

        if warnings:
            print(f"⚠️  配置验证通过（{len(warnings)} 个警告）:")
            for warn in warnings:
                print(f"   ⚠ {warn}")
        else:
            print(f"✅ 配置验证通过: {env}")

        # 显示配置摘要
        print("")
        print("📋 配置摘要:")
        print(f"   环境: {settings.env}")
        print(f"   调试模式: {'是' if settings.debug else '否'}")
        print(f"   HTTP Base URL: {settings.http.base_url or '(未配置)'}")

        return 0

    except Exception as e:
        print(f"❌ 配置验证失败: {e}")
        return 1


def _print_settings(settings, source: str) -> None:
    """打印配置信息

    Args:
        settings: 配置对象
        source: 配置来源描述
    """
    lines = [
        f"🔧 环境配置 - {settings.env}",
        f"📁 配置来源: {source}",
        "=" * 50,
        f"环境: {settings.env}",
        f"调试模式: {'是' if settings.debug else '否'}",
    ]

    # HTTP 配置
    if settings.http:
        lines.extend(
            [
                "",
                "📡 HTTP 配置:",
                f"   Base URL: {settings.http.base_url or '(未配置)'}",
                f"   超时: {settings.http.timeout}s",
                f"   重试次数: {settings.http.max_retries}",
            ]
        )

    # 数据库配置
    if settings.db and settings.db.host:
        lines.extend(
            [
                "",
                "🗄️  数据库配置:",
                f"   主机: {settings.db.host}:{settings.db.port}",
                f"   数据库: {settings.db.name or '(未配置)'}",
                f"   连接池: {settings.db.pool_size}",
            ]
        )

    # Redis 配置
    if settings.redis and settings.redis.host:
        lines.extend(
            [
                "",
                "📦 Redis 配置:",
                f"   主机: {settings.redis.host}:{settings.redis.port}",
                f"   数据库: {settings.redis.db}",
            ]
        )

    # 可观测性配置
    if settings.observability:
        lines.extend(
            [
                "",
                "👁️  可观测性配置:",
                f"   启用: {'是' if settings.observability.enabled else '否'}",
                f"   Allure: {'是' if settings.observability.allure_recording else '否'}",
                f"   调试输出: {'是' if settings.observability.debug_output else '否'}",
            ]
        )

    print("\n".join(lines))


__all__ = ["env_show", "env_init", "env_validate"]
