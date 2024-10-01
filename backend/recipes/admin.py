# для входа в админку: shvab-vladimir@yandex.ru pythonpracticum
from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    fields = [
        'name',
        'image',
        'text',
        'cooking_time',
        'tags',
        'short_link',
        'favorite_count',
    ]
    readonly_fields = ['short_link', 'favorite_count']
    filter_horizontal = ('tags',)
    inlines = [RecipeIngredientInline]
    list_display = ['name', 'author']
    search_fields = ['author__username', 'name']
    list_filter = ['tags']

    @admin.display(description="Количество добавлений в избранное")
    def favorite_count(self, obj):
        return obj.favorites.count()

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'ingredient']
    search_fields = ['recipe']
