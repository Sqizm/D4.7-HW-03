import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from django.core.mail import EmailMultiAlternatives
from datetime import timedelta
from django.utils import timezone
from news.models import News, Subscriber

logger = logging.getLogger(__name__)


def my_job():
    # Определяю переменную, которая содер. дату на неделю назад от текущего момента.
    last_week = timezone.now() - timedelta(days=7)

    # Для каждого подписчика из модели Subscriber создаю элек. письмо
    for subscriber in Subscriber.objects.prefetch_related('user'):
        # Выполняю запрос к модели News, фильтрую статьи, которые были созданы после, и относятся к категории 'Статья'
        new_articles = News.objects.filter(dateCreate__gte=last_week, category__name='Статья').prefetch_related(
            'category')

        text_content = [f'Здравствуйте! Вышли новые статьи, так как вы подписались на категорию "Статья"\n\n']
        html_content = [f'Здравствуйте! Вышли новые статьи, так как вы подписались на категорию "Статья"<br><br>']

        # Добавляю информацию о каждой статьи в элек. письмо
        for article in new_articles:
            text_content.append(f'Заголовок: {article.name}; '
                                f'Жанр: {article.genre}; '
                                f'http://127.0.0.1:8000{article.get_absolute_url()}\n')
            html_content.append(f'Заголовок: {article.name}; '
                                f'Жанр: {article.genre}; '
                                f'<a href="http://127.0.0.1:8000{article.get_absolute_url()}">Статья</a><br>')

        if len(text_content) > 1:
            subject = f'Вышли новые статьи'
            msg = EmailMultiAlternatives(subject,
                                         ''.join(text_content),
                                         settings.DEFAULT_FROM_EMAIL,
                                         [subscriber.user.email])
            msg.attach_alternative(''.join(html_content), "text/html")
            msg.send()


# The `close_old_connections` decorator ensures that database connections,
# that have become unusable or are obsolete, are closed before and after your
# job has run. You should use it to wrap any jobs that you schedule that access
# the Django database in any way.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age`
    from the database.
    It helps to prevent the database from filling up with old historical
    records that are no longer useful.

    :param max_age: The maximum length of time to retain historical
                    job execution records. Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(
                day_of_week="fri", hour="18", minute="00"   # Отправка статей каждую пятницу в 18:00
            ),
            id="my_job",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача 'my_job'.")
        print("Добавлена задача 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена еженедельная задача: 'delete_old_job_executions'.")
        print("Добавлена еженедельная задача: 'delete_old_job_executions'.")

        try:
            logger.info("Запуск scheduler...")
            print("Запуск scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Остановка scheduler...")
            print("Остановка scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler успешно завершил работу!")
            print("Scheduler успешно завершил работу!")
