#!/bin/bash
# 微信公众号文章推送器 - 自动安装脚本

echo "========================================="
echo "微信公众号文章推送器 - 安装程序"
echo "========================================="

# 检查Python版本
echo "检查Python版本..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ 未找到Python3，请先安装Python 3.x"
    exit 1
fi

# 升级pip
echo "升级pip..."
pip3 install --upgrade pip

# 安装依赖
echo "安装Python依赖..."
pip3 install -r requirements.txt

# 安装Playwright浏览器
echo "安装Playwright浏览器驱动..."
playwright install

echo ""
echo "========================================="
echo "✅ 安装完成！"
echo "========================================="
echo ""
echo "使用方法:"
echo "1. 运行启动脚本: python3 start.py"
echo "2. 选择模式开始使用"
echo ""
echo "或者直接运行:"
echo "python3 wechat_publisher_cli.py"
echo ""