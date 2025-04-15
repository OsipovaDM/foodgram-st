from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    '''
    Кастомная модель Пользователя
    '''
    email = models.EmailField('email address', unique=True, max_length=254)
    avatar = models.ImageField(
        'avatar', upload_to='avatars/', default='avatars/default_avatar.png')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        # Человекочитаемое имя
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    # Отображение при обращении к объекту
    def __str__(self):
        return self.first_name

