from ..models import Post, Category
from django import template

register = template.Library()

# 获得最近5个Post
# 注册为模板标签，可以在django模板中使用
@register.simple_tag()
def get_recent_posts(num=5):
    return Post.objects.all().order_by('-created_time')[:num]

# 归档
# 返回一个list
# created_time: Post的创建时间
# month: 精度
# order='DESC': 表明降序排列
@register.simple_tag()
def archives():
    return Post.objects.dates('created_time', 'month', order='DESC')

# 分类
@register.simple_tag()
def get_categories():
    return Category.objects.all()