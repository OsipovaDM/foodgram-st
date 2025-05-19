from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель пользователя, расширяющая стандартную AbstractUser.

    Добавляет:
    - Обязательное уникальное email-поле в качестве идентификатора
    - Поле для аватара пользователя с дефолтным значением

    Attributes:
        email (EmailField): Уникальный email пользователя (для входа)
        avatar (ImageField): Аватар с путем загрузки и дефолтным значением
        USERNAME_FIELD: Поле, используемое для аутентификации (email)
        REQUIRED_FIELDS: Обязательные поля при создании пользователя
    """
    email = models.EmailField(
        'Email адрес',
        unique=True,
        max_length=254,
        help_text='Обязательное поле. Максимум 254 символа.'
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='avatars/',
        default='avatars/default_avatar.png',
        help_text='Изображение профиля пользователя'
    )

    # Использование email вместо username для аутентификации
    USERNAME_FIELD = 'email'
    # Дополнительные обязательные поля
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']

    def __str__(self):
        """
        Строковое представление пользователя.

        Returns:
            str: Имя пользователя или email, если имя не указано
        """
        return self.first_name or self.email
