#!/bin/bash

# 版本更新脚本

if [ $# -eq 0 ]; then
    echo "用法: ./update_version.sh <新版本号>"
    echo "示例: ./update_version.sh 0.2.0"
    exit 1
fi

NEW_VERSION=$1

echo "🔄 更新版本号到 $NEW_VERSION..."

# 更新 pyproject.toml
sed -i '' "s/version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml

echo "✅ 版本号已更新为 $NEW_VERSION"
echo "📝 请检查 pyproject.toml 文件确认更新正确"
echo "🚀 现在可以运行 ./publish.sh 发布新版本"
