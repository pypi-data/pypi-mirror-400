#!/bin/bash
# 快速修复：为 Runner 添加标签

echo "🔧 注销当前 Runner..."
gitlab-runner unregister --name "macOS ARM64 Runner - liuyingwendeMacBook-Pro.local"

echo ""
echo "📝 重新注册 Runner（带标签）..."
gitlab-runner register \
  --non-interactive \
  --url "https://git.yyrd.com/" \
  --registration-token "GR1348941M7oV7pjwGxbNsoKLVTaQ" \
  --executor shell \
  --description "macOS ARM64 Runner - $(hostname)" \
  --tag-list "macos,arm64"

echo ""
echo "✅ Runner 已重新注册并添加标签"
echo ""
echo "验证："
gitlab-runner list

echo ""
echo "重启 Runner 服务："
brew services restart gitlab-runner
