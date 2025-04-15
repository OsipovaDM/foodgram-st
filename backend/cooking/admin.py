from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Recipe, Ingredient, Composition,
    Follow, Favourites, ShoppingList, ShortLink)

admin.site.register(Composition)
admin.site.register(Follow)
admin.site.register(Favourites)
admin.site.register(ShoppingList)
admin.site.register(ShortLink)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    '''
    Класс описания настроек админ-зоны для модели Рецепт
    '''
    # Поля карточки объекта
    fields = (
        'author', 'name', 'image', 'text',
        'cooking_time', 'favourites_count',)
    # Недоступные для редактирования поля
    readonly_fields = ('favourites_count',)
    # Поля страницы списка объектов
    list_display = ('author', 'name',)
    # Разрешение редактирование полей на странице списка объектов
    list_editable = ()
    # Разрешение поиска по полям
    search_fields = ('author__first_name', 'name',)
    # Разрешение фильтрации по полям
    list_filter = ()
    # Переход к редактированию при клике на поле
    list_display_links = ('name',)
    # Установка заначения вместо пустых
    empty_value_display = 'Не задано'

    def favourites_count(self, obj):
        """Возвращает количество добавлений рецепта в избранное с человекочитаемым заголовком"""
        result = Favourites.objects.filter(recipe=obj).count()
        return mark_safe(result)

    favourites_count.short_description = 'В избранном (раз)'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    '''
    Класс описания настроек админ-зоны для модели Ингредиент
    '''
    # Поля страницы списка объектов
    list_display = ('name', 'measurement_unit')
    # Разрешение редактирование полей на странице списка объектов
    list_editable = ()
    # Разрешение поиска по полям
    search_fields = ('name',)
    # Разрешение фильтрации по полям
    list_filter = ()
    # Переход к редактированию при клике на поле
    list_display_links = ()
    # Установка заначения вместо пустых
    empty_value_display = 'Не задано'
