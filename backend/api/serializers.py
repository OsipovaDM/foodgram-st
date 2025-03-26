from djoser.serializers import UserSerializer
from rest_framework import serializers  # https://www.django-rest-framework.org/api-guide/serializers/
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from cooking.models import (
    Recipe, Ingredient, Сomposition,
    User, Follow, Favourites, ShoppingList)


class BaseSerialiser(serializers.ModelSerializer):
    '''
    Абстрактный сериализатор полей recipe, user
    '''
    class Meta:
        fields = ('recipe', 'user')
        abstract = True


# Не знаю, насколько мне это понадобится
# Возможно, придется добавлять сюда поля is_subscribed, avatar
class CustomUserSerializer(UserSerializer):
    '''
    Переопределен набор полей сериализатора для Пользователя
    '''
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'avatar',)


class IngredientSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели Ingredient
    '''
    title = serializers.SlugField(
        validators=[UniqueValidator(queryset=Ingredient.objects.all())]
    )

    class Meta:
        model = Ingredient
        fields = ('title', 'unit',)
        read_only = ('', )


class RecipeSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели Recipe
    '''
    author = CustomUserSerializer()
    ingredients = IngredientSerializer(many=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    text = serializers.SlugField(
        validators=[UniqueValidator(queryset=Recipe.objects.all())]
    )

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',)
        read_only = ('is_favorited', 'is_in_shopping_cart')
        validators = [UniqueTogetherValidator(
            queryset=Recipe.objects.all(),
            fields=('author', 'title')
        )]

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.choosers.get(id=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.buyers.get(id=user).exists()
        return False


class СompositionSerialiser(serializers.ModelSerializer):
    '''
    Сериализатор модели Сomposition
    '''
    class Meta:
        model = Сomposition
        fields = ('recipe', 'ingredient', 'quantity',)
        read_only = ('', )
        validators = [UniqueTogetherValidator(
            queryset=Сomposition.objects.all(),
            fields=('recipe', 'ingredient')
        )]

    # Проверка на положительность количества ингридиентов в рецепте
    def validate_quantity(self, quantity):
        if quantity <= 0:
            raise serializers.ValidationError(
                'Количество должно быть положительно')
        return quantity


class FollowSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели Follow
    '''
    class Meta:
        model = Follow
        fields = ('author', 'user',)
        read_only = ('', )
        validators = [UniqueTogetherValidator(
            queryset=Follow.objects.all(),
            fields=('author', 'user')
        )]


class FavouritesSerializer(BaseSerialiser):
    '''
    Сериализатор модели Favourites
    '''
    class Meta:
        model = Favourites
        read_only = ('', )
        validators = [UniqueTogetherValidator(
            queryset=Favourites.objects.all(),
            fields=('recipe', 'user')
        )]


class ShoppingListSerializer(BaseSerialiser):
    '''
    Сериализатор модели ShoppingList
    '''
    class Meta:
        model = ShoppingList
        read_only = ('', )
        validators = [UniqueTogetherValidator(
            queryset=Favourites.objects.all(),
            fields=('recipe', 'user')
        )]
