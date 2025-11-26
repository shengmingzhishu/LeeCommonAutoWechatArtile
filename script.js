// 编辑器状态
let editorState = {
    elements: [],
    selectedElement: null,
    nextId: 1
};

// 模板存储
let templates = JSON.parse(localStorage.getItem('wechatEditorTemplates')) || {};

// 默认模板
const defaultTemplates = {
    "图片排版模板": {
        name: "图片排版模板",
        elements: [
            {
                id: "title_1",
                type: "title",
                x: 50,
                y: 50,
                text: "精美图片排版",
                fontSize: 28,
                color: "#222222",
                fontWeight: "bold",
                textAlign: "center",
                width: 500,
                height: 60
            },
            {
                id: "img_1",
                type: "image",
                x: 50,
                y: 130,
                src: "https://via.placeholder.com/600x400.png",
                width: 600,
                height: 400
            },
            {
                id: "text_1",
                type: "text",
                x: 50,
                y: 550,
                text: "图片描述文字",
                fontSize: 16,
                color: "#555555",
                fontWeight: "normal",
                textAlign: "center",
                width: 600,
                height: 40
            }
        ],
        createdAt: new Date().toISOString()
    },
    "图书介绍模板": {
        name: "图书介绍模板",
        elements: [
            {
                id: "book_title",
                type: "title",
                x: 50,
                y: 50,
                text: "本周推荐好书",
                fontSize: 32,
                color: "#222222",
                fontWeight: "bold",
                textAlign: "center",
                width: 600,
                height: 60
            },
            {
                id: "book_1",
                type: "image",
                x: 50,
                y: 130,
                src: "https://via.placeholder.com/120x180.png",
                width: 120,
                height: 180
            },
            {
                id: "book_info_1",
                type: "text",
                x: 190,
                y: 130,
                text: "《书籍一》\n作者：作者名\n这是一本非常棒的书籍，内容丰富，值得一读。",
                fontSize: 14,
                color: "#333333",
                fontWeight: "normal",
                textAlign: "left",
                width: 400,
                height: 180
            }
        ],
        createdAt: new Date().toISOString()
    },
    "Markdown模板": {
        name: "Markdown模板",
        elements: [
            {
                id: "md_example",
                type: "markdown",
                x: 50,
                y: 50,
                content: "# 欢迎使用Markdown模板\n\n这是一段**加粗**的文本和*斜体*文本。\n\n- 列表项1\n- 列表项2\n- 列表项3\n\n> 这是一个引用块",
                fontSize: 16,
                color: "#333333",
                width: 600,
                height: 400
            }
        ],
        createdAt: new Date().toISOString()
    }
};

// 初始化编辑器
document.addEventListener('DOMContentLoaded', function() {
    initializeEditor();
    setupEventListeners();
    loadSavedTemplates();
    // 添加默认模板（如果本地没有模板）
    if (Object.keys(templates).length === 0) {
        templates = { ...defaultTemplates };
        saveTemplatesToStorage();
        loadSavedTemplates();
    }
});

function initializeEditor() {
    const svgEditor = document.getElementById('svgEditor');
    
    // 添加点击事件以取消选择
    svgEditor.addEventListener('click', function(e) {
        if (e.target === svgEditor) {
            selectElement(null);
        }
    });
}

function setupEventListeners() {
    // 拖拽组件事件
    setupDragAndDrop();
    
    // 按钮事件
    document.getElementById('saveTemplateBtn').addEventListener('click', saveTemplate);
    document.getElementById('loadTemplateBtn').addEventListener('click', loadTemplate);
    document.getElementById('exportTemplateBtn').addEventListener('click', exportTemplate);
    document.getElementById('importTemplateBtn').addEventListener('click', importTemplate);
    document.getElementById('publishBtn').addEventListener('click', publishToWechat);
    
    // 文件输入事件（用于导入模板）
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.id = 'templateFileInput';
    fileInput.style.display = 'none';
    fileInput.accept = '.json';
    document.body.appendChild(fileInput);
    
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const template = JSON.parse(e.target.result);
                    templates[template.name] = template;
                    saveTemplatesToStorage();
                    loadSavedTemplates();
                    alert('模板导入成功！');
                } catch (error) {
                    alert('模板文件格式错误！');
                }
            };
            reader.readAsText(file);
        }
    });
    
    document.getElementById('importTemplateBtn').addEventListener('click', function() {
        fileInput.click();
    });
}

function setupDragAndDrop() {
    const components = document.querySelectorAll('.component');
    components.forEach(component => {
        component.addEventListener('dragstart', function(e) {
            e.dataTransfer.setData('text/plain', this.dataset.type);
            this.classList.add('dragging');
        });
        
        component.addEventListener('dragend', function(e) {
            this.classList.remove('dragging');
        });
    });
    
    const svgEditor = document.getElementById('svgEditor');
    
    svgEditor.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('drop-target');
    });
    
    svgEditor.addEventListener('dragleave', function(e) {
        this.classList.remove('drop-target');
    });
    
    svgEditor.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('drop-target');
        
        const type = e.dataTransfer.getData('text/plain');
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        createElement(type, x, y);
    });
}

function createElement(type, x, y) {
    let element;
    const id = 'element_' + editorState.nextId++;
    
    switch (type) {
        case 'text':
            element = createTextElement(id, x, y);
            break;
        case 'title':
            element = createTitleElement(id, x, y);
            break;
        case 'image':
            element = createImageElement(id, x, y);
            break;
        case 'divider':
            element = createDividerElement(id, x, y);
            break;
        case 'template-image':
            element = createImageTemplate(id, x, y);
            break;
        case 'template-book':
            element = createBookTemplate(id, x, y);
            break;
        case 'template-md':
            element = createMarkdownTemplate(id, x, y);
            break;
        default:
            return;
    }
    
    editorState.elements.push(element);
    renderElements();
    selectElement(element.id);
}

function createTextElement(id, x, y) {
    return {
        id: id,
        type: 'text',
        x: x,
        y: y,
        text: '请输入文本',
        fontSize: 16,
        color: '#333333',
        fontWeight: 'normal',
        textAlign: 'left',
        width: 200,
        height: 40
    };
}

function createTitleElement(id, x, y) {
    return {
        id: id,
        type: 'title',
        x: x,
        y: y,
        text: '标题',
        fontSize: 24,
        color: '#222222',
        fontWeight: 'bold',
        textAlign: 'left',
        width: 300,
        height: 50
    };
}

function createImageElement(id, x, y) {
    return {
        id: id,
        type: 'image',
        x: x,
        y: y,
        src: 'https://via.placeholder.com/300x200.png',
        width: 300,
        height: 200
    };
}

function createDividerElement(id, x, y) {
    return {
        id: id,
        type: 'divider',
        x: x,
        y: y,
        width: 400,
        height: 2,
        color: '#cccccc'
    };
}

function createImageTemplate(id, x, y) {
    // 创建一个图片排版模板，包含标题和几张图片
    const elements = [];
    
    // 标题
    elements.push({
        id: id + '_title',
        type: 'title',
        x: x,
        y: y,
        text: '图片排版标题',
        fontSize: 24,
        color: '#222222',
        fontWeight: 'bold',
        textAlign: 'left',
        width: 400,
        height: 50
    });
    
    // 图片1
    elements.push({
        id: id + '_img1',
        type: 'image',
        x: x,
        y: y + 70,
        src: 'https://via.placeholder.com/300x200.png',
        width: 300,
        height: 200
    });
    
    // 文本描述
    elements.push({
        id: id + '_text1',
        type: 'text',
        x: x,
        y: y + 290,
        text: '图片描述文字',
        fontSize: 16,
        color: '#333333',
        fontWeight: 'normal',
        textAlign: 'left',
        width: 300,
        height: 40
    });
    
    return {
        id: id,
        type: 'group',
        elements: elements
    };
}

function createBookTemplate(id, x, y) {
    // 创建一个图书介绍模板，包含5本书的介绍
    const elements = [];
    
    // 主标题
    elements.push({
        id: id + '_maintitle',
        type: 'title',
        x: x,
        y: y,
        text: '本周推荐好书',
        fontSize: 28,
        color: '#222222',
        fontWeight: 'bold',
        textAlign: 'center',
        width: 500,
        height: 60
    });
    
    const bookHeight = 180;
    for (let i = 0; i < 5; i++) {
        // 书的图片
        elements.push({
            id: id + '_book_img' + (i+1),
            type: 'image',
            x: x,
            y: y + 80 + i * bookHeight,
            src: 'https://via.placeholder.com/120x160.png',
            width: 120,
            height: 160
        });
        
        // 书的信息
        elements.push({
            id: id + '_book_info' + (i+1),
            type: 'text',
            x: x + 140,
            y: y + 80 + i * bookHeight,
            text: `书名: 书籍${i+1}\n作者: 作者${i+1}\n简介: 这里是关于这本书的简要介绍，描述书籍的主要内容和特点。`,
            fontSize: 14,
            color: '#333333',
            fontWeight: 'normal',
            textAlign: 'left',
            width: 350,
            height: 160
        });
    }
    
    return {
        id: id,
        type: 'group',
        elements: elements
    };
}

function createMarkdownTemplate(id, x, y) {
    // 创建一个Markdown渲染模板
    return {
        id: id,
        type: 'markdown',
        x: x,
        y: y,
        content: '# 标题\n\n这是一段**加粗**的文本和*斜体*文本。\n\n- 列表项1\n- 列表项2\n- 列表项3\n\n> 这是一个引用块',
        fontSize: 16,
        color: '#333333',
        width: 500,
        height: 300
    };
}

function renderElements() {
    const svgEditor = document.getElementById('svgEditor');
    svgEditor.innerHTML = '';
    
    editorState.elements.forEach(element => {
        if (element.type === 'group') {
            // 渲染组合元素
            element.elements.forEach(subElement => {
                renderElement(svgEditor, subElement);
            });
        } else {
            renderElement(svgEditor, element);
        }
    });
}

function renderElement(svgContainer, element) {
    let svgElement;
    
    switch (element.type) {
        case 'text':
        case 'title':
            svgElement = document.createElementNS('http://www.w3.org/2000/svg', 'foreignObject');
            svgElement.setAttribute('x', element.x);
            svgElement.setAttribute('y', element.y);
            svgElement.setAttribute('width', element.width);
            svgElement.setAttribute('height', element.height);
            
            const div = document.createElement('div');
            div.innerHTML = element.text;
            div.style.fontSize = element.fontSize + 'px';
            div.style.color = element.color;
            div.style.fontWeight = element.fontWeight;
            div.style.textAlign = element.textAlign;
            div.style.width = '100%';
            div.style.height = '100%';
            div.style.overflow = 'hidden';
            div.style.wordWrap = 'break-word';
            div.style.padding = '5px';
            div.contentEditable = true;
            div.style.outline = 'none';
            div.dataset.elementId = element.id;
            
            div.addEventListener('input', function() {
                const id = this.dataset.elementId;
                const el = findElementById(id);
                if (el) {
                    el.text = this.innerHTML;
                }
            });
            
            svgElement.appendChild(div);
            break;
            
        case 'image':
            svgElement = document.createElementNS('http://www.w3.org/2000/svg', 'image');
            svgElement.setAttribute('x', element.x);
            svgElement.setAttribute('y', element.y);
            svgElement.setAttribute('width', element.width);
            svgElement.setAttribute('height', element.height);
            svgElement.setAttribute('href', element.src);
            svgElement.dataset.elementId = element.id;
            svgElement.style.cursor = 'pointer';
            svgElement.addEventListener('click', function() {
                selectElement(this.dataset.elementId);
            });
            break;
            
        case 'divider':
            svgElement = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            svgElement.setAttribute('x', element.x);
            svgElement.setAttribute('y', element.y);
            svgElement.setAttribute('width', element.width);
            svgElement.setAttribute('height', element.height);
            svgElement.setAttribute('fill', element.color);
            svgElement.dataset.elementId = element.id;
            svgElement.style.cursor = 'pointer';
            svgElement.addEventListener('click', function() {
                selectElement(this.dataset.elementId);
            });
            break;
            
        case 'markdown':
            svgElement = document.createElementNS('http://www.w3.org/2000/svg', 'foreignObject');
            svgElement.setAttribute('x', element.x);
            svgElement.setAttribute('y', element.y);
            svgElement.setAttribute('width', element.width);
            svgElement.setAttribute('height', element.height);
            
            const mdDiv = document.createElement('div');
            mdDiv.innerHTML = renderMarkdown(element.content);
            mdDiv.style.fontSize = element.fontSize + 'px';
            mdDiv.style.color = element.color;
            mdDiv.style.width = '100%';
            mdDiv.style.height = '100%';
            mdDiv.style.overflow = 'auto';
            mdDiv.style.padding = '10px';
            mdDiv.dataset.elementId = element.id;
            
            svgElement.appendChild(mdDiv);
            break;
    }
    
    // 添加选择边框（如果元素被选中）
    if (editorState.selectedElement === element.id) {
        svgElement.style.stroke = '#1AAD19';
        svgElement.style.strokeWidth = '2';
        svgElement.style.strokeDasharray = '5,5';
    }
    
    // 添加点击选择事件
    if (element.type !== 'text' && element.type !== 'title') {
        svgElement.addEventListener('click', function(e) {
            e.stopPropagation();
            selectElement(element.id);
        });
    }
    
    svgContainer.appendChild(svgElement);
}

function selectElement(elementId) {
    editorState.selectedElement = elementId;
    renderElements();
    updatePropertiesPanel();
}

function findElementById(id) {
    for (const element of editorState.elements) {
        if (element.id === id) {
            return element;
        }
        // 检查组合元素
        if (element.type === 'group') {
            for (const subElement of element.elements) {
                if (subElement.id === id) {
                    return subElement;
                }
            }
        }
    }
    return null;
}

function updatePropertiesPanel() {
    const panel = document.getElementById('propertiesContent');
    panel.innerHTML = '';
    
    if (!editorState.selectedElement) {
        panel.innerHTML = '<p>选中元素以编辑属性</p>';
        return;
    }
    
    const element = findElementById(editorState.selectedElement);
    if (!element) {
        panel.innerHTML = '<p>选中元素以编辑属性</p>';
        return;
    }
    
    // 根据元素类型创建不同的属性编辑器
    switch (element.type) {
        case 'text':
        case 'title':
            createTextPropertiesPanel(panel, element);
            break;
        case 'image':
            createImagePropertiesPanel(panel, element);
            break;
        case 'divider':
            createDividerPropertiesPanel(panel, element);
            break;
        case 'markdown':
            createMarkdownPropertiesPanel(panel, element);
            break;
        default:
            panel.innerHTML = '<p>该元素类型暂不支持属性编辑</p>';
    }
}

function createTextPropertiesPanel(panel, element) {
    panel.innerHTML = `\n        <label>文本内容:</label>\n        <textarea id="textValue" rows="4">${element.text}</textarea>\n        \n        <label>字体大小:</label>\n        <input type="number" id="fontSize" value="${element.fontSize}">\n        \n        <label>文字颜色:</label>\n        <input type="color" id="color" value="${element.color}">\n        \n        <label>字体粗细:</label>\n        <select id="fontWeight">\n            <option value="normal" ${element.fontWeight === 'normal' ? 'selected' : ''}>普通</option>\n            <option value="bold" ${element.fontWeight === 'bold' ? 'selected' : ''}>粗体</option>\n        </select>\n        \n        <label>对齐方式:</label>\n        <select id="textAlign">\n            <option value="left" ${element.textAlign === 'left' ? 'selected' : ''}>左对齐</option>\n            <option value="center" ${element.textAlign === 'center' ? 'selected' : ''}>居中</option>\n            <option value="right" ${element.textAlign === 'right' ? 'selected' : ''}>右对齐</option>\n        </select>\n    `;
    
    // 绑定事件
    document.getElementById('textValue').addEventListener('input', function() {
        element.text = this.value;
        renderElements();
        selectElement(element.id);
    });
    
    document.getElementById('fontSize').addEventListener('input', function() {
        element.fontSize = parseInt(this.value);
        renderElements();
        selectElement(element.id);
    });
    
    document.getElementById('color').addEventListener('input', function() {
        element.color = this.value;
        renderElements();
        selectElement(element.id);
    });
    
    document.getElementById('fontWeight').addEventListener('change', function() {
        element.fontWeight = this.value;
        renderElements();
        selectElement(element.id);
    });
    
    document.getElementById('textAlign').addEventListener('change', function() {
        element.textAlign = this.value;
        renderElements();
        selectElement(element.id);
    });
}

function createImagePropertiesPanel(panel, element) {
    panel.innerHTML = `\n        <label>图片链接:</label>\n        <input type="text" id="imageSrc" value="${element.src}">\n        \n        <label>宽度:</label>\n        <input type="number" id="imageWidth" value="${element.width}">\n        \n        <label>高度:</label>\n        <input type="number" id="imageHeight" value="${element.height}">\n    `;
    
    document.getElementById('imageSrc').addEventListener('input', function() {
        element.src = this.value;
        renderElements();
        selectElement(element.id);
    });
    
    document.getElementById('imageWidth').addEventListener('input', function() {
        element.width = parseInt(this.value);
        renderElements();
        selectElement(element.id);
    });
    
    document.getElementById('imageHeight').addEventListener('input', function() {
        element.height = parseInt(this.value);
        renderElements();
        selectElement(element.id);
    });
}

function createDividerPropertiesPanel(panel, element) {
    panel.innerHTML = `\n        <label>线条颜色:</label>\n        <input type="color" id="dividerColor" value="${element.color}">\n        \n        <label>宽度:</label>\n        <input type="number" id="dividerWidth" value="${element.width}">\n        \n        <label>高度:</label>\n        <input type="number" id="dividerHeight" value="${element.height}">\n    `;
    
    document.getElementById('dividerColor').addEventListener('input', function() {
        element.color = this.value;
        renderElements();
        selectElement(element.id);
    });
    
    document.getElementById('dividerWidth').addEventListener('input', function() {
        element.width = parseInt(this.value);
        renderElements();
        selectElement(element.id);
    });
    
    document.getElementById('dividerHeight').addEventListener('input', function() {
        element.height = parseInt(this.value);
        renderElements();
        selectElement(element.id);
    });
}

function createMarkdownPropertiesPanel(panel, element) {
    panel.innerHTML = `\n        <label>Markdown内容:</label>\n        <textarea id="markdownContent" rows="8">${element.content}</textarea>\n        \n        <label>字体大小:</label>\n        <input type="number" id="mdFontSize" value="${element.fontSize}">\n        \n        <label>文字颜色:</label>\n        <input type="color" id="mdColor" value="${element.color}">\n    `;
    
    document.getElementById('markdownContent').addEventListener('input', function() {
        element.content = this.value;
        renderElements();
        selectElement(element.id);
    });
    
    document.getElementById('mdFontSize').addEventListener('input', function() {
        element.fontSize = parseInt(this.value);
        renderElements();
        selectElement(element.id);
    });
    
    document.getElementById('mdColor').addEventListener('input', function() {
        element.color = this.value;
        renderElements();
        selectElement(element.id);
    });
}

// 模板相关功能
function saveTemplate() {
    const name = prompt('请输入模板名称:');
    if (!name) return;
    
    const template = {
        name: name,
        elements: JSON.parse(JSON.stringify(editorState.elements)), // 深拷贝
        createdAt: new Date().toISOString()
    };
    
    templates[name] = template;
    saveTemplatesToStorage();
    loadSavedTemplates();
    
    alert('模板已保存！');
}

function loadTemplate() {
    const name = prompt('请输入要加载的模板名称:');
    if (!name || !templates[name]) {
        alert('模板不存在！');
        return;
    }
    
    const template = templates[name];
    editorState.elements = JSON.parse(JSON.stringify(template.elements)); // 深拷贝
    renderElements();
    selectElement(null);
    
    alert('模板已加载！');
}

function exportTemplate() {
    const name = prompt('请输入要导出的模板名称:');
    if (!name || !templates[name]) {
        alert('模板不存在！');
        return;
    }
    
    const template = templates[name];
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(template, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", name + ".json");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
}

function importTemplate() {
    // 通过文件输入实现，在setupEventListeners中已处理
    document.getElementById('templateFileInput').click();
}

function saveTemplatesToStorage() {
    localStorage.setItem('wechatEditorTemplates', JSON.stringify(templates));
}

function loadSavedTemplates() {
    const list = document.getElementById('savedTemplatesList');
    list.innerHTML = '';
    
    for (const name in templates) {
        const template = templates[name];
        const li = document.createElement('li');
        li.className = 'template-item';
        li.innerHTML = `\n            <span>${template.name}</span>\n            <div class="actions">\n                <button class="load" onclick="loadSpecificTemplate('${name}')">加载</button>\n                <button class="delete" onclick="deleteTemplate('${name}')">删除</button>\n            </div>\n        `;
        list.appendChild(li);
    }
}

function loadSpecificTemplate(name) {
    if (!templates[name]) return;
    
    const template = templates[name];
    editorState.elements = JSON.parse(JSON.stringify(template.elements)); // 深拷贝
    renderElements();
    selectElement(null);
}

function deleteTemplate(name) {
    if (confirm(`确定要删除模板 "${name}" 吗？`)) {
        delete templates[name];
        saveTemplatesToStorage();
        loadSavedTemplates();
    }
}

// Markdown渲染函数（增强版）
function renderMarkdown(mdText) {
    let html = mdText;
    
    // 代码块处理（需要特殊处理）
    html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    
    // 标题（支持1-6级标题）
    html = html.replace(/^###### (.*$)/gim, '<h6>$1</h6>');
    html = html.replace(/^##### (.*$)/gim, '<h5>$1</h5>');
    html = html.replace(/^#### (.*$)/gim, '<h4>$1</h4>');
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$2</h2>'); // 修复：使用$2而不是$1
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    // 修复上面的正则表达式问题，重新处理标题
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    
    // 加粗（支持**和__）
    html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
    html = html.replace(/__(.*?)__/gim, '<strong>$1</strong>');
    
    // 斜体（支持*和_）
    html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');
    html = html.replace(/_(.*?)_/gim, '<em>$1</em>');
    
    // 行内代码
    html = html.replace(/`(.*?)`/g, '<code>$1</code>');
    
    // 无序列表
    html = html.replace(/^\- (.*$)/gim, '<li>$1</li>');
    html = html.replace(/^\* (.*$)/gim, '<li>$1</li>');
    html = html.replace(/^\+ (.*$)/gim, '<li>$1</li>');
    
    // 有序列表
    html = html.replace(/^\d+\. (.*$)/gim, '<li>$1</li>');
    
    // 将列表项包装在ul/ol中
    html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
    // 这里需要更复杂的逻辑来正确处理列表，简化起见，我们用一个近似方法
    
    // 引用
    html = html.replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>');
    
    // 链接
    html = html.replace(/\[(.*?)\]\((.*?)\)/gim, '<a href="$2" target="_blank">$1</a>');
    
    // 图片
    html = html.replace(/!\[(.*?)\]\((.*?)\)/gim, '<img src="$2" alt="$1" style="max-width: 100%;">');
    
    // 段落 - 将换行符转换为段落
    html = html.replace(/\n\n/gim, '</p><p>');
    html = '<p>' + html + '</p>';
    html = html.replace(/<p><\/p>/gim, '');
    
    // 清理多余的换行符
    html = html.replace(/\n/gim, '<br>');
    
    // 添加样式类以便进一步样式化
    html = html.replace(/<h1>/g, '<h1 class="md-h1">');
    html = html.replace(/<h2>/g, '<h2 class="md-h2">');
    html = html.replace(/<h3>/g, '<h3 class="md-h3">');
    html = html.replace(/<h4>/g, '<h4 class="md-h4">');
    html = html.replace(/<h5>/g, '<h5 class="md-h5">');
    html = html.replace(/<h6>/g, '<h6 class="md-h6">');
    html = html.replace(/<strong>/g, '<strong class="md-strong">');
    html = html.replace(/<em>/g, '<em class="md-em">');
    html = html.replace(/<ul>/g, '<ul class="md-ul">');
    html = html.replace(/<ol>/g, '<ol class="md-ol">');
    html = html.replace(/<li>/g, '<li class="md-li">');
    html = html.replace(/<blockquote>/g, '<blockquote class="md-blockquote">');
    html = html.replace(/<code>/g, '<code class="md-code">');
    html = html.replace(/<pre>/g, '<pre class="md-pre">');
    
    return html;
}

// 发布到微信公众号
function publishToWechat() {
    // 将编辑器内容转换为适合微信公众号的格式
    const content = generateWechatContent();
    
    // 保存当前编辑的内容到本地存储，以便发布脚本使用
    localStorage.setItem('wechatArticleContent', JSON.stringify({
        elements: editorState.elements,
        content: content
    }));
    
    // 在新窗口中打开发布页面
    window.open('publish.html', '_blank', 'width=900,height=700');
}

function generateWechatContent() {
    let content = '';
    
    editorState.elements.forEach(element => {
        if (element.type === 'group') {
            // 处理组合元素
            element.elements.forEach(subElement => {
                content += generateElementContent(subElement);
            });
        } else {
            content += generateElementContent(element);
        }
    });
    
    return content;
}

function generateElementContent(element) {
    switch (element.type) {
        case 'text':
            return `<p style="font-size:${element.fontSize}px; color:${element.color}; text-align:${element.textAlign}; line-height: 1.8;">${element.text}</p>`;
        case 'title':
            return `<h2 style="font-size:${element.fontSize}px; color:${element.color}; font-weight:${element.fontWeight}; text-align:${element.textAlign}; margin: 20px 0;">${element.text}</h2>`;
        case 'image':
            return `<div style="text-align: center; margin: 20px 0;"><img src="${element.src}" style="max-width: 100%; height: auto; border-radius: 4px;" width="${element.width}" height="${element.height}"></div>`;
        case 'divider':
            return `<hr style="border: 0; height: ${element.height}px; background-color: ${element.color}; margin: 20px 0;">`;
        case 'markdown':
            return renderMarkdown(element.content);
        default:
            return '';
    }
}
