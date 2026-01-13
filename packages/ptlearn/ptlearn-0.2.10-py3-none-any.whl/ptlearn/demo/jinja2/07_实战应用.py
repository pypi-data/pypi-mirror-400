"""
Jinja2 实战应用
===============
本文件展示 Jinja2 在实际项目中的常见应用场景：
- 生成配置文件
- 生成代码
- 邮件模板
- 报告生成
"""

from jinja2 import Environment, Template
from pathlib import Path
import json

# region 示例1: 生成配置文件
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例1: 生成配置文件")
    print("=" * 50)
    
    # Nginx 配置模板
    nginx_template = Template("""
server {
    listen {{ port }};
    server_name {{ domain }};
    
    {% for location in locations %}
    location {{ location.path }} {
        proxy_pass {{ location.upstream }};
        {% if location.cache %}
        proxy_cache_valid 200 {{ location.cache_time }};
        {% endif %}
    }
    {% endfor %}
}
""")
    
    config = {
        "port": 80,
        "domain": "example.com",
        "locations": [
            {"path": "/", "upstream": "http://localhost:8000", "cache": False},
            {"path": "/api", "upstream": "http://localhost:3000", "cache": True, "cache_time": "10m"},
            {"path": "/static", "upstream": "http://localhost:9000", "cache": True, "cache_time": "1d"},
        ]
    }
    
    print(nginx_template.render(**config).strip())
    print()
# endregion

# region 示例2: 生成代码
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例2: 生成代码")
    print("=" * 50)
    
    # Python 类生成模板
    class_template = Template("""
class {{ class_name }}:
    \"\"\"{{ description }}\"\"\"
    
    def __init__(self{% for attr in attributes %}, {{ attr.name }}: {{ attr.type }}{% if attr.default is defined %} = {{ attr.default }}{% endif %}{% endfor %}):
        {% for attr in attributes %}
        self.{{ attr.name }} = {{ attr.name }}
        {% endfor %}
    
    def __repr__(self):
        return f"{{ class_name }}({% for attr in attributes %}{{ attr.name }}={self.{{ attr.name }}!r}{% if not loop.last %}, {% endif %}{% endfor %})"
""")
    
    model = {
        "class_name": "User",
        "description": "用户模型类",
        "attributes": [
            {"name": "name", "type": "str"},
            {"name": "age", "type": "int"},
            {"name": "email", "type": "str", "default": "''"},
        ]
    }
    
    print(class_template.render(**model).strip())
    print()
# endregion

# region 示例3: 邮件模板
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例3: 邮件模板")
    print("=" * 50)
    
    email_template = Template("""
尊敬的 {{ user.name }}：

感谢您在 {{ site_name }} 的订单！

订单详情：
订单号：{{ order.id }}
下单时间：{{ order.date }}

商品列表：
{% for item in order.items %}
  - {{ item.name }} x {{ item.quantity }}  ¥{{ "%.2f" | format(item.price * item.quantity) }}
{% endfor %}

商品总计：¥{{ "%.2f" | format(order.items | sum(attribute='price') * order.items | sum(attribute='quantity')) }}
运费：¥{{ "%.2f" | format(order.shipping) }}
{% if order.discount > 0 %}
优惠：-¥{{ "%.2f" | format(order.discount) }}
{% endif %}
实付金额：¥{{ "%.2f" | format(order.total) }}

如有问题，请联系客服。

{{ site_name }} 团队
""")
    
    data = {
        "site_name": "购物网",
        "user": {"name": "张三"},
        "order": {
            "id": "ORD20240101001",
            "date": "2024-01-01 10:30:00",
            "items": [
                {"name": "Python编程指南", "quantity": 1, "price": 89.00},
                {"name": "机械键盘", "quantity": 1, "price": 299.00},
            ],
            "shipping": 10.00,
            "discount": 20.00,
            "total": 378.00
        }
    }
    
    print(email_template.render(**data).strip())
    print()
# endregion

# region 示例4: 生成 SQL 语句
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例4: 生成 SQL 语句")
    print("=" * 50)
    
    # 注意：实际项目中应使用参数化查询防止 SQL 注入
    # 这里仅作为模板生成示例
    
    sql_template = Template("""
CREATE TABLE {{ table_name }} (
    {% for col in columns %}
    {{ col.name }} {{ col.type }}{% if col.primary %} PRIMARY KEY{% endif %}{% if col.not_null %} NOT NULL{% endif %}{% if col.default is defined %} DEFAULT {{ col.default }}{% endif %}{% if not loop.last %},{% endif %}
    {% endfor %}
);

{% if indexes %}
{% for idx in indexes %}
CREATE INDEX idx_{{ table_name }}_{{ idx.name }} ON {{ table_name }} ({{ idx.columns | join(', ') }});
{% endfor %}
{% endif %}
""")
    
    schema = {
        "table_name": "users",
        "columns": [
            {"name": "id", "type": "INTEGER", "primary": True},
            {"name": "username", "type": "VARCHAR(50)", "not_null": True},
            {"name": "email", "type": "VARCHAR(100)", "not_null": True},
            {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"},
        ],
        "indexes": [
            {"name": "username", "columns": ["username"]},
            {"name": "email", "columns": ["email"]},
        ]
    }
    
    print(sql_template.render(**schema).strip())
    print()
# endregion

# region 示例5: 生成 Markdown 报告
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("示例5: 生成 Markdown 报告")
    print("=" * 50)
    
    report_template = Template("""
# {{ title }}

生成时间：{{ generated_at }}

## 概述

{{ summary }}

## 数据统计

| 指标 | 数值 |
|------|------|
{% for stat in statistics %}
| {{ stat.name }} | {{ stat.value }} |
{% endfor %}

## 详细数据

{% for section in sections %}
### {{ section.title }}

{{ section.content }}

{% endfor %}
""")
    
    report_data = {
        "title": "月度销售报告",
        "generated_at": "2024-01-15",
        "summary": "本月销售表现良好，同比增长15%。",
        "statistics": [
            {"name": "总销售额", "value": "¥1,234,567"},
            {"name": "订单数", "value": "5,678"},
            {"name": "客单价", "value": "¥217.5"},
        ],
        "sections": [
            {"title": "热销商品", "content": "手机、电脑、耳机位列前三。"},
            {"title": "区域分布", "content": "华东地区贡献了40%的销售额。"},
        ]
    }
    
    print(report_template.render(**report_data).strip())
    print()
# endregion
