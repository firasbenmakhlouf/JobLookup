# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-27 10:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annonce', '0005_offer_created_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cv',
            name='user',
        ),
        migrations.AddField(
            model_name='user',
            name='cv',
            field=models.FileField(default=1, upload_to='cv/'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='CV',
        ),
    ]
