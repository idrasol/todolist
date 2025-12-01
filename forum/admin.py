from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_notice', 'views', 'created_at']
    list_filter = ['is_notice', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['views', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
