# Generated by Django 2.2.19 on 2022-05-23 18:37

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='cart',
            field=models.ManyToManyField(related_name='in_carts_of_users', to='recipes.Recipe', verbose_name='Список покупок'),
        ),
        migrations.AlterField(
            model_name='user',
            name='favorites',
            field=models.ManyToManyField(related_name='in_favorites_of_users', to='recipes.Recipe', verbose_name='Избранное'),
        ),
        migrations.AlterField(
            model_name='user',
            name='subscriptions',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Подписчики'),
        ),
    ]
