# Generated by Django 4.1.3 on 2022-11-29 13:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0004_purchase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='purchases', to='finance.product'),
        ),
    ]
