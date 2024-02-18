from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from .models import News, Category
from .filters import NewsFilter
from .forms import NewsForm


# Класс список всех новостей.
class NewsList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = News

    # Поле, которое будет использоваться для сортировки объектов
    # В данном случае, новость сортируется в порядке от более свежой к самой старой.
    ordering = ['-dateCreate']

    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'news.html'

    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'news'

    # На одной странице будет не больше 10 новостей и видны номера лишь ближайших страниц,
    # а также возможность перехода к первой или последней странице.
    paginate_by = 10


# Класс только одна новость.
class NewsDetail(DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельной новости
    model = News

    # Используем другой шаблон — onlynews.html
    template_name = 'onlynews.html'

    # Название объекта, в котором будет выбранна пользователем новость
    context_object_name = 'onlynews'


# Класс поиск
class NewsSearch(ListView):
    model = News
    template_name = 'news_search.html'
    context_object_name = 'news_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = NewsFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


# Класс создать новость/статью
class NewsCreate(PermissionRequiredMixin, CreateView):
    raise_exception = True
    form_class = NewsForm
    model = News

    def get_permission_required(self):
        if self.request.path == '/news/create/':
            return ['news.add_news']
        elif self.request.path == '/articles/create/':
            return ['news.add_news']
        else:
            return super().get_permission_required

    def get_template_names(self):
        if self.request.path == '/news/create/':
            return ['news_create.html']
        elif self.request.path == '/articles/create/':
            return ['articles_create.html']
        else:
            return super().get_template_names()

    def form_valid(self, form):
        news = form.save(commit=False)
        if self.request.path == '/news/create/':
            category = Category.objects.get(name='Новость')
            news.category = category
        if self.request.path == '/articles/create/':
            category = Category.objects.get(name='Статья')
            news.category = category
        return super().form_valid(form)


# Класс редактировать новость/статью
class NewsUpdate(PermissionRequiredMixin, UpdateView):
    raise_exception = True
    form_class = NewsForm
    model = News

    def get_permission_required(self):
        if self.request.path == reverse('news_update', kwargs={'pk': self.kwargs['pk']}):
            return ['news.change_news']
        elif self.request.path == reverse('articles_update', kwargs={'pk': self.kwargs['pk']}):
            return ['news.change_news']
        else:
            return super().get_permission_required()

    def get_template_names(self):
        if self.request.path == reverse('news_update', kwargs={'pk': self.kwargs['pk']}):
            return ['news_update.html']
        elif self.request.path == reverse('articles_update', kwargs={'pk': self.kwargs['pk']}):
            return ['articles_update.html']
        else:
            return super().get_template_names()


# Класс удалить новость/статью
class NewsDelete(PermissionRequiredMixin, DeleteView):
    raise_exception = True
    model = News

    def get_permission_required(self):
        if self.request.path == reverse('news_delete', kwargs={'pk': self.kwargs['pk']}):
            return ['news.delete_news']
        elif self.request.path == reverse('articles_delete', kwargs={'pk': self.kwargs['pk']}):
            return ['news.delete_news']
        else:
            return super().get_permission_required()

    def get_template_names(self):
        if self.request.path == reverse('news_delete', kwargs={'pk': self.kwargs['pk']}):
            return ['news_delete.html']
        elif self.request.path == reverse('articles_delete', kwargs={'pk': self.kwargs['pk']}):
            return ['articles_delete.html']
        else:
            return super().get_template_names()

    success_url = reverse_lazy('news')
