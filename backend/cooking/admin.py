from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Recipe, Ingredient, Сomposition,
    Follow, Favourites, ShoppingList)

admin.site.register(Сomposition)
admin.site.register(Follow)
admin.site.register(Favourites)
admin.site.register(ShoppingList)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    '''
    Класс описания настроек админ-зоны для модели Рецепт
    '''
    # Поля карточки объекта
    fields = (
        'author', 'title', 'picture', 'description',
        'cooking_time', 'favourites_count',)
    # Недоступные для редактирования поля
    readonly_fields = ('favourites_count',)
    # Поля страницы списка объектов
    list_display = ('author', 'title',)
    # Разрешение редактирование полей на странице списка объектов
    list_editable = ()
    # Разрешение поиска по полям
    search_fields = ('author', 'title',)
    # Разрешение фильтрации по полям
    list_filter = ()
    # Переход к редактированию при клике на поле
    list_display_links = ('title',)
    # Установка заначения вместо пустых
    empty_value_display = 'Не задано'

    def favourites_count(self, obj):
        result = Favourites.objects.filter(recipe=obj).count()
        return mark_safe(result)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    '''
    Класс описания настроек админ-зоны для модели Ингредиент
    '''
    # Поля страницы списка объектов
    list_display = ('title', 'unit')
    # Разрешение редактирование полей на странице списка объектов
    list_editable = ()
    # Разрешение поиска по полям
    search_fields = ('title',)
    # Разрешение фильтрации по полям
    list_filter = ()
    # Переход к редактированию при клике на поле
    list_display_links = ()
    # Установка заначения вместо пустых
    empty_value_display = 'Не задано'
