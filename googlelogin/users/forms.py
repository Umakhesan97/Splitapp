# forms.py
from django import forms
from .models import ExpenseTable, membersTable
import re

class GroupCreationForm(forms.Form):
    group_name = forms.CharField(
        max_length=150,
        help_text="Describe your group name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 100%;'})
    )
    add_members = forms.CharField(
        max_length=1000,
        help_text="Add group members",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'style': 'width: 100%;'})
        )
    description = forms.CharField(
        max_length=150,
        help_text="Describe your Group Description",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'style': 'width: 100%;'})
    )

class UpdateCreatedForm(forms.Form):
    total_amount = forms.IntegerField(
        min_value=0,
        help_text="Enter Amount for current expense",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    date = forms.CharField(
        max_length=10,
        help_text="DD/MM/YYYY",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    expense_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False
    )

    def clean_date(self):
        date = self.cleaned_data['date']
        date_pattern = re.compile(r'^\d{2}/\d{2}/\d{4}$')
        if not date_pattern.match(date):
            raise forms.ValidationError('Invalid date format. Please use DD/MM/YYYY.')
        return date