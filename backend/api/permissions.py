from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):
    '''
    Разрешает все действия автору записи, иначе  только чтение
    '''

    # Определяет права на уровне запроса и пользователя
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    # Определяет права на уровне объекта
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user