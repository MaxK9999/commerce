# Generated by Django 4.2.5 on 2023-10-04 14:13

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0016_remove_auction_watchlist_auction_watchlist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auction',
            name='watchlist',
        ),
        migrations.AddField(
            model_name='auction',
            name='watchlist',
            field=models.ManyToManyField(blank=True, null=True, related_name='watchlist', to=settings.AUTH_USER_MODEL),
        ),
    ]
