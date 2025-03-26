from rest_framework.pagination import PageNumberPagination


# https://www.django-rest-framework.org/api-guide/pagination/
class CatsPagination(PageNumberPagination):
    '''
    Пагинатор. Возможность указание размера страницы в параметрах запроса
    '''
    page_size_query_param = 'limit'
