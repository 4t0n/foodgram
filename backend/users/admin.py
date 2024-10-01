from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .models import Favorite, Follow, ShoppingCart

User = get_user_model()


class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 0


class FollowInline(admin.TabularInline):
    model = Follow
    extra = 0


class ShoppingCartInline(admin.TabularInline):
    model = ShoppingCart
    extra = 0


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ['email', 'username']
    inlines = [FavoriteInline, FollowInline, ShoppingCartInline]


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['author', 'user']
    search_fields = ['author', 'user']
    list_filter = ['user']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']
    search_fields = ['user', 'recipe']
    list_filter = ['user']


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']
    search_fields = ['user', 'recipe']
    list_filter = ['user']


admin.site.unregister(Group)
