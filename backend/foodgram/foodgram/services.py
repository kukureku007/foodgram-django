import csv

from django.conf import settings
from django.contrib.auth import get_user_model

from recipes.models import Ingredient, IngredientsInRecipes, Recipe, Tag

User = get_user_model()


def import_model_from_csv(klass, file_path):
    with open(file_path) as file:
        reader = csv.reader(file)
        headers = next(reader)
        for row in reader:
            obj = klass()
            for count, attribute_name in enumerate(headers):
                setattr(obj, attribute_name, row[count])
            obj.save()


def import_users_from_csv(file_path):
    with open(file_path) as file:
        reader = csv.reader(file)
        headers = next(reader)[4:]
        # id, username, password, email - для create_user()
        for row in reader:
            pk_, username, password, email = row[:4]
            row = row[4:]
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            user.pk = pk_
            User.objects.get(username=username).delete()

            for count, attribute_name in enumerate(headers):
                setattr(user, attribute_name, row[count])
            user.save()


def import_model_to_model(klass_root, klass, related_name, file_path):
    with open(file_path) as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            obj = klass_root.objects.get(pk=row[1])
            topping = klass.objects.get(pk=row[2])
            klass_method = getattr(obj, f'{related_name}')
            klass_method.add(topping)


def delete_user_db():
    print('THIS WILL REPLACE ALL YOUR DATA FROM DB BY DEMO')
    if input('Do You Want To Continue? [y/n]') != 'y':
        return
    User.objects.all().delete()
    Tag.objects.all().delete()
    Recipe.objects.all().delete()
    Ingredient.objects.all().delete()
    IngredientsInRecipes.objects.all().delete()
    # удаление связей m2m с авто таблицами
    Recipe.tags.through.objects.all().delete()
    User.favorites.through.objects.all().delete()
    User.cart.through.objects.all().delete()
    User.subscriptions.through.objects.all().delete()


def import_demo():
    import_users_from_csv('demo-base/users.csv')
    import_model_from_csv(Ingredient, 'demo-base/ingredients.csv')
    import_model_from_csv(Tag, 'demo-base/tags.csv')
    import_model_from_csv(Recipe, 'demo-base/recipes.csv')
    import_model_from_csv(
        IngredientsInRecipes,
        'demo-base/igredients_in_recipes.csv'
    )
    import_model_to_model(Recipe, Tag, 'tags', 'demo-base/recipe_tags.csv')
    import_model_to_model(User, Recipe, 'favorites', 'demo-base/favorites.csv')
    import_model_to_model(User, Recipe, 'cart', 'demo-base/cart.csv')
    import_model_to_model(
        User, User, 'subscriptions',
        'demo-base/subscriptions.csv'
    )


def import_demo_db_for_sure():
    delete_user_db()
    import_demo()


def ingredients_in_cart(user: User):
    """
    Перед запуском функции необходимо удостовериться, что
    в корзине есть хотя бы один рецепт.
    на выходе словарь 'ingredient_id' : 'amount'
    """

    result = {}
    ingredients_already_add = set()

    for recipe in user.cart.all():

        for item in recipe.ingredientsinrecipes_set.all():

            ingredient_id = item.ingredient.id
            amount = item.amount

            if ingredient_id in ingredients_already_add:
                result[ingredient_id] += amount
            else:
                result[ingredient_id] = amount

            ingredients_already_add.add(ingredient_id)

    return result


def make_cart_file(user: User):
    ingredients = ingredients_in_cart(user)
    file_name = f'{settings.CART_ROOT}/{user.username}-cart.txt'

    with open(file_name, 'w', encoding='utf-8') as file:
        for ingredient_id in ingredients.keys():
            ingredient = Ingredient.objects.get(pk=ingredient_id)
            amount = ingredients[ingredient_id]

            line = f'{ingredient.name}: {amount}'
            f'({ingredient.measurement_unit})\n'
            file.write(line)

    return file_name
