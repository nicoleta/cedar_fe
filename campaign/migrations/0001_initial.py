# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('campaign_type', models.IntegerField()),
                ('status', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('daily_cap', models.DecimalField(default=0, max_digits=14, decimal_places=6)),
                ('monthly_cap', models.DecimalField(default=0, max_digits=14, decimal_places=6)),
                ('total_cap', models.DecimalField(default=0, max_digits=14, decimal_places=6)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('bid_type', models.IntegerField()),
                ('bid', models.DecimalField(default=0, max_digits=14, decimal_places=6)),
                ('min_bid', models.DecimalField(default=0, max_digits=14, decimal_places=6)),
                ('daily_frequency_cap', models.IntegerField(default=0)),
                ('minutes_frequency', models.IntegerField(default=1440)),
                ('advertiser', models.ForeignKey(related_name='campaigns', to='account.Advertiser')),
            ],
        ),
        migrations.CreateModel(
            name='NativeAd',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('status', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('url', models.CharField(max_length=256)),
                ('title', models.CharField(max_length=128)),
                ('campaign', models.ForeignKey(related_name='ads', to='campaign.Campaign')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NativeAdDataAsset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('asset_type', models.IntegerField()),
                ('value', models.CharField(max_length=256)),
                ('ad', models.ForeignKey(related_name='data_assets', to='campaign.NativeAd')),
            ],
        ),
        migrations.CreateModel(
            name='NativeAdImageAsset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('asset_type', models.IntegerField()),
                ('filename', models.CharField(max_length=256)),
                ('original_width', models.IntegerField()),
                ('original_height', models.IntegerField()),
                ('ad', models.ForeignKey(related_name='image_assets', to='campaign.NativeAd')),
            ],
        ),
    ]
