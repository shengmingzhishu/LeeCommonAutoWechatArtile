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
    
    print("请选择操作:")
    print("1. 开始推送文章 (交互式模式)")
    print("2. 查看使用说明")
    print("3. 退出")
    
    while True:
        choice = input("\n请输入选择 (1-3): ").strip()
        
        if choice == "1":
            # 运行交互式版本
            try:
                from wechat_publisher_cli import main as cli_main
                cli_main()
            except ImportError as e:
                print(f"❌ 依赖导入错误: {e}")
                print("💡 请先运行: python3 -c 'from wechat_publisher_cli import main'")
            break
        elif choice == "2":
            print("""
📋 使用说明:
──────────

🚀 功能:
  自动打开微信公众号后台，填写并发布文章

📝 使用流程:
  1. 启动程序后，按提示输入文章信息
  2. 标题: 文章标题（必填）
  3. 作者: 作者姓名（可留空，默认"北屿"）
  4. 内容: 文章正文（支持多行，输入"END"结束）
  5. 摘要: 文章摘要（可留空，自动生成）
  6. 确认信息后程序自动执行推送

⚠️  注意事项:
  - 需要提前登录微信公众平台
  - 确保网络连接正常
  - 浏览器会自动打开并执行操作

🔧 安装依赖:
  pip3 install playwright
  playwright install

💡 提示:
  - 输入内容时支持多行，文章内容输入"END"结束
  - 摘要留空会自动生成（取内容前50字符）
            """)
        elif choice == "3":
            print("👋 感谢使用！")
            break
        else:
            print("❌ 无效选择，请输入1-3")


if __name__ == "__main__":
    main()
