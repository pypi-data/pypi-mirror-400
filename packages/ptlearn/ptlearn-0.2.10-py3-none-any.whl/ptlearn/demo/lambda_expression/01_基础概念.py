"""
Lambda 表达式基础概念
====================
Lambda 是 Python 中创建匿名函数的方式，适用于简单的单行函数场景。
语法: lambda 参数: 表达式
"""

# region 示例1: 最简单的 lambda
if True:  # 改为 False 可跳过此示例
    # lambda 创建一个匿名函数，冒号后面是返回值表达式
    add_one = lambda x: x + 1
    
    print("=== 最简单的 lambda ===")
    print(f"add_one(5) = {add_one(5)}")  # 输出: 6
    print(f"add_one(10) = {add_one(10)}")  # 输出: 11
    
    # 等价的普通函数写法
    def add_one_func(x):
        return x + 1
    
    print(f"普通函数 add_one_func(5) = {add_one_func(5)}")
# endregion

# region 示例2: 多参数 lambda
if False:  # 改为 False 可跳过此示例
    # lambda 可以接受多个参数，用逗号分隔
    add = lambda x, y: x + y
    multiply = lambda x, y, z: x * y * z
    
    print("\n=== 多参数 lambda ===")
    print(f"add(3, 5) = {add(3, 5)}")  # 输出: 8
    print(f"multiply(2, 3, 4) = {multiply(2, 3, 4)}")  # 输出: 24
# endregion

# region 示例3: 无参数 lambda
if False:  # 改为 False 可跳过此示例
    # lambda 也可以没有参数
    get_pi = lambda: 3.14159
    say_hello = lambda: "Hello, World!"
    
    print("\n=== 无参数 lambda ===")
    print(f"get_pi() = {get_pi()}")
    print(f"say_hello() = {say_hello()}")
# endregion

# region 示例4: 带默认参数的 lambda
if False:  # 改为 False 可跳过此示例
    # lambda 支持默认参数值
    greet = lambda name, greeting="你好": f"{greeting}, {name}!"
    power = lambda base, exp=2: base ** exp
    
    print("\n=== 带默认参数的 lambda ===")
    print(f"greet('小明') = {greet('小明')}")  # 使用默认问候语
    print(f"greet('小红', '早上好') = {greet('小红', '早上好')}")  # 自定义问候语
    print(f"power(3) = {power(3)}")  # 3的平方 = 9
    print(f"power(2, 10) = {power(2, 10)}")  # 2的10次方 = 1024
# endregion

# region 示例5: lambda 立即调用
if False:  # 改为 False 可跳过此示例
    # lambda 可以定义后立即调用（IIFE 模式）
    result = (lambda x, y: x + y)(10, 20)
    
    print("\n=== lambda 立即调用 ===")
    print(f"(lambda x, y: x + y)(10, 20) = {result}")  # 输出: 30
    
    # 实际应用：快速计算
    area = (lambda r: 3.14159 * r ** 2)(5)
    print(f"半径为5的圆面积 = {area:.2f}")
# endregion
