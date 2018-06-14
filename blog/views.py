# coding:utf-8
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Post, Category
import markdown
from comments.forms import CommentForm

# 首页
def index(request):
    # return HttpResponse(u"欢迎光临我的博客!")
    # 按创建时间倒序排序的post_list传入index
    post_list = Post.objects.all().order_by('-created_time')
    return render(request, 'blog/index.html', context={
        'title': '张一碰的首页',
        'welcome': '欢迎访问我的博客',
        'post_list': post_list
    })

# 详情页
def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # 渲染markdown
    # 使用了三个拓展，分别是 extra、codehilite、toc
    # extra 本身包含很多拓展
    # codehilite 是语法高亮拓展，为后面的实现代码高亮功能提供基础
    # toc 则允许我们自动生成目录
    post.body = markdown.markdown(post.body, extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
    ])

    form = CommentForm()
    comment_list = post.comment_set.all()
    context = {'post': post,
               'from': form,
               'comment_list': comment_list
               }

    return render(request, 'blog/detail.html', context=context)

# 归档
def archives(request, year, month):
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month).order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})

# 分类
def category(request, pk):
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate).order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})


