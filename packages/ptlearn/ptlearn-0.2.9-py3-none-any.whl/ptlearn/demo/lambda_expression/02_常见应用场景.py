"""
Lambda 表达式常见应用场景
========================
Lambda 最常与内置函数 sorted(), map(), filter(), reduce() 配合使用。
"""

# region 示例1: 与 sorted() 配合 - 自定义排序
if True:  # 改为 False 可跳过此示例
    print("=== sorted() 自定义排序 ===")
    
    # 按字符串长度排序
    words = ["apple", "pie", "banana", "cat"]
    sorted_by_len = sorted(words, key=lambda x: len(x))
    print(f"按长度排序: {sorted_by_len}")
    
    # 按绝对值排序
    numbers = [-5, 2, -1, 8, -3]
    sorted_by_abs = sorted(numbers, key=lambda x: abs(x))
    print(f"按绝对值排序: {sorted_by_abs}")
    
    # 字典列表按指定字段排序
    students = [
        {"name": "小明", "score": 85},
        {"name": "小红", "score": 92},
        {"name": "小刚", "score": 78},
    ]
    sorted_by_score = sorted(students, key=lambda s: s["score"], reverse=True)
    print(f"按成绩降序: {[s['name'] + ':' + str(s['score']) for s in sorted_by_score]}")
# endregion

# region 示例2: 与 map() 配合 - 批量转换
if True:  # 改为 False 可跳过此示例
    print("\n=== map() 批量转换 ===")
    
    # 数字平方
    numbers = [1, 2, 3, 4, 5]
    squares = list(map(lambda x: x ** 2, numbers))
    print(f"平方: {numbers} -> {squares}")
    
    # 字符串处理
    names = ["alice", "bob", "charlie"]
    capitalized = list(map(lambda s: s.capitalize(), names))
    print(f"首字母大写: {names} -> {capitalized}")
    
    # 多序列并行处理
    a = [1, 2, 3]
    b = [10, 20, 30]
    sums = list(map(lambda x, y: x + y, a, b))
    print(f"对应元素相加: {a} + {b} = {sums}")
# endregion

# region 示例3: 与 filter() 配合 - 条件筛选
if True:  # 改为 False 可跳过此示例
    print("\n=== filter() 条件筛选 ===")
    
    # 筛选偶数
    numbers = range(1, 11)
    evens = list(filter(lambda x: x % 2 == 0, numbers))
    print(f"1-10中的偶数: {evens}")
    
    # 筛选非空字符串
    items = ["hello", "", "world", None, "python", ""]
    non_empty = list(filter(lambda x: x, items))  # 利用真值判断
    print(f"非空元素: {non_empty}")
    
    # 筛选及格的学生
    scores = {"小明": 85, "小红": 58, "小刚": 92, "小李": 45}
    passed = dict(filter(lambda item: item[1] >= 60, scores.items()))
    print(f"及格学生: {passed}")
# endregion

# region 示例4: 与 reduce() 配合 - 累积计算
if True:  # 改为 False 可跳过此示例
    from functools import reduce
    
    print("\n=== reduce() 累积计算 ===")
    
    # 累加
    numbers = [1, 2, 3, 4, 5]
    total = reduce(lambda acc, x: acc + x, numbers)
    print(f"累加 {numbers} = {total}")
    
    # 累乘（阶乘）
    factorial_5 = reduce(lambda acc, x: acc * x, range(1, 6))
    print(f"5! = {factorial_5}")
    
    # 找最大值
    values = [3, 1, 4, 1, 5, 9, 2, 6]
    max_val = reduce(lambda a, b: a if a > b else b, values)
    print(f"{values} 中的最大值: {max_val}")
# endregion

# region 示例5: 与 max()/min() 配合
if True:  # 改为 False 可跳过此示例
    print("\n=== max()/min() 自定义比较 ===")
    
    # 找最长的单词
    words = ["python", "java", "go", "javascript"]
    longest = max(words, key=lambda w: len(w))
    shortest = min(words, key=lambda w: len(w))
    print(f"最长单词: {longest}, 最短单词: {shortest}")
    
    # 找成绩最高的学生
    students = [("小明", 85), ("小红", 92), ("小刚", 78)]
    top_student = max(students, key=lambda s: s[1])
    print(f"成绩最高: {top_student[0]} ({top_student[1]}分)")
# endregion
