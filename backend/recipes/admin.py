from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, Tag


@admin.register(Ingredient, Recipe, RecipeIngredient, Tag)
class UserAdmin(admin.ModelAdmin):
    pass
