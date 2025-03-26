from djoser.serializers import UserSerializer
from rest_framework import serializers
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
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class RecipeSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели Recipe
    '''
    class Meta:
        model = Recipe
        fields = ('author', 'title', 'picture', 'description', 'cooking_time',)
        read_only = ('', )
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('author', 'title')
            ),
            UniqueValidator(
                queryset=Recipe.objects.all(),
                fields=('description')
            )
        ]


class IngredientSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели Ingredient
    '''
    class Meta:
        model = Ingredient
        fields = ('title', 'unit',)
        read_only = ('', )
        validators = [UniqueValidator(
            queryset=Ingredient.objects.all(),
            fields=('title')
        )]


class Сomposition(serializers.ModelSerializer):
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
