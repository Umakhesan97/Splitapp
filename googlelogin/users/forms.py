# forms.py
from django import forms

class GroupCreationForm(forms.Form):
    group_name = forms.CharField(max_length=255)
    initial_members = forms.CharField(help_text="Enter emails or usernames separated by commas")
    total_amount = forms.IntegerField(min_value=0, help_text="Enter a positive integer for total amount")