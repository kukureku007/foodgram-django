# Generated by Django 2.2.19 on 2022-05-21 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20220521_0808'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Recipe_to_ingredient',
            new_name='Ingredients_in_recipes',
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=200),
        ),
    ]
