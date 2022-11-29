# Generated by Django 4.1.3 on 2022-11-29 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deposit',
            name='date_of_payment',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='product',
            name='alias_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
