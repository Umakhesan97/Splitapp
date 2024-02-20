from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from .forms import GroupCreationForm, UpdateCreatedForm
from .models import Group, GroupMembers, ExpenseTable, membersTable
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.models import User
from django.db import transaction


# Create your views here.

def login(request):
    return render(request, 'login.html')

@login_required
def home(request):
    # groups = Group.objects.all()
    user = request.user
    user_mail_id = user.email
    user_name = str(user)
    owned_groups = Group.objects.filter(owner=user)
    member_groups = Group.objects.filter(group_members__name__mail_id=user_mail_id)
    groups = (owned_groups | member_groups).distinct()

    table = membersTable.objects.filter(mail_id=user_mail_id).first()
    if table:
        table.user_name = user_name
        table.save()
    else:
        membersTable.objects.create(mail_id=user_mail_id, user_name=user_name)

    return render(request, 'home.html', {'groups': groups, 'user_mail_id': user_mail_id, 'user_name': user_name})


def user_logout(request):
    auth_logout(request)
    return redirect('login')

# def create_group(request):
#     form = GroupCreationForm()

#     if request.method == 'POST':
#         form = GroupCreationForm(request.POST)

#         if form.is_valid():
#             group_name = form.cleaned_data['group_name']
#             description = form.cleaned_data['description']
#             initial_members = form.cleaned_data['add_members'].split(',')

#             group = Group.objects.create(group_name=group_name, owner=request.user, description=description)

#             with transaction.atomic():
#                 for member_email in initial_members:
#                     user_name = member_email.split('@')[0]

#                     # Check if the email already exists in membersTable
#                     member_instance, created = membersTable.objects.get_or_create(
#                         mail_id=member_email,
#                         defaults={'user_name': user_name}
#                     )

#                     # Check if the member is not already part of the group
#                     if not GroupMembers.objects.filter(name=member_instance, group=group).exists():
#                         group_member = GroupMembers.objects.create(name=member_instance, group=group)
#                         group_member.save()

#             return redirect('home')  # Moved the redirect outside the loop

#     return render(request, 'create_group.html', {'form': form})

def create_group(request):
    form = GroupCreationForm()

    if request.method == 'POST':
        form = GroupCreationForm(request.POST)

        if form.is_valid():
            group_name = form.cleaned_data['group_name']
            description = form.cleaned_data['description']
            initial_members = form.cleaned_data['add_members'].split(',')

            group = Group.objects.create(group_name=group_name, owner=request.user, description=description)

            with transaction.atomic():
                for member_email in initial_members:
                    user_name = member_email.split('@')[0]

                    # Check if the email already exists in membersTable
                    member_instance, created = membersTable.objects.get_or_create(
                        mail_id=member_email,
                        defaults={'user_name': user_name}
                    )

                    # Check if the member is not already part of the group
                    if not GroupMembers.objects.filter(name=member_instance, group=group).exists():
                        group_member = GroupMembers.objects.create(name=member_instance, group=group)
                        group_member.save()

            return redirect('home')  # Moved the redirect outside the loop

    return render(request, 'create_group.html', {'form': form})

def group_detail(request, group_id):
    
    group = get_object_or_404(Group, id=group_id)
    latest_expense = ExpenseTable.objects.filter(group=group)
    user = request.user
    user_mail_id = user.email
    is_owner = request.user == group.owner
    is_member = Group.objects.filter(group_members__name__mail_id=user_mail_id)
    update_amount = UpdateCreatedForm()

    if request.method == 'POST' and 'delete' in request.POST:
        expense_id = request.POST.get('expense_id')
        expense = get_object_or_404(ExpenseTable, id=expense_id)
        total_amount_to_subtract = expense.amount
        group = Group.objects.get(id=group_id)
        group_members = GroupMembers.objects.filter(group=group)
        total_members = len(group_members)
        group.total_amount -= total_amount_to_subtract
        group.save()
        for member in group_members:
            member.share -= total_amount_to_subtract / total_members
            member.save()
        expense.delete()
        return redirect('group_detail', group_id=group.id)
        
    elif request.method=='POST' and 'edit' in request.POST:
        return render(request, 'edit_expense.html', group_id=group.id, expenseTable=UpdateCreatedForm())
    
    if request.method == 'POST':
        update_amount_input = UpdateCreatedForm(request.POST)
        if update_amount_input.is_valid():
            total_amount = update_amount_input.cleaned_data['total_amount']
            group = Group.objects.get(id=group_id)
            group.total_amount += total_amount
            group.save()
            group_members = GroupMembers.objects.filter(group=group)
            total_members = len(group_members)
            for member in group_members:
                member.share += total_amount / total_members
                member.save()
            expense_description = update_amount_input.cleaned_data['description']
            expense_date = update_amount_input.cleaned_data['date']
            expense_amount = update_amount_input.cleaned_data['total_amount']
            expense_list = ExpenseTable.objects.create(description=expense_description, date=expense_date, amount=expense_amount, group=group)
            expense_list.save()
            return redirect('group_detail', group_id=group.id)
    else:
        update_amount = UpdateCreatedForm()

    return render(request, 'group_detail.html', {'group': group, 'update_amount': update_amount, 'expenseTable':latest_expense, 'is_owner': is_owner, 'is_member':is_member, 'expenseTable': latest_expense,})


def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group_members = GroupMembers.objects.filter(group=group)
    initial_members = ', '.join([member.name.mail_id for member in group_members])

    if request.method == 'POST':
        form = GroupCreationForm(request.POST)
        if form.is_valid():
            group.group_name = form.cleaned_data['group_name']
            group.description = form.cleaned_data['description']
            new_members = form.cleaned_data['add_members'].split(',')
            existing_members = [member.mail_id for member in membersTable.objects.all()]
            for new_member_email in new_members:
                print('new_member_email : ', new_member_email)
                new_member_email = new_member_email.strip()
                print('new_member_email : ', new_member_email)
                if new_member_email in existing_members:
                    print(f"{new_member_email} already exists in the memberstable.")
                else:
                    print(f"{new_member_email} does not exist in the memberstable.")
                    user_name = new_member_email.split('@')[0]
                    table, created = membersTable.objects.get_or_create(
                        mail_id=new_member_email,
                        defaults={'user_name': user_name}
                    )
                    if created:
                        print(f"New member {new_member_email} added to membersTable.")
                    if not GroupMembers.objects.filter(name=table, group=group).exists():
                        group_member = GroupMembers.objects.create(name=table, group=group)
                        group_member.save()

            group.save()
            total_members = len(group_members)
            for member in group_members:
                member.share = group.total_amount / total_members
                member.save()

            return redirect('group_detail', group_id=group.id)

    else:
        form = GroupCreationForm(initial={
            'group_name': group.group_name,
            'add_members': initial_members,
            'description': group.description,
        })

    return render(request, 'edit_group.html', {'group': group, 'form': form})



def edit_expense(request, group_id):
    expense_id = request.POST.get('expense_id')
    group = get_object_or_404(Group, id=group_id)
    expense = get_object_or_404(ExpenseTable, group=group, id=expense_id)
    form = UpdateCreatedForm(initial={
            'total_amount': expense.amount,
            'date': expense.date,
            'description': expense.description,
            'expense_id': expense.id,
            })

    if request.method == 'POST' and 'update' in request.POST:
        update_data = UpdateCreatedForm(request.POST)
        expense = get_object_or_404(ExpenseTable, group=group, id=expense_id)

        if update_data.is_valid():
            with transaction.atomic():
                old_amount = expense.amount
                new_amount = update_data.cleaned_data['total_amount']
                amount_difference = new_amount - old_amount

                group.total_amount += amount_difference
                group.save()

                group_members = GroupMembers.objects.filter(group=group)
                total_members = len(group_members)
                for member in group_members:
                    member.share += amount_difference / total_members
                    member.save()

                expense.amount = new_amount
                expense.description = update_data.cleaned_data['description']
                expense.date = update_data.cleaned_data['date']
                expense.save()

        return redirect('group_detail', group_id=group_id)

    return render(request, 'edit_expense.html', {'form': form, 'group': group, 'group_id': group_id})