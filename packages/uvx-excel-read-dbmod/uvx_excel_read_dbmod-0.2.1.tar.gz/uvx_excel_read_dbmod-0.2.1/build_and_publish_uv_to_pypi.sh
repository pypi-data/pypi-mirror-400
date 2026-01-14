#!/bin/bash
# uvx-excel-read-dbmod 包构建和发布脚本 - 发布到 PyPI

set -e

# 加载 .env 文件中的环境变量
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 配置 PyPI 凭据
export PYPI_USERNAME="__token__"
export PYPI_PASSWORD="${PYPI_API_TOKEN:-$TWINE_PASSWORD}"

echo "🚀 uvx-excel-read-dbmod 包发布到 PyPI (使用 uv)"
echo "======================================"

# 配置
PYPI_URL="${PYPI_URL:-https://upload.pypi.org/legacy/}"
PACKAGE_NAME="uvx-excel-read-dbmod"

# 检查必要工具
echo "🔍 安装构建工具..."
uv pip install build twine

# 清理旧构建
echo "🗑️  清理旧构建文件..."
rm -rf build/ dist/ *.egg-info/ src/*.egg-info/

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

# 验证包
echo "🔍 验证包..."
uv run python -m twine check dist/*

# 自动上传到 PyPI
echo "🚀 上传到 PyPI..."
uv run python -m twine upload \
  --repository-url "$PYPI_URL" \
  --username "$PYPI_USERNAME" \
  --password "$PYPI_PASSWORD" \
  dist/*

if [ $? -eq 0 ]; then
    echo "🎉 发布成功！"
    echo ""
    echo "📋 安装命令："
    echo "pip install $PACKAGE_NAME"
    echo ""
    echo "📋 使用命令："
    echo "uvx --from $PACKAGE_NAME uvx-excel-read-dbmod"
else
    echo "❌ 上传失败"
    exit 1
fi