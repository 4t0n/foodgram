from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

from foodgram_backend.constants import (LENGTH_RECIPE_NAME, LENGTH_TAG_NAME,
                                        LENGTH_SLUG, MIN_COOKING_TIME,
                                        MIN_INGREDIENT_AMOUNT,
                                        LENGTH_INGREDIENT_NAME,
                                        LENGTH_MEASUREMENT_UNIT)


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название', max_length=LENGTH_TAG_NAME
    )
    slug = models.SlugField(
        verbose_name='Slug', max_length=LENGTH_SLUG, unique=True
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=LENGTH_INGREDIENT_NAME,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=LENGTH_MEASUREMENT_UNIT,
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=LENGTH_RECIPE_NAME,
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=False,
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_COOKING_TIME),],
        verbose_name='Время приготовления (мин)',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='RecipeIngredient',
    )

    short_link = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_to_ingredient',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_to_recipe',
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_INGREDIENT_AMOUNT),],
    )
