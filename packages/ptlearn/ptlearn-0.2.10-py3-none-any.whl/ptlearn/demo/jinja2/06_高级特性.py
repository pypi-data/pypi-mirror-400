"""
Jinja2 高级特性
===============
本文件介绍 Jinja2 的高级功能：
- 自定义测试
- 全局变量和函数
- 空白控制
- 沙箱环境
"""

from jinja2 import Environment, Template, sandbox

# region 示例1: 测试 (Tests)
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例1: 测试 (Tests)")
    print("=" * 50)
    
    # 测试用于检查变量的特性，使用 is 关键字
    template_str = """
{% if number is odd %}{{ number }} 是奇数{% endif %}
{% if number is even %}{{ number }} 是偶数{% endif %}
{% if name is defined %}name 已定义: {{ name }}{% endif %}
{% if items is iterable %}items 可迭代{% endif %}
{% if value is none %}value 是 None{% endif %}
{% if text is string %}text 是字符串{% endif %}
"""
    template = Template(template_str)
    print(template.render(
        number=7,
        name="测试",
        items=[1, 2, 3],
        value=None,
        text="hello"
    ).strip())
    print()
# endregion

# region 示例2: 自定义测试
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例2: 自定义测试")
    print("=" * 50)
    
    env = Environment()
    
    # 定义自定义测试函数
    def is_prime(n):
        """检查是否为质数"""
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    def is_palindrome(s):
        """检查是否为回文"""
        s = str(s).lower()
        return s == s[::-1]
    
    # 注册测试
    env.tests["prime"] = is_prime
    env.tests["palindrome"] = is_palindrome
    
    template = env.from_string("""
{% for n in numbers %}
{{ n }}: {% if n is prime %}质数{% else %}非质数{% endif %}
{% endfor %}

{% for word in words %}
{{ word }}: {% if word is palindrome %}回文{% else %}非回文{% endif %}
{% endfor %}
""")
    print(template.render(
        numbers=[2, 4, 7, 9, 11],
        words=["level", "hello", "radar"]
    ).strip())
    print()
# endregion

# region 示例3: 全局变量和函数
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例3: 全局变量和函数")
    print("=" * 50)
    
    from datetime import datetime
    
    env = Environment()
    
    # 添加全局变量
    env.globals["site_name"] = "我的网站"
    env.globals["version"] = "1.0.0"
    
    # 添加全局函数
    env.globals["now"] = datetime.now
    env.globals["range"] = range
    
    template = env.from_string("""
站点: {{ site_name }} v{{ version }}
当前时间: {{ now().strftime('%Y-%m-%d %H:%M') }}
数字序列: {% for i in range(1, 6) %}{{ i }} {% endfor %}
""")
    print(template.render().strip())
    print()
# endregion

# region 示例4: 空白控制
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例4: 空白控制")
    print("=" * 50)
    
    # 使用 - 符号去除空白
    # {%- 去除标签前的空白
    # -%} 去除标签后的空白
    
    template_normal = Template("""
{% for i in items %}
{{ i }}
{% endfor %}
""")
    
    template_trimmed = Template("""
{%- for i in items -%}
{{ i }}
{%- endfor -%}
""")
    
    items = ["A", "B", "C"]
    print("普通模板输出:")
    print(repr(template_normal.render(items=items)))
    
    print("\n去除空白后:")
    print(repr(template_trimmed.render(items=items)))
    
    # 也可以在环境级别设置
    env = Environment(trim_blocks=True, lstrip_blocks=True)
    print()
# endregion

# region 示例5: 沙箱环境
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例5: 沙箱环境")
    print("=" * 50)
    
    # 沙箱环境限制模板可以执行的操作，提高安全性
    env = sandbox.SandboxedEnvironment()
    
    # 正常操作可以执行
    template = env.from_string("{{ items | join(', ') }}")
    print("安全操作:", template.render(items=["a", "b", "c"]))
    
    # 危险操作会被阻止
    try:
        # 尝试访问私有属性
        template = env.from_string("{{ ''.__class__.__mro__ }}")
        template.render()
    except sandbox.SecurityError as e:
        print(f"安全错误: 访问私有属性被阻止")
    print()
# endregion

# region 示例6: 行语句和行注释
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例6: 行语句和行注释")
    print("=" * 50)
    
    # 配置行语句前缀
    env = Environment(
        line_statement_prefix='#',
        line_comment_prefix='##'
    )
    
    template = env.from_string("""
# for item in items
- {{ item }}
# endfor
## 这是一个行注释，不会出现在输出中
""")
    print(template.render(items=["Python", "Java", "Go"]).strip())
    print()
# endregion
