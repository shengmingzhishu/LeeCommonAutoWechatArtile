import json
import time
import os
import re
from playwright.sync_api import Playwright, sync_playwright, expect

def get_article_data():
    """从文件或localStorage模拟获取文章数据"""
    # 在实际应用中，这里会从浏览器的localStorage获取数据
    # 为了演示，我们创建一个示例数据
    try:
        # 尝试从文件读取文章数据（前端保存的数据）
        if os.path.exists('article_data.json'):
            with open('article_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
    except:
        pass
    
    # 如果没有找到文件，返回示例数据
    return {
        "title": "示例文章标题",
        "author": "作者名",
        "summary": "这是一篇示例文章的摘要",
        "cover": "",
        "isOriginal": False,
        "content": "<p>这里是文章内容</p>",
        "timestamp": int(time.time())
    }

def run_publisher(playwright: Playwright, article_data: dict) -> None:
    """使用Playwright发布文章到微信公众号"""
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    try:
        # 导航到微信公众号平台
        page.goto("https://mp.weixin.qq.com/")
        print("请先登录微信公众号平台...")
        
        # 等待用户登录
        input("请在浏览器中登录微信公众号平台，然后按回车继续...")
        
        # 跳转到素材管理或新建文章页面
        # 这里需要根据实际的页面结构调整
        page.goto("https://mp.weixin.qq.com/cgi-bin/home?t=home/index")
        
        # 点击新建图文消息
        # 根据原始脚本，需要点击图像元素
        with page.expect_popup() as page1_info:
            # 原始脚本是点击第4个图像元素，这里我们根据页面结构调整
            page.locator("img").nth(4).click()
        
        page1 = page1_info.value
        page1.wait_for_load_state()
        
        # 填写标题
        title_selector = page1.locator("role=textbox[name='请在这里输入标题']")
        if title_selector.count() > 0:
            title_selector.fill(article_data.get("title", "默认标题"))
        
        # 填写作者
        author_selector = page1.locator("role=textbox[name='请输入作者']")
        if author_selector.count() > 0:
            author_selector.fill(article_data.get("author", ""))
        
        # 填写正文内容
        # 这里需要根据实际的编辑器结构来填充内容
        content_selectors = page1.locator("div").filter(has_text=re.compile(r"^从这里开始写正文$"))
        if content_selectors.count() > 0:
            content_selectors.first.fill(article_data.get("content", ""))
        
        # 如果有封面图片
        if article_data.get("cover"):
            try:
                page1.locator("role=link[name='从图片库选择']").click()
                # 选择图片
                page1.locator("role=img[name='图片描述']").first.click()
                page1.locator("role=button[name='下一步']").click()
                page1.locator("role=button[name='确认']").click()
            except:
                print("设置封面图片时出错")
        
        # 填写摘要
        summary_selector = page1.locator("role=textbox[name='选填，不填写则默认抓取正文开头部分文字，摘要会在转发卡片和公众号会话展示。']")
        if summary_selector.count() > 0:
            summary_selector.fill(article_data.get("summary", ""))
        
        # 设置标签
        try:
            page1.locator("#js_article_tags_area").get_by_text("未添加").click()
            page1.locator("role=textbox[name='请选择合集']").fill("自动发布")
            page1.locator("role=textbox[name='请选择合集']").press("Enter")
            page1.locator("role=button[name='确认']").click()
        except:
            print("设置标签时出错")
        
        # 保存为草稿或发布
        try:
            # 点击发布按钮（这里可能是"保存"或"发布"按钮）
            publish_btn = page1.locator("role=button[name='保存为草稿']")
            if publish_btn.count() > 0:
                publish_btn.click()
                time.sleep(1)
                publish_btn.click()  # 可能需要点击两次
                print("文章已发布/保存为草稿")
            else:
                print("未找到发布按钮")
        except Exception as e:
            print(f"发布文章时出错: {e}")
        
        time.sleep(2)
        
    except Exception as e:
        print(f"执行发布流程时出错: {e}")
    finally:
        context.close()
        browser.close()

def main():
    """主函数"""
    print("微信公众号文章发布工具")
    print("正在获取文章数据...")
    
    # 获取文章数据
    article_data = get_article_data()
    print(f"获取到文章数据: {article_data.get('title', '未知标题')}")
    
    # 使用Playwright发布文章
    print("启动浏览器并开始发布...")
    with sync_playwright() as playwright:
        run_publisher(playwright, article_data)

if __name__ == "__main__":
    main()