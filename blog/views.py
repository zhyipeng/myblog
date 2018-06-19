# coding:utf-8
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Post, Category, Tag
import markdown
from comments.forms import CommentForm
from django.views.generic import ListView, DetailView
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
from django.db.models import Q
'''
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
'''

# 首页
class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # is_paginated 是一个布尔变量，用于指示是否已分页
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        # 调用 pagination_data 方法返回显示分页所需的数据(dict)
        pagination_data = self.pagination_data(paginator, page, is_paginated)

        # 将分页导航条的模板变量更新到 context 中，注意 pagination_data 方法返回的也是一个字典。
        context.update(pagination_data)

        other = {'title': '张一碰的主页',
                 'welcome': '张一碰的主页',}
        context.update(other)

        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            return {}

        # 当前页左右两边的连续页码
        left = []
        right = []

        # 是否需要显示省略号
        left_has_more = False
        right_has_more = False

        # 是否需要显示第一页和最后一页
        first = False
        last = False

        # 当前请求页码
        page_number = page.number

        # 分页后总页数
        total_pages = paginator.num_pages

        # 分页页码列表
        page_range = paginator.page_range

        if page_number==1:
            right = page_range[page_number:page_number+2]

            if right[-1]<total_pages-1:
                right_has_more = True

            if right[-1]<total_pages:
                last = True

        elif page_number == total_pages:
            left = page_range[(page_number-3) if (page_number-3)>0 else 0:page_number-1]

            if left[0] > 2:
                left_has_more = True

            if left[0] > 1:
                first = True

        else:
            left = page_range[(page_number-3) if (page_number-3)>0 else 0:page_number-1]
            right = page_range[page_number:page_number+2]

            if right[-1]<total_pages-1:
                right_has_more = True
            if right[-1]<total_pages:
                last = True
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
        data = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }

        return data


'''
# 详情页
def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    post.increase_views()

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
               'comment_list': comment_list,
               'title': post.title,
               'welcome': post.title
               }

    return render(request, 'blog/detail.html', context=context)
'''

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        # 覆写 get 方法的目的是因为每当文章被访问一次，就得将文章阅读量 +1
        # get 方法返回的是一个 HttpResponse 实例
        # 之所以需要先调用父类的 get 方法，是因为只有当 get 方法被调用后，
        # 才有 self.object 属性，其值为 Post 模型实例，即被访问的文章 post
        response = super(PostDetailView, self).get(request, *args, **kwargs)

        # self.object 即为被访问的Post
        self.object.increase_views()

        return response

    def get_object(self, queryset=None):
        # 覆写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
        post = super(PostDetailView, self).get_object(queryset=None)
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            TocExtension(configs=[('slugify', slugify)]),
        ])
        post.body = md.convert(post.body)
        post.toc = md.toc
        return post

    def get_context_data(self, **kwargs):
        # 覆写 get_context_data 的目的是因为除了将 post 传递给模板外（DetailView 已经帮我们完成），
        # 还要把评论表单、post 下的评论列表传递给模板。
        context = super(PostDetailView, self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'form': form,
            'comment_list': comment_list
        })
        return context

'''
# 归档
def archives(request, year, month):
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month).order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list,
                                                       'title': year+'年'+month+'月的文章',
                                                       'welcome': year+'年'+month+'月的文章'})
'''

class ArchivesView(IndexView):
    def get_queryset(self):
        return super(ArchivesView, self).get_queryset().filter(created_time__year=self.kwargs.get('year'),
                                                               created_time__month=self.kwargs.get('month'))
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')
        pagination_data = self.pagination_data(paginator, page, is_paginated)

        context.update(pagination_data)
        year = self.object_list[0].created_time.year
        month = self.object_list[0].created_time.month
        title = str(year) + ' 年 ' + str(month) + ' 月 '
        other = {'title': title,
                 'welcome': title, }
        context.update(other)

        return context


'''
# 分类
def category(request, pk):
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate).order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list,
                                                       'title': cate.name,
                                                       'welcome': cate.name})
'''

class CategoryView(IndexView):
    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')
        pagination_data = self.pagination_data(paginator, page, is_paginated)

        context.update(pagination_data)
        title = self.object_list[0].category
        other = {'title': title,
                 'welcome': title, }
        context.update(other)

        return context

class TagView(IndexView):
    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tag=tag)
    '''
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')
        pagination_data = self.pagination_data(paginator, page, is_paginated)

        context.update(pagination_data)
        title = self.object_list[0].tag
        other = {'title': title,
                 'welcome': title, }
        context.update(other)

        return context
    '''

def search(request):
    q = request.GET.get('q')
    error_msg = ''

    if not q:
        error_msg = '请输入关键字'
        return render(request, 'blog/index.html', {'error_msg': error_msg})

    post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
    return render(request, 'blog/index.html', {'error_msg': error_msg,
                                               'post_list': post_list})