from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .validators import name_validator
from foodgram_backend.constants import LENGTH_EMAIL, LENGTH_USERNAME


class CustomUser(AbstractUser):

    username = models.CharField(
        'Никнейм',
        unique=True,
        max_length=LENGTH_USERNAME,
        validators=(UnicodeUsernameValidator(), name_validator),
    )

    email = models.EmailField(
        'Адрес эл.почты',
        unique=True,
        max_length=LENGTH_EMAIL,
    )
    password = models.CharField('Пароль', max_length=128)
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='users/',
        null=True,
        blank=True,
        default=None
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

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('date_joined',)


class Follow(models.Model):

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_following'
            )
        ]
