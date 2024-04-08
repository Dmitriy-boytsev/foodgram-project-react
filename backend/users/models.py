from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import UsersConstants


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
        max_length=UsersConstants.EMAIL_LENGTH_MAX,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        unique=True,
        max_length=UsersConstants.NAME_LENGTH_MAX,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=UsersConstants.NAME_LENGTH_MAX,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=UsersConstants.NAME_LENGTH_MAX,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Подписчик',
                             related_name='follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE,
                                  verbose_name='Подписка',
                                  related_name='following')

    class Meta:
        constraints = (
            models.UniqueConstraint(
                name='unique_subscription',
                fields=('user', 'following')
            ),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'подписки'

    def __str__(self):
        return (
            f'Пользователь {self.user.username} '
            f'подписан на {self.author.username}'
        )
