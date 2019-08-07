# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-08-06 09:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0006_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='comment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='post.Comment'),
        ),
    ]