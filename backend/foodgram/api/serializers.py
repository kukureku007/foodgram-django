from rest_framework import serializers

from recipes.models import Tag, Ingredient, Recipe, IngredientsInRecipes
from users.models import User


# "is_subscribed": false
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientsInRecipesSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsInRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')


# "is_favorited": true,
# "is_in_shopping_cart": true,
class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientsInRecipesSerializer(
        source='ingredientsinrecipes_set',
        many=True
    )

    class Meta:
        model = Recipe
        fields = '__all__'


# список покупок избранное подписки