# from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from cooking.models import (
    Recipe, Ingredient, Сomposition,
    User, Follow, Favourites, ShoppingList)
from .serializers import (
    RecipeSerializer, IngredientSerializer, СompositionSerialiser,
    CustomUserSerializer, FollowSerializer, FavouritesSerializer,
    ShoppingListSerializer)
from .pagination import CatsPagination


class RecipeViewSet(viewsets.ModelViewSet):
    '''
    Все операции CRUD с моделью Рецепт
    '''
    # pagination_class = CatsPagination
    serializer_class = RecipeSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            user = -1
        recipes = Recipe.objects.all()
        if self.request.query_params.get('is_favorited') == "1":
            recipes = recipes.filter(choosers=user)

        if self.request.query_params.get('is_in_shopping_cart') == "1":
            recipes = recipes.filter(buyers=user)

        if 'author' in self.request.query_params:
            recipes = recipes.filter(author=user)

        return recipes


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
    serializer_class = СompositionSerialiser


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
    serializer_class = CustomUserSerializer
