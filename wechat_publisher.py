import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    # page.goto("https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=77&createType=0&token=955605123&lang=zh_CN&timestamp=1764138196228")
    # page.get_by_role("link", name="登录").click()
    page.goto("https://mp.weixin.qq.com/cgi-bin/home?t=home/index&lang=zh_CN&token=99978170")
    with page.expect_popup() as page1_info:
        page.get_by_role("img").nth(4).click()
    page1 = page1_info.value
    page1.get_by_role("textbox", name="请在这里输入标题").click()
    page1.get_by_role("textbox", name="请在这里输入标题").fill("AAA")
    page1.get_by_role("textbox", name="请输入作者").click()
    page1.get_by_role("textbox", name="请输入作者").fill("BBB")
    page1.locator("section").click()
    page1.locator("div").filter(has_text=re.compile(r"^从这里开始写正文$")).nth(5).fill("CCCCC")
    page1.get_by_role("link", name="从图片库选择").click()
    page1.get_by_role("img", name="图片描述").first.click()
    page1.get_by_role("button", name="下一步").click()
    page1.get_by_role("button", name="确认").click()
    page1.get_by_role("textbox", name="选填，不填写则默认抓取正文开头部分文字，摘要会在转发卡片和公众号会话展示。").click()
    page1.get_by_role("textbox", name="选填，不填写则默认抓取正文开头部分文字，摘要会在转发卡片和公众号会话展示。").fill("DDD")
    page1.locator("#js_article_tags_area").get_by_text("未添加").click()
    page1.get_by_role("textbox", name="请选择合集").click()
    page1.get_by_role("textbox", name="请选择合集").fill("FF")
    page1.get_by_role("textbox", name="请选择合集").press("Enter")
    page1.get_by_role("button", name="确认").click()
    page1.get_by_role("button", name="保存为草稿").click()
    page1.get_by_role("button", name="保存为草稿").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)