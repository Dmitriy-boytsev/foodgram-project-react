from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from api.fields import Base64ImageField
from api.validators import validate_username
from recipes.constants import RecipeConstants
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.constants import UsersConstants
from users.models import Subscription

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class UsersSerializer(UserSerializer):
    """Сериализатор пользователей."""

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username',
                  'first_name', 'last_name',
                  'is_subscribed',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return request.user.is_authenticated and obj.following.filter(
            user_id=request.user.id
        ).exists()


class MiniRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор короткой формы рецептов."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionSerializer(UsersSerializer):
    """Сериализатор подписок."""

    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UsersSerializer.Meta):
        fields = UsersSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ('email', 'username',
                            'first_name', 'last_name')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        serializer = MiniRecipeSerializer(
            recipes, many=True, read_only=True, context=self.context
        )
        return serializer.data


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания подписки."""

    class Meta:
        model = Subscription
        fields = (
            'user',
            'following'
        )

    def validate(self, data):
        user = data['user']
        following = data['following']
        if user == following:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя!')

        if user.follower.filter(following=following).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя!')
        return data

    def to_representation(self, instance):
        return SubscriptionSerializer(
            instance.following,
            context=self.context
        ).data


class UserRegistrationSerializer(UserCreateSerializer):
    """Сериализатор регистрации пользователей."""

    username = serializers.CharField(
        max_length=UsersConstants.NAME_LENGTH_MAX,
        validators=[validate_username])

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте."""

    id = serializers.IntegerField(source='ingredients.id')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)

    def validate_id(self, id_value):
        if not Ingredient.objects.filter(id=id_value).exists():
            raise serializers.ValidationError(
                'Данный ингредиент не существует!'
            )
        return id_value

    def validate_amount(self, amount_value):
        if amount_value < RecipeConstants.INGREDIENT_AMOUNT_MIN:
            raise serializers.ValidationError(
                f"""Количество ингредиентов не может быть меньше
                 {RecipeConstants.INGREDIENT_AMOUNT_MIN}!"""
            )
        if amount_value > RecipeConstants.INGREDIENT_AMOUNT_MAX:
            raise serializers.ValidationError(
                f"""Количество ингредиентов не может быть больше
                 {RecipeConstants.INGREDIENT_AMOUNT_MAX}!"""
            )
        return amount_value


class RecipeIngredientDetailSerializer(serializers.ModelSerializer):
    """Сериализатор детальной информации об ингредиентах в рецепте."""

    id = serializers.IntegerField(source='ingredients.id')
    name = serializers.CharField(source='ingredients.name')
    measurement_unit = serializers.CharField(
        source='ingredients.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetCreateSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов для безопасных запросов."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientDetailSerializer(
        source='recipe_ingredients', many=True
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and user.favorites.filter(
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and user.shopping_cart.filter(
            recipe=obj
        ).exists()

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        validated_data['author'] = user
        recipe = Recipe.objects.create(**validated_data)
        return recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True, required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        ingredients_data = data.get('recipe_ingredients')
        if not ingredients_data:
            raise serializers.ValidationError({
                'recipe_ingredients': 'Поле ингредиентов обязательно!'
            })
        ingredient_ids = [
            ingredient['ingredients']['id'] for ingredient in ingredients_data
        ]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не могут повторяться!'
            )
        tags_data = data.get('tags')
        if not tags_data:
            raise serializers.ValidationError({
                'tags': 'Поле тегов обязательно!'
            })
        if len(tags_data) != len(set(tags_data)):
            raise serializers.ValidationError('Теги не могут повторяться!')
        return data

    def create_ingredients(self, recipe, ingredients_data):
        recipe_ingredients = (
            RecipeIngredient(
                recipe=recipe,
                ingredients_id=ingredient_data['ingredients']['id'],
                amount=ingredient_data['amount']
            ) for ingredient_data in ingredients_data
        )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create_tags(self, recipe, tags_data):
        recipe.tags.set(tags_data)

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('recipe_ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        self.create_ingredients(recipe, ingredients_data)
        self.create_tags(recipe, tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')
        instance.recipe_ingredients.all().delete()
        self.create_ingredients(instance, ingredients_data)
        instance.tags.clear()
        self.create_tags(instance, tags_data)
        instance = super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeGetCreateSerializer(instance, context=context).data


class BaseRecipeActionSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для Избранного и Корзины покупок."""

    class Meta:
        fields = ('recipe', 'user')

    def validate(self, data):
        recipe_value = data.get('recipe')
        user = self.context.get('request').user

        if not Recipe.objects.filter(id=recipe_value.id).exists():
            raise serializers.ValidationError('Данного рецепта не существует!')

        if self.Meta.model.objects.filter(user=user,
                                          recipe=recipe_value).exists():
            raise serializers.ValidationError('Рецепт уже добавлен.')

        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['recipe'] = MiniRecipeSerializer(instance.recipe).data
        return representation['recipe']


class FavoriteSerializer(BaseRecipeActionSerializer):
    """Сериализатор Избранного."""

    class Meta(BaseRecipeActionSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(BaseRecipeActionSerializer):
    """Сериализатор Корзины покупок."""

    class Meta(BaseRecipeActionSerializer.Meta):
        model = ShoppingCart


class ShoppingCartDownloadSerializer(serializers.Serializer):
    """Сериализатор скачивания Корзины покупок."""

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def validate(self, shopping_cart_data):
        user = self.context.get('request').user
        if not ShoppingCart.objects.filter(user=user).exists():
            raise serializers.ValidationError('Корзина покупок пуста')
        return shopping_cart_data
