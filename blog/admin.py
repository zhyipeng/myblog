from django.contrib import admin
from .models import Post, Category, Tag

# Register your models here.

# 希望能看到文章的更多信息，而不仅仅是文章
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_time', 'modified_time', 'author']

# 把新注册的PostAdmin也注册进来
admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)