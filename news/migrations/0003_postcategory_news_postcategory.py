# Generated by Django 4.2.10 on 2024-02-24 16:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_subscriber'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categoryThrough', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='news.category')),
                ('postThrough', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='news.news')),
            ],
        ),
        migrations.AddField(
            model_name='news',
            name='postCategory',
            field=models.ManyToManyField(related_name='news_post_categories', through='news.PostCategory', to='news.category'),
        ),
    ]
