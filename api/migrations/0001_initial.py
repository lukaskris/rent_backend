# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-01-08 11:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('click', models.IntegerField()),
                ('expired_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('active', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='AdsBundle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='AdsOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('bundle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.AdsBundle')),
            ],
        ),
        migrations.CreateModel(
            name='Employees',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('phone', models.TextField()),
                ('email', models.TextField()),
                ('image_url', models.FileField(default='', upload_to='images/employees/')),
            ],
        ),
        migrations.CreateModel(
            name='Features',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('status', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Employees')),
            ],
        ),
        migrations.CreateModel(
            name='OrderDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('feature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Features')),
            ],
        ),
        migrations.CreateModel(
            name='OrderHeader',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('invoice_ref_number', models.TextField()),
                ('grand_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('expired_date', models.DateTimeField()),
                ('payment_date', models.DateTimeField()),
                ('check_in_time', models.DateTimeField()),
                ('check_out_time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='OrderStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.BooleanField()),
                ('attachments', models.FileField(upload_to='images/products/')),
                ('contact_person_name', models.CharField(max_length=200)),
                ('contact_person_phone', models.CharField(max_length=200)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Employees')),
            ],
        ),
        migrations.CreateModel(
            name='ProductsDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent_id', models.CharField(max_length=200)),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('type_selling', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Features')),
            ],
        ),
        migrations.CreateModel(
            name='ProductsDetailFeatures',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('features', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Features')),
                ('product_detail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.ProductsDetail')),
            ],
        ),
        migrations.CreateModel(
            name='TypeSelling',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=200)),
                ('password', models.CharField(max_length=200)),
                ('email', models.CharField(max_length=200)),
                ('name', models.TextField()),
                ('phone', models.TextField()),
                ('image_url', models.FileField(default='', upload_to='images/users/')),
                ('token', models.CharField(max_length=200)),
                ('status', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='orderheader',
            name='order_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.OrderStatus'),
        ),
        migrations.AddField(
            model_name='orderheader',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Products'),
        ),
        migrations.AddField(
            model_name='orderheader',
            name='type_selling',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.TypeSelling'),
        ),
        migrations.AddField(
            model_name='orderheader',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Users'),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='order_header',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.OrderHeader'),
        ),
        migrations.AddField(
            model_name='ad',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Products'),
        ),
    ]
