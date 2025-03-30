# from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import  mixins, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

from cooking.models import (
    Recipe, Ingredient, Composition,
    User, Follow, Favourites, ShoppingList)
from .serializers import (
    RecipeDetailSerializer, IngredientSerializer, CompositionSerialiser,
    CustomUserSerializer, FollowSerializer, FavouritesSerializer,
    ShoppingListSerializer, RecipeCreateUpdateSerializer, RecipeBriefSerializer,)
from .pagination import CatsPagination


class RecipeViewSet(viewsets.ModelViewSet):
    '''
    Все операции CRUD с моделью Рецепт
    '''
    pagination_class = CatsPagination
    serializer_class = RecipeDetailSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        recipes = Recipe.objects.all()
        user = self.request.user
        if user.is_anonymous:
            user = -1
        if self.request.query_params.get('is_favorited') == "1":
            recipes = recipes.filter(choosers=user)

        if self.request.query_params.get('is_in_shopping_cart') == "1":
            recipes = recipes.filter(buyers=user)

        if 'author' in self.request.query_params:
            recipes = recipes.filter(author=user)

        return recipes

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,  # Работа с одним объектом
        methods=['get'],  # Разрешены только GET запросы
        url_path='get-link'  # Ссылка для вызова метода
    )
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        link = request.build_absolute_uri(f'/s/{recipe.id}')
        return Response({"short-link": link})

    @action(
        detail=False,  # Работа с полным набором объектов
        methods=['post', 'delete'],  # Разрешены только POST, DELETE запросы
        url_path=r'(?P<recipe_id>\d+)/shopping_cart'
    )
    def shopping_cart(self, request, recipe_id=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        serializer = RecipeBriefSerializer(recipe)
        item = ShoppingList.objects.filter(recipe=recipe, user=user).first()

        if request.method == 'POST':
            if item is None:
                ShoppingList.objects.create(recipe=recipe, user=user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'detail': 'Рецепт уже есть в списке покупок.'}, status=status.HTTP_400_BAD_REQUEST)

        if item is None:
            return Response({'detail': 'Рецепт отсутствует в списке покупок.'}, status=status.HTTP_400_BAD_REQUEST)
        
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ShoppingListViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    '''
    Операции POST и DELETE с моделью Список покупок
    '''
    queryset = Recipe.objects.all()  # Список элементов для представления
    serializer_class = ShoppingListSerializer

    # def perform_create(self, serializer, recipe_id):
    #     user = self.request.user
    #     recipe = Recipe.objects.get_object_or_404(pk=recipe_id)
    #     ShoppingList.objects.create(recipe=recipe, user=user)
    #     serializer.save()


class IngredientViewSet(viewsets.ModelViewSet):
    '''
    Все операции CRUD с моделью Ингредиент
    '''
    queryset = Ingredient.objects.all()  # Список элементов для представления
    serializer_class = IngredientSerializer


class CompositionViewSet(viewsets.ModelViewSet):
    '''
    Все операции CRUD с моделью Состав
    '''
    queryset = Composition.objects.all()  # Список элементов для представления
    serializer_class = CompositionSerialiser


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


class UserViewSet(viewsets.ModelViewSet):
    '''
    Все операции CRUD с моделью Рецепт
    '''
    queryset = User.objects.all()  # Список элементов для представления
    serializer_class = CustomUserSerializer
