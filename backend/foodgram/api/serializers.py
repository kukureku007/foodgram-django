import base64
from uuid import uuid4

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer as DjoserUserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import Ingredient, IngredientsInRecipes, Recipe, Tag
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


class UserCreateSerializer(DjoserUserSerializer):
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
    # id = PrimaryKeyRelatedField(queryset=User.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsInRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ImageFieldBase64Input(serializers.ImageField):
    def to_internal_value(self, data):
        try:
            format, image_string = data.split(';base64,')
            file_format = format.split('/')[-1]
            file_name = f'{str(uuid4())}.{file_format}'
            return ContentFile(base64.b64decode(image_string), name=file_name)
        except ValueError:
            raise serializers.ValidationError(
                'Ошибка в переданном изображении.'
            )


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientsInRecipesSerializer(
        source='ingredientsinrecipes_set',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = ImageFieldBase64Input()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

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
        '''
        Валидируем теги
        на выходе список объектов тегов
        '''
        # проверка, что входной список, состоит только из int
        if not all(isinstance(tag, int) for tag in tags_ids):
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

        if not ingregients_with_amount:
            raise ValidationError(
                {'ingredients': 'Список ингредиентов пуст.'}
            )

        for _ in range(len(ingregients_with_amount)):
            ing = ingregients_with_amount.pop(0)

            serializer = IngredientsInRecipesSerializer(data=ing)
            if not serializer.is_valid():
                raise ValidationError({'ingredients': 'Проверьте ингредиенты'})

            ingredient_id = ing['id']
            amount = ing['amount']

            if ingredient_id in ingredients_already_checked:
                raise ValidationError({
                    'ingredients': [(f'Вы несколько раз добавили '
                                    f'ингредиент с id={ingredient_id}')]
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

        for ingregient_with_amount in ingregients_with_amount:
            recipe.add_ingredient_with_amount(*ingregient_with_amount)

        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingregients_with_amount = validated_data.pop('ingredients')

        super().update(recipe, validated_data)

        recipe.tags.clear()
        recipe.tags.add(*tags)

        recipe.ingredients.clear()
        for ingregient_with_amount in ingregients_with_amount:
            recipe.add_ingredient_with_amount(*ingregient_with_amount)

        return recipe


class RecipeSerializerLight(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')
        read_only_fields = ('id', 'name', 'cooking_time', 'image')


class UserSerializerWithRecipes(UserSerializer):
    recipes = RecipeSerializerLight(
        many=True
    )
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()
