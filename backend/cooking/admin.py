from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Recipe, Ingredient, Composition,
    Follow, Favourites, ShoppingList, ShortLink
)


# Регистрация простых моделей без кастомной админ-конфигурации
admin.site.register(Composition)
admin.site.register(Follow)
admin.site.register(Favourites)
admin.site.register(ShoppingList)
admin.site.register(ShortLink)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Админ-панель для управления рецептами.

    Attributes:
        fields: Поля для отображения в форме редактирования
        readonly_fields: Неизменяемые поля
        list_display: Поля в списке объектов
        search_fields: Поля для поиска
        list_display_links: Поля-ссылки для перехода к редактированию
        empty_value_display: Замещение пустых значений
    """
    fields = (
        'author', 'name', 'image', 'text',
        'cooking_time', 'favourites_count',
    )
    readonly_fields = ('favourites_count',)
    list_display = ('author', 'name')
    list_editable = ()
    search_fields = ('author__first_name', 'name')
    list_filter = ()
    list_display_links = ('name',)
    empty_value_display = 'Не задано'

    def favourites_count(self, obj):
        """
        Возвращает количество добавлений рецепта в избранное.

        Args:
            obj: Объект рецепта

        Returns:
            str: HTML-безопасная строка с количеством добавлений
        """
        result = Favourites.objects.filter(recipe=obj).count()
        return mark_safe(f'<b>{result}</b>')

    favourites_count.short_description = 'В избранном (раз)'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Админ-панель для управления ингредиентами.

    Attributes:
        list_display: Поля в списке объектов
        search_fields: Поля для поиска
        empty_value_display: Замещение пустых значений
    """
    list_display = ('name', 'measurement_unit')
    list_editable = ()
    search_fields = ('name',)
    list_filter = ()
    list_display_links = ()
    empty_value_display = 'Не задано'
