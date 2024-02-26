from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from django.core.mail import EmailMultiAlternatives, mail_managers, mail_admins


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="Имя")
    last_name = forms.CharField(label="Фамилия")

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )


class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)

        # Добавляем новых пользователей в группу, только тех, кто зарег. с помощью станд. регис.
        common_users = Group.objects.get(name="common users")
        user.groups.add(common_users)

        # Отправляем письмо новому пользователю, о том, что успешно зарег.
        subject = 'Добро пожаловать в наш новостной портал!'
        text = f'{user.username}, вы успешно зарегистрировались на сайте!'
        html = (
            f'<b>{user.username}</b>, вы успешно зарегистрировались на '
            f'<a href="http://127.0.0.1:8000/products">сайте</a>!'
        )
        msg = EmailMultiAlternatives(
            subject=subject, body=text, from_email=None, to=[user.email]
        )
        msg.attach_alternative(html, "text/html")
        msg.send()

        # Отправляем письма менеджерам и админам, о том, что зарег. новый пользователь.
        sub = 'Новый пользователь!'
        m_mess = f'Пользователь {user.username} зарегистрировался на сайте.'
        mail_managers(subject=sub, message=m_mess)
        mail_admins(subject=sub, message=m_mess)
        return user
