from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.six import python_2_unicode_compatible
import markdown
from django.utils.html import strip_tags
# Create your models here.

# 分类数据库
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# 标签数据库
class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# 文章数据库
# python_2_unicode_compatible 装饰器用于兼容 Python2
@python_2_unicode_compatible
class Post(models.Model):
    '''
    文章数据库包含字段：标题title 正文body  创建时间created_time
    修改时间modified_time 摘要excerpt  分类category 标签tag 作者author
    '''
    title = models.CharField(max_length=100)
    body = models.TextField()
    created_time = models.DateField()
    modified_time = models.DateField()

    # blank 为true表示参数可以为空值
    excerpt = models.CharField(max_length=200, blank=True)

    # ForeignKey，即一对多的关联关系(一个分类下可以有多篇文章)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    # 而对于标签来说，一篇文章可以有多个标签，同一个标签下也可能有多篇文章，
    # 所以我们使用 ManyToManyField，表明这是多对多的关联关系。文章可以没有标签，所以blank可以为true
    tag = models.ManyToManyField(Tag, blank=True)

    # 文章作者，这里 User 是从 django.contrib.auth.models 导入的。
    # django.contrib.auth 是 Django 内置的应用，专门用于处理网站用户的注册、登录等流程，
    # User 是 Django 为我们已经写好的用户模型。
    # 这里我们通过 ForeignKey 把文章和 User 关联了起来。
    # 因为我们规定一篇文章只能有一个作者，而一个作者可能会写多篇文章，因此这是一对多的关联关系，和 Category 类似
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # 记录文章访问次数
    # PositiveIntegerField类型的值只允许为正整数或0
    views = models.PositiveIntegerField(default=0)

    # 当文章被访问时，views += 1
    def increase_views(self):
        self.views += 1
        # update_fields 参数告诉 Django 只更新数据库中 views 字段的值
        self.save(update_fields=['views'])

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    # 自动生成摘要
    def save(self, *args, **kwargs):
        if not self.excerpt:
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
            # 先将 Markdown 文本渲染成 HTML 文本
            # strip_tags 去掉 HTML 文本的全部 HTML 标签
            # 从文本摘取前 54 个字符赋给 excerpt
            self.excerpt = strip_tags(md.convert(self.body))[:54]

        # 调用父类的 save 方法将数据保存到数据库中
        super(Post, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_time']
