"""
Jinja2 宏和包含
===============
宏(macro)类似于函数，可以复用模板片段。
include 用于包含其他模板文件。
"""

from jinja2 import Environment, DictLoader, Template

# region 示例1: 定义和使用宏
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例1: 定义和使用宏")
    print("=" * 50)
    
    template_str = """
{% macro input(name, value='', type='text') %}
<input type="{{ type }}" name="{{ name }}" value="{{ value }}">
{% endmacro %}

{% macro button(text, type='submit') %}
<button type="{{ type }}">{{ text }}</button>
{% endmacro %}

表单元素:
{{ input('username') }}
{{ input('password', type='password') }}
{{ input('email', 'test@example.com', 'email') }}
{{ button('提交') }}
{{ button('重置', 'reset') }}
"""
    template = Template(template_str)
    print(template.render().strip())
    print()
# endregion

# region 示例2: 宏的 caller 功能
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例2: 宏的 caller 功能")
    print("=" * 50)
    
    # caller() 允许在宏中插入调用者提供的内容
    template_str = """
{% macro card(title) %}
<div class="card">
    <h3>{{ title }}</h3>
    <div class="content">
        {{ caller() }}
    </div>
</div>
{% endmacro %}

{% call card('用户信息') %}
<p>姓名: 张三</p>
<p>年龄: 25</p>
{% endcall %}

{% call card('系统状态') %}
<p>CPU: 45%</p>
<p>内存: 60%</p>
{% endcall %}
"""
    template = Template(template_str)
    print(template.render().strip())
    print()
# endregion

# region 示例3: 从其他模板导入宏
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例3: 从其他模板导入宏")
    print("=" * 50)
    
    templates = {
        "macros.html": """
{% macro list_item(text) %}<li>{{ text }}</li>{% endmacro %}
{% macro link(url, text) %}<a href="{{ url }}">{{ text }}</a>{% endmacro %}
""",
        "page.html": """
{% from "macros.html" import list_item, link %}

<ul>
{{ list_item('项目1') }}
{{ list_item('项目2') }}
{{ list_item('项目3') }}
</ul>

{{ link('https://python.org', 'Python官网') }}
"""
    }
    
    env = Environment(loader=DictLoader(templates))
    template = env.get_template("page.html")
    print(template.render().strip())
    print()
# endregion

# region 示例4: include 包含模板
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例4: include 包含模板")
    print("=" * 50)
    
    templates = {
        "header.html": "<header>网站头部 - {{ site_name }}</header>",
        "footer.html": "<footer>版权所有 © 2024</footer>",
        "page.html": """
{% include "header.html" %}

<main>
页面主要内容
</main>

{% include "footer.html" %}
"""
    }
    
    env = Environment(loader=DictLoader(templates))
    template = env.get_template("page.html")
    print(template.render(site_name="我的网站").strip())
    print()
# endregion

# region 示例5: include 的高级用法
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例5: include 的高级用法")
    print("=" * 50)
    
    templates = {
        "sidebar.html": "<aside>侧边栏内容</aside>",
        "page.html": """
{# ignore missing: 如果模板不存在则忽略 #}
{% include "nonexistent.html" ignore missing %}

{# with context: 传递当前上下文（默认行为） #}
{% include "sidebar.html" %}

{# without context: 不传递上下文 #}
{% include "sidebar.html" without context %}
"""
    }
    
    env = Environment(loader=DictLoader(templates))
    template = env.get_template("page.html")
    print(template.render().strip())
    print()
# endregion
