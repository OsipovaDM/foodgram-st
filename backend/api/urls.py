from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (RecipeViewSet,)

router = SimpleRouter()
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include('djoser.urls')),  # Управление пользователями Django
    path('auth/', include('djoser.urls.jwt')),  # Управление JWT-токенами
    path('', include(router.urls)),  # Добавление эндпоинтов, сформированных роутером
]

# Available endpoints
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
