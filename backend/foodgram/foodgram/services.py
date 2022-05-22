import csv

from recipes.models import (
    Ingredient,
    Tag, Recipe, Ingredients_in_recipes,
    Favorite, Shopping_cart
)
from django.contrib.auth import get_user_model

User = get_user_model()


# TODO change id to pk
def import_model_from_csv(klass, file_path):
    with open(file_path) as file:
        reader = csv.reader(file)
        headers = next(reader)
        for row in reader:
            obj = klass()
            for count, attribute_name in enumerate(headers):
                setattr(obj, attribute_name, row[count])
            obj.save()
    # return klass.objects.all()


def import_users_from_csv(file_path):
    with open(file_path) as file:
        reader = csv.reader(file)
        headers = next(reader)
        # id, username, password, email - для create_user()
        headers = headers[4:]
        print(headers)
        for row in reader:
            id_, username, password, email = row[:4]
            row = row[4:]
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            user.id = id_
            User.objects.get(username=username).delete()

            for count, attribute_name in enumerate(headers):
                setattr(user, attribute_name, row[count])
            user.save()


# def import_model_to_model(klass_intermediate, klass_root, klass, file_path):
    # with open(file_path) as file:
        # reader = csv.reader(file)
        # next(reader)
        # for row in reader:
            # obj = klass_root.objects.get(pk=row[1])
            # topping = klass.objects.get(pk=row[2])
            # eval(f'obj.{related_name}.add(topping)')

            # klass_root.RELATED.add(klass)


def import_relations_tags(file_path):
    with open(file_path) as file:
        reader = csv.reader(file)
        # считать "в пустоту" headers
        next(reader)
        for row in reader:
            recipe_id, tag_id = row[1], row[2]
            recipe = Recipe.objects.get(id=recipe_id)
            tag = Tag.objects.get(id=tag_id)
            recipe.tags.add(tag)


def import_subscriptions(file_path):
    with open(file_path) as file:
        reader = csv.reader(file)
        # считать "в пустоту" headers
        next(reader)
        for row in reader:
            from_user_pk, to_user_pk = row[1:]
            from_user = User.objects.get(pk=from_user_pk)
            to_user = User.objects.get(pk=to_user_pk)
            from_user.subscriptions.add(to_user)


def import_demo_db_for_sure():
    print('THIS WILL REPLACE ALL YOUR DATA FROM DB BY DEMO')
    if input('Do You Want To Continue? [y/n]') != 'y':
        return
    User.objects.all().delete()
    Tag.objects.all().delete()
    Recipe.objects.all().delete()
    Ingredient.objects.all().delete()
    Ingredients_in_recipes.objects.all().delete()
    # удаление связей между рецептами и тегами
    Recipe.tags.through.objects.all().delete()
    Favorite.objects.all().delete()
    Shopping_cart.objects.all().delete()
    User.subscriptions.through.objects.all().delete()

    import_users_from_csv('demo-base/users.csv')
    import_model_from_csv(Ingredient, 'demo-base/ingredients.csv')
    import_model_from_csv(Tag, 'demo-base/tags.csv')
    import_model_from_csv(Recipe, 'demo-base/recipes.csv')
    import_model_from_csv(
        Ingredients_in_recipes,
        'demo-base/igredients_in_recipes.csv'
    )
    import_relations_tags('demo-base/recipe_tags.csv')
    import_model_from_csv(Favorite, 'demo-base/favorites.csv')
    import_model_from_csv(Shopping_cart, 'demo-base/cart.csv')
    import_subscriptions('demo-base/subscriptions.csv')
