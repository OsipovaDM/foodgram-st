from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    '''
    Модель для хранения информации о рецептах
    '''
    author = models.ForeignKey(
        User, verbose_name='Автор', on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(
        'Название', max_length=50)
    picture = models.ImageField(
        'Картинка', upload_to='pictures/', null=True, blank=True)
    description = models.TextField(
        'Текстовое описание', unique=True)
    cooking_time = models.DurationField('Время приготовления', help_text='В минутах')

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('author', 'title'), name='AuthorTitle'),
        )
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title


class BaseModel(models.Model):
    '''
    Абстрактная модель.
    Добавляет к модели связь с рецептом и пользователем
    '''
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт', on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, verbose_name='Пользователь', on_delete=models.CASCADE)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('user', 'recipe'), name='UserRecipe'),
        )
        abstract = True

    def __str__(self):
        return self.user.__str__() + ' -- ' + self.recipe.__str__()


class Ingredient(models.Model):
    '''
    Модель для хранения информации об ингредиентах
    '''
    title = models.CharField(
        'Название', max_length=50, unique=True)
    unit = models.CharField(
        'Единица измерения', max_length=50)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    '''
    Модель связывает рецепты и ингредиенты
    '''
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient, verbose_name='Ингредиент', on_delete=models.CASCADE)
    quantity = models.FloatField(
        'Количество')

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('recipe', 'ingredient'), name='RecipeIngridient'),
        )
        verbose_name = 'ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return self.recipe.__str__() + ': ' + self.ingredient.__str__() + ' (' + self.ingredient.unit + ') ' + ' -- ' + str(self.quantity)


class Follow(models.Model):
    '''
    Модель связывает пользователей
    с авторами рецептов, на которых они подписаны
    '''
    author = models.ForeignKey(
        User, verbose_name='Автор', on_delete=models.CASCADE, related_name='authors')
    user = models.ForeignKey(
        User, verbose_name='Подписчик', on_delete=models.CASCADE, related_name='users')

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('author', 'user'), name='AuthorUser'),
        )
        verbose_name = 'автор -- подписчик '
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return self.author.__str__() + ' -- ' + self.user.__str__()


class Favourites(BaseModel):
    '''
    Модель связывает избранные рецепты с пользователями
    '''

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'


class SoppingList(BaseModel):
    '''
    Модель связывает пользователей и рецепты, добавленные в список покупок
    '''

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
