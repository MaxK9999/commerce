# Generated by Django 4.2.5 on 2023-10-05 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0020_bid_is_winner'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='closed_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
