from rest_framework import viewsets
from rest_framework import filters
from recipes.models import Tag, Ingredient, Recipe
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.response import Response
from django.http import FileResponse

from django.contrib.auth import get_user_model
from djoser.serializers import SetPasswordSerializer
from rest_framework.decorators import action

from foodgram.services import make_cart_file
from .pagination import PageNumberWithLimitPagination
from .permissions import AuthorOnly
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          RecipeSerializer,
                          UserSerializer,
                          UserCreateSerializer,
                          RecipeSerializerLight,
                          UserSerializerWithRecipes)
from .mixins import CreateListRetrieveViewSet

User = get_user_model()


class UserViewSet(CreateListRetrieveViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberWithLimitPagination

    def get_queryset(self):
        if self.action == 'subscriptions':
            return self.request.user.subscriptions.all()
        return super().get_queryset()

    def get_object(self):
        if self.action == 'me':
            return self.request.user
        return super().get_object()

    def get_permissions(self):
        if self.action in ('me', 'set_password', 'subscriptions', 'subscribe'):
            return (IsAuthenticated(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action in ('subscriptions', 'subscribe'):
            return UserSerializerWithRecipes
        return super().get_serializer_class()

    @action(('get',), detail=False)
    def me(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @action(('post',), detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(('get',), detail=False)
    def subscriptions(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(('post', 'delete'), detail=False,
            url_path=r'(?P<pk>\d+)/subscribe')
    def subscribe(self, request, *args, **kwargs):
        user_object = self.get_object()
        user = self.request.user

        if user_object == user:
            return Response(
                {'errors': 'Вы не можете подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if self.request.method == 'POST':
            if user_object in user.subscriptions.all():
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.subscriptions.add(user_object)
            return Response(
                self.get_serializer(user_object).data,
                status=status.HTTP_201_CREATED
            )
        if not (user_object in user.subscriptions.all()):
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.subscriptions.remove(user_object)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
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


# dissallow patch !!
class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberWithLimitPagination
    # http_method_names: ('get', '')

    def get_permissions(self):
        if self.action in ('update', 'destroy'):
            return (AuthorOnly | IsAdminUser,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('favorite', 'shopping_cart'):
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

    @action(('post', 'delete'), detail=False,
            url_path=r'(?P<pk>\d+)/shopping_cart')
    def shopping_cart(self, request, *args, **kwargs):
        recipe = self.get_object()
        user = self.request.user

        if self.request.method == 'POST':
            if recipe in user.cart.all():
                return Response(
                    {'errors': 'Данный рецепт уже находится в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.cart.add(recipe)
            return Response(
                self.get_serializer(recipe).data,
                status=status.HTTP_201_CREATED
            )

        if not (recipe in user.cart.all()):
            return Response(
                {'errors': 'Данного рецепта нет в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.cart.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(('get',), detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        user = request.user

        if not user.cart.count():
            return Response(
                {'errors': 'Ваша корзина пуста.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        file_name = make_cart_file(user)

        return FileResponse(open(file_name, 'rb'), as_attachment=True)
