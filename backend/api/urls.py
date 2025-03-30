from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import SimpleRouter

from .views import (RecipeViewSet, IngredientViewSet)

router = SimpleRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include('djoser.urls')),  # Управление пользователями Django
    path('auth/', include('djoser.urls.authtoken')), # 
    path('', include(router.urls)),  # Добавление эндпоинтов, сформированных роутером
    path('schema/', SpectacularAPIView.as_view(), name='schema'),  # Динамическая спецификация
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # Динамическая спецификация
]

# Available endpoints

# http://127.0.0.1:8000/api/docs/

# api/users/ -- регистрация
# api/users/me -- получить/обновить пользователя
# api/users/resend_activation/
# api/users/set_password/
# api/users/reset_password/
# api/users/reset_password_confirm/
# api/users/set_username/
# api/users/reset_username/
# api/users/reset_username_confirm/
# api/auth/token/login/ (Token Based Authentication) -- получить токен
# api/auth/token/logout/ (Token Based Authentication) -- удалить токен
# api/auth/jwt/create/ (JSON Web Token Authentication) -- создать токен
# api/auth/jwt/refresh/ (JSON Web Token Authentication) -- получить новый токен по истечению срока
# api/auth/jwt/verify/ (JSON Web Token Authentication)
