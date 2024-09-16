from django.contrib import admin

from .models import CustomUser, Follow


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    search_fields = ['email', 'username']


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    pass
