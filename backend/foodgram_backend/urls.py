from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from api.views import redirect_short_link


urlpatterns = [
    # Административная панель Django
    path('admin/', admin.site.urls),

    # API endpoints (основные маршруты приложения)
    path('api/', include('api.urls')),

    # Обработка сокращенных ссылок
    path('s/<str:abridged>/', redirect_short_link, name='redirect-short-link'),
]

# В режиме разработки обслуживаем медиа-файлы через Django
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
