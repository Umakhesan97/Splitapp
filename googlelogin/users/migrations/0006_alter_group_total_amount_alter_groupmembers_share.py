# Generated by Django 5.0.2 on 2024-02-17 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_group_total_amount_groupmembers_share'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='total_amount',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='groupmembers',
            name='share',
            field=models.FloatField(default=0, null='False'),
        ),
    ]
