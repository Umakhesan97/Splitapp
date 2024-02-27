from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from .forms import GroupCreationForm, UpdateCreatedForm
from .models import Group, GroupMembers, ExpenseTable, membersTable
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib import messages
from users.tasks import send_acceptance_email, send_amount_email
from celery.result import AsyncResult
from django.http import HttpResponseServerError
# Create your views here.

def login(request):
    return render(request, 'login.html')

@login_required
def home(request):
    try:
        user = request.user
        user_mail_id = user.email
        user_name = str(user)
        owned_groups = Group.objects.filter(owner=user)
        member_groups = Group.objects.filter(
            Q(group_members__name__mail_id=user_mail_id) & Q(group_members__invitation_accepted=1)
        )
        groups = (owned_groups | member_groups).distinct()

        table = membersTable.objects.filter(mail_id=user_mail_id).first()
        if table:
            table.user_name = user_name
            table.save()
        else:
            membersTable.objects.create(mail_id=user_mail_id, user_name=user_name)

        return render(request, 'home.html', {'groups': groups, 'user_mail_id': user_mail_id, 'user_name': user_name})
    except Exception as e:
        error_message = f"An error occurred: {e}"
        return render(request, 'error_page.html', {'error_message': error_message})

@login_required
def user_logout(request):
    auth_logout(request)
    return redirect('login')

# def send_acceptance_email(user_email, group_name, group_id):
#     subject = 'You have been added to {}'.format(group_name)
#     html_message = render_to_string('email_template.html', {'group_name': group_name, 'group_id': group_id})
#     message = 'Dear user, you have been added to the group "{}". Welcome!'.format(group_name)
#     from_email = 'testingsplitapp@gmail.com'
#     recipient_list = [user_email]

#     send_mail(subject, message, from_email, recipient_list, html_message=html_message, fail_silently=False)

# def send_amount_email(user_email, group_name, group_id, user_share, total_amount):
#     subject = 'Your '.format(group_name),' group have added expense. Total expense : '.format(total_amount)
#     html_message = render_to_string('update_amount_template.html', {'group_name': group_name, 'group_id': group_id, 'total_amount': total_amount, 'user_share': user_share})
#     message = 'Dear user, your share is '.format(user_share)
#     from_email = 'testingsplitapp@gmail.com'
#     recipient_list = [user_email]

#     send_mail(subject, message, from_email, recipient_list, html_message=html_message, fail_silently=False)

@login_required
def create_group(request):
    form = GroupCreationForm()
    try:
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
                        member_instance, created = membersTable.objects.get_or_create(
                            mail_id=member_email,
                            defaults={'user_name': user_name}
                        )
                        group_id = group.id
                        print("hello for celery")
                        print(member_email, group_name, group_id)
                        result = send_acceptance_email.apply_async(args=[member_email, group_name, group_id])
                        result_status = result.get()
                        if result_status == 'SUCCESS':
                            print("Email sent successfully")
                        else:
                            print(f"Task status: {result_status}")
                        print("AFTER send_acceptance_email")
                        if not GroupMembers.objects.filter(name=member_instance, group=group).exists():
                            group_member = GroupMembers.objects.create(name=member_instance, group=group)
                            group_member.save()
                messages.success(request, f'Group "{group_name}" created successfully!')
                return redirect('home')
    except Exception as e:
        error_message = f"An error occurred: {e}"
        messages.error(request, error_message)
    return render(request, 'create_group.html', {'form': form})

@login_required
def accept_invitation(request, group_id):
    try:
        members_table = membersTable.objects.get(mail_id=request.user.email)
        group_member = GroupMembers.objects.get(name=members_table, group_id=group_id)
        group_member.invitation_accepted = 1
        group_member.group_id = group_id
        group_member.save()
    except membersTable.DoesNotExist:
        pass
    return redirect('home')

@login_required
def decline_invitation(request, group_id):
    try:
        members_table = membersTable.objects.get(mail_id=request.user.email)
        group_member = GroupMembers.objects.get(name=members_table, group_id=group_id)
        group_member.invitation_accepted = 0
        group_member.group_id = group_id
        group_member.save()
    except membersTable.DoesNotExist:
        pass
    return redirect('home')

def group_detail(request, group_id):
    try:
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
            return render(request, 'edit_expense.html', {'group_id': group.id, 'expenseTable': UpdateCreatedForm()})
        
        if request.method == 'POST':
            update_amount_input = UpdateCreatedForm(request.POST)
            if update_amount_input.is_valid():
                total_amount = update_amount_input.cleaned_data['total_amount']
                group.total_amount += total_amount
                group.save()
                group_members = GroupMembers.objects.filter(group=group)
                total_members = len(group_members)
                for member in group_members:
                    member.share += total_amount / total_members
                    share = member.share
                    group_id= group_id
                    group_name = group.group_name
                    for member in group_members:
                        member_name_id = member.name_id
                        members_mail_id = membersTable.objects.get(id=member_name_id).mail_id
                        user_email=members_mail_id
                        group_name=group_name
                        group_id=group_id
                        user_share=share
                        send_amount_email.apply_async(args=[user_email, group_name, group_id, user_share, total_amount])
                        result = send_acceptance_email.apply_async(args=[member_email, group_name, group_id])
                        result_status = result.get()
                        if result_status == 'SUCCESS':
                            print("Email sent successfully")
                        else:
                            print(f"Task status: {result_status}")
                        print("AFTER send_amount_email")
                    member.save()
                expense_description = update_amount_input.cleaned_data['description']
                expense_date = update_amount_input.cleaned_data['date']
                expense_amount = update_amount_input.cleaned_data['total_amount']
                expense_list = ExpenseTable.objects.create(description=expense_description, date=expense_date, amount=expense_amount, group=group)
                expense_list.save()
                return redirect('group_detail', group_id=group.id)
        else:
            update_amount = UpdateCreatedForm()

        return render(request, 'group_detail.html', {'group': group, 'update_amount': update_amount, 'expenseTable': latest_expense, 'is_owner': is_owner, 'is_member': is_member, 'expenseTable': latest_expense})
    
    except Exception as e:
        error_message = f"An error occurred: {e}"
        return render(request, 'error_template.html', {'error_message': error_message})

def edit_group(request, group_id):
    try:
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
                    new_member_email = new_member_email.strip()
                    if new_member_email in existing_members:
                        print(f"{new_member_email} already exists in the memberstable.")
                    else:
                        print(f"{new_member_email} does not exist in the memberstable.")
                        user_name = new_member_email.split('@')[0]
                        table, created = membersTable.objects.get_or_create(
                            mail_id=new_member_email,
                            defaults={'user_name': user_name}
                        )
                        if not GroupMembers.objects.filter(name=table, group=group).exists():
                            group_member = GroupMembers.objects.create(name=table, group=group)
                            group_member.save()
                            send_acceptance_email.delay(user_email=new_member_email, group_name=group.group_name, group_id=group.id)

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
    except Exception as e:
        error_message = f"An error occurred: {e}"
        return render(request, 'error_template.html', {'error_message': error_message})



def edit_expense(request, group_id):
    try:
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
    
    except Exception as e:
        error_message = f"An error occurred: {e}"
        return render(request, 'error_template.html', {'error_message': error_message})