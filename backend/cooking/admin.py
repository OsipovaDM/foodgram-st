from django.contrib import admin

from .models import (
    Recipe, Ingredient, RecipeIngredient,
    User, Follow, Favourites, SoppingList)

# admin.site.register(Recipe)
# admin.site.register(Ingredient)
admin.site.register(RecipeIngredient)
admin.site.register(Follow)
admin.site.register(Favourites)
admin.site.register(SoppingList)


class UserAdmin(admin.ModelAdmin):
    '''
    Класс описания настроек админ-зоны для модели Пользователь
    '''
    # Поля страницы списка объектов
    list_display = ()
    # Разрешение редактирование полей на странице списка объектов
    list_editable = ()
    # Разрешение поиска по полям
    search_fields = ()
    # Разрешение фильтрации по полям
    list_filter = ()
    # Переход к редактированию при клике на поле
    list_display_links = ()
    # Установка заначения вместо пустых
    empty_value_display = 'Не задано'


class RecipeAdmin(admin.ModelAdmin):
    '''
    Класс описания настроек админ-зоны для модели Рецепт
    '''
    # Поля страницы списка объектов
    list_display = ('author', 'title')
    # Разрешение редактирование полей на странице списка объектов
    list_editable = ()
    # Разрешение поиска по полям
    search_fields = ('author', 'title')
    # Разрешение фильтрации по полям
    list_filter = ()
    # Переход к редактированию при клике на поле
    list_display_links = ()
    # Установка заначения вместо пустых
    empty_value_display = 'Не задано'


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


# Регистрируем кастомное представление админ-зоны для моделей
# admin.site.register(User, UserAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
