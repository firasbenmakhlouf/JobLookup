# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-17 18:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annonce', '0009_auto_20160917_1303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='cv',
            field=models.FileField(upload_to='/media/cv/'),
        ),
    ]
