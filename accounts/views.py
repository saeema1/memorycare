from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, PatientProfileForm, PatientRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import Reminder


def home(request):
    return render(request, 'accounts/landing.html')


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Role-based redirect for compatibility with older login form
            if hasattr(user, 'role'):
                if user.role == 'DOCTOR':
                    return redirect('dashboard:doctor_dashboard')
                if user.role == 'CAREGIVER':
                    return redirect('dashboard:caregiver_dashboard')
                return redirect('dashboard:patient_dashboard')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = UserLoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


def login_view(request):
    """Authenticate and redirect users based on their role."""
    # If user is already authenticated, send them to their dashboard immediately
    if request.user.is_authenticated:
        role = getattr(request.user, 'role', '')
        if isinstance(role, str):
            r = role.upper()
            if r == 'DOCTOR':
                return redirect('dashboard:doctor_dashboard')
            if r == 'CAREGIVER':
                return redirect('dashboard:caregiver_dashboard')
            if r == 'PATIENT':
                return redirect('dashboard:patient_dashboard')
        return redirect('dashboard:home')
    # Use the project's AuthenticationForm-compatible form so the template
    # renders fields and CSRF works correctly.
    # Support optional `next` parameter (safe/relative URLs only), otherwise redirect by role
    next_url = request.POST.get('next') or request.GET.get('next')
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # If a safe next URL was provided, honour it (allows redirect back to requested page)
            if next_url and (next_url.startswith('/') or url_has_allowed_host_and_scheme(next_url, {request.get_host()})):
                return redirect(next_url)

            role = getattr(user, 'role', '').upper()
            if role == 'DOCTOR':
                return redirect('dashboard:doctor_dashboard')
            elif role == 'CAREGIVER':
                return redirect('dashboard:caregiver_dashboard')
            else:
                return redirect('dashboard:patient_dashboard')
    else:
        form = UserLoginForm(request)

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    logout(request)
    return redirect('login')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please login.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def register_patient(request):
    from django.shortcuts import render, redirect
    # PatientRegistrationForm is an alias to the patient/user registration form
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            # Ensure role uses model's choice value
            patient.role = 'PATIENT'
            patient.save()
            return redirect('dashboard:doctor_dashboard')
    else:
        form = PatientRegistrationForm()

    return render(request, 'accounts/register_patient.html', {'form': form})


@login_required
def register_caregiver(request):
    """Simple caregiver registration endpoint used by admins/doctors."""
    from django.shortcuts import render, redirect
    # Reuse PatientRegistrationForm for the example; ideally create a dedicated CaregiverRegistrationForm
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            caregiver = form.save(commit=False)
            caregiver.role = 'CAREGIVER'
            caregiver.save()
            return redirect('dashboard:doctor_dashboard')
    else:
        form = PatientRegistrationForm()

    return render(request, 'accounts/register_caregiver.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def profile(request):
    """Display current user's profile with assigned staff and recent reminders"""
    user_profile = request.user
    reminders = user_profile.reminders.order_by('-scheduled_for')[:20]
    return render(request, 'accounts/profile.html', {'user_profile': user_profile, 'reminders': reminders})


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


@login_required
def reminders_list(request):
    reminders = request.user.reminders.order_by('-scheduled_for')
    return render(request, 'accounts/reminders.html', {'reminders': reminders})


@login_required
def reminder_create_ajax(request):
    """AJAX endpoint to allow patients to create simple reminders."""
    from django.http import JsonResponse
    from django.utils import timezone
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)
    title = request.POST.get('title') or request.POST.get('name')
    message = request.POST.get('message', '')
    scheduled = request.POST.get('scheduled_for')
    if not title or not scheduled:
        return JsonResponse({'ok': False, 'errors': 'title and scheduled_for required'}, status=400)
    try:
        from django.utils.dateparse import parse_datetime
        dt = parse_datetime(scheduled)
        if dt is None:
            raise ValueError
    except Exception:
        return JsonResponse({'ok': False, 'errors': 'Invalid scheduled_for'}, status=400)
    r = Reminder.objects.create(patient=request.user, title=title, message=message, scheduled_for=dt)
    return JsonResponse({'ok': True, 'reminder': {'id': r.id, 'title': r.title, 'scheduled_for': r.scheduled_for.isoformat(), 'read': r.read}})


@login_required
def reminder_mark_read(request, reminder_id):
    reminder = get_object_or_404(Reminder, id=reminder_id, patient=request.user)
    reminder.read = True
    reminder.save()
    messages.success(request, 'Reminder marked as read')
    return redirect('accounts:reminders')
