from django import template

register = template.Library()


@register.filter()
def asterisk(text):
    forbidden_words = ['производство']
    words = text.split()
    result = []

    if isinstance(text, str):
        raise TypeError('Аргумент должен быть строкой (тип str)')

    for word in words:
        if word in forbidden_words:
            result.append(word[0] + '*' * (len(word)-2) + word[-1])
        else:
            result.append(word)
    return " ".join(result)
