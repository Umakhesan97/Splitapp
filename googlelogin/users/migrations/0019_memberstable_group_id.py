# Generated by Django 5.0.2 on 2024-02-26 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_memberstable_invitation_accepted'),
    ]

    operations = [
        migrations.AddField(
            model_name='memberstable',
            name='group_id',
            field=models.IntegerField(default=False),
        ),
    ]
