from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Название', max_length=200)
    measurement_unit = models.CharField(
        verbose_name='Единица измерения', max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(verbose_name='Название', max_length=200)
    color = models.CharField(verbose_name='Цвет', max_length=200, null=True)
    slug = models.SlugField(verbose_name='Slug', unique=True, null=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='in_recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='IngredientsInRecipes',
        related_name='in_recipes'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    cooking_time = models.IntegerField(verbose_name='Время готовки (мин.)')
    text = models.TextField(verbose_name='Описание')
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/',
        blank=True,
        null=True
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    def add_ingredient_with_amount(self, ingredient, amount):
        self.ingredients.add(ingredient, through_defaults={'amount': amount})

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientsInRecipes(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        validators=(MaxValueValidator(10000),)
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='ingredient_must_be_unique_in_recipe'
            ),
        )

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'
