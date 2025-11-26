#!/bin/bash

echo "微信公众号文章排版编辑器"
echo "========================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查Playwright是否已安装
if ! python3 -c "import playwright" &> /dev/null; then
    echo "正在安装Playwright..."
    pip3 install playwright
    playwright install chromium
fi

echo "请选择操作："
echo "1) 启动可视化编辑器"
echo "2) 发布文章到微信公众号"
echo -n "请输入选择 (1 或 2): "

read choice

if [ "$choice" = "1" ]; then
    echo "启动可视化编辑器..."
    echo "请在浏览器中打开 http://localhost:8080/final_editor.html"
    
    # 启动HTTP服务器
    python3 -m http.server 8080 &
    SERVER_PID=$!
    
    echo "服务器已启动，PID: $SERVER_PID"
    echo "按 Ctrl+C 停止服务器"
    
    # 等待用户中断
    while kill -0 $SERVER_PID 2>/dev/null; do
        sleep 1
    done

elif [ "$choice" = "2" ]; then
    echo "启动微信公众号发布工具..."
    python3 wechat_publisher.py

else
    echo "无效选择，请运行脚本并选择 1 或 2"
fi