"""
Jinja2 控制结构
===============
本文件介绍 Jinja2 的控制流语句：条件判断和循环。
使用 {% %} 语法块来编写控制逻辑。
"""

from jinja2 import Template

# region 示例1: if 条件判断
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例1: if 条件判断")
    print("=" * 50)
    
    template_str = """
{% if score >= 90 %}
成绩: 优秀
{% elif score >= 60 %}
成绩: 及格
{% else %}
成绩: 不及格
{% endif %}
"""
    template = Template(template_str)
    
    for score in [95, 75, 45]:
        result = template.render(score=score).strip()
        print(f"分数 {score}: {result}")
    print()
# endregion

# region 示例2: for 循环遍历列表
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例2: for 循环遍历列表")
    print("=" * 50)
    
    template_str = """
水果列表:
{% for fruit in fruits %}
- {{ fruit }}
{% endfor %}
"""
    template = Template(template_str)
    result = template.render(fruits=["苹果", "香蕉", "橙子"])
    print(result.strip())
    print()
# endregion

# region 示例3: 循环变量 loop
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例3: 循环变量 loop")
    print("=" * 50)
    
    # loop 对象提供循环的元信息
    template_str = """
{% for item in items %}
{{ loop.index }}. {{ item }} (索引: {{ loop.index0 }}, 剩余: {{ loop.revindex }})
{% endfor %}
总数: {{ items | length }}
"""
    template = Template(template_str)
    result = template.render(items=["Python", "Java", "Go"])
    print(result.strip())
    
    # loop 的常用属性:
    # loop.index    - 当前迭代次数（从1开始）
    # loop.index0   - 当前迭代次数（从0开始）
    # loop.first    - 是否是第一次迭代
    # loop.last     - 是否是最后一次迭代
    # loop.length   - 序列长度
    # loop.revindex - 到循环结束的迭代次数（从1开始）
    print()
# endregion

# region 示例4: 遍历字典
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例4: 遍历字典")
    print("=" * 50)
    
    template_str = """
用户信息:
{% for key, value in user.items() %}
  {{ key }}: {{ value }}
{% endfor %}
"""
    template = Template(template_str)
    user = {"姓名": "张三", "年龄": 28, "城市": "深圳"}
    print(template.render(user=user).strip())
    print()
# endregion

# region 示例5: 循环中的条件过滤
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例5: 循环中的条件过滤")
    print("=" * 50)
    
    # 使用 if 过滤循环项
    template_str = """
及格的学生:
{% for student in students if student.score >= 60 %}
- {{ student.name }}: {{ student.score }}分
{% endfor %}
"""
    template = Template(template_str)
    students = [
        {"name": "小明", "score": 85},
        {"name": "小红", "score": 45},
        {"name": "小刚", "score": 72},
        {"name": "小美", "score": 58},
    ]
    print(template.render(students=students).strip())
    print()
# endregion

# region 示例6: 空循环处理 else
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例6: 空循环处理 else")
    print("=" * 50)
    
    template_str = """
{% for item in items %}
- {{ item }}
{% else %}
列表为空，没有数据
{% endfor %}
"""
    template = Template(template_str)
    
    print("有数据时:")
    print(template.render(items=["A", "B"]).strip())
    
    print("\n无数据时:")
    print(template.render(items=[]).strip())
    print()
# endregion
