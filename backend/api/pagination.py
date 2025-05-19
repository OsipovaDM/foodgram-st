from rest_framework.pagination import PageNumberPagination


class CatsPagination(PageNumberPagination):
    """
    Кастомный пагинатор для API, позволяющий клиенту указывать размер страницы.

    Наследуется от стандартного PageNumberPagination DRF.
    Добавляет возможность динамического изменения размера
    страницы через параметр запроса.

    Attributes:
        page_size_query_param (str): Имя параметра запроса
        для указания размера страницы. По умолчанию 'limit'.
    """
    page_size_query_param = 'limit'
