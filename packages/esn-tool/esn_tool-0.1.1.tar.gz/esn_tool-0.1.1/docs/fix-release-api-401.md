# 修复 GitLab Release API 权限问题

## 问题
Release 创建失败，显示 `401 Unauthorized`。

## 原因
`CI_JOB_TOKEN` 在某些 GitLab 版本中没有创建 Release 的权限。

## 解决方案

### 方式 1：使用 Project Access Token（推荐）

1. **创建 Project Access Token**：
   - 访问：`https://git.yyrd.com/esn_tool/esn-command-line/-/settings/access_tokens`
   - Name: `ci-release-token`
   - Role: `Maintainer` 或 `Developer`
   - Scopes: 勾选 `api`
   - Expiration: 设置过期时间（或留空不过期）
   - 点击 **Create project access token**
   - **复制生成的 Token**（只显示一次）

2. **添加 CI/CD 变量**：
   - 访问：`https://git.yyrd.com/esn_tool/esn-command-line/-/settings/ci_cd`
   - 展开 **Variables** 部分
   - 点击 **Add variable**
   - Key: `GITLAB_TOKEN`
   - Value: 刚才复制的 Token
   - Protected: ✅
   - Masked: ✅
   - 点击 **Add variable**

3. **修改脚本使用新的 Token**：
   编辑 `scripts/create-release.sh`，将：
   ```bash
   --header "PRIVATE-TOKEN: ${CI_JOB_TOKEN}"
   ```
   改为：
   ```bash
   --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}"
   ```

### 方式 2：启用 CI_JOB_TOKEN 权限（如果 GitLab 版本支持）

1. 访问：`https://git.yyrd.com/esn_tool/esn-command-line/-/settings/ci_cd`
2. 展开 **Token Access** 部分
3. 查找并启用 Release 相关权限

### 方式 3：简化方案 - 只使用 Artifacts（无需 Token）

如果不想配置 Token，可以禁用自动 Release：
- 从 Artifacts 手动下载 PKG
- 或者手动创建 Release 并上传文件

## 推荐步骤

使用 **方式 1**（最可靠）：
1. 创建 Project Access Token
2. 添加为 CI/CD 变量
3. 修改脚本使用新 Token
4. 重新运行 Pipeline
