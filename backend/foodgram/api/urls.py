from django.urls import include, path
from rest_framework import routers

from .views import TagViewSet, IngredientViewSet, RecipeViewSet

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

urlpatterns = [
    path('', include(router.urls)),
]
