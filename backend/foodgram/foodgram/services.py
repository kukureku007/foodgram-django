import csv

from recipes.models import (
    Ingredient,
    Tag, Recipe, Ingredients_in_recipes
)
from django.contrib.auth import get_user_model

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
            eval(f'obj.{related_name}.add(topping)')


def delete_user_db():
    print('THIS WILL REPLACE ALL YOUR DATA FROM DB BY DEMO')
    if input('Do You Want To Continue? [y/n]') != 'y':
        return
    User.objects.all().delete()
    Tag.objects.all().delete()
    Recipe.objects.all().delete()
    Ingredient.objects.all().delete()
    Ingredients_in_recipes.objects.all().delete()
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
        Ingredients_in_recipes,
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
