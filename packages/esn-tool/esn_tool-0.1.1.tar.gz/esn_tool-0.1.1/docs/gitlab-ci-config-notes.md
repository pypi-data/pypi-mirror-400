# GitLab CI 配置注释说明

## Release 镜像配置选项

`.gitlab-ci.yml` 中 `release` 阶段的 `image` 配置有三个选项：

### 选项 1: 官方镜像（公有 GitLab）
```yaml
image: registry.gitlab.com/gitlab-org/release-cli:latest
```
- ✅ 适用于：可以访问 gitlab.com 的环境
- ❌ 不适用于：私有部署的 GitLab（无外网访问）

### 选项 2: Registry Mirror（推荐给私有 GitLab）
```yaml
image: ${CI_REGISTRY}/mirrors/gitlab-org/release-cli:latest
```
- ✅ 适用于：配置了 Registry Mirror 的私有 GitLab
- 需要先在私有 Registry 中导入镜像

### 选项 3: 禁用 Release 功能
注释掉整个 `release` 阶段：
```yaml
# release:
#   stage: release
#   ...
```
- ✅ 适用于：不需要自动 Release 的场景
- 手动从 Pipeline Artifacts 下载即可

## 当前配置

当前 `.gitlab-ci.yml` 使用**选项 2**，请根据您的环境选择：

- **有 Registry Mirror**：保持当前配置
- **无 Registry Mirror**：改用选项 3（注释掉 release）
- **公有 GitLab**：改用选项 1

## 如何选择？

快速判断：
```bash
# 测试是否可以 pull 官方镜像
docker pull registry.gitlab.com/gitlab-org/release-cli:latest

# 成功 → 使用选项 1
# 失败 → 使用选项 2 或 3
```
