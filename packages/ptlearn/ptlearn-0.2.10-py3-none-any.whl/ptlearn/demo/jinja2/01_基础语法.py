"""
Jinja2 基础语法
===============
Jinja2 是 Python 中最流行的模板引擎，用于生成动态文本内容。
本文件介绍 Jinja2 的基本语法：变量、表达式和注释。

安装: pip install Jinja2
"""

from jinja2 import Template

# region 示例1: 变量渲染
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例1: 变量渲染")
    print("=" * 50)
    
    # 使用 {{ }} 语法插入变量
    template = Template("你好, {{ name }}!")
    result = template.render(name="世界")
    print(result)
    
    # 渲染多个变量
    template = Template("{{ greeting }}, {{ name }}! 今天是 {{ day }}。")
    result = template.render(greeting="早上好", name="小明", day="星期三")
    print(result)
    print()
# endregion

# region 示例2: 访问对象属性和字典
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例2: 访问对象属性和字典")
    print("=" * 50)
    
    # 访问字典的值 - 两种方式等价
    template = Template("姓名: {{ user.name }}, 年龄: {{ user['age'] }}")
    user = {"name": "张三", "age": 25}
    print(template.render(user=user))
    
    # 访问对象属性
    class Person:
        def __init__(self, name, city):
            self.name = name
            self.city = city
    
    template = Template("{{ person.name }} 来自 {{ person.city }}")
    person = Person("李四", "北京")
    print(template.render(person=person))
    print()
# endregion

# region 示例3: 表达式和运算
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例3: 表达式和运算")
    print("=" * 50)
    
    # 数学运算
    template = Template("{{ a }} + {{ b }} = {{ a + b }}")
    print(template.render(a=10, b=20))
    
    # 字符串拼接
    template = Template("全名: {{ first ~ ' ' ~ last }}")
    print(template.render(first="张", last="三"))
    
    # 比较运算（结果为布尔值）
    template = Template("{{ score }} 分, 是否及格: {{ score >= 60 }}")
    print(template.render(score=75))
    print()
# endregion

# region 示例4: 注释语法
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例4: 注释语法")
    print("=" * 50)
    
    # {# #} 中的内容不会出现在输出中
    template_str = """
姓名: {{ name }}
{# 这是一个注释，不会被渲染 #}
城市: {{ city }}
"""
    template = Template(template_str)
    result = template.render(name="王五", city="上海")
    print(result.strip())
    print()
# endregion

# region 示例5: 默认值和未定义变量处理
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例5: 默认值和未定义变量处理")
    print("=" * 50)
    
    # 使用 default 过滤器设置默认值
    template = Template("欢迎, {{ username | default('游客') }}!")
    print(template.render())  # 未传入 username
    print(template.render(username="管理员"))
    
    # 检查变量是否已定义
    template = Template("{% if name is defined %}你好, {{ name }}{% else %}请登录{% endif %}")
    print(template.render())
    print(template.render(name="小红"))
    print()
# endregion
