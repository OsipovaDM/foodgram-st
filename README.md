Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

- Шаги к успеху:
  - Сохранить спецификацию
  - Создать приложения:
    - Проект
    - БД
    - api
    - users
  - Создать базу данных:
    - Переопределить пользователя
    - Рецепт
    - Ингридиент
    - Состав
    - Подписки
    - Избранное
    - Список покупок
    - Добавить ограничения на допустимые значения полей
  - Админ-зона:
    - Русский язык
    - Регистрация приложений
    - Поиск/фильтрация по заданным полям
  - Авторизация пользователей
  - Сериализаторы
  - Представления
  - Статические страницы
  - 
  - requirements.txt

- Немного про команды:
  - Создание проекта:
    django-admin startproject название_проекта # Создать проект
    python manage.py startapp имя_приложения # Создание приложения в проекте
    INSTALLED_APPS = [ 'имя_приложения.apps.ИмяПриложенияConfig', ... ] # Регистрация приложения
    python manage.py runserver # Запуск проекта
  - База данных:
    python manage.py makemigrations # создание новых миграций на основе изменений, внесённых в модели
    python manage.py migrate # применение миграций
    python manage.py loaddata имя_файла.json # Загрузить данные из файла имя_файла.json в базу данных
  - Админка:
    python manage.py createsuperuser # Создание суперпользователя
  - Аунтефикация пользователей:
    pip install djoser djangorestframework-simplejwt==4.7.2
    from datetime import timedelta
    INSTALLED_APPS = ('django.contrib.auth', ... 'rest_framework', 'djoser',)
    REST_FRAMEWORK = { 'DEFAULT_PERMISSION_CLASSES': [ 'rest_framework.permissions.IsAuthenticated', ], 'DEFAULT_AUTHENTICATION_CLASSES': [ 'rest_framework_simplejwt.authentication.JWTAuthentication', ], }
    SIMPLE_JWT = { 'ACCESS_TOKEN_LIFETIME': timedelta(days=1), 'AUTH_HEADER_TYPES': ('Bearer',), } # Устанавливаем срок жизни токена
    мигрировать
    urlpatterns = [ ... path('auth/', include('djoser.urls')), path('auth/', include('djoser.urls.jwt')), ] 



- Тестовая база данных
    Как оператор данных, сгенерируй список из 
    10 записей в JSON формате с полями
    {
        "model": "auth.user",
        "fields": {
        "username": логин,
        "password": пароль
        }
    }
    15 уникальных записей в JSON формате с полями
    {
        "model": "cooking.recipe",
        "fields": {
        "author": чилсо от 1 до 5,
        "title": Название рецепта,
        "description": шаги приготовления рецепта,
        "cooking_time": количество минут целое число в двойных кавычках
        }
    }
    20 уникальных записей в JSON формате с полями
    {
        "model": "cooking.ingredient",
        "fields": {
        "title": Название ингридиента,
        "unit": единицы измерения
        }
    }
    30 уникальных записей в JSON формате с полями
    {
        "model": "cooking.recipeingredient",
        "fields": {
        "recipe": номер рецепта,
        "ingredient": номер ингредиента,
        "quantity": количество ингредиента
        }
    }
    20 уникальных записей в JSON формате с полями
    {
        "model": "cooking.follow",
        "fields": {
        "author": целое от 1 до 10,
        "user": целое от 1 до 10 != author
        }
    }
    20 уникальных записей в JSON формате с полями
    {
        "model": "cooking.favourites",
        "fields": {
        "recipe": целое от 1 до 15,
        "user": целое от 1 до 10
        }
    }
    30 уникальных записей в JSON формате с полями
    {
        "model": "cooking.soppinglist",
        "fields": {
        "recipe": числа от 1 до 15,
        "user": числа от 1 до 10
        }
    }
    



- НЕ реализовано:
  - Переопределить методы работы с пользователями
  - Сокращенные ссылки генерируются, но не являются действительными

