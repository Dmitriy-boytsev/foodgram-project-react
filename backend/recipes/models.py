from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from .constants import(
    IngredientConstants, RecipeConstants, TagConstants
)
from users.models import User


class ShoppingFavorite(models.Model):
    """Абстрактный класс для Избанного и Покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=TagConstants.NAME_LENGTH_MAX,
        unique=True,
    )
    color = ColorField(
        verbose_name='Цвет',
        max_length=TagConstants.COLOR_LENGTH_MAX,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'теги'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} (цвет: {self.color})'


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=IngredientConstants.NAME_LENGTH_MAX,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=IngredientConstants.UNIT_LENGTH_MAX,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_ingredient_measurement_unit'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=RecipeConstants.NAME_LENGTH_MAX,
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images/', )
    text = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                RecipeConstants.COOK_TIME_MIN,
                message=f"""Минимальное время приготовления -
                 {RecipeConstants.COOK_TIME_MIN} минута!"""),
            MaxValueValidator(
                RecipeConstants.COOK_TIME_MAX,
                message='Максимальное значение должно быть не более '
                        f'{RecipeConstants.COOK_TIME_MAX} минут'),
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name


class Favorite(ShoppingFavorite):
    """Модель избранных рецептов."""

    class Meta(ShoppingFavorite.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'избранные'
        default_related_name = 'favorites'
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe',), name='unique_favorite'),
        )

    def __str__(self):
        return f'Рецепт "{self.recipe}" добавлен в Избранное'


class ShoppingCart(ShoppingFavorite):
    """Модель корзины покупок."""

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'корзина покупок'
        default_related_name = 'shopping_cart'
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'), name='unique_shopping_cart'),
        )

    def __str__(self):
        return f'Рецепт "{self.recipe}" добавлен в Корзину покупок'


class RecipeIngredient(models.Model):
    """Модель связи рецепта и ингредиентов."""

    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(
            RecipeConstants.INGREDIENT_AMOUNT_MIN,
            message=f"""Должен быть минимум
                        {RecipeConstants.INGREDIENT_AMOUNT_MIN} ингредиент"""),
            MaxValueValidator(
                RecipeConstants.INGREDIENT_AMOUNT_MAX,
                message=f"""Максимальное значение должно быть не более
                        {RecipeConstants.INGREDIENT_AMOUNT_MAX}!"""),
        ]
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'ингредиенты в рецепте'
        constraints = (
            models.UniqueConstraint(fields=('ingredients', 'recipe'),
                                    name='unique_recipe_ingredients'),
        )

    def __str__(self):
        return (
            f'{self.ingredients.name} '
            f'({self.ingredients.measurement_unit}) - {self.amount}'
        )
