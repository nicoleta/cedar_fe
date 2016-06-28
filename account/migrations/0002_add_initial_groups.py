# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models

from django.contrib.auth.models import Group


def add_initial_groups(apps, schema_editor):
    group, created = Group.objects.get_or_create(name='advertisers')   
    group, created = Group.objects.get_or_create(name='account_reps') 
    group, created = Group.objects.get_or_create(name='finance') 

class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_initial_groups),
    ]
