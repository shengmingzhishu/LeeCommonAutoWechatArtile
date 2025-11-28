#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章推送器 - 交互式命令行版本
提供友好的用户输入界面，比硬编码版本更便捷
"""

import re
import sys
from playwright.sync_api import Playwright, sync_playwright
from typing import Optional


class WeChatPublisherCLI:
    def __init__(self):
        self.title = ""
        self.author = ""
        self.content = ""
        self.summary = ""
        
    def get_user_input(self):
        """获取用户输入的文章信息"""
        print("=" * 60)
        print("🚀 微信公众号文章推送器")
        print("=" * 60)
        
        # 文章标题
        while True:
            self.title = input("📝 请输入文章标题: ").strip()
            if self.title:
                break
            print("❌ 标题不能为空，请重新输入")
        
        # 作者（可跳过，使用默认值）
        author_input = input("👤 请输入作者 (回车使用默认'北屿'): ").strip()
        self.author = author_input if author_input else "北屿"
        
        # 文章内容
        print("\n📄 请输入文章内容 (输入 'END' 结束):")
        content_lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            content_lines.append(line)
        
        self.content = "\n".join(content_lines)
        if not self.content.strip():
            print("❌ 文章内容不能为空")
            return False
            
        # 文章摘要（可跳过）
        summary_input = input("📋 请输入文章摘要 (回车自动生成): ").strip()
        if summary_input:
            self.summary = summary_input
        else:
            # 自动生成摘要：取前50个字符
            self.summary = self.content[:50] + ("..." if len(self.content) > 50 else "")
            
        return True
        
    def confirm_input(self) -> bool:
        """确认输入信息"""
        print("\n" + "=" * 60)
        print("📋 请确认输入的信息:")
        print("=" * 60)
        print(f"📝 标题: {self.title}")
        print(f"👤 作者: {self.author}")
        print(f"📄 内容预览: {self.content[:100]}{'...' if len(self.content) > 100 else ''}")
        print(f"📋 摘要: {self.summary}")
        print("=" * 60)
        
        while True:
            confirm = input("✅ 确认信息无误? (y/n): ").strip().lower()
            if confirm in ['y', 'yes', '是']:
                return True
            elif confirm in ['n', 'no', '否']:
                return False
            else:
                print("❌ 请输入 y/n")
                
    def run_wechat_publish(self, playwright: Playwright) -> None:
        """执行微信文章发布"""
        print("\n🚀 开始执行微信文章推送...")
        
        try:
            print("🌐 正在打开浏览器...")
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            print("🔗 正在访问微信公众平台...")
            page.goto("https://mp.weixin.qq.com/cgi-bin/home?t=home/index&lang=zh_CN&token=99978170")
            
            print("🔑 正在点击登录...")
            with page.expect_popup() as page1_info:
                page.get_by_role("img").nth(4).click()
            page1 = page1_info.value
            
            print(f"📝 正在填写文章标题: {self.title}")
            page1.get_by_role("textbox", name="请在这里输入标题").click()
            page1.get_by_role("textbox", name="请在这里输入标题").fill(self.title)
            
            print(f"👤 正在填写作者: {self.author}")
            page1.get_by_role("textbox", name="请输入作者").click()
            page1.get_by_role("textbox", name="请输入作者").fill(self.author)
            
            print("📄 正在填写文章内容...")
            page1.locator("section").click()
            page1.locator("div").filter(has_text=re.compile(r"^从这里开始写正文$")).nth(5).fill(self.content)
            
            print("🖼️ 正在选择封面图片...")
            page1.get_by_role("link", name="从图片库选择").click()
            page1.get_by_role("img", name="图片描述").first.click()
            page1.get_by_role("button", name="下一步").click()
            page1.get_by_role("button", name="确认").click()
            
            print(f"📋 正在填写文章摘要: {self.summary}")
            page1.get_by_role("textbox", name="选填，不填写则默认抓取正文开头部分文字，摘要会在转发卡片和公众号会话展示。").click()
            page1.get_by_role("textbox", name="选填，不填写则默认抓取正文开头部分文字，摘要会在转发卡片和公众号会话展示。").fill(self.summary)
            
            print("💾 正在保存为草稿...")
            page1.get_by_role("button", name="保存为草稿").click()
            
            print("\n🎉 文章推送完成！")
            print("✅ 请检查浏览器窗口确认操作结果")
            
            context.close()
            browser.close()
            
        except Exception as e:
            print(f"\n❌ 推送过程中发生错误: {str(e)}")
            print("💡 请检查:")
            print("   1. 微信公众平台登录状态")
            print("   2. 网络连接")
            print("   3. Playwright浏览器驱动")
            raise
            
    def run(self):
        """运行主程序"""
        try:
            # 获取用户输入
            if not self.get_user_input():
                print("❌ 输入取消")
                return
                
            # 确认输入
            if not self.confirm_input():
                print("❌ 取消推送操作")
                return
                
            print("\n" + "🎯 " + "开始执行推送任务...")
            
            # 执行推送
            with sync_playwright() as playwright:
                self.run_wechat_publish(playwright)
                
            print("\n✨ 任务完成！")
            
        except KeyboardInterrupt:
            print("\n\n⏸️ 操作被用户中断")
        except Exception as e:
            print(f"\n💥 程序执行出错: {str(e)}")
            print("💡 如有问题，请检查网络连接和微信公众号登录状态")
        finally:
            print("\n👋 感谢使用微信公众号文章推送器！")


def main():
    """主函数"""
    try:
        publisher = WeChatPublisherCLI()
        publisher.run()
    except ImportError as e:
        print(f"❌ 缺少必要依赖: {e}")
        print("💡 请先安装playwright: pip install playwright")
        print("   然后安装浏览器: playwright install")
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")


if __name__ == "__main__":
    main()
