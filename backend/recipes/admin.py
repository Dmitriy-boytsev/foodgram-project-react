from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class IngredientInline(admin.TabularInline):
    """Inline-модель ингредиентов."""

    model = RecipeIngredient
    extra = 3
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Административный класс для управления рецептами."""

    list_display = (
        'name',
        'author',
        'get_favorites',
        'get_ingredients',
    )
    list_filter = ('author', 'name', 'tags',)
    search_fields = ('name', 'author__username', 'tags')
    inlines = (IngredientInline,)
    empty_value_display = '-пусто-'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('author').prefetch_related('tags')

    def get_ingredients(self, obj):
        return ', '.join([
            ingredients.name for ingredients
            in obj.ingredients.all()])

    get_ingredients.short_description = 'Ингредиенты'

    def get_favorites(self, obj):
        return obj.favorites.count()

    get_favorites.short_description = 'Избранное'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Административный класс для управления ингредиентами."""

    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Административный класс для управления тегами."""

    list_display = (
        'name',
        'color',
        'slug',
    )
    search_fields = ('name', 'slug')
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Административный класс для управления списка избранных рецептов."""

    list_display = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__title',)
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Административный класс для управления корзиной покупок."""

    list_display = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)
    empty_value_display = '-пусто-'
