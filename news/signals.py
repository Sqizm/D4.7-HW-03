from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import News
from django.conf import settings


# Метод с сигналом многие ко многим, для отправ. уведом. подписчикам
@receiver(m2m_changed, sender=News.postCategory.through)
def notify_subscribers(sender, instance, action, **kwargs):
    if action == "post_add":
        new_news = instance  # Извлекаю новую новость из переданного экземпляра instance,
        category = new_news.category  # получаю категорию этой новости,
        subscribers = category.subscribers.all()  # и извлекаю всех подписчиков subscribers этой категории.
        for subscriber in subscribers:  # Прохожу по каждому подписчику и для каждого создаю письмо.
            user = subscriber.user
            subject = 'Новая новость в категории "Новость"'

            text_content = (f'Заголовок: {new_news.name}\n'
                            f'Жанр: {new_news.genre}\n\n'
                            f'Ссылка на прочтение новости: http://127.0.0.1:8000{instance.get_absolute_url()}'
                            )

            html_content = (f'Заголовок: {instance.name}<br>'
                            f'Жанр: {new_news.genre}<br>'
                            f'<a href="http://127.0.0.1:8000{instance.get_absolute_url()}">'
                            f'Ссылка на прочтение новости</a>'
                            )
            # Отправляю каждому подписчику письмо.
            msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
