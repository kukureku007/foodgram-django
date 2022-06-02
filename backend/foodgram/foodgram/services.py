import csv
from math import ceil

from django.conf import settings
from django.contrib.auth import get_user_model
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

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


def import_model_from_csv_with_relative(klass, klass_related, file_path):
    with open(file_path) as file:
        reader = csv.reader(file)
        headers = next(reader)

        # Из заголовков забираем поле, связанное со связующей моделью
        relative_header = headers[-1]
        headers = headers[:-1]
        for row in reader:

            # Значение связующего поля. Например, значение username
            relative_value = row[-1]

            row = row[:-1]

            obj = klass()

            # Устанавливаем все несозависимые поля
            for count, attribute_name in enumerate(headers):
                setattr(obj, attribute_name, row[count])

            # Из заголовка получаем аттрибуты созависимой модели.
            # Например, для модели User - это: author-username
            attribute_name, relative_key = relative_header.split('-')

            # Устанавливаем связь между объектами.
            # Пример:
            # obj.author = klass_relative.objects.get(username=relative_value),
            # где author - attribute_name, username - relative_key
            setattr(obj, attribute_name, klass_related.objects.get(
                **{relative_key: relative_value})
            )
            obj.save()


def import_users_from_csv(file_path):
    with open(file_path) as file:
        reader = csv.reader(file)
        headers = next(reader)[3:]
        # username, password, email - для create_user()
        for row in reader:
            username, password, email = row[:3]
            row = row[3:]
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            User.objects.get(username=username).delete()

            for count, attribute_name in enumerate(headers):
                setattr(user, attribute_name, row[count])
            user.save()


def import_model_to_model(klass, klass_related, related_name, file_path):
    with open(file_path) as file:
        reader = csv.reader(file)
        header = next(reader)
        # получаем названия аттрибутов связанных классов
        klass_key, klass_rel_key = header

        for row in reader:
            # Получаем объект первого класса
            obj = klass.objects.get(
                **{klass_key: row[0]}
            )
            # Получаем объект второго класса
            topping = klass_related.objects.get(
                **{klass_rel_key: row[1]}
            )
            # Добавляем второй объект к первому
            klass_method = getattr(obj, f'{related_name}')
            klass_method.add(topping)


def import_ingredients(klass, klass_related, related_name, file_path):
    with open(file_path) as file:
        reader = csv.reader(file)
        header = next(reader)
        # получаем названия аттрибутов связанных классов
        _, klass_key, klass_rel_key = header

        for row in reader:
            # Получаем объект первого класса

            obj = klass.objects.get(
                **{klass_key: row[2]}
            )
            # Получаем объект второго класса
            topping = klass_related.objects.get(
                **{klass_rel_key: row[1]}
            )

            # Добавляем второй объект к первому
            klass_method = getattr(obj, f'{related_name}')
            klass_method.add(topping, through_defaults={'amount': row[0]})


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
    import_model_from_csv_with_relative(Recipe, User, 'demo-base/recipes.csv')
    import_model_to_model(Recipe, Tag, 'tags', 'demo-base/recipe_tags.csv')
    import_model_to_model(User, Recipe, 'favorites', 'demo-base/favorites.csv')
    import_model_to_model(User, Recipe, 'cart', 'demo-base/cart.csv')
    import_model_to_model(
        User, User, 'subscriptions',
        'demo-base/subscriptions.csv'
    )
    import_ingredients(
        Recipe,
        Ingredient,
        'ingredients',
        'demo-base/igredients_in_recipes.csv'
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

            line = (f'{ingredient.name}: {amount}'
                    f'({ingredient.measurement_unit})\n')
            file.write(line)

    return file_name


def make_cart_file_pdf(user: User):
    pdfmetrics.registerFont(TTFont(
        'FreeSans',
        f'{settings.STATIC_ROOT}/fonts/FreeSans.ttf'
    ))
    ingredients = ingredients_in_cart(user)
    file_name = f'{settings.CART_ROOT}/{user.username}-cart.pdf'

    my_canvas = canvas.Canvas(file_name, pagesize=A4)
    x = 100
    lines_per_list = 10
    total_count = len(ingredients.keys())
    page_num = int(ceil(total_count / lines_per_list))

    ings = iter(ingredients.keys())

    for page in range(page_num):
        my_canvas.setFont('FreeSans', 18)
        my_canvas.drawString(
            x, 800,
            f'Список покупок. Страница: {page + 1}'
        )
        my_canvas.drawString(
            x, 750,
            f'Пользователь: {user.username}'
        )
        y = 700

        for _ in range(lines_per_list):
            try:
                ingredient_id = next(ings)
                ingredient = Ingredient.objects.get(pk=ingredient_id)
                amount = ingredients[ingredient_id]
                line = (f'{ingredient.name}: {amount}'
                        f'({ingredient.measurement_unit})')
                y -= 50
                my_canvas.drawString(x, y, line)

            except StopIteration:
                break

        my_canvas.showPage()
    my_canvas.save()

    return file_name
