import base64
import random
import string

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.forms import ModelForm
from django.http import HttpRequest

from foodgram_backend.constants import SHORT_LINK_LENGTH
from .models import Ingredient, Recipe, RecipeIngredient, Tag


User = get_user_model()


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    fields = ['name', 'image', 'text', 'cooking_time', 'tags', 'short_link']
    readonly_fields = ['short_link',]
    filter_horizontal = ('tags',)
    inlines = [RecipeIngredientInline]
    list_display = ['name', 'author']
    search_fields = ['author', 'name']
    list_filter = ['tags']

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        short_link = ''.join(
            random.choices(
                string.ascii_letters + string.digits,
                k=SHORT_LINK_LENGTH
            )
        )
        while True:
            try:
                obj.short_link = short_link
                obj.save
                break
            except IntegrityError:
                pass
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
    pass
