from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import SimpleRouter

from .views import RecipeViewSet, IngredientViewSet, CustomUserViewSet


# Инициализация простого роутера для автоматической генерации URL-путей
router = SimpleRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    # Аутентификация через Djoser (токены)
    path('auth/', include('djoser.urls.authtoken')),

    # Основные API endpoints через роутер
    path('', include(router.urls)),

    # OpenAPI schema generation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI документация
    path(
        'docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
]
