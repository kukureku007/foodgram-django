from django.contrib.auth.models import AbstractUser
from django.db import models


# TODO можно подписаться на самого себя!!
class User(AbstractUser):
    subscriptions = models.ManyToManyField('self', symmetrical=False)
    favorites = models.ManyToManyField(
        'recipes.Recipe',
        related_name='in_favorites_of_users'
    )
    cart = models.ManyToManyField(
        'recipes.Recipe',
        related_name='in_carts_of_users'
    )
