#!/bin/bash
#
# GitLab Release 创建脚本
# 使用 GitLab API 创建 Release 并附加产物链接
#

set -e

# 检查必要的环境变量
: "${CI_COMMIT_TAG:?需要 CI_COMMIT_TAG 环境变量}"
: "${CI_PROJECT_ID:?需要 CI_PROJECT_ID 环境变量}"
: "${CI_API_V4_URL:?需要 CI_API_V4_URL 环境变量}"
: "${CI_PROJECT_URL:?需要 CI_PROJECT_URL 环境变量}"

# 优先使用 GITLAB_TOKEN，回退到 CI_JOB_TOKEN
if [ -n "${GITLAB_TOKEN}" ]; then
  AUTH_TOKEN="${GITLAB_TOKEN}"
  echo "ℹ️  使用 GITLAB_TOKEN 进行认证"
elif [ -n "${CI_JOB_TOKEN}" ]; then
  AUTH_TOKEN="${CI_JOB_TOKEN}"
  echo "ℹ️  使用 CI_JOB_TOKEN 进行认证（可能权限不足）"
else
  echo "❌ 错误: 需要 GITLAB_TOKEN 或 CI_JOB_TOKEN 环境变量"
  exit 1
fi

echo "🚀 创建 Release: ${CI_COMMIT_TAG}"

# 从 tag 中提取版本号（去掉 v 前缀）
VERSION="${CI_COMMIT_TAG#v}"  # 如果 tag 是 v0.1.0，VERSION 就是 0.1.0

# 构建下载链接
# 私有 GitLab 使用基于 ref 的 artifacts 下载更可靠
PKG_URL="${CI_PROJECT_URL}/-/jobs/artifacts/${CI_COMMIT_TAG}/raw/dist/esn-${VERSION}-arm64.pkg?job=build:macos:arm64"

# 说明文字
echo "📦 版本: ${VERSION}"
echo "🔗 下载链接: ${PKG_URL}"

# 创建 Release 描述（使用 heredoc）
read -r -d '' DESCRIPTION << EOM || true
## ESN Tool ${CI_COMMIT_TAG}

### 📦 下载安装包

**ARM64** (M1/M2/M3 Mac): [esn-${VERSION}-arm64.pkg](${PKG_URL})

> 💡 如果上面的链接无法下载，请：
> 1. 访问 [Pipeline Artifacts](${CI_PROJECT_URL}/-/pipelines/${CI_PIPELINE_ID})
> 2. 点击 \`build:macos:arm64\` 作业
> 3. 下载 artifacts 中的 \`dist/esn-${VERSION}-arm64.pkg\`

### 安装方式
\`\`\`bash
sudo installer -pkg esn-${VERSION}-arm64.pkg -target /
\`\`\`

### 卸载方式
\`\`\`bash
sudo /usr/local/share/esntool/uninstall.sh
\`\`\`
EOM

# 使用 jq 构建 JSON payload
PAYLOAD=$(jq -n \
  --arg tag "${CI_COMMIT_TAG}" \
  --arg name "Release ${CI_COMMIT_TAG}" \
  --arg desc "${DESCRIPTION}" \
  --arg pkg_name "esn-${VERSION}-arm64.pkg" \
  --arg pkg_url "${PKG_URL}" \
  '{
    tag_name: $tag,
    name: $name,
    description: $desc,
    assets: {
      links: [
        {
          name: $pkg_name,
          url: $pkg_url,
          link_type: "package"
        }
      ]
    }
  }')

# 调用 GitLab API 创建 Release
HTTP_CODE=$(curl --silent --output /tmp/release_response.json --write-out "%{http_code}" \
  --request POST \
  --header "PRIVATE-TOKEN: ${AUTH_TOKEN}" \
  --header "Content-Type: application/json" \
  --data "${PAYLOAD}" \
  "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/releases")

# 检查响应
if [ "${HTTP_CODE}" = "201" ]; then
  echo "✅ Release ${CI_COMMIT_TAG} 创建成功"
  echo ""
  echo "🔗 查看 Release:"
  echo "   ${CI_PROJECT_URL}/-/releases/${CI_COMMIT_TAG}"
  exit 0
else
  echo "❌ Release 创建失败 (HTTP ${HTTP_CODE})"
  echo ""
  echo "响应内容:"
  cat /tmp/release_response.json | jq '.' || cat /tmp/release_response.json
  exit 1
fi
