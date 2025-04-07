from django.http import HttpResponse
from rest_framework import mixins, viewsets, status, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from cooking.models import (
    Recipe, Ingredient,
    User, Follow, Favourites, ShoppingList)
from .serializers import (
    RecipeDetailSerializer, IngredientSerializer,
    CustomUserSerializer, FollowSerializer,
    RecipeCreateUpdateSerializer, RecipeBriefSerializer, AvatarSerializer, PasswordSerializer, CustomUserCreateSerializer)
from .pagination import CatsPagination
from .permissions import AuthorOrReadOnly


class RecipeViewSet(viewsets.ModelViewSet):
    '''

    '''
    permission_classes = [AuthorOrReadOnly,]
    serializer_class = RecipeDetailSerializer
    pagination_class = CatsPagination

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

    @action(['get'], True, url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        link = request.build_absolute_uri(f'/s/{recipe.id}')
        return Response({"short-link": link})

    @action(['post', 'delete'], True)
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
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

    @action(['get'], False, permission_classes=[permissions.IsAuthenticated])
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

    @action(['post', 'delete'], True)
    def favorite(self, request, pk=None):  #!!!Скорее всего можно как-то объединить с добавлением в список покупок
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
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
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class CustomUserViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    '''

    '''
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CatsPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserSerializer

    @action(['get'], False, permission_classes=[permissions.IsAuthenticated,])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(['put', 'delete'], False, r'me/avatar', permission_classes=[permissions.IsAuthenticated,])
    def avatar(self, request): #!!!Очень похожую штуку делала в Рецептах
        user = request.user
        if request.method == 'PUT':
            if request.data:
                serializer = AvatarSerializer(instance=user, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({"avatar": user.avatar.url})
            return Response({'detail': 'Мало данных.'}, status=status.HTTP_400_BAD_REQUEST)

        if user.avatar:
            user.avatar.delete()
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Аватар отсутствует в профиле.'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(['post'], False, permission_classes=[permissions.IsAuthenticated,])
    def set_password(self, request): #!!!Опять очень типичная структура
        context = self.get_serializer_context()
        serializer = PasswordSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['get'], False, permission_classes=[permissions.IsAuthenticated,])
    def subscriptions(self, request, *args, **kwargs):
        user = request.user
        authors = User.objects.filter(followers__follower=user)
        context = self.get_serializer_context()

        paginator = CatsPagination()
        paginated_authors = paginator.paginate_queryset(authors, request)
        serializer = FollowSerializer(paginated_authors, many=True, context=context)
        return paginator.get_paginated_response(serializer.data)

    @action(['post', 'delete'], True, permission_classes=[permissions.IsAuthenticated,])
    def subscribe(self, request, pk=None, *args, **kwargs): # явно можно объединить с другими методами
        # параметры obj, User, FollowSerializer, Follow...filter(author=dep, follower=obj) и create(...)
        obj = request.user
        dep = get_object_or_404(User, pk=pk) # dep от слова dependence
        context = self.get_serializer_context()
        serializer = FollowSerializer(dep, context=context)
        item = Follow.objects.filter(author=dep, follower=obj).first()

        if request.method == 'POST':
            if item is None:
                if obj == dep:
                    return Response({'author': 'Нельзя подписаться на самого себя.'}, status=status.HTTP_400_BAD_REQUEST)
                Follow.objects.create(author=dep, follower=obj)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'author': 'Вы уже подписаны на данного автора.'}, status=status.HTTP_400_BAD_REQUEST)

        if item is None:
            return Response({'author': 'Вы не подписаны на данного автора.'}, status=status.HTTP_400_BAD_REQUEST)
        
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
