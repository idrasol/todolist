from django.contrib import admin
from .models import Board, Post


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'creator__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('board', 'user', 'content', 'position_x', 'position_y', 'created_at')
    list_filter = ('created_at', 'board')
    search_fields = ('content', 'user__username', 'board__title')
    readonly_fields = ('created_at', 'updated_at')

