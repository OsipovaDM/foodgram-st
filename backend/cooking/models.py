from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

User = get_user_model()


class Recipe(models.Model):
    """
    Модель рецепта с основной информацией о кулинарном рецепте.

    Attributes:
        author (ForeignKey): Ссылка на автора рецепта
        name (CharField): Название рецепта
        image (ImageField): Изображение блюда
        text (TextField): Подробное описание рецепта
        cooking_time (PositiveIntegerField): Время приготовления в минутах
        ingredients (ManyToManyField): Связь с ингредиентами через Composition
        choosers (ManyToManyField): Пользователи, добавившие в избранное
        buyers (ManyToManyField): Пользователи, добавившие в список покупок
        created (DateTimeField): Дата и время создания
    """

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField('Название', max_length=256)
    image = models.ImageField('Картинка', upload_to='pictures/')
    text = models.TextField('Текстовое описание')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        help_text='В минутах'
    )
    ingredients = models.ManyToManyField(
        to="Ingredient",
        through="Composition",
        related_name="recipes"
    )
    choosers = models.ManyToManyField(
        to="users.User",
        through="Favourites",
        related_name="preferred",
    )
    buyers = models.ManyToManyField(
        to="users.User",
        through="ShoppingList",
        related_name="purchases",
    )
    created = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'name'),
                name='unique_author_recipe'
            ),
        )
        ordering = ['-created']
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} (автор: {self.author.username})'

    def get_absolute_url(self):
        """Возвращает абсолютный URL для доступа к деталям рецепта."""
        return reverse("recipes-detail", kwargs={"pk": self.pk})


class BaseModel(models.Model):
    """
    Абстрактная базовая модель для связей пользователь-рецепт.

    Attributes:
        recipe (ForeignKey): Ссылка на рецепт
        user (ForeignKey): Ссылка на пользователя
    """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='+'
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='+'
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe'
            ),
        )

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class Ingredient(models.Model):
    """
    Модель ингредиента с единицами измерения.

    Attributes:
        name (CharField): Название ингредиента (уникальное)
        measurement_unit (CharField): Единица измерения
    """

    name = models.CharField(
        'Название',
        max_length=128,
        unique=True
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=64
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Composition(models.Model):
    """
    Промежуточная модель для связи рецептов и
    ингредиентов с указанием количества.

    Attributes:
        recipe (ForeignKey): Ссылка на рецепт
        ingredient (ForeignKey): Ссылка на ингредиент
        amount (PositiveIntegerField): Количество ингредиента
    """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='components'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField('Количество')

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            ),
        )
        verbose_name = 'состав'
        verbose_name_plural = 'Составы'

    def __str__(self):
        return f'{self.recipe}: {self.ingredient} - {self.amount}'


class Follow(models.Model):
    """
    Модель подписки пользователей на авторов рецептов.

    Attributes:
        author (ForeignKey): Автор рецептов
        follower (ForeignKey): Подписчик
    """

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='followers'
    )
    follower = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'follower'),
                name='unique_author_follower'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('follower')),
                name='prevent_self_follow'
            ),
        )
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.follower} подписан на {self.author}'


class Favourites(BaseModel):
    """Модель для хранения избранных рецептов пользователей."""

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'


class ShoppingList(BaseModel):
    """Модель для хранения списков покупок пользователей."""

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'


class ShortLink(models.Model):
    """
    Модель для сокращенных ссылок на рецепты.

    Attributes:
        origin (URLField): Оригинальная ссылка
        abridged (CharField): Сокращенный код
    """

    origin = models.URLField('Оригинальная ссылка',
                             max_length=255, unique=True)
    abridged = models.CharField('Сокращенный код',
                                max_length=50, unique=True)

    class Meta:
        verbose_name = 'сокращенная ссылка'
        verbose_name_plural = 'Сокращенные ссылки'

    def __str__(self):
        return f'Ссылка {self.abridged}'
