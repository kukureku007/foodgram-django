from rest_framework import viewsets
from rest_framework import filters
from recipes.models import Tag, Ingredient, Recipe
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from djoser.serializers import SetPasswordSerializer
from rest_framework.decorators import action

from .serializers import (TagSerializer,
                          IngredientSerializer,
                          RecipeSerializer,
                          UserSerializer,
                          UserCreateSerializer,
                          RecipeSerializerLight)
from .mixins import CreateListRetrieveViewSet

User = get_user_model()


class UserViewSet(CreateListRetrieveViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def get_instance(self):
        return self.request.user

    def get_permissions(self):
        if self.action in ('me', 'set_password'):
            return (IsAuthenticated(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return super().get_serializer_class()

    @action(('get',), detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(('post',), detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ('^name',)


# check permissions on del
# check permissions on update
class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)

    def get_permissions(self):
        if self.action == 'favorite':
            return (IsAuthenticated(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'favorite':
            return RecipeSerializerLight
        return super().get_serializer_class()

    def get_queryset(self):
        # print(self.request.auth)
        # print(self.request.user)
        # print(self.request)
        # need parser to fav, cart etc
        # print(self.request.data)
        # print(self.request.query_params)
        # q = self.request.query_params
        # print(q.keys())
        # print(q.items())

        # for key in q:
        #     print(q[key])

        # print(self.request.query_params.dict())

        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            tags=self.request.data['tags'],
            ingredients=self.request.data['ingredients']
        )

    def perform_update(self, serializer):
        serializer.save(
            tags=self.request.data['tags'],
            ingredients=self.request.data['ingredients']
        )

    @action(('post', 'delete'), detail=False,
            url_path=r'(?P<pk>\d+)/favorite')
    def favorite(self, request, *args, **kwargs):
        recipe = self.get_object()
        user = self.request.user

        if self.request.method == 'POST':
            if recipe in user.favorites.all():
                return Response(
                    {'errors': 'Данный рецепт уже находится в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.favorites.add(recipe)
            return Response(
                self.get_serializer(recipe).data,
                status=status.HTTP_201_CREATED
            )

        if not (recipe in user.favorites.all()):
            return Response(
                {'errors': 'Данного рецепта нет в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.favorites.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)
