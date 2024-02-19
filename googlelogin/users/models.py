from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Group(models.Model):
    group_name = models.CharField(max_length=100, null='False')
    owner = models.ForeignKey(User, on_delete=models.CASCADE,  related_name='owned_groups', null='False')
    total_amount = models.FloatField(default=0)
    description = models.CharField(max_length=300, null='True')

class GroupMembers(models.Model):
    name = models.CharField(max_length=100, null='False')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_members", null='False')
    join_date = models.DateTimeField(auto_now_add=True)
    share = models.FloatField(null='False', default=0)

class ExpenseTable(models.Model):
    description = models.CharField(max_length=100, null ='False')
    date = models.CharField(max_length=10, null='False')
    amount = models.FloatField(null='False')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="expenses", null='False')
