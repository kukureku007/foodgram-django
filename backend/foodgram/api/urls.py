from django.urls import include, path
from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

app_name = 'api'
router_v1 = routers.DefaultRouter()

router_v1.register(
    r'(?P<version>v1)/tags',
    TagViewSet,
    basename='api-tags'
)

router_v1.register(
    r'(?P<version>v1)/ingredients',
    IngredientViewSet,
    basename='api-ingredients'
)

router_v1.register(
    r'(?P<version>v1)/recipes',
    RecipeViewSet,
    basename='api-recipes'
)

router_v1.register(
    r'(?P<version>v1)/users',
    UserViewSet,
    basename='api-users'
)


urlpatterns = [
    path('v1/auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls))
]
