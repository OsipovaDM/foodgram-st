from django.http import HttpResponse
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import  filters, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

from cooking.models import (
    Recipe, Ingredient,
    User, Follow, Favourites, ShoppingList)
from .serializers import (
    RecipeDetailSerializer, IngredientSerializer,
    CustomUserSerializer, FollowSerializer,
    RecipeCreateUpdateSerializer, RecipeBriefSerializer, CustomUserCreateSerializer,)
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

    @action(
        detail=False,  # Работа с полным набором объектов
        methods=['get'],  # Разрешены только GET запросы
    )
    def download_shopping_cart(self, request):
        user = request.user
        shop_list = {}

        for recipe in user.purchases.all():
            for component in recipe.component.all():
                name = component.ingredient.name
                amount = component.amount
                measurement_unit = component.ingredient.measurement_unit

                if name in shop_list:
                    shop_list[name]['amount'] += amount
                else:
                    shop_list[name] = {
                        'amount': amount,
                        'measurement_unit': measurement_unit
                    }
        
        # Форматируем список в текстовый вид
        text_content = "Список покупок:\n\n"
        for ingredient, data in shop_list.items():
            text_content += f"{ingredient}: {data['amount']} ({data['measurement_unit']})\n"

        # Создаём файловый ответ
        response = HttpResponse(text_content, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response

    @action(
        detail=False,  # Работа с полным набором объектов
        methods=['post', 'delete'],  # Разрешены только POST, DELETE запросы
        url_path=r'(?P<recipe_id>\d+)/favorite'
    )
    def favorite(self, request, recipe_id=None):  #!!!Скорее всего можно как-то объединить с добавлением в список покупок
        user = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        serializer = RecipeBriefSerializer(recipe)
        item = Favourites.objects.filter(recipe=recipe, user=user).first()

        if request.method == 'POST':
            if item is None:
                Favourites.objects.create(recipe=recipe, user=user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'detail': 'Рецепт уже в избранном.'}, status=status.HTTP_400_BAD_REQUEST)

        if item is None:
            return Response({'detail': 'Рецепт отсутствует в избранном.'}, status=status.HTTP_400_BAD_REQUEST)
        
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    Только GET методы с моделью Ингредиент
    '''
    queryset = Ingredient.objects.all()  # Список элементов для представления
    serializer_class = IngredientSerializer

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class FollowViewSet(viewsets.ModelViewSet):
    '''
    Все операции CRUD с моделью Подписка
    '''
    queryset = Follow.objects.all()  # Список элементов для представления
    serializer_class = FollowSerializer


class CustomUserViewSet(DjoserUserViewSet):
    '''
    Все операции CRUD с моделью Рецепт
    '''
    pagination_class = CatsPagination
    serializer_class = CustomUserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserSerializer
    
    def list(self, request):
        queryset = User.objects.all()
        context = self.get_serializer_context()
        serializer = CustomUserSerializer(queryset, context=context, many=True)
        return Response(serializer.data)
