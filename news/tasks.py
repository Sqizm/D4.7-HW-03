from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from .models import News, Subscriber
from django.conf import settings
from datetime import timedelta
from django.utils import timezone


# Та же самая функция "которая уже задокументирована" в файле signals.py, запуск. она уже как задача Celery.
# Функция является простой, для выпол. в таске.
@shared_task
def notify_subscribers_task(new_news_id):
    new_news = News.objects.get(id=new_news_id)  # Извлекаю новую новость из переданного экземпляра new_news_id,
    category = new_news.category  # получаю категорию этой новости,
    subscribers = category.subscribers.all()  # и извлекаю всех подписчиков subscribers этой категории.
    for subscriber in subscribers:  # Прохожу по каждому подписчику и для каждого создаю письмо.
        user = subscriber.user
        subject = 'Новая новость в категории "Новость"'

        text_content = (f'Заголовок: {new_news.name}\n'
                        f'Жанр: {new_news.genre}\n\n'
                        f'Ссылка на прочтение новости: http://127.0.0.1:8000{new_news.get_absolute_url()}'
                        )

        html_content = (f'Заголовок: {new_news.name}<br>'
                        f'Жанр: {new_news.genre}<br>'
                        f'<a href="http://127.0.0.1:8000{new_news.get_absolute_url()}">'
                        f'Ссылка на прочтение новости</a>'
                        )
        # Отправляю каждому подписчику письмо.
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        # print("Письмо успешно отправилось на почту как задача от Celery!")


# Похожая функция из apscheduler, она отправ. еженедельную рассылку с последними новостями. Запус. как задача Celery.
@shared_task
def send_weekly_newsletter():
    # Определяю переменную, которая содер. дату на неделю назад от текущего момента.
    last_week = timezone.now() - timedelta(days=7)

    # Для каждого подписчика из модели Subscriber создаю элек. письмо
    for subscriber in Subscriber.objects.prefetch_related('user'):
        # Выполняю запрос к модели News, фильтрую новости, которые были созданы после, и относятся к категории 'Новость'
        new_news = News.objects.filter(dateCreate__gte=last_week, category__name='Новость').prefetch_related(
            'category')

        text_content = [f'Здравствуйте! Вышли новые новости, так как вы подписались на категорию "Новость"\n\n']
        html_content = [f'Здравствуйте! Вышли новые новости, так как вы подписались на категорию "Новость"<br><br>']

        # Добавляю информацию о каждой новости в элек. письмо
        for n in new_news:
            text_content.append(f'Заголовок: {n.name}; '
                                f'Жанр: {n.genre}; '
                                f'http://127.0.0.1:8000{n.get_absolute_url()}\n')
            html_content.append(f'Заголовок: {n.name}; '
                                f'Жанр: {n.genre}; '
                                f'<a href="http://127.0.0.1:8000{n.get_absolute_url()}">Новость</a><br>')

        if len(text_content) > 1:
            subject = f'Вышли новые новости'
            msg = EmailMultiAlternatives(subject,
                                         ''.join(text_content),
                                         settings.DEFAULT_FROM_EMAIL,
                                         [subscriber.user.email])
            msg.attach_alternative(''.join(html_content), "text/html")
            print("Уведомления со списком новостей успешно отправились!")
            msg.send()
