#!/bin/bash
# Memory MCP 包构建和发布脚本 - 使用 uv

set -e

# 加载 .env 文件
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "🚀 Memory MCP 包发布到 Nexus3 (使用 uv)"
echo "======================================"

# 配置
NEXUS_URL="${NEXUS_URL:-https://nexus3.m.6do.me:4000/}"
PACKAGE_NAME="uvx-excel-read-dbmod"

# 检查必要的环境变量
if [ -z "$NEXUS_USERNAME" ] || [ -z "$NEXUS_PASSWORD" ]; then
    echo "❌ 缺少必要的环境变量: NEXUS_USERNAME, NEXUS_PASSWORD"
    echo "请在 .env 文件中配置"
    exit 1
fi

# 读取版本号
if [ ! -f "VERSION" ]; then
    echo "❌ VERSION 文件不存在"
    exit 1
fi

VERSION=$(cat VERSION | tr -d '[:space:]')
echo "📋 当前版本: $VERSION"

# 检查必要工具
echo "🔍 安装构建工具..."
uv pip install build twine

# 版本号已动态读取，无需更新文件

# 清理旧构建
echo "🗑️  清理旧构建文件..."
rm -rf build/ dist/ *.egg-info/

# 构建包
echo "📦 构建包..."
uv run python -m build

# 检查构建结果
if [ ! -d "dist" ] || [ -z "$(ls -A dist/)" ]; then
    echo "❌ 构建失败，dist 目录为空"
    exit 1
fi

echo "✅ 构建完成，生成的文件："
ls -la dist/

# 自动上传
echo "🚀 上传到 Nexus3..."
uv run python -m twine upload \
  --repository-url "$NEXUS_URL/repository/pip-hosted/" \
  --username "$NEXUS_USERNAME" \
  --password "$NEXUS_PASSWORD" \
  dist/*

if [ $? -eq 0 ]; then
    echo "🎉 发布成功！"
    echo ""
    echo "📋 安装命令："
    echo "uv pip install -i $NEXUS_URL/repository/pypi-group/simple $PACKAGE_NAME"
else
    echo "❌ 上传失败"
    exit 1
fi
