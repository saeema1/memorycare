from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import (
    UserLoginForm,
    PatientProfileForm,
    PatientRegistrationForm,
    CaregiverRegistrationForm
)
from .models import Reminder


# =======================
# Landing Page
# =======================
def home(request):
    return render(request, 'accounts/landing.html')


# =======================
# LOGIN
# =======================
def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # 🔥 ROLE BASED REDIRECT (IMPORTANT)
            if user.is_patient:
                return redirect('dashboard:patient_dashboard')
            elif user.is_caregiver:
                return redirect('dashboard:caregiver_dashboard')
            elif user.is_doctor:
                return redirect('dashboard:doctor_dashboard')
            else:
                logout(request)
                messages.error(request, 'User role not assigned.')
                return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


# =======================
# REGISTER LANDING
# =======================
def register(request):
    role = request.GET.get('role')
    if role == 'caregiver':
        return redirect('accounts:register_caregiver')
    return redirect('accounts:register_patient')


# =======================
# PATIENT REGISTRATION
# =======================
def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'PATIENT'
            user.save()

            login(request, user)
            messages.success(request, 'Patient registration successful.')
            return redirect('dashboard:patient_dashboard')
    else:
        form = PatientRegistrationForm()

    return render(request, 'accounts/register_patient.html', {'form': form})


# =======================
# CAREGIVER REGISTRATION
# =======================
def register_caregiver(request):
    if request.method == 'POST':
        form = CaregiverRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'CAREGIVER'
            user.save()

            login(request, user)
            messages.success(request, 'Caregiver registration successful.')
            return redirect('dashboard:caregiver_dashboard')
    else:
        form = CaregiverRegistrationForm()

    return render(request, 'accounts/register_caregiver.html', {'form': form})


# =======================
# LOGOUT
# =======================
def user_logout(request):
    logout(request)
    return redirect('accounts:login')


# =======================
# PROFILE
# =======================
@login_required
def profile(request):
    reminders = request.user.reminders.order_by('-scheduled_for')[:20]
    return render(
        request,
        'accounts/profile.html',
        {
            'user_profile': request.user,
            'reminders': reminders
        }
    )


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('accounts:profile')
    else:
        form = PatientProfileForm(instance=request.user)

    return render(request, 'accounts/profile_edit.html', {'form': form})


# =======================
# REMINDERS
# =======================
@login_required
def reminders_list(request):
    reminders = request.user.reminders.order_by('-scheduled_for')
    return render(request, 'accounts/reminders.html', {'reminders': reminders})


@login_required
def reminder_create_ajax(request):
    from django.http import JsonResponse
    from django.utils.dateparse import parse_datetime

    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)

    title = request.POST.get('title')
    message = request.POST.get('message', '')
    scheduled = request.POST.get('scheduled_for')

    if not title or not scheduled:
        return JsonResponse({'ok': False, 'error': 'Missing fields'}, status=400)

    dt = parse_datetime(scheduled)
    if not dt:
        return JsonResponse({'ok': False, 'error': 'Invalid datetime'}, status=400)

    reminder = Reminder.objects.create(
        patient=request.user,
        title=title,
        message=message,
        scheduled_for=dt
    )

    return JsonResponse({
        'ok': True,
        'reminder': {
            'id': reminder.id,
            'title': reminder.title,
            'scheduled_for': reminder.scheduled_for.isoformat(),
            'read': reminder.read
        }
    })


@login_required
def reminder_mark_read(request, reminder_id):
    reminder = get_object_or_404(
        Reminder,
        id=reminder_id,
        patient=request.user
    )
    reminder.read = True
    reminder.save()
    messages.success(request, 'Reminder marked as read')
    return redirect('accounts:reminders')
