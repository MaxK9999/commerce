# Generated by Django 4.2.5 on 2023-10-04 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0017_remove_auction_watchlist_auction_watchlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='current_bid',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='bid',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
