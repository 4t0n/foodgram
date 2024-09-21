from django.contrib import admin
from django.contrib.auth.models import Group

from .models import CustomUser, Follow


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    search_fields = ['email', 'username']
    filter_horizontal = ('favorite', 'shopping_cart')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['author', 'user']
    search_fields = ['author', 'user']


admin.site.unregister(Group)
