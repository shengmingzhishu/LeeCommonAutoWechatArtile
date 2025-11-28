import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import re
from playwright.sync_api import Playwright, sync_playwright


class WeChatPublisherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("微信公众号文章推送器")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="微信公众号文章推送器", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 文章标题
        ttk.Label(main_frame, text="文章标题:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(main_frame, width=50, font=("Arial", 10))
        self.title_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 作者
        ttk.Label(main_frame, text="作者:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.author_entry = ttk.Entry(main_frame, width=50, font=("Arial", 10))
        self.author_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.author_entry.insert(0, "北屿")
        
        # 文章内容
        ttk.Label(main_frame, text="文章内容:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.content_text = scrolledtext.ScrolledText(main_frame, width=60, height=15, font=("Arial", 10))
        self.content_text.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 文章摘要
        ttk.Label(main_frame, text="文章摘要:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W, pady=5)
        self.summary_entry = ttk.Entry(main_frame, width=50, font=("Arial", 10))
        self.summary_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        # 推送按钮
        self.push_button = ttk.Button(button_frame, text="开始推送", command=self.start_publish, style="Accent.TButton")
        self.push_button.pack(side=tk.LEFT, padx=5)
        
        # 清空按钮
        clear_button = ttk.Button(button_frame, text="清空内容", command=self.clear_content)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # 状态显示
        ttk.Label(main_frame, text="运行状态:", font=("Arial", 10, "bold")).grid(row=7, column=0, sticky=tk.W, pady=(20, 5))
        self.status_text = scrolledtext.ScrolledText(main_frame, width=60, height=8, font=("Arial", 9))
        self.status_text.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 绑定回车键到推送按钮
        self.root.bind('<Return>', lambda event: self.start_publish())
        
    def log_message(self, message):
        """在状态区域显示日志消息"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_content(self):
        """清空所有输入内容"""
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.author_entry.insert(0, "北屿")
        self.content_text.delete(1.0, tk.END)
        self.summary_entry.delete(0, tk.END)
        
    def validate_input(self):
        """验证输入内容"""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        content = self.content_text.get(1.0, tk.END).strip()
        summary = self.summary_entry.get().strip()
        
        if not title:
            messagebox.showerror("输入错误", "请输入文章标题")
            return False
            
        if not author:
            messagebox.showerror("输入错误", "请输入作者")
            return False
            
        if not content:
            messagebox.showerror("输入错误", "请输入文章内容")
            return False
            
        return True
        
    def start_publish(self):
        """开始推送文章"""
        if not self.validate_input():
            return
            
        # 在新线程中运行推送功能，避免阻塞GUI
        thread = threading.Thread(target=self.publish_article, daemon=True)
        thread.start()
        
    def publish_article(self):
        """执行文章推送功能"""
        try:
            self.push_button.config(state='disabled')
            self.log_message("开始启动浏览器...")
            
            title = self.title_entry.get().strip()
            author = self.author_entry.get().strip()
            content = self.content_text.get(1.0, tk.END).strip()
            summary = self.summary_entry.get().strip()
            
            if not summary:
                summary = content[:50] + "..." if len(content) > 50 else content
                
            with sync_playwright() as playwright:
                self.run_wechat_publish(playwright, title, author, content, summary)
                
        except Exception as e:
            self.log_message(f"推送过程中发生错误: {str(e)}")
            messagebox.showerror("推送失败", f"推送过程中发生错误:\n{str(e)}")
        finally:
            self.push_button.config(state='normal')
            
    def run_wechat_publish(self, playwright: Playwright, title: str, author: str, content: str, summary: str) -> None:
        """执行微信文章发布"""
        try:
            self.log_message("正在打开微信公众平台...")
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            self.log_message("正在访问微信公众平台首页...")
            page.goto("https://mp.weixin.qq.com/cgi-bin/home?t=home/index&lang=zh_CN&token=99978170")
            
            self.log_message("正在点击登录...")
            with page.expect_popup() as page1_info:
                page.get_by_role("img").nth(4).click()
            page1 = page1_info.value
            
            self.log_message(f"正在填写文章标题: {title}")
            page1.get_by_role("textbox", name="请在这里输入标题").click()
            page1.get_by_role("textbox", name="请在这里输入标题").fill(title)
            
            self.log_message(f"正在填写作者: {author}")
            page1.get_by_role("textbox", name="请输入作者").click()
            page1.get_by_role("textbox", name="请输入作者").fill(author)
            
            self.log_message("正在填写文章内容...")
            page1.locator("section").click()
            page1.locator("div").filter(has_text=re.compile(r"^从这里开始写正文$")).nth(5).fill(content)
            
            self.log_message("正在选择封面图片...")
            page1.get_by_role("link", name="从图片库选择").click()
            page1.get_by_role("img", name="图片描述").first.click()
            page1.get_by_role("button", name="下一步").click()
            page1.get_by_role("button", name="确认").click()
            
            self.log_message(f"正在填写文章摘要: {summary}")
            page1.get_by_role("textbox", name="选填，不填写则默认抓取正文开头部分文字，摘要会在转发卡片和公众号会话展示。").click()
            page1.get_by_role("textbox", name="选填，不填写则默认抓取正文开头部分文字，摘要会在转发卡片和公众号会话展示。").fill(summary)
            
            self.log_message("正在保存为草稿...")
            page1.get_by_role("button", name="保存为草稿").click()
            
            self.log_message("文章推送完成！")
            messagebox.showinfo("推送成功", "文章已成功推送到微信公众平台！")
            
            context.close()
            browser.close()
            
        except Exception as e:
            self.log_message(f"推送过程中发生错误: {str(e)}")
            raise


def main():
    root = tk.Tk()
    app = WeChatPublisherGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()