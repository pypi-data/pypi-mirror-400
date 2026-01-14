#!/bin/bash
# 小红书笔记提取器 - 构建脚本

set -e  # 遇到错误时退出

echo "🔨 开始构建小红书笔记提取器..."

# 清理旧的构建文件
echo "🧹 清理旧的构建文件..."
rm -rf build/ dist/ *.egg-info/ xhs_note_extractor.egg-info/

# 安装构建工具
echo "🔧 安装构建工具..."
pip install --upgrade pip setuptools wheel build

# 构建包
echo "📦 构建包..."
python -m build --wheel --sdist

# 显示构建结果
echo "✅ 构建完成！"
echo "📦 构建的包："
ls -la dist/

echo ""
echo "🚀 下一步："
echo "1. 测试包: pip install dist/*.whl"
echo "2. 发布包: ./scripts/publish.sh"