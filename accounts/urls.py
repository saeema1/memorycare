from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('register/patient/', views.register_patient, name='register_patient'),
    path('register/caregiver/', views.register_caregiver, name='register_caregiver'),

    path('logout/', views.user_logout, name='logout'),

    # Patient-specific
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('reminders/', views.reminders_list, name='reminders'),
    path('reminders/<int:reminder_id>/read/', views.reminder_mark_read, name='reminder_mark_read'),
    path('reminders/create/ajax/', views.reminder_create_ajax, name='reminder_create_ajax'),
]
