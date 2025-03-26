from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    '''
    Кастомная модель Пользователя
    '''
    avatar = models.ImageField(
        'avatar', upload_to='avatars/', null=True, blank=True)

    class Meta:
        # Человекочитаемое имя
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    # Отображение при обращении к объекту
    def __str__(self):
        return self.username
