# Generated by Django 5.0.2 on 2024-02-18 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_group_description_groupmembers_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupmembers',
            name='description',
            field=models.CharField(max_length=100, null='False'),
            preserve_default='False',
        ),
    ]
