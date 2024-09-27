from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from foodgram_backend.constants import (
    LENGTH_EMAIL,
    LENGTH_USERNAME,
    LENGTH_FIRST_NAME,
    LENGTH_LAST_NAME,
)


class User(AbstractUser):
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
    favorite = models.ManyToManyField(
        verbose_name='Избранное',
        to='recipes.Recipe',
        related_name='favorites',
        symmetrical=False,
        blank=True,
    )
    shopping_cart = models.ManyToManyField(
        verbose_name='Список покупок',
        to='recipes.Recipe',
        related_name='shopping',
        symmetrical=False,
        blank=True,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-date_joined', 'username')

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        verbose_name='подписчик',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        verbose_name='автор',
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_user_following'
            )
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('author', 'user')

    def __str__(self):
        return f'Подписка {self.user} на {self.author}'
