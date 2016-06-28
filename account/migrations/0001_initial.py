# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Advertiser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('status', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AuthLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=75, null=True)),
                ('ip_address', models.GenericIPAddressField(null=True)),
                ('date_used', models.DateTimeField(auto_now=True)),
                ('requested_url', models.CharField(max_length=512)),
                ('message', models.CharField(max_length=512, null=True)),
                ('authenticated', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address1', models.CharField(max_length=64, null=True)),
                ('address2', models.CharField(max_length=64, null=True)),
                ('city', models.CharField(max_length=32, null=True)),
                ('state', models.CharField(max_length=32, null=True)),
                ('country', models.CharField(max_length=2, null=True)),
                ('postal_code', models.CharField(max_length=16, null=True)),
                ('phone', models.CharField(max_length=32, null=True)),
                ('api_token', models.CharField(max_length=64, null=True)),
                ('stripe_id', models.CharField(max_length=128, null=True)),
                ('user', models.OneToOneField(related_name='user_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
