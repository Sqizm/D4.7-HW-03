from django_filters import FilterSet, CharFilter, DateTimeFilter, ModelChoiceFilter
from django.forms import DateTimeInput
from .models import Category


class NewsFilter(FilterSet):
    # Выбрал поле iexact, оно ищет новости с точным совпадением по названию заголовка. Как было указано в ТЗ где,
    # надо было посмотреть как указан фильтр name на приложенном сайте. Можно выбрать поле icontains, оно ищет
    # по частичному совпадению.
    name = CharFilter(lookup_expr='iexact', label='Название заголовка')

    category = ModelChoiceFilter(
        field_name='category',
        queryset=Category.objects.all(),
        label='Тип поста',
        empty_label='Все посты'
    )

    genre = CharFilter(lookup_expr='iexact', label='Категория')

    dateCreate = DateTimeFilter(
        field_name='dateCreate',
        lookup_expr='gt',
        widget=DateTimeInput(
            format='%d-%m-%YT%H:%M',
            attrs={'type': 'datetime-local'},
        ),
        label='Дата'
    )
