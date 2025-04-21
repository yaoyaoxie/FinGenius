CREATE_HTML_TOOL_PROMPT = """你是一个专业的网页前端开发专家，精通HTML、CSS和JavaScript。
你的任务是根据用户的需求，直接生成完整、美观、功能齐全的网页代码。

请遵循以下规范：
1. 代码应符合最新的HTML5、CSS3标准
2. 使用语义化标签，确保网页结构清晰
3. 优先使用Flex和Grid布局，确保响应式设计
4. 默认添加移动端适配
5. 采用现代化设计风格
6. 可以使用Bootstrap、Tailwind等主流CSS框架
7. 可以使用原生JavaScript或Vue.js、React等框架
8. 所有资源应使用CDN链接或内联到HTML中
9. 包含必要的交互效果
10. 代码应干净、优化、无冗余
11. 如无特殊要求，应优先使用Bootstrap 5框架快速构建页面
12. 确保所有中文内容使用UTF-8编码，避免乱码问题

输出格式：
```html
<!DOCTYPE html>
<html>
...完整的HTML代码...
</html>
```

请只输出HTML代码，不要有任何其他解释性文字。
"""

CREATE_HTML_TEMPLATE_PROMPT = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>网页标题</title>
    <style>
        /* 现代化CSS样式 */
        :root {
            --primary-color: #4a6bdf;
            --secondary-color: #5d7efa;
            --accent-color: #f3f4f6;
            --text-color: #333;
            --light-text: #666;
            --border-radius: 8px;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            color: var(--text-color);
            line-height: 1.6;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            margin-bottom: 30px;
            text-align: center;
        }

        h1 {
            color: var(--primary-color);
            margin-bottom: 15px;
        }

        .container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
        }

        .card {
            background: white;
            border-radius: var(--border-radius);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            padding: 20px;
            transition: transform 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
        }

        .btn {
            display: inline-block;
            background: var(--primary-color);
            color: white;
            padding: 10px 20px;
            border-radius: var(--border-radius);
            text-decoration: none;
            transition: background 0.3s ease;
        }

        .btn:hover {
            background: var(--secondary-color);
        }

        @media (max-width: 768px) {
            .container {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>页面标题</h1>
        <p>页面描述或副标题</p>
    </header>

    <main class="container">
        <section class="card">
            <h2>内容区域 1</h2>
            <p>这里是一些内容描述...</p>
            <a href="#" class="btn">按钮</a>
        </section>

        <section class="card">
            <h2>内容区域 2</h2>
            <p>这里是一些内容描述...</p>
            <a href="#" class="btn">按钮</a>
        </section>
    </main>

    <footer>
        <p>&copy; 2023 网站名称. 版权所有.</p>
    </footer>

    <script>
        // JavaScript 交互代码
        document.addEventListener('DOMContentLoaded', function() {
            console.log('页面已加载完成');

            // 示例：为所有按钮添加点击事件
            const buttons = document.querySelectorAll('.btn');
            buttons.forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    alert('按钮被点击了!');
                });
            });
        });
    </script>
</body>
</html>
"""
