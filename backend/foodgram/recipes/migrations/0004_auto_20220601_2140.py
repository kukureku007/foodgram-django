# Generated by Django 2.2.19 on 2022-06-01 21:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20220601_2050'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='recipe',
            name='pub_date_must_be_greater_or_equal_than_today',
        ),
    ]