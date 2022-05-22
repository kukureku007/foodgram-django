from django.contrib.auth.models import AbstractUser
from django.db import models


# TODO можно подписаться на самого себя!!
class User(AbstractUser):
    subscriptions = models.ManyToManyField('self', symmetrical=False)
    # favorites = models.ManyToManyField(Recipe)
    # cart = models.ManyToManyField(Recipe)


# user one-to-one
# favorites
# cart
# User.user1to1.favorites.all()