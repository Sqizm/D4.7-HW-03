from django import forms
from .models import News


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['name', 'genre', 'description']
        labels = {
            'name': 'Название заголовка',
            'genre': 'Категория',
            'description': 'Описание'
        }
