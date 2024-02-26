from django.db import models
from django.contrib.auth.models import User

class membersTable(models.Model):
    user_name = models.CharField(max_length=50, null=False, default=None)
    mail_id = models.CharField(max_length=100, null=False, unique=True)

    def __str__(self):
        if self.user_name is None:
            return "<No username>"
        else:
            return self.user_name

class Group(models.Model):
    group_name = models.CharField(max_length=100, null=False, default=None)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_groups', null=False, default=None)
    total_amount = models.FloatField(default=0, null=False)
    description = models.CharField(max_length=300, null=True, default=None)

class GroupMembers(models.Model):
    name = models.ForeignKey('membersTable', on_delete=models.CASCADE, null=False, default=None)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name="group_members", null=False, default=None)
    join_date = models.DateTimeField(auto_now_add=True)
    share = models.FloatField(null='False', default=0)
    invitation_accepted = models.BooleanField(default=False)

class ExpenseTable(models.Model):
    description = models.CharField(max_length=100, null=False, default=None)
    date = models.CharField(max_length=10, null=False, default=0)
    amount = models.FloatField( null=False, default=0)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="expenses", null=False, default=None)
