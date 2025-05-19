from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели пользователя.

    Настройки включают:
    - Отображаемые поля в формах редактирования
    - Отображение списка пользователей
    - Поиск и фильтрацию
    - Поведение элементов интерфейса

    Attributes:
        fields: Поля для отображения в форме редактирования
        list_display: Поля в списке объектов
        search_fields: Поля для поиска
        empty_value_display: Замещение пустых значений
    """
    # Основные поля для редактирования
    fields = (
        'email',
        'username',
        'first_name',
        'last_name',
        'avatar',
    )

    # Поля для отображения в списке пользователей
    list_display = (
        'first_name',
        'email',
    )

    # Поля, по которым доступен поиск
    search_fields = (
        'first_name',
        'email',
    )

    # Неизменяемые параметры
    list_editable = ()
    list_filter = ()
    list_display_links = ()
    empty_value_display = 'Не задано'
