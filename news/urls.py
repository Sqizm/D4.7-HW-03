from django.urls import path
# Импортируем созданное нами представление
from .views import NewsList, NewsDetail, NewsSearch, NewsCreate, NewsUpdate, NewsDelete
from django.views.decorators.cache import cache_page

urlpatterns = [
    # Вызываем метод as_view.
    # path('news/', cache_page(60)(NewsList.as_view()), name='news'),  # Кэширования главной страницы на 1 минуту.
    # # Вызываем метод as_view для страниц по id.
    # # Кэширования каждой страницы на 5 минут.
    # path('news/<int:pk>/', cache_page(300)(NewsDetail.as_view()), name='onlynews'),
    path('news/', NewsList.as_view(), name='news'),
    # Вызываем метод as_view для страниц по id.
    path('news/<int:pk>/', NewsDetail.as_view(), name='onlynews'),
    # Отдельная страница поиск.
    path('news/search/', NewsSearch.as_view(), name='news_search'),
    path('news/create/', NewsCreate.as_view(), name='news_create'),
    path('news/<int:pk>/edit/', NewsUpdate.as_view(), name='news_update'),
    path('news/<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),
    path('articles/create/', NewsCreate.as_view(), name='articles_create'),
    path('articles/<int:pk>/edit/', NewsUpdate.as_view(), name='articles_update'),
    path('articles/<int:pk>/delete/', NewsDelete.as_view(), name='articles_delete'),
]
