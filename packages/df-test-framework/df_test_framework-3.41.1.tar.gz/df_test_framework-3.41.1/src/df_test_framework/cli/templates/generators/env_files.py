"""环境配置文件生成模板

用于生成 YAML 配置文件（v3.35.0+ 推荐）和 .env 系列配置文件（回退模式）
"""

# ============================================================
# YAML 配置模板（v3.35.0+ 推荐）
# ============================================================

# config/base.yaml - 基础配置模板
YAML_BASE_TEMPLATE = """# =============================================================================
# 项目基础配置（所有环境共享）
#
# 生成命令: df-test gen settings --with-yaml
# 生成时间: {timestamp}
#
# v3.38.6 YAML 配置说明:
# - config/base.yaml           基础配置（所有环境通用）
# - config/environments/dev.yaml    开发环境配置
# - config/environments/test.yaml   测试环境配置
# - config/environments/staging.yaml 预发布环境配置
# - config/environments/prod.yaml   生产环境配置
# - config/environments/local.yaml  本地配置（不提交git，优先级最高）
# - config/secrets/.env.local       敏感信息（不提交git）
#
# 切换环境:
#   pytest tests/ --env=test      # 测试环境（默认）
#   pytest tests/ --env=staging   # 预发布环境
#   pytest tests/ --env=local     # 本地调试配置
# =============================================================================

# 默认环境
env: dev

# ============================================================
# HTTP 配置
# ============================================================
http:
  base_url: http://localhost:8000/api
  timeout: 30
  max_retries: 3

# ============================================================
# 可观测性配置
# ============================================================
observability:
  enabled: true
  debug_output: false  # 设为 true 启用调试输出（需要 pytest -s）
  allure_recording: true

# ============================================================
# 签名中间件配置（可选）
# ============================================================
# signature:
#   enabled: true
#   priority: 10
#   algorithm: md5
#   secret: change_me_in_production
#   header: X-Sign
#   include_paths:
#     - /api/**
#   exclude_paths:
#     - /health
#     - /metrics

# ============================================================
# Bearer Token 中间件配置（可选）
# ============================================================
# bearer_token:
#   enabled: true
#   priority: 20
#   source: login
#   login_url: /auth/login
#   credentials:
#     username: admin
#     password: admin123
#   token_path: data.token
#   include_paths:
#     - /api/**
#   exclude_paths:
#     - /auth/login
#     - /auth/register

# ============================================================
# 数据库配置（可选）
# ============================================================
# db:
#   host: localhost
#   port: 3306
#   name: test_db
#   user: root
#   password: password
#   pool_size: 10
#   charset: utf8mb4

# ============================================================
# Redis 配置（可选）
# ============================================================
# redis:
#   host: localhost
#   port: 6379
#   db: 0
#   password: null

# ============================================================
# 日志配置（v3.38.6 最佳实践）
# ============================================================
logging:
  level: INFO
  format: text          # text（开发）或 json（生产）
  # use_utc: false      # 生产环境建议启用 UTC 时间戳
  # add_callsite: false # 调试时启用，添加文件名/函数名/行号

# ============================================================
# 脱敏配置（v3.40.0+ 统一脱敏服务）
# ============================================================
# 默认配置已启用脱敏，覆盖常见敏感字段（password/token/secret等）
# 仅在需要自定义时取消注释
# sanitize:
#   enabled: true
#   default_strategy: partial  # partial/full/hash
#   console:
#     enabled: false  # 本地调试时可关闭控制台脱敏

# ============================================================
# 测试配置
# ============================================================
test:
  keep_test_data: false  # 设为 true 保留测试数据（调试用）
  # repository_package: {project_name}.repositories  # UoW 自动发现 Repository
  # apis_package: {project_name}.apis                # API 自动发现（@api_class）

# ============================================================
# 数据清理配置（v3.18.0+ 配置驱动清理）
# ============================================================
# cleanup:
#   enabled: true
#   mappings:
#     orders:
#       table: order_table
#       field: order_no
#     users:
#       table: user_table
#       field: user_id
#   # 使用方式: cleanup.add("orders", order_no)
"""

# config/environments/dev.yaml - 开发环境配置
YAML_DEV_TEMPLATE = """# =============================================================================
# 开发环境配置（v3.38.6）
#
# 继承: base.yaml（自动深度合并）
# 使用: pytest tests/ --env=dev
# =============================================================================

env: dev

http:
  base_url: http://dev-api.example.com/api
  timeout: 60

logging:
  level: DEBUG
  format: text
  add_callsite: true  # 开发环境启用调用位置信息

observability:
  debug_output: true  # 开发环境启用调试输出
"""

# config/environments/test.yaml - 测试环境配置
YAML_TEST_TEMPLATE = """# =============================================================================
# 测试环境配置（v3.38.6）
#
# 继承: base.yaml（自动深度合并）
# 使用: pytest tests/ --env=test（默认）
#
# 说明: 这是 CI/CD 环境的默认配置
# =============================================================================

env: test

http:
  base_url: http://test-api.example.com/api
  timeout: 30

logging:
  level: INFO
  format: text

observability:
  debug_output: false  # CI 环境关闭调试输出
"""

# config/environments/staging.yaml - 预发布环境配置
YAML_STAGING_TEMPLATE = """# =============================================================================
# 预发布环境配置（v3.38.6）
#
# 继承: base.yaml（自动深度合并）
# 使用: pytest tests/ --env=staging
#
# 说明: 接近生产环境的配置，用于最终验证
# =============================================================================

env: staging

http:
  base_url: https://staging-api.example.com/api
  timeout: 30

logging:
  level: INFO
  format: json          # 预发布环境使用 JSON 格式
  use_utc: true         # 使用 UTC 时间戳
  # 脱敏默认启用，无需配置

observability:
  debug_output: false
"""

# config/environments/prod.yaml - 生产环境配置
YAML_PROD_TEMPLATE = """# =============================================================================
# 生产环境配置（v3.38.6）
#
# ⚠️ 警告: 生产环境配置，请勿泄露敏感信息！
# 继承: base.yaml（自动深度合并）
# 使用: pytest tests/ --env=prod -m smoke
#
# 说明: 仅运行冒烟测试，确保核心功能正常
# =============================================================================

env: prod

http:
  base_url: https://api.example.com/api
  timeout: 30

logging:
  level: WARNING        # 生产环境只记录警告及以上
  format: json          # 生产环境使用 JSON 格式
  use_utc: true         # 使用 UTC 时间戳（ISO 8601）
  file: logs/test.log   # 日志文件
  rotation: "500 MB"    # 日志轮转
  retention: "30 days"  # 日志保留
  # 脱敏默认启用，无需配置

observability:
  debug_output: false   # 生产环境禁止调试输出
  allure_recording: true
"""

# config/environments/local.yaml - 本地调试配置
YAML_LOCAL_TEMPLATE = """# =============================================================================
# 本地调试配置（v3.38.6）
#
# ⚠️ 此文件不应提交到版本控制（已在 .gitignore 中排除）
#
# 继承: dev（使用开发环境作为基础，覆盖调试选项）
# 使用: pytest tests/ --env=local --log-cli-level=DEBUG -v -s
#
# 快速调试命令:
#   pytest tests/ --env=local -v                    # 普通模式
#   pytest tests/ --env=local --log-cli-level=DEBUG -v -s  # DEBUG日志+调试输出
#   pytest tests/test_example.py --env=local --pdb -v -s   # 失败时进入调试器
#
# 详见: docs/guides/local_debug_quickstart.md
# =============================================================================

# 继承 dev 环境配置
_extends: environments/dev.yaml
env: local
debug: true

# 日志配置（本地调试）
logging:
  level: DEBUG         # DEBUG 级别日志
  format: text         # 彩色文本输出

# 本地调试时关闭脱敏，查看完整数据
sanitize:
  console:
    enabled: false

# 可观测性配置
observability:
  debug_output: true   # 启用调试输出（显示请求/响应详情）

# 测试配置
test:
  keep_test_data: true # 保留测试数据便于调试
  # repository_package: {project_name}.repositories  # UoW 自动发现 Repository
  # apis_package: {project_name}.apis                # API 自动发现（@api_class）
"""

# config/secrets/.env.local - 敏感信息配置
SECRETS_ENV_LOCAL_TEMPLATE = """# =============================================================================
# 敏感信息配置（本地）- v3.38.6
#
# ⚠️ 此文件不应提交到版本控制（已在 .gitignore 中排除）
# 用于存储密码、API密钥等敏感信息
#
# 配置优先级（从高到低）:
#   1. 环境变量
#   2. config/secrets/.env.local（本文件）
#   3. config/environments/{env}.yaml
#   4. config/base.yaml
# =============================================================================

# ============================================================
# 调试配置（可选，也可在 local.yaml 中配置）
# ============================================================
# 启用调试输出（需要 pytest -s 显示输出）
# OBSERVABILITY__DEBUG_OUTPUT=true
# 日志级别
# LOGGING__LEVEL=DEBUG

# ============================================================
# 签名密钥
# ============================================================
# SIGNATURE__SECRET=your_secret_key

# ============================================================
# 数据库密码
# ============================================================
# DB__PASSWORD=your_db_password

# ============================================================
# Redis 密码
# ============================================================
# REDIS__PASSWORD=your_redis_password

# ============================================================
# Token 凭证
# ============================================================
# BEARER_TOKEN__CREDENTIALS__PASSWORD=your_login_password
"""

# ============================================================
# .env 配置模板（回退模式）
# ============================================================

# .env - 基础配置模板
ENV_BASE_TEMPLATE = """# =============================================================================
# 项目环境配置文件（.env 回退模式）
#
# 推荐使用 YAML 配置: df-test gen settings --with-yaml
# 生成时间: {timestamp}
#
# v3.38.6 配置说明:
# - 推荐使用 YAML 配置（config/base.yaml + config/environments/*.yaml）
# - 此 .env 文件作为回退模式，当 config/ 目录不存在时使用
# - 无 APP_ 前缀（v3.34.1+）
# - 使用 __ 嵌套分隔符（HTTP__BASE_URL）
#
# 切换环境:
#   ENV=dev pytest    # 使用开发环境
#   ENV=test pytest   # 使用测试环境
#   ENV=prod pytest   # 使用生产环境
# =============================================================================

# ============================================================
# 基础配置
# ============================================================
ENV=dev

# ============================================================
# HTTP 配置
# ============================================================
HTTP__BASE_URL=http://localhost:8000/api
HTTP__TIMEOUT=30
HTTP__MAX_RETRIES=3

# ============================================================
# 可观测性配置
# ============================================================
OBSERVABILITY__ENABLED=true
OBSERVABILITY__DEBUG_OUTPUT=false
OBSERVABILITY__ALLURE_RECORDING=true

# ============================================================
# 签名中间件配置（可选）
# ============================================================
# SIGNATURE__ENABLED=true
# SIGNATURE__ALGORITHM=md5
# SIGNATURE__SECRET=change_me_in_production

# ============================================================
# Token 中间件配置（可选）
# ============================================================
# BEARER_TOKEN__ENABLED=true
# BEARER_TOKEN__SOURCE=login
# BEARER_TOKEN__LOGIN_URL=/auth/login
# BEARER_TOKEN__CREDENTIALS__USERNAME=admin
# BEARER_TOKEN__CREDENTIALS__PASSWORD=admin123

# ============================================================
# 数据库配置（可选）
# ============================================================
# DB__HOST=localhost
# DB__PORT=3306
# DB__NAME=test_db
# DB__USER=root
# DB__PASSWORD=password
# DB__POOL_SIZE=10
# DB__CHARSET=utf8mb4

# ============================================================
# Redis 配置（可选）
# ============================================================
# REDIS__HOST=localhost
# REDIS__PORT=6379
# REDIS__PASSWORD=
# REDIS__DB=0

# ============================================================
# 日志配置（v3.38.6 最佳实践）
# ============================================================
LOGGING__LEVEL=INFO
LOGGING__FORMAT=text
# LOGGING__USE_UTC=false       # 生产环境建议启用 UTC 时间戳
# LOGGING__ADD_CALLSITE=false  # 调试时启用，添加文件名/函数名/行号
# LOGGING__FILE=logs/app.log   # 日志文件路径

# 脱敏配置（v3.40.0+ 默认启用，仅在需要关闭时配置）
# SANITIZE__CONSOLE__ENABLED=false  # 本地调试时关闭控制台脱敏

# ============================================================
# 测试配置
# ============================================================
# TEST__KEEP_TEST_DATA=false   # 设为 true 保留测试数据（调试用）
# TEST__REPOSITORY_PACKAGE={project_name}.repositories  # UoW 自动发现 Repository
# TEST__APIS_PACKAGE={project_name}.apis                # API 自动发现（@api_class）

# ============================================================
# 数据清理配置（v3.18.0+ 配置驱动清理）
# ============================================================
# CLEANUP__ENABLED=true
# CLEANUP__MAPPINGS__orders__table=order_table
# CLEANUP__MAPPINGS__orders__field=order_no
# CLEANUP__MAPPINGS__users__table=user_table
# CLEANUP__MAPPINGS__users__field=user_id

# ============================================================
# 业务配置
# ============================================================
BUSINESS_TEST_USER_ID=test_user_001
BUSINESS_TEST_ROLE=admin
"""

# .env.dev - 开发环境配置
ENV_DEV_TEMPLATE = """# =============================================================================
# 开发环境配置（.env 回退模式）- v3.38.6
#
# 优先级: 高于 .env，低于 .env.local
# 使用方式: ENV=dev pytest
# =============================================================================

ENV=dev

HTTP__BASE_URL=http://dev-api.example.com/api
HTTP__TIMEOUT=60

LOGGING__LEVEL=DEBUG
LOGGING__FORMAT=text
LOGGING__ADD_CALLSITE=true
OBSERVABILITY__DEBUG_OUTPUT=true

# 签名密钥（开发环境）
# SIGNATURE__SECRET=dev_secret_key_12345

# 数据库配置（开发环境）
# DB__HOST=dev-mysql.example.com
# DB__NAME=dev_test_db
# DB__USER=dev_user
# DB__PASSWORD=dev_password
"""

# .env.test - 测试环境配置
ENV_TEST_TEMPLATE = """# =============================================================================
# 测试环境配置（.env 回退模式）- v3.38.6
#
# 优先级: 高于 .env，低于 .env.local
# 使用方式: ENV=test pytest
# 说明: 这是 CI/CD 环境的默认配置
# =============================================================================

ENV=test

HTTP__BASE_URL=http://test-api.example.com/api
HTTP__TIMEOUT=30

LOGGING__LEVEL=INFO
LOGGING__FORMAT=text
OBSERVABILITY__DEBUG_OUTPUT=false

# 签名密钥（测试环境）
# SIGNATURE__SECRET=test_secret_key_12345

# 数据库配置（测试环境）
# DB__HOST=test-mysql.example.com
# DB__NAME=test_db
# DB__USER=test_user
# DB__PASSWORD=test_password
"""

# .env.prod - 生产环境配置
ENV_PROD_TEMPLATE = """# =============================================================================
# 生产环境配置（.env 回退模式）- v3.38.6
#
# ⚠️ 警告: 生产环境配置，请勿泄露敏感信息！
# 优先级: 高于 .env，低于 .env.local
# 使用方式: ENV=prod pytest -m smoke
# 说明: 仅运行冒烟测试，确保核心功能正常
# =============================================================================

ENV=prod

HTTP__BASE_URL=https://api.example.com/api
HTTP__TIMEOUT=30

LOGGING__LEVEL=WARNING
LOGGING__FORMAT=json
LOGGING__USE_UTC=true
LOGGING__FILE=logs/test.log
OBSERVABILITY__DEBUG_OUTPUT=false
# 脱敏默认启用，无需配置

# 签名密钥（生产环境）
# SIGNATURE__SECRET=CHANGE_ME_STRONG_SECRET

# 数据库配置（生产环境）
# DB__HOST=prod-mysql.example.com
# DB__NAME=prod_db
# DB__USER=prod_user
# DB__PASSWORD=CHANGE_ME_STRONG_PASSWORD
"""

# .env.example - 配置示例（用于版本控制）
ENV_EXAMPLE_TEMPLATE = """# =============================================================================
# 环境配置示例文件（.env 回退模式）
#
# 推荐使用 YAML 配置: df-test gen settings --with-yaml
#
# 使用说明:
# 1. 复制此文件为 .env
# 2. 修改配置值
# 3. .env 文件不应提交到版本控制
# =============================================================================

# ============================================================
# 基础配置
# ============================================================
ENV=dev

# ============================================================
# HTTP 配置
# ============================================================
HTTP__BASE_URL=http://localhost:8000/api
HTTP__TIMEOUT=30
HTTP__MAX_RETRIES=3

# ============================================================
# 可观测性配置
# ============================================================
OBSERVABILITY__ENABLED=true
OBSERVABILITY__DEBUG_OUTPUT=false
OBSERVABILITY__ALLURE_RECORDING=true

# ============================================================
# 签名中间件配置（可选）
# ============================================================
# SIGNATURE__ENABLED=true
# SIGNATURE__ALGORITHM=md5
# SIGNATURE__SECRET=your_secret_key_here

# ============================================================
# Token 中间件配置（可选）
# ============================================================
# BEARER_TOKEN__ENABLED=true
# BEARER_TOKEN__SOURCE=login
# BEARER_TOKEN__LOGIN_URL=/auth/login
# BEARER_TOKEN__CREDENTIALS__USERNAME=your_username
# BEARER_TOKEN__CREDENTIALS__PASSWORD=your_password

# ============================================================
# 数据库配置（可选）
# ============================================================
# DB__HOST=localhost
# DB__PORT=3306
# DB__NAME=your_database
# DB__USER=your_username
# DB__PASSWORD=your_password

# ============================================================
# Redis 配置（可选）
# ============================================================
# REDIS__HOST=localhost
# REDIS__PORT=6379
# REDIS__PASSWORD=
# REDIS__DB=0
"""

__all__ = [
    # YAML 配置模板（v3.35.0+ 推荐）
    "YAML_BASE_TEMPLATE",
    "YAML_DEV_TEMPLATE",
    "YAML_TEST_TEMPLATE",
    "YAML_STAGING_TEMPLATE",
    "YAML_PROD_TEMPLATE",
    "YAML_LOCAL_TEMPLATE",
    "SECRETS_ENV_LOCAL_TEMPLATE",
    # .env 配置模板（回退模式）
    "ENV_BASE_TEMPLATE",
    "ENV_DEV_TEMPLATE",
    "ENV_TEST_TEMPLATE",
    "ENV_PROD_TEMPLATE",
    "ENV_EXAMPLE_TEMPLATE",
]
