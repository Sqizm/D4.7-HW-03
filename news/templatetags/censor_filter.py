import re   # Регулярные выражения
from django import template


register = template.Library()


@register.filter()
def censor(text):
    forbidden_words = ['производство']

    # Проверяем, чтобы фильтр цензурирования применялся только к переменным строкового типа.
    if not isinstance(text, str):
        # Если фильтр применяется не к строке, выкидываем исключение.
        raise TypeError('Переменная должна быть строкой')

    for word in forbidden_words:
        pattern = r'\b' + re.escape(word) + r'\b'
        replacement = word[0] + '*' * (len(word) - 1)
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)  # Заменяем совпавшые слова.
    return text
