import base64  # 

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers  # https://www.django-rest-framework.org/api-guide/serializers/
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from cooking.models import (
    Recipe, Ingredient, Сomposition,
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
    name = serializers.SlugField(
        validators=[UniqueValidator(queryset=Ingredient.objects.all())]
    )

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit',)
        read_only = ('', )


class СompositionSerialiser(serializers.ModelSerializer):
    '''
    Сериализатор модели Сomposition
    '''
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = Сomposition
        fields = ('id', 'name', 'measurement_unit', 'amount',)
        read_only = ('', )
        validators = [UniqueTogetherValidator(
            queryset=Сomposition.objects.all(),
            fields=('recipe', 'ingredient')
        )]

    # Проверка на положительность количества ингридиентов в рецепте
    def validate_amount(self, amount):
        if amount <= 0:
            raise serializers.ValidationError(
                'Количество должно быть положительно')
        return amount


class RecipeSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели Recipe
    '''
    author = CustomUserSerializer()
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = СompositionSerialiser(source='component', many=True)
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
            if obj.choosers.filter(id=user.id).exists():
                return True
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if obj.buyers.filter(id=user.id).exists():
                return True
        return False


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
