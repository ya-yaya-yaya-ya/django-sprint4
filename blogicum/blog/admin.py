from django.contrib import admin

from blog.models import Category, Comment, Location, Post
from constants import EMPTY_VALUE_DISPLAY


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'location',
        'is_published',
        'pub_date',
        'category',
        'author'
    )
    list_editable = (
        'is_published',
        'category'
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)
    empty_value_display = EMPTY_VALUE_DISPLAY


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'is_published',
        'created_at',
        'slug',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('title',)
    list_filter = ('slug',)
    list_display_links = ('title',)
    empty_value_display = EMPTY_VALUE_DISPLAY


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('name',)
    list_display_links = ('name',)
    empty_value_display = EMPTY_VALUE_DISPLAY


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'post',
        'created_at',
    )
    search_fields = ('text',)
    list_display_links = ('text',)
    empty_value_display = EMPTY_VALUE_DISPLAY


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Comment, CommentAdmin)
