from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from .models import News, Category, Subscriber
from .filters import NewsFilter
from .forms import NewsForm
from .tasks import notify_subscribers_task


# Класс представления список всех новостей.
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


# Класс представления только одна новость.
class NewsDetail(DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельной новости
    model = News

    # Используем другой шаблон — onlynews.html
    template_name = 'onlynews.html'

    # Название объекта, в котором будет выбранна пользователем новость
    context_object_name = 'onlynews'


# Класс представления поиск
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


# Класс представления создать новость/статью
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
            news.save()  # Сохраняю обьект news для получения значения id
            news.postCategory.add(category)  # Добавляю категорию в поле многие ко многим. Для сигнала отправ. уведом.
            notify_subscribers_task(news.id)  # Вызываю задачу отправ. уведомл. теперь от Celery.
        elif self.request.path == '/articles/create/':
            category = Category.objects.get(name='Статья')
            news.category = category
        else:
            news.save()  # Просто сохраняю обьект news
        return super().form_valid(form)


# Класс представления редактировать новость/статью
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


# Класс представления удалить новость/статью
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


# Класс представления подписки
@login_required
@csrf_protect
def subscriptions(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Subscriber.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':
            Subscriber.objects.filter(
                user=request.user,
                category=category,
            ).delete()

    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(
            Subscriber.objects.filter(
                user=request.user,
                category=OuterRef('pk'),
            )
        )
    ).order_by('name')
    return render(
        request,
        'subscriptions.html',
        {'categories': categories_with_subscriptions},
    )
