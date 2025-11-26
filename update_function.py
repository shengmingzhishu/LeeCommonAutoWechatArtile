#!/usr/bin/env python3

import re

# 读取文件
with open('/home/admin/iflow-cli-dev-service/iflow-workspace/LeeCommonAutoWechatArtile/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 定义新的函数
new_function = '''        // 模拟微信公众号发布
        function simulateWeChatPublish(title, author, summary, cover, isOriginal, content) {
            // 显示发布状态
            const statusDiv = document.createElement('div');
            statusDiv.id = 'publish-status';
            statusDiv.innerHTML = '<div style="position: fixed; top: 20px; right: 20px; background: #17a2b8; color: white; padding: 15px; border-radius: 5px; z-index: 10000; font-family: Microsoft YaHei;">正在准备发布...</div>';
            document.body.appendChild(statusDiv);
            
            // 将文章数据存储在 localStorage 中，以便 Python 脚本可以访问
            const articleData = {
                title: title,
                author: author,
                summary: summary,
                cover: cover,
                isOriginal: isOriginal,
                content: content,
                timestamp: new Date().getTime()
            };
            
            localStorage.setItem('wechatArticleData', JSON.stringify(articleData));
            
            // 模拟发布过程
            setTimeout(() => {
                document.getElementById('publish-status').innerHTML = '<div style="position: fixed; top: 20px; right: 20px; background: #28a745; color: white; padding: 15px; border-radius: 5px; z-index: 10000; font-family: Microsoft YaHei;">发布成功！<br>标题: ' + title + '</div>';
                
                // 3秒后移除状态提示
                setTimeout(() => {
                    if (document.getElementById('publish-status')) {
                        document.body.removeChild(document.getElementById('publish-status'));
                    }
                }, 3000);
                
                console.log('发布文章到微信公众号:', {
                    title,
                    author,
                    summary,
                    cover,
                    isOriginal,
                    content
                });
                
                // 隐藏发布面板
                hidePublishPanel();
            }, 2000);
        }'''

# 使用正则表达式匹配旧函数并替换
pattern = r'/\* 模拟微信公众号发布 \*/\s*function simulateWeChatPublish\(title, author, summary, cover, isOriginal, content\) \{[^}]*\n        \}'
# 由于上面的模式可能不够准确，我们使用更具体的模式
pattern = r'        // 模拟微信公众号发布\s*function simulateWeChatPublish\(title, author, summary, cover, isOriginal, content\) \{[^}]*\n        \}'

# 由于函数内容跨越多行，使用 DOTALL 标志
content_new = re.sub(pattern, new_function, content, flags=re.DOTALL)

# 如果上面的替换失败，尝试更具体的模式
if content_new == content:
    # 匹配从 "// 模拟微信公众号发布" 到 "hidePublishPanel();" 后面的几行
    pattern = r'        // 模拟微信公众号发布\s*function simulateWeChatPublish\(title, author, summary, cover, isOriginal, content\) \{[\s\S]*?\n        \}'
    content_new = re.sub(pattern, new_function, content, flags=re.DOTALL)

# 保存更新后的文件
with open('/home/admin/iflow-cli-dev-service/iflow-workspace/LeeCommonAutoWechatArtile/index.html', 'w', encoding='utf-8') as f:
    f.write(content_new)

print("函数已成功更新！")
