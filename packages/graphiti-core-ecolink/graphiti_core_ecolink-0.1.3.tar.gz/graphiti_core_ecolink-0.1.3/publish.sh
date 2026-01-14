#!/bin/bash

# Graphiti Core Ecolink 发布脚本

echo "🚀 开始发布 graphiti-core-ecolink..."

# 检查是否安装了必要工具
if ! command -v python -m build &> /dev/null; then
    echo "❌ 请先安装 build: pip install build"
    exit 1
fi

if ! command -v python -m twine &> /dev/null; then
    echo "❌ 请先安装 twine: pip install twine"
    exit 1
fi

# 1. 清理旧的构建文件
echo "🧹 清理旧的构建文件..."
rm -rf dist/
rm -rf build/
rm -rf *.egg-info/

# 2. 构建包
echo "📦 构建包..."
python -m build

# 3. 检查包
echo "🔍 检查包..."
python -m twine check dist/*

# 4. 询问发布环境
echo "请选择发布环境："
echo "1) 测试环境 (testpypi)"
echo "2) 生产环境 (pypi)"
read -p "请输入选择 (1/2): " choice

case $choice in
    1)
        echo "📤 上传到 PyPI 测试环境..."
        python -m twine upload --repository testpypi dist/*
        echo "✅ 测试环境发布完成！"
        echo "📥 测试安装命令: pip install --index-url https://test.pypi.org/simple/ graphiti-core-ecolink"
        ;;
    2) 
        echo "📤 上传到 PyPI 生产环境..."
        python -m twine upload dist/*
        echo "✅ 生产环境发布完成！"
        echo "📥 安装命令: pip install graphiti-core-ecolink"
        ;;
    *)
        echo "❌ 无效选择，取消发布"
        exit 1
        ;;
esac

echo "📖 导入示例: from graphiti_core_ecolink import Graphiti"
