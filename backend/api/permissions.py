from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):
    """
    Кастомный класс разрешений, позволяющий:
    - Чтение (SAFE_METHODS) для всех пользователей
    - Полный доступ только автору объекта
    - Создание/изменение только аутентифицированным пользователям

    Наследуется от BasePermission DRF.
    Реализует двухуровневую проверку прав:
    1. На уровне запроса (has_permission)
    2. На уровне объекта (has_object_permission)
    """

    def has_permission(self, request, view):
        """
        Проверка прав на уровне запроса.

        Args:
            request: Запрос пользователя
            view: View, обрабатывающий запрос

        Returns:
            bool: True если:
                  - Метод в SAFE_METHODS (GET, HEAD, OPTIONS)
                  - Пользователь аутентифицирован
        """
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """
        Проверка прав на уровне конкретного объекта.

        Args:
            request: Запрос пользователя
            view: View, обрабатывающий запрос
            obj: Проверяемый объект

        Returns:
            bool: True если:
                  - Метод в SAFE_METHODS
                  - Пользователь является автором объекта
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
