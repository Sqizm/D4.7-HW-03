from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
# from django.core.cache import cache


# Модель 'Пост'
class News(models.Model):
    # Поле - название новости/статьи, имеет уникальность.
    name = models.CharField(max_length=128, unique=True)

    # Поле - текст новости/статьи
    description = models.TextField()

    # Поле - автоматическая дата и время создания.
    dateCreate = models.DateTimeField(auto_now_add=True)

    # Поле категории будет ссылаться на модель категории
    category = models.ForeignKey(
        to='Category',
        on_delete=models.CASCADE,
        related_name='news',  # все новости/статьи в категории будут доступны через поле news
    )

    # Промежуточное поле связи многие ко многим
    postCategory = models.ManyToManyField('Category', through='PostCategory', related_name='news_post_categories')

    # Поле жанра новости/статьи
    genre = models.CharField(max_length=24)

    # Метод, выводит заголовок и текст новости/статьи.
    def __str__(self):
        return f'{self.name.title()}: {self.description[:20]} Дата публикации: {self.dateCreate}'

    def get_absolute_url(self):
        return reverse('onlynews', args=[str(self.id)])

    # def save(self, *args, **kwargs):
    #     if self.category.name == 'Статья':
    #         cache_key = f'onlynews_{self.id}'
    #         previous_article_id = cache.get(cache_key)
    #         if previous_article_id is None or self.id != previous_article_id:
    #             cache.set(cache_key, self.id, timeout=None)
    #     super(News, self).save(*args, **kwargs)


# Модель 'Пост Категория'
class PostCategory(models.Model):
    postThrough = models.ForeignKey('News', on_delete=models.CASCADE)
    categoryThrough = models.ForeignKey('Category', on_delete=models.CASCADE)


# Модель 'Категория'
class Category(models.Model):
    # Поле - название категории, имеет уникальность.
    name = models.CharField(max_length=24, unique=True)

    # Метод, выводит название категории.
    def __str__(self):
        return self.name.title()


# Модель 'Подписок' для хранения подписок пользователей
class Subscriber(models.Model):
    # Поле пользователя
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )

    # Поле категория для подписок пользователя
    category = models.ForeignKey(
        to='Category',
        on_delete=models.CASCADE,
        related_name='subscribers',
    )

    def __str__(self):
        return f'{self.user.username} - {self.category.name}'
