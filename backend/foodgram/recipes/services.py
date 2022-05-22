import csv

from .models import Ingredient, Tag, Recipe, Ingredients_in_recipes
from django.contrib.auth import get_user_model

User = get_user_model()


# rc.import_model_from_csv(Ingredient, 'demo-base/ingredients.csv')
def import_model_from_csv(klass, file_path):
    with open(file_path) as file:
        reader = csv.reader(file)
        headers = next(reader)
        # print(headers)
        for row in reader:
            # print(row)
            obj = klass()
            for count, attribute_name in enumerate(headers):
                setattr(obj, attribute_name, row[count])
            obj.save()
            # print('-------------')
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
            # print(user.id)
            user.id = id_
            User.objects.get(username=username).delete()
            # user.save()

            for count, attribute_name in enumerate(headers):
                setattr(user, attribute_name, row[count])
            user.save()


def import_relations_tags(file_path):
    with open(file_path) as file:
        reader = csv.reader(file)
        # read headers
        next(reader)
        for row in reader:
            print(row)
            recipe_id, tag_id = row[1], row[2]
            recipe = Recipe.objects.get(id=recipe_id)
            tag = Tag.objects.get(id=tag_id)
            recipe.tags.add(tag)


def import_demo_db_for_sure():
    print['THIS WILL REPLACE ALL YOUR DATA FROM DB BY DEMO']
    if input('Do You Want To Continue? [y/n]') != 'y':
        return
    User.objects.all().delete()
    Tag.objects.all().delete()
    Recipe.objects.all().delete()
    Ingredient.objects.all().delete()
    Ingredients_in_recipes.objects.delete()
    # удаление связей тэго с рецептами
    # MyModel.relations.through.objects.all().delete()

    import_users_from_csv('demo-base/users.csv')
    import_model_from_csv(Ingredient, 'demo-base/ingredients.csv')
    import_model_from_csv(Tag, 'demo-base/tags.csv')
    import_model_from_csv(Recipe, 'demo-base/recipes.csv')
    import_model_from_csv(
        Ingredients_in_recipes,
        'demo-base/igredients_in_recipes.csv'
    )

    # tags
