from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(UserAdmin):
    """Административный класс для управления пользователями."""

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('email', 'username')
    search_fields = ('username', 'email', 'first_name', 'last_name',)
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Административный класс для управления подписками."""

    list_display = ('user', 'following',)
    list_filter = ('user', 'following',)
    search_fields = ('user__username', 'following__username',)
    empty_value_display = '-пусто-'
