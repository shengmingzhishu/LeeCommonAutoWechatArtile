import re
import json
import os
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright, article_data: dict) -> None:
    """
    使用Playwright发布文章到微信公众号
    :param playwright: Playwright实例
    :param article_data: 文章数据，包含标题、作者、内容等
    """
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    try:
        # 访问微信公众号后台
        page.goto("https://mp.weixin.qq.com/")
        print("请在页面上手动登录微信公众号后台...")
        print("登录后请按Enter键继续...")
        input()  # 等待用户登录
        
        # 导航到图文消息页面
        page.wait_for_timeout(3000)  # 等待页面加载
        # 通常在首页点击“素材管理”或“新建群发”
        try:
            # 尝试点击“素材管理”，然后“新建图文”
            media_link = page.get_by_text("素材管理")
            if media_link.count() > 0:
                media_link.click()
                page.wait_for_timeout(1000)
                page.get_by_text("新建图文").click()
            else:
                # 或者直接点击首页的写文章按钮
                page.get_by_role("button", name="新建群发").click()
                page.get_by_text("图文消息").click()
                page.get_by_text("自定义").click()
        except:
            # 如果找不到特定元素，让用户手动导航到编辑页面
            print("请手动导航到图文编辑页面...")
            input("到达编辑页面后按Enter键继续...")
        
        page.wait_for_timeout(2000)
        
        # 现在我们假设已经在图文编辑页面
        # 填写标题
        title_input = page.locator("input[placeholder*='标题' i]")
        if title_input.count() > 0:
            title_input.fill(article_data.get("title", "通过编辑器发布的文章"))
        
        # 填写作者
        author_input = page.locator("input[placeholder*='作者' i]")
        if author_input.count() > 0:
            author_input.fill(article_data.get("author", "系统"))
        
        # 填写摘要（可选）
        summary_input = page.locator("textarea[placeholder*='摘要' i]")
        if summary_input.count() > 0:
            summary_input.fill(article_data.get("summary", ""))
        
        # 等待编辑器加载
        page.wait_for_timeout(2000)
        
        # 获取编辑器iframe并填充内容
        try:
            # 尝试找到编辑器的iframe
            editor_iframe = page.frame_locator("#ueditor_0")  # 微信编辑器的iframe
            if editor_iframe:
                editor_body = editor_iframe.locator("body")
                if editor_body.count() > 0:
                    editor_body.click()  # 点击激活编辑器
                    editor_body.fill("")  # 清空内容
                    # 直接设置innerHTML，因为fill只适用于纯文本
                    editor_iframe.frame_element().evaluate(f"node => node.contentDocument.body.innerHTML = `{article_data.get('content', '<p>无内容</p>')}`")
                else:
                    # 如果直接的body找不到，尝试其他方式
                    print("无法直接访问编辑器内容，请手动粘贴以下内容:")
                    print(article_data.get("content", ""))
            else:
                # 如果iframe方式不行，尝试直接在页面中查找编辑区域
                editor_div = page.locator("#js_content")  # 微信编辑器的主要内容区域
                if editor_div.count() > 0:
                    # 清空并填充内容
                    page.evaluate("() => { document.querySelector('#js_content').innerHTML = `" + article_data.get("content", "<p>无内容</p>") + "`; }")
                else:
                    print("未找到编辑器区域，请手动粘贴以下内容:")
                    print(article_data.get("content", ""))
        except Exception as e:
            print(f"填充编辑器内容时出错: {e}")
            print("请手动粘贴以下内容到编辑器:")
            print(article_data.get("content", ""))
        
        print("标题、作者、摘要和正文内容已尝试填充")
        print("如果内容没有正确填充，请手动完成")
        
        # 如果有封面图片，上传它
        if "cover_image_url" in article_data and article_data["cover_image_url"]:
            try:
                cover_upload_btn = page.locator("text=上传封面图片")
                if cover_upload_btn.count() > 0:
                    cover_upload_btn.click()
                    # 这里需要处理文件上传，可能需要下载图片到本地再上传
                    print(f"请上传封面图片: {article_data['cover_image_url']}")
            except:
                print("未找到封面上传按钮，请手动上传封面图片")
        
        print("文章内容已准备就绪，请在页面上完成发布操作")
        print("可以点击'保存为草稿'或'群发'来发布文章")
        
        # 保持页面打开，让用户完成发布
        input("完成发布后，按Enter键关闭浏览器...")
        
    except Exception as e:
        print(f"发布过程中出现错误: {e}")
        input("按Enter键关闭浏览器...")
    
    finally:
        # 确保浏览器关闭
        context.close()
        browser.close()


def load_article_from_editor():
    """
    从浏览器本地存储加载通过编辑器创建的文章内容
    检查本地是否有保存的编辑器内容文件
    """
    # 首先尝试从本地文件加载（如果用户保存了）
    try:
        with open("article_content.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return {
                "title": data.get("title", "通过编辑器发布的文章"),
                "author": data.get("author", "系统"),
                "summary": data.get("summary", ""),
                "content": generate_content_from_elements(data.get("elements", [])),
                "cover_image_url": data.get("cover_image_url", "")
            }
    except FileNotFoundError:
        print("未找到本地文章内容文件 'article_content.json'")
        print("尝试从浏览器本地存储获取内容...")
    
    # 如果没有本地文件，提示用户从编辑器复制内容
    print("\n请在编辑器中完成文章编辑，然后:")
    print("1. 点击'发布到公众号'按钮")
    print("2. 填写标题、作者等信息")
    print("3. 在控制台中会显示生成的内容")
    print("\n或者，您也可以直接在这里输入文章内容:")
    
    # 作为示例，返回一个默认的文章
    return {
        "title": "通过编辑器发布的文章",
        "author": "系统",
        "summary": "这是一篇通过可视化编辑器创建并发布的文章",
        "content": "<h2>欢迎使用微信公众号文章编辑器</h2><p>这是通过可视化SVG编辑器创建的文章内容。</p><p>支持多种元素类型：</p><ul><li>文本和标题</li><li>图片</li><li>Markdown格式</li></ul><p>可以使用预设模板快速创建文章。</p>",
        "cover_image_url": ""
    }


def generate_content_from_elements(elements):
    """
    根据元素列表生成HTML内容
    """
    content = ""
    
    for element in elements:
        if element.get('type') == 'group':
            # 处理组合元素
            for sub_element in element.get('elements', []):
                content += generate_element_html(sub_element)
        else:
            content += generate_element_html(element)
    
    return content


def generate_element_html(element):
    """
    根据元素类型生成HTML
    """
    element_type = element.get('type', '')
    
    if element_type == 'text':
        return f'<p style="font-size:{element.get("fontSize", 16)}px; color:{element.get("color", "#333")}; text-align:{element.get("textAlign", "left")}; line-height: 1.8;">{element.get("text", "")}</p>'
    elif element_type == 'title':
        return f'<h2 style="font-size:{element.get("fontSize", 24)}px; color:{element.get("color", "#222")}; font-weight:{element.get("fontWeight", "bold")}; text-align:{element.get("textAlign", "left")}; margin: 20px 0;">{element.get("text", "")}</h2>'
    elif element_type == 'image':
        return f'<div style="text-align: center; margin: 20px 0;"><img src="{element.get("src", "")}" style="max-width: 100%; height: auto; border-radius: 4px;" width="{element.get("width", 300)}" height="{element.get("height", 200)}"></div>'
    elif element_type == 'divider':
        return f'<hr style="border: 0; height: {element.get("height", 2)}px; background-color: {element.get("color", "#ccc")}; margin: 20px 0;">'
    elif element_type == 'markdown':
        # 简单的Markdown转HTML（与前端逻辑保持一致）
        md_content = element.get("content", "")
        # 基本转换
        import re
        html_content = md_content
        # 转换标题
        html_content = re.sub(r'^# (.*$)', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.*$)', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^### (.*$)', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        # 转换粗体
        html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
        # 转换斜体
        html_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_content)
        # 转换段落
        html_content = html_content.replace('\n\n', '</p><p>')
        html_content = f'<p>{html_content}</p>'
        html_content = html_content.replace('<p></p>', '')
        # 转换换行
        html_content = html_content.replace('\n', '<br>')
        return html_content
    else:
        return ''


def publish_from_editor():
    """
    从编辑器导出的内容发布到微信公众号
    """
    print("微信公众号文章发布工具")
    print("="*30)
    
    # 加载编辑器创建的文章数据
    article_data = load_article_from_editor()
    
    print(f"文章标题: {article_data['title']}")
    print(f"作者: {article_data['author']}")
    print(f"摘要: {article_data['summary']}")
    print(f"内容预览: {article_data['content'][:100]}...")
    
    confirm = input("\n是否发布此文章到微信公众号? (y/N): ")
    if confirm.lower() != 'y':
        print("发布已取消")
        return
    
    # 启动Playwright并发布
    with sync_playwright() as playwright:
        run(playwright, article_data)


if __name__ == "__main__":
    publish_from_editor()