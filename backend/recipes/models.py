from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from shortuuid.django_fields import ShortUUIDField

from foodgram_backend.constants import (
    LENGTH_RECIPE_NAME,
    LENGTH_TAG_NAME,
    LENGTH_SLUG,
    MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
    LENGTH_INGREDIENT_NAME,
    LENGTH_MEASUREMENT_UNIT,
)

from .querysets import RecipeQuerySet

User = get_user_model()


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        verbose_name='Название', max_length=LENGTH_TAG_NAME
    )
    slug = models.SlugField(
        verbose_name='Slug', max_length=LENGTH_SLUG, unique=True
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ('name', 'slug')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        verbose_name='Название',
        max_length=LENGTH_INGREDIENT_NAME,
        unique=True,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=LENGTH_MEASUREMENT_UNIT,
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='user_recipes',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=LENGTH_RECIPE_NAME,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/images/',
        blank=False,
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_COOKING_TIME)],
        verbose_name='Время приготовления (мин)',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    short_link = ShortUUIDField(length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = RecipeQuerySet.as_manager()

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at', 'name')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/recipes/{self.pk}/'


class RecipeIngredient(models.Model):
    """Промежуточная модель для связи рецепта и ингредиента."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_to_ingredient',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_to_recipe',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_INGREDIENT_AMOUNT)],
        verbose_name='Количество',
    )

    class Meta:
        verbose_name_plural = 'Ингредиенты для рецептов'
        ordering = ('recipe', 'ingredient')
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
            )
        ]

    def __str__(self):
        return f'{self.ingredient} для {self.recipe}'
