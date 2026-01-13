"""
Jinja2 模板继承
===============
模板继承是 Jinja2 最强大的功能之一，允许创建基础模板并在子模板中扩展。
这是构建大型项目时组织模板的核心机制。
"""

from jinja2 import Environment, BaseLoader, DictLoader

# region 示例1: 基本的模板继承
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例1: 基本的模板继承")
    print("=" * 50)
    
    # 使用 DictLoader 模拟文件系统中的模板
    templates = {
        "base.html": """
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}默认标题{% endblock %}</title>
</head>
<body>
    <header>网站头部</header>
    <main>
        {% block content %}
        默认内容
        {% endblock %}
    </main>
    <footer>网站底部</footer>
</body>
</html>
""",
        "home.html": """
{% extends "base.html" %}

{% block title %}首页{% endblock %}

{% block content %}
<h1>欢迎来到首页</h1>
<p>这是首页的内容</p>
{% endblock %}
"""
    }
    
    env = Environment(loader=DictLoader(templates))
    template = env.get_template("home.html")
    print(template.render().strip())
    print()
# endregion

# region 示例2: 使用 super() 保留父模板内容
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例2: 使用 super() 保留父模板内容")
    print("=" * 50)
    
    templates = {
        "base.html": """
{% block content %}
<p>基础内容</p>
{% endblock %}
""",
        "child.html": """
{% extends "base.html" %}

{% block content %}
{{ super() }}
<p>子模板追加的内容</p>
{% endblock %}
"""
    }
    
    env = Environment(loader=DictLoader(templates))
    template = env.get_template("child.html")
    print(template.render().strip())
    print()
# endregion

# region 示例3: 多级继承
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例3: 多级继承")
    print("=" * 50)
    
    templates = {
        "base.html": """
[基础布局]
{% block body %}基础内容{% endblock %}
""",
        "layout.html": """
{% extends "base.html" %}
{% block body %}
[布局层]
{% block content %}布局内容{% endblock %}
{% endblock %}
""",
        "page.html": """
{% extends "layout.html" %}
{% block content %}
[页面层] 最终页面内容
{% endblock %}
"""
    }
    
    env = Environment(loader=DictLoader(templates))
    template = env.get_template("page.html")
    print(template.render().strip())
    print()
# endregion

# region 示例4: 块的作用域
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例4: 块的作用域 (scoped)")
    print("=" * 50)
    
    templates = {
        "base.html": """
{% for item in items %}
{% block item scoped %}{{ item }}{% endblock %}
{% endfor %}
""",
        "child.html": """
{% extends "base.html" %}
{% block item %}[{{ item }}]{% endblock %}
"""
    }
    
    # scoped 关键字让块可以访问循环变量
    env = Environment(loader=DictLoader(templates))
    template = env.get_template("child.html")
    print(template.render(items=["A", "B", "C"]).strip())
    print()
# endregion
