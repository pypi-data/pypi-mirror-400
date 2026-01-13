"""
Lambda 表达式进阶技巧
====================
探索 lambda 的高级用法，包括条件表达式、嵌套、闭包等。
"""

# region 示例1: lambda 中的条件表达式
if True:  # 改为 False 可跳过此示例
    print("=== lambda 中的条件表达式 ===")
    
    # 三元表达式: value_if_true if condition else value_if_false
    abs_val = lambda x: x if x >= 0 else -x
    print(f"abs_val(-5) = {abs_val(-5)}")
    print(f"abs_val(3) = {abs_val(3)}")
    
    # 判断奇偶
    odd_or_even = lambda n: "偶数" if n % 2 == 0 else "奇数"
    print(f"7 是 {odd_or_even(7)}")
    print(f"10 是 {odd_or_even(10)}")
    
    # 嵌套条件（不推荐过度使用，影响可读性）
    grade = lambda score: "优秀" if score >= 90 else ("良好" if score >= 80 else ("及格" if score >= 60 else "不及格"))
    print(f"95分: {grade(95)}, 75分: {grade(75)}, 55分: {grade(55)}")
# endregion

# region 示例2: lambda 与闭包
if True:  # 改为 False 可跳过此示例
    print("\n=== lambda 与闭包 ===")
    
    # lambda 可以捕获外部变量
    def make_multiplier(n):
        return lambda x: x * n
    
    double = make_multiplier(2)
    triple = make_multiplier(3)
    
    print(f"double(5) = {double(5)}")  # 10
    print(f"triple(5) = {triple(5)}")  # 15
    
    # 创建一系列函数
    powers = [lambda x, n=i: x ** n for i in range(5)]
    # 注意: n=i 是关键，否则所有 lambda 都会捕获循环结束时的 i 值
    print(f"2的0-4次方: {[f(2) for f in powers]}")
# endregion

# region 示例3: 闭包陷阱与解决方案
if True:  # 改为 False 可跳过此示例
    print("\n=== 闭包陷阱 ===")
    
    # 错误示例：所有 lambda 共享同一个变量 i
    funcs_wrong = [lambda x: x + i for i in range(3)]
    print(f"错误结果 (都使用最后的i=2): {[f(10) for f in funcs_wrong]}")  # [12, 12, 12]
    
    # 正确示例：使用默认参数捕获当前值
    funcs_right = [lambda x, i=i: x + i for i in range(3)]
    print(f"正确结果: {[f(10) for f in funcs_right]}")  # [10, 11, 12]
# endregion

# region 示例4: lambda 作为字典值
if True:  # 改为 False 可跳过此示例
    print("\n=== lambda 作为字典值（策略模式）===")
    
    # 简单计算器
    operations = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: a / b if b != 0 else "除数不能为0",
    }
    
    def calculate(a, op, b):
        return operations.get(op, lambda a, b: "未知操作")(a, b)
    
    print(f"10 + 3 = {calculate(10, '+', 3)}")
    print(f"10 - 3 = {calculate(10, '-', 3)}")
    print(f"10 * 3 = {calculate(10, '*', 3)}")
    print(f"10 / 3 = {calculate(10, '/', 3):.2f}")
    print(f"10 / 0 = {calculate(10, '/', 0)}")
# endregion

# region 示例5: lambda 与 *args, **kwargs
if True:  # 改为 False 可跳过此示例
    print("\n=== lambda 与可变参数 ===")
    
    # 接受任意数量参数
    sum_all = lambda *args: sum(args)
    print(f"sum_all(1, 2, 3, 4, 5) = {sum_all(1, 2, 3, 4, 5)}")
    
    # 接受关键字参数
    format_person = lambda **kwargs: f"{kwargs.get('name', '匿名')} - {kwargs.get('age', '未知')}岁"
    print(f"format_person(name='小明', age=20) = {format_person(name='小明', age=20)}")
    print(f"format_person() = {format_person()}")
    
    # 混合使用
    mixed = lambda x, *args, **kwargs: f"x={x}, args={args}, kwargs={kwargs}"
    print(f"mixed(1, 2, 3, a=4, b=5) = {mixed(1, 2, 3, a=4, b=5)}")
# endregion
