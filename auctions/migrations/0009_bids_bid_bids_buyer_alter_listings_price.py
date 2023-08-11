# Generated by Django 4.2.2 on 2023-07-03 10:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("auctions", "0008_comments_author_comments_listing_comments_message"),
    ]

    operations = [
        migrations.AddField(
            model_name="bids",
            name="bid",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="bids",
            name="buyer",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="buyer",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="listings",
            name="price",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="price",
                to="auctions.bids",
            ),
        ),
    ]