#!/bin/bash
# 小红书笔记提取器 - 发布脚本

set -e  # 遇到错误时退出

echo "🚀 开始发布小红书笔记提取器..."

# 检查是否在虚拟环境中
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  警告: 未在虚拟环境中运行"
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 发布已取消"
        exit 1
    fi
fi

# 检查必要的工具是否安装
echo "🔍 检查必要工具..."
for tool in python pip twine; do
    if ! command -v $tool &> /dev/null; then
        echo "❌ $tool 未安装"
        exit 1
    fi
done
echo "✅ 所有必要工具已安装"

# 清理旧的构建文件
echo "🧹 清理旧的构建文件..."
rm -rf build/ dist/ *.egg-info/ xhs_note_extractor.egg-info/

# 安装构建工具
echo "🔧 安装构建工具..."
pip install --upgrade pip setuptools wheel twine build

# 运行测试
echo "🧪 运行测试..."
python -m pytest tests/ -v || {
    echo "❌ 测试失败"
    exit 1
}
echo "✅ 测试通过"

# 构建包
echo "📦 构建包..."
python -m build --wheel --sdist
echo "✅ 构建完成"

# 检查构建的包
echo "🔍 检查构建的包..."
ls -la dist/

# 验证包
echo "🔍 验证包..."
twine check dist/*
echo "✅ 包验证通过"

# 询问是否上传到PyPI
read -p "是否上传到PyPI? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 上传到PyPI..."
    twine upload dist/*
    echo "✅ 上传完成"
else
    echo "ℹ️  跳过上传步骤"
fi

echo "🎉 发布流程完成！"
echo "📦 构建的包位于 dist/ 目录中"