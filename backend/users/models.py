from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models

from foodgram_backend.constants import (
    LENGTH_EMAIL,
    LENGTH_USERNAME,
    LENGTH_FIRST_NAME,
    LENGTH_LAST_NAME,
)


class FoodgramUser(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        unique=True,
        max_length=LENGTH_USERNAME,
        validators=(UnicodeUsernameValidator(),),
    )
    email = models.EmailField(
        unique=True,
        max_length=LENGTH_EMAIL,
    )
    first_name = models.CharField(max_length=LENGTH_FIRST_NAME)
    last_name = models.CharField(max_length=LENGTH_LAST_NAME)
    avatar = models.ImageField(
        upload_to='users/', null=True, blank=True, default=None
    )
    subscriptions = models.ManyToManyField(
        'self',
        verbose_name='Подписки',
        through='Follow',
        related_name='followers',
        symmetrical=False,
        blank=True,
    )
    favorites = models.ManyToManyField(
        to='recipes.Recipe',
        verbose_name='Избранное',
        through='Favorite',
        related_name='favorite',
        symmetrical=False,
        blank=True,
    )
    shopping_cart = models.ManyToManyField(
        to='recipes.Recipe',
        verbose_name='Список покупок',
        through='ShoppingCart',
        related_name='shopping',
        symmetrical=False,
        blank=True,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-date_joined', 'username')

    def __str__(self):
        return self.username


class Favorite(models.Model):
    """Промежуточная модель для избранного."""

    user = models.ForeignKey(
        FoodgramUser,
        verbose_name='пользователь',
        on_delete=models.CASCADE,
        related_name='favorite_to_user',
    )
    recipe = models.ForeignKey(
        to='recipes.Recipe',
        verbose_name='рецепт',
        on_delete=models.CASCADE,
        related_name='user_to_favorite',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]
        verbose_name = 'рецепт в избранном'
        verbose_name_plural = 'Избранное'
        ordering = ('user', 'recipe')


class ShoppingCart(models.Model):
    """Промежуточная модель для корзины."""

    user = models.ForeignKey(
        FoodgramUser,
        verbose_name='пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_to_user',
    )
    recipe = models.ForeignKey(
        to='recipes.Recipe',
        verbose_name='рецепт',
        on_delete=models.CASCADE,
        related_name='user_to_shopping',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping'
            )
        ]
        verbose_name = 'рецепт в корзине'
        verbose_name_plural = 'Корзина'
        ordering = ('user', 'recipe')


class Follow(models.Model):
    """Промежуточная модель для подписок."""

    user = models.ForeignKey(
        FoodgramUser,
        verbose_name='подписчик',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        FoodgramUser,
        verbose_name='автор',
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_following',
            )
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('author', 'user')

    def __str__(self):
        return f'Подписка {self.user} на {self.author}'

    def clean(self):
        if self.user == self.author:
            raise ValidationError("Вы не можете подписаться на самого себя!")
        return super().clean()
