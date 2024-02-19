
from django.urls import path,include
from django.contrib.auth import  views as auth_views
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('social-auth', include('social_django.urls', namespace='social')),
    path('', views.home, name='home'),
    path('create_group/', views.create_group, name='create_group'),
    path('edit_expense/<int:group_id>/', views.edit_expense, name='edit_expense' ),
    path('group_detail/<int:group_id>/', views.group_detail, name='group_detail'),
]