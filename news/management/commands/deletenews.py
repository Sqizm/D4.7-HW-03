from django.core.management.base import BaseCommand, CommandError
from news.models import News


class Command(BaseCommand):
    help = 'Подсказка вашей команды'  # показывает подсказку при вводе "python manage.py <ваша команда> --help"

    # напоминать ли о миграциях. Если тру — то будет напоминание о том, что не сделаны все миграции (если такие есть)
    requires_migrations_checks = True

    def handle(self, *args, **options):
        self.stdout.readable()
        sh_genre = News.objects.filter(category=1).values_list('genre', flat=True)
        self.stdout.write(f'Все новости с жанрами:\n{sh_genre}\nВыбери жанр для удаления новостей.')
        answer = input('Введи жанр для удаления новостей: ')

        try:
            answer = answer.lower()
            self.stdout.write(f'Вы ввели жанр: {answer}')
            news_to_delete = News.objects.filter(genre=answer, category=1)
            if news_to_delete.exists():
                news_to_delete.delete()
                self.stdout.write(self.style.SUCCESS(f'Все новости с жанром {answer} успешно удалены.'))
            else:
                self.stdout.write(self.style.ERROR(f'Новостей с жанром {answer} не найдено, отмена команды.'))
        except News.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Жанр {answer} не найден в базе данных, отмена команды.'))
        # except News.MultipleObjectsReturned:
        #     self.stdout.write(self.style.ERROR(f'Обнаружено несколько новостей с жанром {answer}, отмена команды.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Произошла ошибка: {e}'))
