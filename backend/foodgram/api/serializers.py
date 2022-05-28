from rest_framework import serializers
from djoser.serializers import (UserCreateSerializer
                                as DjoserUserCreateSerializer)

from rest_framework.exceptions import ValidationError

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

    # rename obj to user
    # user to current user
    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj in user.subscriptions.all()
        return False


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


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = serializers.SerializerMethodField(read_only=False)
    # tags = TagSerializer(many=True, read_only=False)
    ingredients = serializers.SerializerMethodField(read_only=False)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_tags(self, recipe):
        return TagSerializer(recipe.tags.all(), many=True).data

    def get_ingredients(self, recipe):
        return IngredientsInRecipesSerializer(
            recipe.ingredientsinrecipes_set.all(), many=True
        ).data

    def get_is_favorited(self, recipe):
        user = self.context['request'].user
        if user.is_authenticated:
            return recipe in user.favorites.all()
        return False

    def get_is_in_shopping_cart(self, recipe):
        user = self.context['request'].user
        if user.is_authenticated:
            return recipe in user.cart.all()
        return False

    def validate_tags(self, tags_ids):
        if any(not isinstance(tag, int) for tag in tags_ids):
            raise ValidationError(
                {'tags': 'Проверьте список тегов. С ним что-то не так.'}
            )
        tags = Tag.objects.filter(pk__in=tags_ids)
        if not tags:
            raise ValidationError(
                {'tags': 'Список тегов пуст или таких тегов не существует.'}
            )
        return tags

    def validate_ingredients(self, ingregients_with_amount):
        # [{'id': 570, 'amount': 2000}, {'id': 1883, 'amount': 500}]
        print(ingregients_with_amount)

        return ingregients_with_amount

    # самый первый этап валидации
    def run_validation(self, data):
        data['tags'] = self.validate_tags(data['tags'])
        data['ingredients'] = self.validate_ingredients(data['ingredients'])

        return super().run_validation(data)

    def validate(self, attrs):
        # провалидировать пользователя
        # attrs['author'] = self.context['request'].user
        # валидация тегов, что это словарь
        # print(type(attrs['tags']))
        # print(attrs)
        # провалидировать все ингредиенты и кол-во
        # attrs['ingredients'] = self.initial_data['ingredients']
        return super().validate(attrs)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingregients_with_amount = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.add(*tags)


        for ingredient in ingregients_with_amount:
            self.ingredients.add(
                Ingredient.objects.get(pk=ingredient['id']),
                through_defaults={'amount': ingredient['amount']}
            )

        # recipe.add_ingredients_with_amount_by_id(ingregients_with_amount)

        return recipe

# список покупок избранное подписки
