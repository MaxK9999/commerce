# Generated by Django 4.2.5 on 2023-10-02 09:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_auction_imgurl'),
    ]

    operations = [
        migrations.RenameField(
            model_name='auction',
            old_name='imgUrl',
            new_name='img',
        ),
    ]
