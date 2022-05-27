from django.urls import include, path
from rest_framework import routers

# from djoser.views import TokenCreateView, TokenDestroyView
# from djoser.views import UserViewSet as DjoserUserViewSet

# from rest_framework.authtoken.views import obtain_auth_token


from .views import TagViewSet, IngredientViewSet, RecipeViewSet, UserViewSet
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

# ...
# url(r'^api-token-auth/', obtain_auth_token),


urlpatterns = [
    # path('', include('djoser.urls')),
    # path('users/', CustomUserViewSet.as_view()),
    # path('users/set_password/', DjoserUserViewSet.set_password),
    path('auth/', include('djoser.urls.authtoken')),
    # path('auth/token/login/', TokenCreateView.as_view()),
    # path('auth/token/logout/', TokenDestroyView.as_view()),
    # path('auth/', obtain_auth_token),
    # path('auth/', include('djoser.urls.jwt')),
    path('', include(router.urls))
]
