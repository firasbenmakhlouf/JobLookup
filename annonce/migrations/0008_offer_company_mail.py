# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-17 12:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annonce', '0007_auto_20160917_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='company_mail',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
    ]
