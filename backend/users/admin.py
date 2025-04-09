from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    '''
    Класс описания настроек админ-зоны для модели Пользователь
    '''
    # Поля отображаемые в карточке объекта
    fields = ('email', 'username', 'first_name', 'last_name', 'avatar',)
    # Поля страницы списка объектов
    list_display = ('first_name', 'email',)
    # Разрешение редактирование полей на странице списка объектов
    list_editable = ()
    # Разрешение поиска по полям
    search_fields = ('first_name', 'email',)
    # Разрешение фильтрации по полям
    list_filter = ()
    # Переход к редактированию при клике на поле
    list_display_links = ()
    # Установка заначения вместо пустых
    empty_value_display = 'Не задано'
