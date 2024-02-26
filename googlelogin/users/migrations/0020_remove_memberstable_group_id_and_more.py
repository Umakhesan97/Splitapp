# Generated by Django 5.0.2 on 2024-02-26 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_memberstable_group_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='memberstable',
            name='group_id',
        ),
        migrations.RemoveField(
            model_name='memberstable',
            name='invitation_accepted',
        ),
        migrations.AddField(
            model_name='groupmembers',
            name='invitation_accepted',
            field=models.BooleanField(default=False),
        ),
    ]
