from secrets import token_urlsafe
from django.http import HttpResponse
from django.shortcuts import redirect
from rest_framework import mixins, viewsets, status, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from cooking.models import (
    Recipe, Ingredient, User, Follow, Favourites, ShoppingList, ShortLink
)
from .serializers import (
    RecipeDetailSerializer, IngredientSerializer,
    CustomUserSerializer, FollowSerializer,
    RecipeCreateUpdateSerializer, RecipeBriefSerializer,
    AvatarSerializer, PasswordSerializer, CustomUserCreateSerializer
)
from .pagination import CatsPagination
from .permissions import AuthorOrReadOnly


@api_view(['GET'])
def redirect_short_link(request, abridged):
    try:
        link = ShortLink.objects.get(abridged=abridged)
        return redirect(link.origin)
    except ShortLink.DoesNotExist:
        return Response({"error": "Ссылка не найдена"}, status=404)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с рецептами (CRUD и дополнительные действия)."""

    permission_classes = [AuthorOrReadOnly]
    serializer_class = RecipeDetailSerializer
    pagination_class = CatsPagination

    def get_serializer_class(self):
        """Определяет класс сериализатора в зависимости от действия."""
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        """
        Возвращает queryset рецептов с возможностью фильтрации:
        - по избранному
        - по списку покупок
        - по автору
        """
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
        """Создает рецепт, устанавливая текущего пользователя как автора."""
        serializer.save(author=self.request.user)

    @action(['get'], True, url_path='get-link')
    def get_link(self, request, pk=None):
        """Генерирует короткую ссылку на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        original_url = request.build_absolute_uri(recipe.get_absolute_url())
        item = ShortLink.objects.filter(origin=original_url).first()
        if item:
            abridged = item.abridged
        else:
            abridged = token_urlsafe(6)[:6]
            ShortLink.objects.create(
                origin=original_url,
                abridged=abridged
            )
        link = request.build_absolute_uri(f'/s/{abridged}')
        return Response({"short-link": link})

    def _handle_item_action(self, request, pk, model, serializer_class,
                            exists_message, not_exists_message):
        """
        Общий метод для обработки добавления/удаления элементов
        (избранное, список покупок).
        """
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = serializer_class(recipe)
        item = model.objects.filter(recipe=recipe, user=user).first()

        if request.method == 'POST':
            if item is None:
                model.objects.create(recipe=recipe, user=user)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                {'detail': exists_message},
                status=status.HTTP_400_BAD_REQUEST
            )

        if item is None:
            return Response(
                {'detail': not_exists_message},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['post', 'delete'], True)
    def shopping_cart(self, request, pk=None):
        """Добавляет/удаляет рецепт в список покупок."""
        return self._handle_item_action(
            request, pk, ShoppingList, RecipeBriefSerializer,
            'Рецепт уже есть в списке покупок.',
            'Рецепт отсутствует в списке покупок.'
        )

    @action(['post', 'delete'], True)
    def favorite(self, request, pk=None):
        """Добавляет/удаляет рецепт в избранное."""
        return self._handle_item_action(
            request, pk, Favourites, RecipeBriefSerializer,
            'Рецепт уже в избранном.',
            'Рецепт отсутствует в избранном.'
        )

    @action(['get'], False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачивает текстовый файл со списком покупок."""
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

        text_content = "Список покупок:\n\n"
        for ingredient, data in shop_list.items():
            text_content += f"{ingredient}: "
            text_content += f"{data['amount']} {data['measurement_unit']}\n"

        response = HttpResponse(
            text_content,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = 'attachment; filename="ShopList.txt"'
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с ингредиентами (только чтение)."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        """Фильтрует ингредиенты по имени (регистронезависимо)."""
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class CustomUserViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """ViewSet для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CatsPagination

    def get_serializer_class(self):
        """Определяет класс сериализатора в зависимости от действия."""
        if self.action == 'create':
            return CustomUserCreateSerializer
        return super().get_serializer_class()

    @action(['get'], False, permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Возвращает информацию о текущем пользователе."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def _handle_avatar_password_action(
            self, request, serializer_class=None,
            delete_handler=None, success_handler=None):
        """
        Общий метод для обработки действий с аватаром и паролем.

        Args:
            request: HTTP запрос
            serializer_class: Класс сериализатора (для PUT)
            delete_handler: Функция для обработки DELETE
            success_handler: Функция для обработки успешного выполнения

        Returns:
            Response: HTTP ответ
        """
        if request.method == 'PUT':
            if not request.data:
                return Response(
                    {'detail': 'Мало данных.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = serializer_class(
                instance=request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return success_handler(serializer.data)

        if request.method == 'DELETE':
            return delete_handler()

    @action(['put', 'delete'], False, 'me/avatar',
            permission_classes=[permissions.IsAuthenticated])
    def avatar(self, request):
        """Обновляет или удаляет аватар пользователя."""

        def handle_delete():
            if not request.user.avatar:
                return Response(
                    {'detail': 'Аватар отсутствует в профиле.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            request.user.avatar.delete()
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return self._handle_avatar_password_action(
            request,
            serializer_class=AvatarSerializer,
            delete_handler=handle_delete,
            success_handler=lambda data: Response(
                {"avatar": request.user.avatar.url})
        )

    @action(['post'], False, permission_classes=[permissions.IsAuthenticated])
    def set_password(self, request):
        """Изменяет пароль пользователя."""
        context = self.get_serializer_context()
        serializer = PasswordSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['get'], False, permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        """Возвращает список подписок пользователя с пагинацией."""
        authors = User.objects.filter(followers__follower=request.user)
        recipes_limit = request.query_params.get('recipes_limit')

        paginator = CatsPagination()
        paginated_authors = paginator.paginate_queryset(authors, request)
        context = self.get_serializer_context()
        context['recipes_limit'] = recipes_limit
        serializer = FollowSerializer(
            paginated_authors,
            many=True,
            context=context
        )
        return paginator.get_paginated_response(serializer.data)

    @action(['post', 'delete'], True,
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk=None):
        """Добавляет/удаляет подписку на автора."""
        user = request.user
        recipes_limit = request.query_params.get('recipes_limit')
        author = get_object_or_404(User, pk=pk)
        context = self.get_serializer_context()
        context['recipes_limit'] = recipes_limit
        serializer = FollowSerializer(author, context=context)
        sub = Follow.objects.filter(author=author, follower=user).first()

        if request.method == 'POST':
            if sub:
                return Response(
                    {'author': 'Вы уже подписаны на данного автора.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user == author:
                return Response(
                    {'author': 'Нельзя подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(author=author, follower=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not sub:
            return Response(
                {'author': 'Вы не подписаны на данного автора.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        sub.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
