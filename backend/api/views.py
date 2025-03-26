from django.shortcuts import render
from djoser.serializers import UserSerializer

from cooking.models import User


# Не знаю, насколько мне это понадобится
# Возможно, придется добавлять сюда поля is_subscribed, avatar
class CustomUserSerializer(UserSerializer):
    '''
    Переопределен набор полей сериализатора для Пользователя
    '''
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')
