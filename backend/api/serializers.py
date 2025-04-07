import base64

from django.contrib.auth import password_validation
from django.contrib.auth.hashers import check_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from cooking.models import (
    Recipe, Ingredient, Composition, User, Follow
)


class Base64ImageField(serializers.ImageField):
    """Поле для работы с изображениями в формате base64."""

    def to_internal_value(self, data):
        """
        Преобразует данные изображения из base64 в файл.

        Args:
            data: Входные данные, может быть строкой base64 или файлом

        Returns:
            ContentFile: Декодированное изображение в виде файла
        """
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')

        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    """Сериализатор для модели пользователя с кастомными полями."""

    email = serializers.EmailField(
        required=True,
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            UnicodeUsernameValidator(),
        ]
    )
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    avatar = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 
            'last_name', 'is_subscribed', 'avatar',
        )

    def get_avatar(self, obj):
        """Возвращает URL аватара пользователя или None."""
        if obj.avatar:
            return obj.avatar.url
        return None

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на автора."""
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.authors.filter(author=user).exists()
        return False


class CustomUserCreateSerializer(CustomUserSerializer):
    """Сериализатор для создания пользователя с паролем."""

    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        """Создает нового пользователя с валидированными данными."""
        return User.objects.create_user(**validated_data)


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class PasswordSerializer(serializers.ModelSerializer):
    """Сериализатор для изменения пароля пользователя."""

    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    current_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('new_password', 'current_password')

    def validate_current_password(self, value):
        """Проверяет корректность текущего пароля."""
        user = self.context['request'].user
        if not check_password(value, user.password):
            raise serializers.ValidationError("Текущий пароль неверный")
        return value

    def validate_new_password(self, value):
        """Валидирует новый пароль."""
        user = self.context['request'].user
        password_validation.validate_password(value, user)
        return value


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class CompositionSerialiser(serializers.ModelSerializer):
    """Сериализатор для состава рецепта (ингредиент + количество)."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', required=False)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', 
        required=False
    )

    class Meta:
        model = Composition
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('name',)
        validators = [
            UniqueTogetherValidator(
                queryset=Composition.objects.all(),
                fields=('recipe', 'ingredient')
            )
        ]

    def validate_amount(self, amount):
        """Проверяет, что количество ингредиента положительное."""
        if amount <= 0:
            raise serializers.ValidationError(
                'Количество должно быть положительно'
            )
        return amount


class RecipeBaseSerialiser(serializers.ModelSerializer):
    """Базовый сериализатор для рецептов с общими полями."""

    author = CustomUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    image = serializers.SerializerMethodField(read_only=True)
    ingredients = CompositionSerialiser(source='component', many=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('author', 'name')
            )
        ]
        abstract = True

    def get_image(self, obj):
        """Возвращает URL изображения рецепта."""
        if obj.image:
            return obj.image.url
        return None

    def get_is_favorited(self, obj):
        """Проверяет, находится ли рецепт в избранном у пользователя."""
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.choosers.filter(id=user.id).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, находится ли рецепт в списке покупок пользователя."""
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.buyers.filter(id=user.id).exists()
        return False


class RecipeBriefSerializer(RecipeBaseSerialiser):
    """Краткий сериализатор рецепта для списков."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('name', 'image', 'cooking_time')


class RecipeDetailSerializer(RecipeBaseSerialiser):
    """Детальный сериализатор рецепта."""
    pass


class RecipeCreateUpdateSerializer(RecipeBaseSerialiser):
    """Сериализатор для создания и обновления рецептов."""

    ingredients = serializers.JSONField()
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=1)

    def validate_ingredients(self, value):
        """Валидирует список ингредиентов."""
        if not value:
            raise serializers.ValidationError(
                'Ingredients list cannot be empty'
            )

        ingredients = []
        seen_ids = set()

        for item in value:
            self._validate_ingredient_item(item, seen_ids)
            ingredients.append(item)

        return ingredients

    def _validate_ingredient_item(self, item, seen_ids):
        """Валидирует отдельный элемент списка ингредиентов."""
        ingredient_id = item.get('id')
        amount = item.get('amount')

        if not ingredient_id or not amount:
            raise serializers.ValidationError(
                'Each ingredient must have id and amount'
            )

        if int(amount) < 1:
            raise serializers.ValidationError('Amount must be at least 1')

        if ingredient_id in seen_ids:
            raise serializers.ValidationError('Ingredients must be unique')

        seen_ids.add(ingredient_id)

    def _process_ingredients(self, recipe, ingredients_data):
        """Обрабатывает список ингредиентов для рецепта."""
        for ingredient in ingredients_data:
            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                raise serializers.ValidationError(
                    f"Ингредиент с индексом {ingredient['id']} не существует."
                )
            Composition.objects.create(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )

    def create(self, validated_data):
        """Создает новый рецепт."""
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self._process_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновляет существующий рецепт."""
        if 'ingredients' not in validated_data:
            raise serializers.ValidationError('Поле "ingredients" обязательно')

        ingredients_data = validated_data.pop('ingredients')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.component.all().delete()
        self._process_ingredients(instance, ingredients_data)

        instance.save()
        return instance

    def to_representation(self, instance):
        """Преобразует экземпляр рецепта для отображения."""
        return RecipeDetailSerializer(instance, context=self.context).data


class FollowSerializer(CustomUserSerializer):
    """Сериализатор для подписок с информацией о рецептах."""

    recipes = RecipeBriefSerializer(read_only=True, many=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes',
            'recipes_count', 'avatar'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('author', 'follower'),
                message='Вы уже подписаны на этого автора'
            )
        ]

    def validate(self, attrs):
        """Проверяет, что пользователь не подписывается на себя."""
        if self.context['request'].user == attrs['author']:
            raise serializers.ValidationError(
                {'author': 'Нельзя подписаться на самого себя'}
            )
        return super().validate(attrs)

    def get_recipes_count(self, obj):
        """Возвращает количество рецептов автора."""
        return obj.recipes.all().count()
