from django.contrib.auth import get_user_model  # Модель пользователя
from django.db import models  # Основная модель
from django.urls import reverse

from users.models import User


class Recipe(models.Model):
    '''
    Модель для хранения информации о рецептах
    '''
    author = models.ForeignKey(
        User, verbose_name='Автор', on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(
        'Название', max_length=50)
    image = models.ImageField(
        'Картинка', upload_to='pictures/')
    text = models.TextField(
        'Текстовое описание')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления', help_text='В минутах')
    ingredients = models.ManyToManyField(
        to="Ingredient", through="Composition", related_name="recipes",)
    choosers = models.ManyToManyField(
        to="users.User",
        through="Favourites",
        related_name="preferred",
    )
    buyers = models.ManyToManyField(
        to="users.User",
        through="ShoppingList",
        related_name="purchases",
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('author', 'name'), name='RecipeUK'),
        )
        # Человекочитаемое имя
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    # Отображение при обращении к объекту
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("recipes-detail", kwargs={"pk": self.pk})
    


class BaseModel(models.Model):
    '''
    Абстрактная модель.
    Добавляет к модели связь с рецептом и пользователем
    '''
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт', on_delete=models.CASCADE, related_name='+')
    user = models.ForeignKey(
        User, verbose_name='Пользователь', on_delete=models.CASCADE, related_name='+')

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('user', 'recipe'), name='UserRecipe'),
        )
        abstract = True

    # Отображение при обращении к объекту
    def __str__(self):
        return self.user.__str__() + ' -- ' + self.recipe.__str__()


class Ingredient(models.Model):
    '''
    Модель для хранения информации об ингредиентах
    '''
    name = models.CharField(
        'Название', max_length=50, unique=True)
    measurement_unit = models.CharField(
        'Единица измерения', max_length=50)

    class Meta:
        # Человекочитаемое имя
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    # Отображение при обращении к объекту
    def __str__(self):
        return self.name


class Composition(models.Model):
    '''
    Модель связывает рецепты и ингредиенты
    '''
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт', on_delete=models.CASCADE, related_name='component')
    ingredient = models.ForeignKey(
        Ingredient, verbose_name='Ингредиент', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        'Количество')

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('recipe', 'ingredient'), name='RecipeIngridient'),
        )
        # Человекочитаемое имя
        verbose_name = 'состав'
        verbose_name_plural = 'Составы'


class Follow(models.Model):
    '''
    Модель связывает пользователей
    с авторами рецептов, на которых они подписаны
    '''
    author = models.ForeignKey(
        User, verbose_name='Автор', on_delete=models.CASCADE, related_name='followers')
    follower = models.ForeignKey(
        User, verbose_name='Подписчик', on_delete=models.CASCADE, related_name='authors')

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('author', 'follower'), name='AuthorFollower'),
            models.CheckConstraint(check=~models.Q(author=models.F('follower')), name='author_not_follower'),
        )
        # Человекочитаемое имя
        verbose_name = 'автор -- подписчик '
        verbose_name_plural = 'Подписки'


class Favourites(BaseModel):
    '''
    Модель связывает избранные рецепты с пользователями
    '''

    class Meta:
        # Человекочитаемое имя
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'


class ShoppingList(BaseModel):
    '''
    Модель связывает пользователей и рецепты, добавленные в список покупок
    '''

    class Meta:
        # Человекочитаемое имя
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'


class ShortLink(models.Model):
    """Описывает короткие ссылки на рецепты"""

    origin = models.URLField('Исходная ссылка на рецепт ', max_length=200, unique=True)
    abridged = models.CharField('Код рецепта', max_length=50, unique=True)

    class Meta:
        # Человекочитаемое имя
        verbose_name = 'перенаправление ссылки'
        verbose_name_plural = 'Перенаправление ссылок'

    def __str__(self):
        return f'{self.origin} <--> {self.abridged}'
