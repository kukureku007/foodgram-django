import django_filters

from recipes.models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(field_name='author__id',)
    tags = django_filters.filters.ModelMultipleChoiceFilter(
        field_name='tags__name',
        to_field_name='name',
        queryset=Tag.objects.all(),
    )
    is_favorited = django_filters.BooleanFilter()

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)
