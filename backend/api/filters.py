from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class IngredientSearchFilter(SearchFilter):
    """Фильтр поиска для ингредиентов по названию."""

    search_param = 'name'


class RecipeFilter(FilterSet):
    """
    Фильтр поиска для рецептов.

    Ключевые параметры:
    tags - позволяет фильтровать рецепты по слагам тегов
    is_favorited - нахождение рецепта в избранном
    is_in_shopping_cart - в корзине покупок.
    """

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, is_favorited_value):
        if is_favorited_value:
            return queryset.filter(favorites__user=self.request.user.id)
        return queryset

    def filter_is_in_shopping_cart(self,
                                   queryset,
                                   name,
                                   is_in_shopping_cart_value):
        if is_in_shopping_cart_value:
            return queryset.filter(shopping_cart__user=self.request.user.id)
        return queryset
