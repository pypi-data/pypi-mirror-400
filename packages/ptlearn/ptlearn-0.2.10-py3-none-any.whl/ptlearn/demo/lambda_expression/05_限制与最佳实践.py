"""
Lambda 表达式的限制与最佳实践
============================
了解 lambda 的局限性，掌握何时使用、何时避免。
"""

# region 示例1: lambda 的限制
if True:  # 改为 False 可跳过此示例
    print("=== lambda 的限制 ===")
    
    # 限制1: 只能包含单个表达式，不能包含语句
    # 错误: lambda x: print(x); return x  # 不能有多条语句
    # 错误: lambda x: if x > 0: return x  # 不能用 if 语句
    
    # 正确: 使用表达式形式
    print_and_return = lambda x: (print(f"值: {x}"), x)[1]  # 技巧：用元组
    result = print_and_return(42)
    print(f"返回值: {result}")
    
    # 限制2: 不能包含赋值
    # 错误: lambda x: y = x + 1  # 不能赋值
    
    # 限制3: 不能使用 try/except
    # 需要异常处理时，应使用普通函数
    
    # 限制4: 没有文档字符串
    f = lambda x: x + 1
    print(f"lambda 的 __doc__: {f.__doc__}")  # None
    print(f"lambda 的 __name__: {f.__name__}")  # <lambda>
# endregion

# region 示例2: 何时使用 lambda
if True:  # 改为 False 可跳过此示例
    print("\n=== 适合使用 lambda 的场景 ===")
    
    # 1. 简单的一次性函数
    numbers = [1, 2, 3, 4, 5]
    doubled = list(map(lambda x: x * 2, numbers))
    print(f"简单转换: {doubled}")
    
    # 2. 排序的 key 参数
    pairs = [(1, 'b'), (2, 'a'), (3, 'c')]
    sorted_pairs = sorted(pairs, key=lambda p: p[1])
    print(f"按第二元素排序: {sorted_pairs}")
    
    # 3. 简单的回调函数
    def apply_operation(value, operation):
        return operation(value)
    
    print(f"apply_operation(5, lambda x: x**2) = {apply_operation(5, lambda x: x**2)}")
# endregion

# region 示例3: 何时避免 lambda
if True:  # 改为 False 可跳过此示例
    print("\n=== 应避免使用 lambda 的场景 ===")
    
    # 1. 复杂逻辑 - 使用普通函数更清晰
    # 不推荐:
    complex_lambda = lambda x: "正数" if x > 0 else ("零" if x == 0 else "负数")
    
    # 推荐:
    def classify_number(x):
        """将数字分类为正数、零或负数"""
        if x > 0:
            return "正数"
        elif x == 0:
            return "零"
        else:
            return "负数"
    
    print(f"lambda 方式: {complex_lambda(5)}")
    print(f"函数方式: {classify_number(5)}")
    
    # 2. 需要复用的函数 - 给它一个有意义的名字
    # 不推荐: 赋值给变量的 lambda
    # square = lambda x: x ** 2  # PEP 8 不推荐
    
    # 推荐: 使用 def
    def square(x):
        """计算平方"""
        return x ** 2
    
    # 3. 需要类型注解时
    def typed_add(a: int, b: int) -> int:
        return a + b
    
    # lambda 不支持类型注解语法
    # untyped_add = lambda a, b: a + b  # 无法添加类型注解
# endregion

# region 示例4: lambda vs 列表推导式
if True:  # 改为 False 可跳过此示例
    print("\n=== lambda + map/filter vs 列表推导式 ===")
    
    numbers = range(1, 11)
    
    # 方式1: lambda + map
    squares_map = list(map(lambda x: x ** 2, numbers))
    
    # 方式2: 列表推导式（通常更 Pythonic）
    squares_comp = [x ** 2 for x in numbers]
    
    print(f"map + lambda: {squares_map}")
    print(f"列表推导式: {squares_comp}")
    
    # 筛选偶数的平方
    # 方式1: lambda + filter + map
    even_squares_1 = list(map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, numbers)))
    
    # 方式2: 列表推导式（更简洁）
    even_squares_2 = [x ** 2 for x in numbers if x % 2 == 0]
    
    print(f"filter + map: {even_squares_1}")
    print(f"列表推导式: {even_squares_2}")
    
    # 结论: 简单场景优先使用列表推导式
# endregion

# region 示例5: PEP 8 关于 lambda 的建议
if True:  # 改为 False 可跳过此示例
    print("\n=== PEP 8 建议 ===")
    
    print("""
    PEP 8 关于 lambda 的建议:
    
    1. 不要将 lambda 表达式赋值给变量
       不推荐: square = lambda x: x ** 2
       推荐:   def square(x): return x ** 2
    
    2. lambda 适合作为参数传递给高阶函数
       推荐: sorted(items, key=lambda x: x.name)
    
    3. 如果 lambda 太复杂，使用普通函数
       复杂的 lambda 会降低代码可读性
    
    4. lambda 的优势是简洁，不是功能
       如果需要文档、类型注解、多行逻辑，用 def
    """)
# endregion
