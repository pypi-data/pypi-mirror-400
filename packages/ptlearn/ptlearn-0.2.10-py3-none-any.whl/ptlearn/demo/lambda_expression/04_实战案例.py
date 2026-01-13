"""
Lambda 表达式实战案例
====================
通过实际场景展示 lambda 的应用价值。
"""

# region 示例1: 数据处理管道
if True:  # 改为 False 可跳过此示例
    print("=== 数据处理管道 ===")
    
    # 模拟数据清洗流程
    raw_data = ["  Alice  ", "BOB", "  charlie ", "", "  DAVID"]
    
    # 定义处理步骤
    strip_space = lambda s: s.strip()
    to_title = lambda s: s.title()
    is_not_empty = lambda s: len(s) > 0
    
    # 组合处理
    cleaned = list(filter(is_not_empty, map(to_title, map(strip_space, raw_data))))
    print(f"原始数据: {raw_data}")
    print(f"清洗后: {cleaned}")
# endregion

# region 示例2: 多级排序
if True:  # 改为 False 可跳过此示例
    print("\n=== 多级排序 ===")
    
    employees = [
        {"name": "张三", "dept": "技术部", "salary": 15000},
        {"name": "李四", "dept": "市场部", "salary": 12000},
        {"name": "王五", "dept": "技术部", "salary": 18000},
        {"name": "赵六", "dept": "市场部", "salary": 12000},
        {"name": "钱七", "dept": "技术部", "salary": 15000},
    ]
    
    # 先按部门排序，同部门按薪资降序，同薪资按姓名排序
    sorted_emp = sorted(employees, key=lambda e: (e["dept"], -e["salary"], e["name"]))
    
    print("按部门、薪资(降序)、姓名排序:")
    for emp in sorted_emp:
        print(f"  {emp['dept']} - {emp['name']}: {emp['salary']}")
# endregion

# region 示例3: 事件回调简化
if True:  # 改为 False 可跳过此示例
    print("\n=== 事件回调简化 ===")
    
    class Button:
        def __init__(self, label):
            self.label = label
            self._on_click = None
        
        def set_click_handler(self, handler):
            self._on_click = handler
        
        def click(self):
            if self._on_click:
                self._on_click()
    
    # 使用 lambda 快速定义回调
    btn1 = Button("提交")
    btn1.set_click_handler(lambda: print("表单已提交!"))
    
    btn2 = Button("取消")
    btn2.set_click_handler(lambda: print("操作已取消!"))
    
    btn1.click()
    btn2.click()
# endregion

# region 示例4: 延迟求值与惰性计算
if True:  # 改为 False 可跳过此示例
    print("\n=== 延迟求值 ===")
    
    # 使用 lambda 延迟计算
    def expensive_computation():
        print("  (执行耗时计算...)")
        return sum(range(1000000))
    
    # 不使用 lambda：立即计算
    # result = expensive_computation()  # 立即执行
    
    # 使用 lambda：延迟到需要时才计算
    lazy_result = lambda: expensive_computation()
    
    print("定义了延迟计算，但还未执行")
    print("现在需要结果了:")
    print(f"结果 = {lazy_result()}")
# endregion

# region 示例5: 函数组合
if True:  # 改为 False 可跳过此示例
    from functools import reduce
    
    print("\n=== 函数组合 ===")
    
    # 定义组合函数
    def compose(*funcs):
        """从右到左组合多个函数"""
        return reduce(lambda f, g: lambda x: f(g(x)), funcs)
    
    # 定义基础函数
    add_10 = lambda x: x + 10
    multiply_2 = lambda x: x * 2
    square = lambda x: x ** 2
    
    # 组合: square(multiply_2(add_10(x)))
    combined = compose(square, multiply_2, add_10)
    
    x = 5
    # 计算过程: 5 -> 15 -> 30 -> 900
    print(f"compose(square, multiply_2, add_10)({x}) = {combined(x)}")
    print(f"验证: (({x} + 10) * 2)² = {((x + 10) * 2) ** 2}")
# endregion

# region 示例6: 缓存装饰器中的应用
if True:  # 改为 False 可跳过此示例
    print("\n=== 缓存装饰器 ===")
    
    def memoize(func):
        cache = {}
        return lambda *args: cache.setdefault(args, func(*args))
    
    # 斐波那契数列（带缓存）
    @memoize
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)
    
    print(f"fib(10) = {fib(10)}")
    print(f"fib(20) = {fib(20)}")
    print(f"fib(30) = {fib(30)}")
# endregion
