#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章推送器 - 快速启动脚本
"""

import os
import sys

def main():
    print("""
╔═══════════════════════════════════════╗
║         微信公众号文章推送器           ║
╚═══════════════════════════════════════╝
    """)
    
    print("请选择运行模式:")
    print("1. 交互式命令行模式 (推荐)")
    print("2. 查看使用说明")
    print("3. 退出")
    
    while True:
        choice = input("\\n请输入选择 (1-3): ").strip()
        
        if choice == "1":
            # 运行交互式版本
            from wechat_publisher_cli import main as cli_main
            cli_main()
            break
        elif choice == "2":
            print("""
使用说明:
─────────

📋 功能说明:
  这个工具可以自动打开微信公众号后台，并自动填写文章信息

🚀 使用方法:
  1. 运行本程序
  2. 选择"交互式命令行模式"
  3. 按提示输入文章标题、作者、内容等
  4. 确认信息后程序会自动打开浏览器执行推送

⚠️  注意事项:
  - 需要先登录微信公众平台
  - 程序会在浏览器中自动完成操作
  - 请确保网络连接正常

🔧 依赖要求:
  - Python 3.x
  - playwright 库: pip install playwright
  - 浏览器驱动: playwright install

💡 使用提示:
  - 文章内容可以输入多行，输入"END"结束
  - 作者可以留空，默认使用"北屿"
  - 摘要可以留空，程序会自动生成
            """)
        elif choice == "3":
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请输入1-3")


if __name__ == "__main__":
    main()