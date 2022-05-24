# from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import filters

from recipes.models import Tag, Ingredient, Recipe
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Выдача всех тегов, тегов по id.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Выдача всех ингредиентов, ингредиентов по id.
    Поиск по частичному вхождению в начале названия ингредиента.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_queryset(self):
        # print(self.request)
        # need parser to fav, cart etc
        # print(self.request.data)
        # print(self.request.query_params)
        # q = self.request.query_params
        # print(q.keys())
        # print(q.items())

        # for key in q:
            # print(q[key])

        # print(self.request.query_params.dict())

        return super().get_queryset()
