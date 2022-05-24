from django.contrib.auth.models import AbstractUser
from django.db import models


# TODO можно подписаться на самого себя!!
class User(AbstractUser):
    subscriptions = models.ManyToManyField(
        'self', verbose_name='Подписчики', symmetrical=False
    )
    favorites = models.ManyToManyField(
        'recipes.Recipe', verbose_name='Избранное',
        related_name='in_favorites_of_users'
    )
    cart = models.ManyToManyField(
        'recipes.Recipe', verbose_name='Список покупок',
        related_name='in_carts_of_users'
    )
