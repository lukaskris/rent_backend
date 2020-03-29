# Generated by Django 3.0.2 on 2020-02-06 08:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20200123_0414'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='products',
            name='attachments',
        ),
        migrations.CreateModel(
            name='ProductImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(upload_to='images/products/', verbose_name='Products')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.Products')),
            ],
        ),
    ]