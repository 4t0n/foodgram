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
        upload_to='users/',
        null=True,
        blank=True,
        default=None
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('date_joined',)


class Follow(models.Model):

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following'
    )
    following = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='followers'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]
