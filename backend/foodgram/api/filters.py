import django_filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(field_name='author__id',)
    tags = django_filters.filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = django_filters.BooleanFilter()

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)
