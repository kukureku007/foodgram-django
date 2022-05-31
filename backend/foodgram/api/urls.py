from django.urls import include, path
from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

# from djoser.views import TokenCreateView, TokenDestroyView
# from djoser.views import UserViewSet as DjoserUserViewSet

# from rest_framework.authtoken.views import obtain_auth_token


# UserViewSet

app_name = 'api'
router = routers.DefaultRouter()

router.register(
    r'tags',
    TagViewSet,
    basename='api-tags'
)

router.register(
    r'ingredients',
    IngredientViewSet,
    basename='api-ingredients'
)

router.register(
    r'recipes',
    RecipeViewSet,
    basename='api-recipes'
)

router.register(
    r'users',
    UserViewSet,
    basename='api-users'
)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
