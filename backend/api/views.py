# from django.shortcuts import render
from rest_framework import viewsets

from cooking.models import (
    Recipe, Ingredient, Сomposition,
    User, Follow, Favourites, ShoppingList)
from .serializers import (
    RecipeSerializer, IngredientSerializer, СompositionSerializer,
    UserSerializer, FollowSerializer, FavouritesSerializer,
    ShoppingListSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    '''
    Все операции CRUD с моделью Рецепт
    '''
    queryset = Recipe.objects.all()  # Список элементов для представления
    serializer_class = RecipeSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    '''
    Все операции CRUD с моделью Ингредиент
    '''
    queryset = Ingredient.objects.all()  # Список элементов для представления
    serializer_class = IngredientSerializer


class СompositionViewSet(viewsets.ModelViewSet):
    '''
    Все операции CRUD с моделью Состав
    '''
    queryset = Сomposition.objects.all()  # Список элементов для представления
    serializer_class = СompositionSerializer


class FollowViewSet(viewsets.ModelViewSet):
    '''
    Все операции CRUD с моделью Подписка
    '''
    queryset = Follow.objects.all()  # Список элементов для представления
    serializer_class = FollowSerializer


class FavouritesViewSet(viewsets.ModelViewSet):
    '''
    Все операции CRUD с моделью Избранное
    '''
    queryset = Favourites.objects.all()  # Список элементов для представления
    serializer_class = FavouritesSerializer


class ShoppingListViewSet(viewsets.ModelViewSet):
    '''
    Все операции CRUD с моделью Список покупок
    '''
    queryset = ShoppingList.objects.all()  # Список элементов для представления
    serializer_class = ShoppingListSerializer


class UserViewSet(viewsets.ModelViewSet):
    '''
    Все операции CRUD с моделью Рецепт
    '''
    queryset = User.objects.all()  # Список элементов для представления
    serializer_class = UserSerializer