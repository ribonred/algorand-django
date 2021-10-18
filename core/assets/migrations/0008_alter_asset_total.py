# Generated by Django 3.2.8 on 2021-10-17 05:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0007_auto_20211017_0554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='total',
            field=models.BigIntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
