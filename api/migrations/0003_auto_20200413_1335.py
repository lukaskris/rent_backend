# Generated by Django 3.0.2 on 2020-04-13 13:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20200413_1325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='apartment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='api.Apartment'),
        ),
    ]