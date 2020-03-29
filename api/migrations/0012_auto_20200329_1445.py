# Generated by Django 3.0.2 on 2020-03-29 14:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20200328_0545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimages',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.Products'),
        ),
        migrations.AlterField(
            model_name='productsdetail',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.Products'),
        ),
    ]
