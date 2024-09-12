from django.contrib import admin

from .models import Ingredient, Recipe, Tag


@admin.register(Ingredient, Recipe, Tag)
class UserAdmin(admin.ModelAdmin):
    pass
