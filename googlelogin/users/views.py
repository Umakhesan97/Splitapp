from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from .forms import GroupCreationForm
from .models import Group, GroupMembers
from django.db.models import Q
from django.contrib.auth.models import User


# Create your views here.

def login(request):
    return render(request, 'login.html')

@login_required
def home(request):
    groups = Group.objects.all()
    return render(request,'home.html', {'groups': groups})

def user_logout(request):
    auth_logout(request)
    return redirect('login')

def create_group(request):
    form = GroupCreationForm()
    if request.method == 'POST':
        form = GroupCreationForm(request.POST)
        if form.is_valid():
            group_name = form.cleaned_data['group_name']
            total_amount = form.cleaned_data['total_amount']
            group = Group.objects.create(group_name=group_name, owner=request.user, total_amount=total_amount)
            initial_members = form.cleaned_data['initial_members'].split(',')
            for member in initial_members:
                total_members = len(initial_members)
                share = total_amount/total_members
                group_member = GroupMembers.objects.create(name=member, group=group, share=share)
                group_member.save()
            return redirect('group_detail', group_id=group.id)
    return render(request, 'create_group.html', {'form': form})

def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    return render(request, 'group_detail.html',{'group': group})