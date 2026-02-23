from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/assign-caregiver/', views.assign_caregiver, name='assign_caregiver'),
    path('caregiver/', views.caregiver_dashboard, name='caregiver_dashboard'),
    path('caregiver/patient/<int:patient_id>/', views.caregiver_patient_detail, name='caregiver_patient_detail'),
    path('patient/', views.patient_dashboard, name='patient_dashboard'),



    # Cognitive Tests
    path('patient/tests/', views.cognitive_tests, name='cognitive_tests'),
    path('patient/tests/memory/', views.test_memory, name='test_memory'),
    path('patient/tests/color/', views.test_color, name='test_color'),
    path('patient/tests/mixed/', views.test_mixed, name='test_mixed'),
    path('patient/tests/save/', views.save_test_result, name='save_test_result'),

    # Mood tracking
    path('patient/mood/', views.mood_view, name='mood'),
    path('patient/mood/ajax/', views.mood_ajax, name='mood_ajax'),

    # Daily Activities
    path('patient/activities/', views.daily_activities, name='daily_activities'),
    path('patient/activities/create/', views.activity_create, name='activity_create'),
    path('patient/activities/<int:activity_id>/toggle/', views.toggle_activity, name='toggle_activity'),
    path('patient/activities/<int:activity_id>/toggle/ajax/', views.toggle_activity_ajax, name='toggle_activity_ajax'),
    path('patient/activities/create/ajax/', views.activity_create_ajax, name='activity_create_ajax'),
    path('patient/dashboard/data/ajax/', views.patient_dashboard_data_ajax, name='patient_dashboard_data_ajax'),


]
