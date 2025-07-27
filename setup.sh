#!/bin/bash

# Setup script for LuLu Dictionary Word Note Generator
# LuLu 词典单词笔记生成器安装脚本

echo "🚀 正在设置 LuLu 词典单词笔记生成器..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 Python 3，但未安装。"
    exit 1
fi

echo "✅ 找到 Python 3"

# Install requirements
echo "📦 正在安装所需包..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ 依赖包安装成功"
else
    echo "❌ 依赖包安装失败"
    exit 1
fi

# Check for keys.json file
if [ ! -f "keys.json" ]; then
    echo "🔑 创建 API 密钥配置文件..."
    cp keys.json.example keys.json
    echo "✅ 已创建 keys.json 文件"
    echo "⚠️  请编辑 keys.json 文件并填入您的 API 密钥"
    echo "📖 详细说明请查看 SETUP_KEYS.md"
else
    echo "✅ keys.json 文件已存在"
fi

# Validate configuration
echo "🔍 验证配置..."
python3 -c "
from config import Config
if Config.validate():
    print('✅ 配置验证成功')
else:
    print('⚠️  配置需要完善，请检查 keys.json 文件')
" 2>/dev/null
echo ""
echo "🎉 安装完成！"
echo ""
echo "� 下一步操作："
echo "1. 编辑 keys.json 文件并填入您的 API 密钥："
echo "   nano keys.json"
echo "   # 或使用您喜欢的编辑器"
echo ""
echo "2. 获取 Gemini API 密钥："
echo "   💡 访问: https://makersuite.google.com/app/apikey"
echo ""
echo "3. 验证配置："
echo "   python3 -c \"from config import Config; Config.validate()\""
echo ""
echo "4. 运行示例："
echo "   python3 examples.py"
echo ""
echo "5. 开始批处理："
echo "   python3 main.py"
echo ""
echo "📚 更多信息请查看 README.md 和 SETUP_KEYS.md"
