# Generated by Django 5.1.2 on 2024-11-03 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_sampling', '0002_alter_foodsampling_food_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foodsampling',
            name='food_quantity',
            field=models.FloatField(),
        ),
    ]
