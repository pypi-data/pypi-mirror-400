"""
Jinja2 过滤器
=============
过滤器用于修改变量的输出，使用管道符 | 连接。
可以链式调用多个过滤器。
"""

from jinja2 import Template, Environment

# region 示例1: 字符串过滤器
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例1: 字符串过滤器")
    print("=" * 50)
    
    template_str = """
原始: {{ text }}
大写: {{ text | upper }}
小写: {{ text | lower }}
首字母大写: {{ text | capitalize }}
标题格式: {{ text | title }}
长度: {{ text | length }}
"""
    template = Template(template_str)
    print(template.render(text="hello WORLD").strip())
    print()
# endregion

# region 示例2: 列表过滤器
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例2: 列表过滤器")
    print("=" * 50)
    
    template_str = """
原始列表: {{ numbers }}
第一个: {{ numbers | first }}
最后一个: {{ numbers | last }}
排序: {{ numbers | sort }}
倒序: {{ numbers | reverse | list }}
求和: {{ numbers | sum }}
连接: {{ words | join(', ') }}
随机: {{ numbers | random }}
"""
    template = Template(template_str)
    print(template.render(
        numbers=[3, 1, 4, 1, 5, 9, 2, 6],
        words=["苹果", "香蕉", "橙子"]
    ).strip())
    print()
# endregion

# region 示例3: 数值过滤器
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例3: 数值过滤器")
    print("=" * 50)
    
    template_str = """
原始值: {{ value }}
绝对值: {{ value | abs }}
四舍五入: {{ pi | round }}
保留2位: {{ pi | round(2) }}
整数: {{ pi | int }}
浮点数: {{ num | float }}
"""
    template = Template(template_str)
    print(template.render(value=-42, pi=3.14159, num="123").strip())
    print()
# endregion

# region 示例4: 过滤器链式调用
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例4: 过滤器链式调用")
    print("=" * 50)
    
    # 多个过滤器从左到右依次执行
    template_str = """
原始: {{ text }}
处理后: {{ text | trim | lower | replace(' ', '_') }}
"""
    template = Template(template_str)
    print(template.render(text="  Hello World  ").strip())
    print()
# endregion

# region 示例5: 安全相关过滤器
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例5: 安全相关过滤器")
    print("=" * 50)
    
    # escape 过滤器转义 HTML 特殊字符
    template_str = """
转义HTML: {{ html | e }}
原始HTML: {{ html | safe }}
"""
    # 注意: 在实际 Web 应用中，safe 过滤器要谨慎使用
    template = Template(template_str)
    print(template.render(html="<script>alert('XSS')</script>").strip())
    print()
# endregion

# region 示例6: 自定义过滤器
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例6: 自定义过滤器")
    print("=" * 50)
    
    # 创建环境并注册自定义过滤器
    env = Environment()
    
    # 定义过滤器函数
    def reverse_string(s):
        """反转字符串"""
        return s[::-1]
    
    def format_price(value, currency="¥"):
        """格式化价格"""
        return f"{currency}{value:.2f}"
    
    # 注册过滤器
    env.filters["reverse"] = reverse_string
    env.filters["price"] = format_price
    
    template = env.from_string("""
反转: {{ text | reverse }}
价格: {{ amount | price }}
美元: {{ amount | price('$') }}
""")
    print(template.render(text="Hello", amount=99.5).strip())
    print()
# endregion
