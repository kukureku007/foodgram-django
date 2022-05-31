from django.contrib import admin

from .models import Ingredient, IngredientsInRecipes, Recipe, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'author',
        'pub_date',
    )
    list_filter = ('name', 'author')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )


@admin.register(IngredientsInRecipes)
class IngredientsInRecipesAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )
    list_filter = ('recipe',)
