from django.contrib.auth.models import User
from django.db import models

from constants import SLUG_LENGTH, TEXT_LENGTH, TITLE_LENGTH


class PublishedModel(models.Model):
    """Абстрактная модель. Добавляет флаг is_published и created_at."""

    created_at = models.DateTimeField('Добавлено', auto_now_add=True)
    is_published = models.BooleanField(
        'Опубликовано', default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.')

    class Meta:
        abstract = True


class TitleModel(models.Model):
    """Абстрактная модель. Добавляет Title."""

    title = models.CharField('Заголовок', max_length=TITLE_LENGTH)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class AuthorModel(models.Model):
    """Абстрактная модель. Добавляет Author."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.author


class Category(PublishedModel, TitleModel):
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        max_length=SLUG_LENGTH,
        unique=True,
        help_text=('Идентификатор страницы для URL; '
                   'разрешены символы латиницы, '
                   'цифры, дефис и подчёркивание.'))

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(PublishedModel):
    name = models.CharField('Название места', max_length=TITLE_LENGTH)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedModel, TitleModel, AuthorModel):
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=('Если установить дату и время '
                   'в будущем — можно делать отложенные публикации.'))
    image = models.ImageField(
        'Изображение', upload_to='post_images', blank=True
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )

    class Meta:
        default_related_name = 'posts'
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    # @property
    # def comment_count(self):
    #     return self.comments.count()

    def __str__(self):
        return f'{self.author} {self.title[:15]}'


class Comment(AuthorModel):
    text = models.TextField('Текст комментария', max_length=TEXT_LENGTH,)
    post = models.ForeignKey(
        Post,
        verbose_name='Комментарии',
        on_delete=models.CASCADE,)
    created_at = models.DateTimeField('Создано', auto_now_add=True,)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self):
        return f'{self.post} {self.text[:15]}'
