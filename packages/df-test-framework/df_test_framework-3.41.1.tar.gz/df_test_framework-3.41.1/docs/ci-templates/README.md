# CI/CD 模板

本目录包含 DF Test Framework 的 CI/CD 配置模板，可直接用于项目集成。

## 可用模板

| 模板 | 平台 | 说明 |
|------|------|------|
| [github-actions.yml](github-actions.yml) | GitHub Actions | 完整的 CI/CD 流水线 |
| [gitlab-ci.yml](gitlab-ci.yml) | GitLab CI/CD | 完整的 CI/CD 流水线 |

## 功能特性

两个模板都包含以下功能：

- **代码质量检查**: Ruff 代码检查和格式验证
- **多 Python 版本测试**: Python 3.12 / 3.13
- **多环境测试**: dev / staging / prod
- **测试覆盖率**: 生成覆盖率报告
- **Allure 报告**: 生成并发布 Allure 测试报告
- **安全审计**: 依赖安全检查
- **构建验证**: 包构建和安装验证

## 使用方法

### GitHub Actions

1. 复制 `github-actions.yml` 到项目的 `.github/workflows/ci.yml`
2. 在 GitHub 仓库设置中配置 Secrets：
   - `DEV_API_URL`: 开发环境 API 地址
   - `STAGING_API_URL`: 预发布环境 API 地址
   - `PROD_API_URL`: 生产环境 API 地址
   - `DB_PASSWORD`: 数据库密码
3. 推送代码触发流水线

```bash
# 复制模板
cp docs/ci-templates/github-actions.yml .github/workflows/ci.yml

# 提交
git add .github/workflows/ci.yml
git commit -m "ci: 添加 GitHub Actions CI/CD 流水线"
git push
```

### GitLab CI/CD

1. 复制 `gitlab-ci.yml` 到项目根目录并重命名为 `.gitlab-ci.yml`
2. 在 GitLab 项目设置 > CI/CD > Variables 中配置：
   - `DEV_API_URL`: 开发环境 API 地址
   - `STAGING_API_URL`: 预发布环境 API 地址
   - `PROD_API_URL`: 生产环境 API 地址
   - `DB_PASSWORD`: 数据库密码（设为 Protected + Masked）
3. 推送代码触发流水线

```bash
# 复制模板
cp docs/ci-templates/gitlab-ci.yml .gitlab-ci.yml

# 提交
git add .gitlab-ci.yml
git commit -m "ci: 添加 GitLab CI/CD 流水线"
git push
```

## 流水线说明

### 阶段

```
lint → test → report → deploy
```

### 触发条件

| 事件 | lint | test | 环境测试 | Allure 报告 |
|------|------|------|----------|-------------|
| Push to main | ✅ | ✅ | ✅ | ✅ |
| Push to develop | ✅ | ✅ | ❌ | ❌ |
| Pull/Merge Request | ✅ | ✅ | ❌ | ❌ |
| 手动触发 | ✅ | ✅ | ✅ | ✅ |
| 定时任务 | ❌ | ✅ | ❌ | ✅ |

### 环境测试

- **test**: 默认环境，本地/CI 测试
- **dev**: 开发环境测试
- **staging**: 预发布环境测试
- **prod**: 生产环境冒烟测试（手动触发）

## 自定义配置

### 修改 Python 版本

```yaml
# GitHub Actions
env:
  PYTHON_VERSION: "3.12"

# GitLab CI
image: python:3.12-slim
```

### 添加额外环境变量

```yaml
# GitHub Actions
env:
  ENV: staging
  HTTP__BASE_URL: ${{ secrets.STAGING_API_URL }}
  CUSTOM_VAR: ${{ secrets.CUSTOM_VAR }}

# GitLab CI
variables:
  TEST_ENV: "staging"
  HTTP__BASE_URL: $STAGING_API_URL
  CUSTOM_VAR: $CUSTOM_VAR
```

### 修改测试命令

```yaml
# 添加标记筛选
uv run pytest tests/ -m "smoke and not slow"

# 排除特定目录
uv run pytest tests/ --ignore=tests/integration/

# 并行执行
uv run pytest tests/ -n auto
```

### 添加服务依赖

```yaml
# GitHub Actions
services:
  mysql:
    image: mysql:8.0
    env:
      MYSQL_ROOT_PASSWORD: test
      MYSQL_DATABASE: test_db
    ports:
      - 3306:3306

# GitLab CI
services:
  - name: mysql:8.0
    alias: mysql
    variables:
      MYSQL_ROOT_PASSWORD: test
      MYSQL_DATABASE: test_db
```

## Allure 报告

### GitHub Actions

Allure 报告自动发布到 GitHub Pages：
- URL: `https://<username>.github.io/<repo>/`
- 需要在仓库设置中启用 GitHub Pages，Source 选择 `gh-pages` 分支

### GitLab CI

Allure 报告自动发布到 GitLab Pages：
- URL: `https://<username>.gitlab.io/<repo>/`
- 需要项目启用 Pages 功能

## 最佳实践

1. **敏感信息**: 所有密码、API 密钥等敏感信息使用 Secrets/Variables
2. **环境隔离**: 不同环境使用不同的配置和数据库
3. **并发控制**: 同一分支只保留最新的运行（GitHub Actions 已配置）
4. **缓存优化**: 使用 uv 缓存加速依赖安装
5. **失败通知**: 配置 Slack/邮件通知（需自行添加）

## 相关文档

- [环境配置指南](../guides/env_config_guide.md)
- [测试执行配置](../guides/test_data.md)
- [Allure 报告集成](../guides/telemetry_guide.md)
