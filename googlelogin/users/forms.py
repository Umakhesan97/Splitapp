# forms.py
from django import forms
from .models import ExpenseTable

class GroupCreationForm(forms.Form):
    group_name = forms.CharField(max_length=255, help_text="Describe your group name")
    initial_members = forms.CharField(help_text="Enter emails or usernames separated by commas |  e.g. user1@email.com, user2, username3")
    description = forms.CharField(max_length=300, help_text="Describe your Group Description")

class UpdateCreatedForm(forms.Form):
    total_amount = forms.IntegerField(min_value=0, help_text="Enter Amount for current expense")
    date = forms.CharField(max_length=10, help_text="DD/MM/YYYY")
    description = forms.CharField(max_length=100)
    expense_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
