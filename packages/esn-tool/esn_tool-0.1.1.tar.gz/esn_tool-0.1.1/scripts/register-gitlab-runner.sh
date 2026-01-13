#!/bin/bash
#
# GitLab Runner 注册脚本 - ARM64 (M1/M2/M3 Mac)
# 请先配置以下变量，然后运行此脚本
#

# ====== 配置区域 ======
# 您的私有 GitLab 实例地址
GITLAB_URL="https://git.yyrd.com/"

# Runner 注册 Token（从 GitLab Settings → CI/CD → Runners 获取）
REGISTRATION_TOKEN="GR1348941M7oV7pjwGxbNsoKLVTaQ"

# Runner 描述
RUNNER_DESCRIPTION="macOS ARM64 Runner - $(hostname)"

# Runner 标签（用于匹配 CI 任务）
RUNNER_TAGS="macos,arm64"

# 可选：如果使用自签名证书，设置 CA 证书路径
# TLS_CA_FILE="/path/to/ca.crt"
TLS_CA_FILE=""

# ====== 脚本开始 ======

echo "════════════════════════════════════════════════════════"
echo "  GitLab Runner 注册脚本 (ARM64)"
echo "════════════════════════════════════════════════════════"
echo ""

# 检查配置
if [ "$REGISTRATION_TOKEN" = "YOUR_REGISTRATION_TOKEN_HERE" ]; then
    echo "❌ 错误: 请先配置 REGISTRATION_TOKEN"
    echo ""
    echo "获取步骤:"
    echo "  1. 打开 GitLab: $GITLAB_URL"
    echo "  2. 进入项目 Settings → CI/CD → Runners"
    echo "  3. 复制 Registration Token"
    echo "  4. 编辑此脚本，替换 REGISTRATION_TOKEN 的值"
    echo ""
    exit 1
fi

# 构建注册命令
CMD="gitlab-runner register \
  --non-interactive \
  --url '$GITLAB_URL' \
  --registration-token '$REGISTRATION_TOKEN' \
  --executor shell \
  --description '$RUNNER_DESCRIPTION' \
  --tag-list '$RUNNER_TAGS'"

# 如果配置了 TLS CA，添加参数
if [ -n "$TLS_CA_FILE" ]; then
    CMD="$CMD --tls-ca-file '$TLS_CA_FILE'"
fi

echo "📝 注册信息:"
echo "  URL: $GITLAB_URL"
echo "  描述: $RUNNER_DESCRIPTION"
echo "  标签: $RUNNER_TAGS"
echo ""

# 执行注册
echo "🚀 开始注册..."
eval $CMD

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Runner 注册成功!"
    echo ""
    echo "下一步:"
    echo "  1. 启动 Runner:"
    echo "     brew services start gitlab-runner"
    echo ""
    echo "  2. 查看 Runner 状态:"
    echo "     gitlab-runner list"
    echo ""
    echo "  3. 在 GitLab 中验证 Runner 已激活:"
    echo "     $GITLAB_URL/your-project/-/settings/ci_cd"
else
    echo ""
    echo "❌ 注册失败"
    echo ""
    echo "故障排查:"
    echo "  - 检查 GitLab URL 是否正确"
    echo "  - 检查 Registration Token 是否有效"
    echo "  - 如果使用自签名证书，确保 TLS_CA_FILE 正确"
    echo ""
    exit 1
fi
