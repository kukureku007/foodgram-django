from django.contrib import admin

from .models import Ingredient, Tag, Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    pass
    # list_display = (
    #     'pk',
    #     'text',
    #     'pub_date',
    #     'author',
    #     'group',
    #     'image',
    # )
    # search_fields = ('text',)
    # list_filter = ('pub_date',)
    # empty_value_display = '-пусто-'
    # list_editable = ('group',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass
