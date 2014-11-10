# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Details',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item_id', models.IntegerField()),
                ('name', models.CharField(max_length=100, null=True)),
                ('icon', models.CharField(max_length=150, null=True)),
                ('description', models.CharField(max_length=255, null=True)),
                ('type', models.CharField(max_length=50, null=True)),
                ('rarity', models.CharField(max_length=50, null=True)),
                ('level', models.IntegerField(null=True)),
                ('vendor_value', models.IntegerField(null=True)),
                ('default_skin', models.IntegerField(null=True)),
                ('flags', models.CharField(max_length=150, null=True)),
                ('game_types', models.CharField(max_length=100, null=True)),
                ('restrictions', models.CharField(max_length=150, null=True)),
                ('profit', models.IntegerField(null=True)),
                ('profit_percent', models.FloatField(null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('details', models.ForeignKey(to='items.Details', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Listing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField()),
                ('unit_price', models.IntegerField()),
                ('quantity', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MarketInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('buy_price', models.IntegerField(null=True)),
                ('buy_quantity', models.IntegerField(null=True)),
                ('sell_price', models.IntegerField(null=True)),
                ('sell_quantity', models.IntegerField(null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('buys', models.ManyToManyField(related_name='market_buys', to='items.Listing')),
                ('sells', models.ManyToManyField(related_name='market_sells', to='items.Listing')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='item',
            name='market',
            field=models.ForeignKey(to='items.MarketInfo', null=True),
            preserve_default=True,
        ),
    ]
