from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='in_recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='Ingredients_in_recipes',
        related_name='in_recipes'
    )
    name = models.CharField(max_length=200)
    cooking_time = models.IntegerField()
    text = models.TextField()
    # image = models.ImageField(
    #     upload_to=''
    #     blank=True
    # )


class Ingredients_in_recipes(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField()
