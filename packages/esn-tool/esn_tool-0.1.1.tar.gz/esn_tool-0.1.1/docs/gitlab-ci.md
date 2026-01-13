# GitLab CI/CD 配置说明

## 概述

本项目使用 GitLab CI/CD 自动构建 macOS 两个架构的 PKG 安装包：
- **ARM64** (Apple Silicon: M1/M2/M3)
- **x86_64** (Intel)

## 前置要求

### 1. 配置 GitLab Runners

您需要在 GitLab 项目中配置两个 macOS Runner，分别对应两种架构：

#### ARM64 Runner 配置

**方式 1：使用提供的注册脚本（推荐）**

```bash
# 1. 安装 GitLab Runner
brew install gitlab-runner

# 2. 编辑脚本，填入 Registration Token
vim scripts/register-gitlab-runner.sh
# 将 REGISTRATION_TOKEN 改为从 GitLab 获取的实际 Token

# 3. 运行注册脚本
./scripts/register-gitlab-runner.sh

# 4. 启动 Runner
brew services start gitlab-runner

# 5. 验证
gitlab-runner list
```

**方式 2：手动注册**

```bash
# 在 M1/M2/M3 Mac 上安装 GitLab Runner
brew install gitlab-runner

# 注册 Runner（替换为您私有 GitLab 的地址）
gitlab-runner register \
  --url https://git.yyrd.com/ \
  --registration-token YOUR_TOKEN \
  --executor shell \
  --description "macOS ARM64 Runner" \
  --tag-list "macos,arm64"

# 启动 Runner
brew services start gitlab-runner
```

> 💡 **私有 GitLab 注意事项**：
> - 将 `git.yyrd.com` 替换为您的 GitLab 实例地址
> - Token 从 **Settings → CI/CD → Runners** 获取
> - 如果使用自签名证书，需要配置 TLS：
>   ```bash
>   gitlab-runner register --tls-ca-file /path/to/ca.crt
>   ```

> 📝 **验证 Runner 状态**：
> ```bash
> # 查看已注册的 Runner
> gitlab-runner list
> 
> # 示例输出：
> # macOS ARM64 Runner - hostname  Executor=shell Token=xxx URL=https://git.yyrd.com/
> ```

#### x86_64 Runner 配置

在 Intel Mac 上执行类似的步骤：

```bash
# 安装 GitLab Runner
brew install gitlab-runner

# 注册（注意标签改为 x86_64）
gitlab-runner register \
  --url https://git.yyrd.com/ \
  --registration-token YOUR_TOKEN \
  --executor shell \
  --description "macOS x86_64 Runner" \
  --tag-list "macos,x86_64"

# 启动
brew services start gitlab-runner
```

> 💡 如果只有 M1 Mac，可以暂时只配置 ARM64 Runner，x86_64 包可以稍后在有 Intel Mac 时再构建。

### 2. Runner 环境准备

在每个 Runner 的 Mac 上安装必要的工具：

```bash
# 安装 uv（Python 包管理器）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 验证安装
uv --version

# 安装 Xcode Command Line Tools（用于 pkgbuild）
xcode-select --install
```

## 私有 GitLab 特殊配置

### 1. Release CLI 镜像配置

私有 GitLab 可能无法直接访问 `registry.gitlab.com`，有以下解决方案：

#### 方案 A：使用私有 Registry Mirror（推荐）

如果您的 GitLab 有配置 Registry Mirror：

编辑 `.gitlab-ci.yml`：
```yaml
release:
  image: ${CI_REGISTRY}/mirrors/gitlab-org/release-cli:latest
```

#### 方案 B：手动导入镜像

在有外网访问的机器上：
```bash
# 拉取镜像
docker pull registry.gitlab.com/gitlab-org/release-cli:latest

# 重新标记
docker tag registry.gitlab.com/gitlab-org/release-cli:latest \
  your-gitlab.com:5050/mirrors/gitlab-org/release-cli:latest

# 推送到私有 Registry
docker push your-gitlab.com:5050/mirrors/gitlab-org/release-cli:latest
```

#### 方案 C：禁用自动 Release（最简单）

如果不需要自动创建 Release，可以注释掉 release 阶段：

```yaml
# release:
#   stage: release
#   ...
```

手动从 Pipeline Artifacts 下载构建产物即可。

### 2. 自签名证书配置

如果私有 GitLab 使用自签名 SSL 证书：

```bash
# 下载 CA 证书
curl -o /usr/local/share/ca-certificates/gitlab.crt \
  https://your-gitlab.com/path/to/ca.crt

# 更新证书信任（macOS）
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain \
  /usr/local/share/ca-certificates/gitlab.crt

# 注册 Runner 时指定 CA
gitlab-runner register --tls-ca-file /path/to/ca.crt
```

### 3. 网络代理配置

如果 Runner 需要通过代理访问 GitLab：

编辑 `/usr/local/etc/gitlab-runner/config.toml`：
```toml
[[runners]]
  environment = ["HTTPS_PROXY=proxy.example.com:8080"]
```

重启 Runner：
```bash
gitlab-runner restart
```

## CI/CD 流程

### 触发条件

CI 流程会在以下情况自动触发：
- ✅ 推送到 `main` 分支
- ✅ 推送到 `develop` 分支
- ✅ 创建 Tag（会自动发布 Release）
- ✅ 创建 Merge Request
- ✅ 手动触发（Web UI）

### 构建阶段

#### Stage 1: Build
并行构建两个架构：

**build:macos:arm64**
- Runner: 带 `macos` 和 `arm64` 标签的 Runner
- 输出: `dist/esn-{version}-arm64.pkg`

**build:macos:x86_64**
- Runner: 带 `macos` 和 `x86_64` 标签的 Runner
- 输出: `dist/esn-{version}-x86_64.pkg`

#### Stage 2: Release（仅 Tag 触发）
- 创建 GitLab Release
- 附加两个架构的 PKG 文件
- 生成发布说明

## 使用方式

### 开发分支构建

正常开发推送即可自动触发构建：

```bash
git add .
git commit -m "feat: add new feature"
git push origin feature-branch
```

### 发布新版本

1. 更新版本号（在 `pyproject.toml` 中）
2. 创建并推送 tag：

```bash
# 更新版本
vim pyproject.toml  # version = "0.2.0"

# 提交版本更新
git add pyproject.toml
git commit -m "chore: bump version to 0.2.0"

# 创建 tag
git tag v0.2.0

# 推送（会自动触发构建和发布）
git push origin main --tags
```

### 手动触发构建

在 GitLab Web UI 中：
1. 进入 **CI/CD → Pipelines**
2. 点击 **Run Pipeline**
3. 选择分支
4. 点击 **Run Pipeline**

## 下载构建产物

### 从 Pipeline Artifacts

1. 进入 **CI/CD → Pipelines**
2. 选择对应的 Pipeline
3. 点击 **build:macos:arm64** 或 **build:macos:x86_64**
4. 在右侧点击 **Browse** 或 **Download** artifacts

### 从 Release（仅 Tag）

1. 进入 **Deployments → Releases**
2. 选择对应版本
3. 下载 PKG 文件

## 常见问题

### Q: Runner 无法找到？

**A:** 检查 Runner 标签配置：

```bash
# 查看已注册的 Runner
gitlab-runner list

# 验证标签
# 确保 ARM64 Runner 有 tags: macos, arm64
# 确保 x86_64 Runner 有 tags: macos, x86_64
```

### Q: 构建失败：找不到 uv？

**A:** 在 Runner 的环境中安装 uv：

```bash
# SSH 到 Runner 所在的 Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# 确保 PATH 正确
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Q: 只想构建一个架构？

**A:** 修改 `.gitlab-ci.yml`，注释掉不需要的任务：

```yaml
# 如果只需要 ARM64
# build:macos:x86_64:
#   extends: .build_macos
#   ...
```

### Q: 如何修改触发条件？

**A:** 编辑 `.gitlab-ci.yml` 中的 `rules` 部分：

```yaml
rules:
  - if: '$CI_COMMIT_BRANCH == "main"'  # 只在 main 分支触发
```

## 优化建议

### 加速构建

CI 已配置缓存来加速构建：
- UV 缓存: `.cache/uv`
- 虚拟环境: `.venv`

### 节省 Runner 资源

如果 Runner 资源有限，可以：
1. 限制并发构建数量
2. 只在必要时触发（如只在 tag 时构建）
3. 设置 artifact 过期时间（默认 30 天）

### 自定义 Release 说明

编辑 `.gitlab-ci.yml` 中的 `release.description` 部分：

```yaml
release:
  description: |
    ## 发布说明
    
    ### 新功能
    - Feature 1
    - Feature 2
    
    ### Bug 修复
    - Fix 1
```

## 监控和通知

可以配置 GitLab 通知：
1. **项目设置 → Integrations**
2. 配置 Email/Slack/钉钉等通知
3. 选择通知事件（Pipeline 成功/失败）

## 参考资料

- [GitLab Runner 文档](https://docs.gitlab.com/runner/)
- [GitLab CI/CD 配置参考](https://docs.gitlab.com/ee/ci/yaml/)
- [项目打包文档](packaging.md)
