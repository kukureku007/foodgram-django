from rest_framework import serializers
from djoser.serializers import (UserCreateSerializer
                                as DjoserUserCreateSerializer)

from recipes.models import Tag, Ingredient, Recipe, IngredientsInRecipes
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return obj in user.subscriptions.all()


class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }


# валидация hex-кода тега
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientsInRecipesSerializer(serializers.ModelSerializer):
    id = serializers.StringRelatedField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsInRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')


# "is_favorited": true,
# "": is_in_shopping_carttrue,
class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = serializers.SerializerMethodField(read_only=False)
    ingredients = serializers.SerializerMethodField(read_only=False)

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_tags(self, obj):
        return TagSerializer(obj.tags.all(), many=True).data

    def get_ingredients(self, obj):
        return IngredientsInRecipesSerializer(
            obj.ingredientsinrecipes_set.all(), many=True
        ).data

    def validate(self, attrs):
        # attrs['author'] = self.context['request'].user
        # провалидировать пользователя
        # провалидировать все тэги
        attrs['tags'] = self.initial_data['tags']
        # провалидировать все ингредиенты и кол-во
        attrs['ingredients'] = self.initial_data['ingredients']
        return super().validate(attrs)

    def create(self, validated_data):
        # change to request.user or in validate
        user = User.objects.get(pk=1)

        tag_ids = validated_data.pop('tags')
        ingregients_amount = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(
            author=user,
            **validated_data
        )

        # добавление тегов
        for tag_id in tag_ids:
            recipe.tags.add(Tag.objects.get(pk=tag_id))

        # добавление ингредиентов
        for ingredient in ingregients_amount:
            recipe.ingredients.add(
                Ingredient.objects.get(pk=ingredient['id']),
                through_defaults={'amount': ingredient['amount']}
            )

        return recipe

# список покупок избранное подписки
