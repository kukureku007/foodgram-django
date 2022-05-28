from rest_framework import serializers
from djoser.serializers import (UserCreateSerializer
                                as DjoserUserCreateSerializer)

from rest_framework.exceptions import ValidationError
# from django.shortcuts import get_object_or_404
# from django.core.exceptions import


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
    id = serializers.IntegerField(
        source='ingredient.id',
        read_only=False
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsInRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')


# patch
# del
class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = serializers.SerializerMethodField(read_only=False)
    # ingredients = IngredientsInRecipesSerializer(many=True, read_only=False)
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
        '''
        Валидируем ингридиенты с количеством
        на выходе список кортежей типа (Ingredient_object, amount)
        '''
        ingredients_already_checked = set()

        for _ in range(len(ingregients_with_amount)):
            ing = ingregients_with_amount.pop(0)

            serializer = IngredientsInRecipesSerializer(data=ing)
            if not serializer.is_valid():
                raise ValidationError({'ingredients': 'Проверьте ингредиенты'})

            ingredient_id = ing['id']
            amount = ing['amount']

            if ingredient_id in ingredients_already_checked:
                raise ValidationError({
                    'ingredients': f'Вы несколько раз добавили '
                                   f'ингредиент с id={ingredient_id}'
                })

            try:
                ingredient = Ingredient.objects.get(pk=ingredient_id)
            except Ingredient.DoesNotExist:
                raise ValidationError({
                    'ingredients': f'Ингредиента id={ingredient_id} '
                                   f'не существует'
                })

            ingredients_already_checked.add(ingredient_id)
            ingregients_with_amount.append((ingredient, amount))

        return ingregients_with_amount

    def run_validation(self, data):
        data['tags'] = self.validate_tags(data['tags'])
        data['ingredients'] = self.validate_ingredients(data['ingredients'])

        return super().run_validation(data)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingregients_with_amount = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.add(*tags)

        for ingredient in ingregients_with_amount:
            recipe.add_ingredient_with_amount(*ingredient)

        return recipe

# список покупок избранное подписки
