# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-01-16 07:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20200114_1224'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('phone_number', models.CharField(blank=True, max_length=20)),
                ('email', models.TextField()),
                ('image_url', models.FileField(default='', upload_to='images/employees/')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
        ),
        migrations.AlterField(
            model_name='features',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.User'),
        ),
        migrations.AlterField(
            model_name='orderheader',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.User'),
        ),
        migrations.AlterField(
            model_name='products',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.User'),
        ),
        migrations.DeleteModel(
            name='Customers',
        ),
        migrations.DeleteModel(
            name='Employees',
        ),
    ]
