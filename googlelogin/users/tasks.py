# yourapp/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string

@shared_task()
def send_acceptance_email(user_email, group_name, group_id):
    print("hello from send_acceptance_email from tasks.py")
    print("user_eamil : ", user_email, "group_name : ", group_name, "group_id:", group_id)
    subject = 'You have been added to {}'.format(group_name)
    html_message = render_to_string('email_template.html', {'group_name': group_name, 'group_id': group_id})
    message = 'Dear user, you have been added to the group "{}". Welcome!'.format(group_name)
    from_email = 'testingsplitapp@gmail.com'
    recipient_list = [user_email]
    send_mail(subject, message, from_email, recipient_list, html_message=html_message, fail_silently=False)

@shared_task()
def send_amount_email(user_email, group_name, group_id, user_share, total_amount):
    subject = 'Your '.format(group_name),' group have added expense. Total expense : '.format(total_amount)
    html_message = render_to_string('update_amount_template.html', {'group_name': group_name, 'group_id': group_id, 'total_amount': total_amount, 'user_share': user_share})
    message = 'Dear user, your share is '.format(user_share)
    from_email = 'testingsplitapp@gmail.com'
    recipient_list = [user_email]
    send_mail(subject, message, from_email, recipient_list, html_message=html_message, fail_silently=False)