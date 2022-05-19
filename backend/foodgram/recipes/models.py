from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=10)
    slug = models.SlugField(unique=True)


# много доделок
class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(max_length=200)
    cooking_time = models.IntegerField()
    text = models.TextField()
    # image = models.ImageField(
    #     upload_to=''
    #     blank=True
    # )


# add related_name, заменить на many-to-many
# on_delete=models.SET_DEFAULT, установить дефолт в модели тега ??
class Recipe_to_tag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='with_tag'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='in_recipes'
    )


class Recipe_to_ingredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='consist_of_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='in_recipes'
    )
    amount = models.IntegerField()
