# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-17 19:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annonce', '0012_auto_20160917_1856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='cv',
            field=models.FileField(blank=True, null=True, upload_to=b''),
        ),
    ]