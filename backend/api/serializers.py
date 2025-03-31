import base64  # 

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers  # https://www.django-rest-framework.org/api-guide/serializers/
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from cooking.models import (
    Recipe, Ingredient, Composition,
    User, Follow, Favourites, ShoppingList)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Если полученный объект строка, и эта строка 
        # начинается с 'data:image'...
        if isinstance(data, str) and data.startswith('data:image'):
            # ...начинаем декодировать изображение из base64.
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(';base64,')  
            # И извлечь расширение файла.
            ext = format.split('/')[-1]  
            # Затем декодировать сами данные и поместить результат в файл,
            # которому дать название по шаблону.
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class BaseSerialiser(serializers.ModelSerializer):
    '''
    Абстрактный сериализатор полей recipe, user
    '''
    class Meta:
        fields = ('recipe', 'user')
        abstract = True


class CustomUserSerializer(UserSerializer):
    '''
    Переопределен набор полей сериализатора для Пользователя
    '''
    avatar = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)  # Подписан ли текущий пользователь на этого

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'avatar',)

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            is_subscribed = obj.authors.filter(author=user).exists()
            return is_subscribed
        return False


class CustomUserCreateSerializer(CustomUserSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',)


class IngredientSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели Ingredient
    '''

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class CompositionSerialiser(serializers.ModelSerializer):
    '''
    Сериализатор модели Composition
    '''
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', required=False)
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit', required=False)

    class Meta:
        model = Composition
        fields = ('id', 'name', 'measurement_unit', 'amount',)
        read_only_fields = ('name', )

    # Проверка на положительность количества ингридиентов в рецепте
    def validate_amount(self, amount):
        if amount <= 0:
            raise serializers.ValidationError(
                'Количество должно быть положительно')
        return amount


class RecipeBaseSerialiser(serializers.ModelSerializer):
    '''
    Абстрактный сериализатор полей recipe
    '''
    author = CustomUserSerializer(read_only=True, default=serializers.CurrentUserDefault())
    image = serializers.SerializerMethodField(read_only=True)
    ingredients = CompositionSerialiser(source='component', many=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',)
        abstract = True

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.choosers.filter(id=user.id).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.buyers.filter(id=user.id).exists()
        return False


class RecipeBriefSerializer(RecipeBaseSerialiser):
    '''
    Сериализатор модели Recipe
    '''
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('name', 'image', 'cooking_time',)


class RecipeDetailSerializer(RecipeBaseSerialiser):
    '''
    Сериализатор модели Recipe
    '''
    pass


class RecipeCreateUpdateSerializer(RecipeBaseSerialiser):
    '''
    Сериализатор модели Recipe
    '''
    ingredients = serializers.JSONField()
    image = Base64ImageField(required=False, allow_null=True)

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Ingredients list cannot be empty'
            )
        ingredients = []
        for item in value:
            ingredient_id = item.get('id')
            amount = item.get('amount')
            if not ingredient_id or not amount:
                raise serializers.ValidationError(
                    'Each ingredient must have id and amount'
                )
            if int(amount) < 1:
                raise serializers.ValidationError(
                    'Amount must be at least 1'
                )
            ingredients.append(item)
        return ingredients

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        #!!!Вынести в отдельную функцию
        for ingredient in ingredients:
            Composition.objects.create(recipe=recipe, ingredient_id=ingredient['id'], amount=ingredient['amount'])
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)  # instance.attr = value

        if ingredients_data is not None:
            instance.component.all().delete()
            lst = []
            for ingredient in ingredients_data:
                Composition.objects.create(recipe=instance, ingredient_id=ingredient['id'], amount=ingredient['amount'])
            instance.ingredients.set(lst)

        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeDetailSerializer(instance, context=self.context).data


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
