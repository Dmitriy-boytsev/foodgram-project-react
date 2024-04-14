from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeGetSerializer, RecipeSerializer,
                             ShoppingCartSerializer,
                             SubscriptionCreateSerializer,
                             SubscriptionSerializer, TagSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeGetSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeSerializer

    def perform_action(self, serializer_class, user, pk):
        serializer = serializer_class(
            data={'user': user.id, 'recipe': pk},
            context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=('POST',), detail=True)
    def favorite(self, request, pk):
        return self.perform_action(FavoriteSerializer, request.user, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self.delete_recipe(Favorite, request.user, pk)

    @action(methods=('POST',), detail=True)
    def shopping_cart(self, request, pk):
        return self.perform_action(ShoppingCartSerializer, request.user, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self.delete_recipe(ShoppingCart, request.user, pk)

    @action(detail=False, methods=('get',),
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = self.get_shopping_cart_items(request.user)
        shopping_list_text = self.prepare_shopping_list_text(
            ingredients, request.user
        )
        return self.download_shopping_list(shopping_list_text, request.user)

    def get_shopping_cart_items(self, user):
        return RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(amount=Sum('amount'))

    def prepare_shopping_list_text(self, ingredients, user):
        today = datetime.today()
        user_full_name = user.get_full_name()
        shopping_list = f'Список покупок для {user_full_name}\n\n'
        shopping_list += f'Дата: {today:%Y-%m-%d}\n\n'
        shopping_list += '\n'.join((
            f'- {ingredient["ingredients__name"]} '
            f'({ingredient["ingredients__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ))
        shopping_list += f'\n\nFoodgram ({today:%Y})'
        return shopping_list

    def download_shopping_list(self, shopping_list_text, user):
        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list_text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    def delete_recipe(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({
            'errors': 'Рецепт уже удален'
        }, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class UserViewSet(UserViewSet):
    """Вьюсет для пользователей."""

    queryset = User.objects.all()
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (permissions.IsAuthenticated,
                                       IsAuthorOrReadOnly,)
        return super().get_permissions()

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):
        get_object_or_404(User, id=id)
        serializer = SubscriptionCreateSerializer(
            data={'user': self.request.user.id, 'following': id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, **kwargs):
        get_object_or_404(
            Subscription,
            user=self.request.user,
            following=self.kwargs.get('id')
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(pages, many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)
