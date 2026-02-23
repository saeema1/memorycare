from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def home(request):
    if request.user.is_doctor:
        return redirect('dashboard:doctor_dashboard')
    elif request.user.is_caregiver:
        return redirect('dashboard:caregiver_dashboard')
    elif request.user.is_patient:
        return redirect('dashboard:patient_dashboard')
    else:
        messages.error(request, 'Invalid role')
        return redirect('accounts:login')


@login_required
def doctor_dashboard(request):
    if not request.user.is_doctor:
        messages.error(request, 'Doctor access required')
        return redirect('dashboard:home')
    
    from accounts.models import User
    
    patients = User.objects.filter(role='PATIENT').select_related('assigned_doctor')
    caregivers = User.objects.filter(role='CAREGIVER')
    
    # For each patient, we might want to know their assigned caregiver (which is a reverse relation check or stored field).
    # Based on User model, patients have 'patients_under_caregiver' reverse relation from caregiver to patient? 
    # Wait, Step 240 model view showed:
    # caregiving_experience_years... 
    # User model didn't explicitly show a 'caregiver' FK on the patient, but the Caregiver dashboard 
    # uses `request.user.patients_under_caregiver.all()`. 
    # This implies a ManyToMany or ForeignKey from Patient to Caregiver, OR Caregiver to Patient.
    # Let's check accounts/models.py again or assume/fix.
    # Actually, looking at the previous caregiver dashboard logic: 
    # caregivers see `request.user.patients_under_caregiver.all()`
    # That implies the related_name on the Patient->Caregiver FK is `patients_under_caregiver`.
    # Let's quickly verify the user model relationship name if possible, OR assume valid structure.
    # Step 240 showed: `class User(AbstractUser)`... I didn't see the specific FK field for caregiver assignment in the first 40 lines.
    # I will assume there is a field on Patient pointing to Caregiver? Or Caregiver pointing to Patient?
    # Usually it's Patient.caregiver = FK(Caregiver).
    # If `request.user.patients_under_caregiver` works for Caregiver, then `User` (Caregiver) has many `patients_under_caregiver`.
    # So `User` (Patient) likely has a FK `caregiver` related_name=`patients_under_caregiver`.
    
    context = {
        'patients': patients,
        'caregivers': caregivers,
    }

    return render(request, 'dashboard/doctor_dashboard.html', context)


@login_required
def assign_caregiver(request):
    if not request.user.is_doctor:
        messages.error(request, 'Access denied')
        return redirect('dashboard:home')
        
    if request.method == 'POST':
        from accounts.models import User
        patient_id = request.POST.get('patient_id')
        caregiver_id = request.POST.get('caregiver_id')
        
        try:
            patient = User.objects.get(id=patient_id, role='PATIENT')
            if caregiver_id:
                caregiver = User.objects.get(id=caregiver_id, role='CAREGIVER')
                patient.assigned_caregiver = caregiver
                patient.save()
                messages.success(request, f'Assigned {caregiver.first_name} to {patient.first_name}.')
            else:
                patient.assigned_caregiver = None
                patient.save()
                messages.info(request, f'Unassigned caregiver from {patient.first_name}.')
        except User.DoesNotExist:
            messages.error(request, 'User not found')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            
    return redirect('dashboard:doctor_dashboard')


@login_required
def caregiver_dashboard(request):
    """Dashboard for caregivers showing assigned patients and alerts."""
    from .models import Alert, TestResult
    if not request.user.is_caregiver:
        messages.error(request, 'Caregiver access required')
        return redirect('dashboard:home')

    # Fetch assigned patients
    patients = request.user.patients_under_caregiver.all()
    
    # Fetch alerts for assigned patients
    from .utils import generate_caregiver_alerts
    alerts = generate_caregiver_alerts(request.user)
    
    # Optional: If you still want to include persistent Alert objects, you can merge them.
    # But for now, we rely on the dynamic ones as requested "update automatically based on patient data".
    # We can assume older 'Alert' model usage is superseded or complementary if we merge.
    # Let's just use the dynamic ones for the "active" display to be responsive.

    # Calculated summary metrics could go here
    total_patients = patients.count()
    active_alerts = len(alerts)
    
    # Fetch recent test results for assigned patients
    recent_results = TestResult.objects.filter(user__in=patients).select_related('user', 'test').order_by('-created_at')[:5]
    
    context = {
        'patients': patients,
        'alerts': alerts,
        'recent_results': recent_results,
        'total_patients': total_patients,
        'active_alerts': active_alerts,
    }
    return render(request, 'dashboard/caregiver_dashboard.html', context)
    
@login_required
def caregiver_patient_detail(request, patient_id):
    """Deep dive into a specific patient's status for the caregiver."""
    from accounts.models import User
    from .models import DailyActivity, TestResult, MoodEntry
    from django.utils import timezone
    
    if not request.user.is_caregiver:
        messages.error(request, 'Access denied')
        return redirect('dashboard:home')
        
    patient = get_object_or_404(User, id=patient_id)
    
    # Permission check: Ensure this patient is assigned to this caregiver
    # Use ID comparison to be safe
    if patient.assigned_caregiver_id != request.user.id:
        messages.error(request, 'You are not assigned to this patient.')
        return redirect('dashboard:caregiver_dashboard')

    # Fetch Data
    today = timezone.localdate()
    # Fetch activities and filter in python to handle recurrences
    activities = DailyActivity.objects.filter(user=patient).order_by('scheduled_for')
    activities_today = [a for a in activities if a.occurs_on(today)]
    
    # Test Results
    test_results = TestResult.objects.filter(user=patient).order_by('-created_at')[:10]
    
    # Mood
    recent_moods = MoodEntry.objects.filter(user=patient).order_by('-created_at')[:7]
    
    # Alerts/Reminders - Only upcoming or today's
    reminders = patient.reminders.filter(scheduled_for__date=today).order_by('scheduled_for')

    # Calculate Health Score
    from .utils import calculate_health_score
    health_score = calculate_health_score(patient)

    # Determine Patient Condition Label
    if health_score >= 80: condition_label = "Stable"
    elif health_score >= 60: condition_label = "Monitoring"
    else: condition_label = "Declining"

    context = {
        'patient': patient,
        'activities': activities_today,
        'test_results': test_results,
        'recent_moods': recent_moods,
        'reminders': reminders,
        'health_score': health_score,
        'condition_label': condition_label,
    }
    return render(request, 'dashboard/caregiver_patient_detail.html', context)


@login_required
def patient_dashboard(request):
    if not request.user.is_patient:
        messages.error(request, 'Patient access required')
        return redirect('dashboard:home')

    # Today's reminders/tasks
    from django.utils import timezone
    today = timezone.localdate()
    reminders_today = request.user.reminders.filter(scheduled_for__date=today).order_by('scheduled_for')

    # Simple health score heuristic
    from .utils import calculate_health_score
    health_score = calculate_health_score(request.user)



    # Today's scheduled activities (include recurrence)
    from .models import DailyActivity
    # Seed activities if user has none (ever)
    # Updated seeding logic for a full daily schedule
    std_time = timezone.now().replace(minute=0, second=0, microsecond=0)
    
    default_activities = [
        {'name': 'Morning Routine', 'type': 'other', 'hour': 7, 'minute': 0},
        {'name': 'Breakfast', 'type': 'meal', 'hour': 8, 'minute': 0},
        {'name': 'Morning Medication', 'type': 'medication', 'hour': 8, 'minute': 30},
        {'name': 'Light Exercise / Walk', 'type': 'exercise', 'hour': 10, 'minute': 0},
        {'name': 'Lunch', 'type': 'meal', 'hour': 12, 'minute': 30},
        {'name': 'Afternoon Rest', 'type': 'rest', 'hour': 14, 'minute': 0},
        {'name': 'Dinner', 'type': 'meal', 'hour': 18, 'minute': 30},
        {'name': 'Evening Medication', 'type': 'medication', 'hour': 20, 'minute': 0},
        {'name': 'Bedtime Routine', 'type': 'rest', 'hour': 21, 'minute': 30},
    ]

    for item in default_activities:
        # Check if this specific activity already exists for the user
        if not DailyActivity.objects.filter(user=request.user, name=item['name']).exists():
            DailyActivity.objects.create(
                user=request.user,
                name=item['name'],
                activity_type=item['type'],
                scheduled_for=std_time.replace(hour=item['hour'], minute=item['minute']),
                recurrence='daily'
            )

    all_activities = DailyActivity.objects.filter(user=request.user).order_by('scheduled_for')
    activities = [a for a in all_activities if a.occurs_on(today)]

    # ... (mood entries logic remains same) ...
    mood_entries = request.user.mood_entries.order_by('-created_at')[:7]

    # ... (form logic remains same) ...
    from .forms import DailyActivityForm
    form = DailyActivityForm()
    if not (request.user.is_doctor or request.user.is_caregiver):
        form.fields.pop('user', None)

    # ... (patient age/vitals logic) ...
    patient = request.user
    patient_age = None
    if getattr(patient, 'date_of_birth', None):
        dob = patient.date_of_birth
        patient_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    # ... (last activity logic) ...
    candidates = []
    if mood_entries: candidates.append(mood_entries[0].created_at)
    latest_activity = DailyActivity.objects.filter(user=request.user).order_by('-updated_at', '-created_at').first()
    if latest_activity: candidates.append(latest_activity.updated_at or latest_activity.created_at)
    latest_reminder = request.user.reminders.order_by('-scheduled_for').first()
    if latest_reminder: candidates.append(latest_reminder.scheduled_for)

    patient_last_activity = max(candidates) if candidates else None

    vitals = {}
    
    # Calculate stats
    total_activities = len(activities)
    completed_activities = sum(1 for a in activities if getattr(a, 'completed', False))
    remaining_activities = total_activities - completed_activities
    percent_completed = 0 if total_activities == 0 else int((completed_activities / total_activities) * 100)

    if health_score >= 75: health_label = 'Good'
    elif health_score >= 50: health_label = 'Fair'
    else: health_label = 'Needs attention'

    # Build Schedule (Merge Reminders + Activities, sort by time)
    schedule_items = []
    for r in reminders_today:
        schedule_items.append({'time': r.scheduled_for, 'title': r.title, 'type': 'reminder', 'completed': r.read})
    for a in activities:
        # Only add time-critical activities to schedule to keep it clean? 
        # User said "Schedule must show only time-based reminders and important events."
        # All DailyActivities have a time, so we include them but maybe we can visually distinguish.
        schedule_items.append({'time': a.scheduled_for, 'title': a.name, 'type': 'activity', 'completed': a.completed, 'obj': a})
    
    # Sort by time
    schedule_items.sort(key=lambda x: x['time'])
    
    # Pre-format time strings for display to avoid template issues
    # Pre-format time strings for display to avoid template issues
    import datetime
    for item in schedule_items:
        t = item['time']
        if t:
            # Format as "08:00 AM – 08:30 AM" (Synthesized 30 min duration as per user request)
            start_str = t.strftime('%I:%M %p')
            end_time = t + datetime.timedelta(minutes=30)
            end_str = end_time.strftime('%I:%M %p')
            item['time_display'] = f"{start_str} – {end_str}"
        else:
            item['time_display'] = 'Time not set'

    context = {
        'reminders_today': reminders_today,
        'health_score': health_score,
        'health_label': health_label,

        'activities': activities,
        'schedule': schedule_items,  # Passed to template
        'total_activities': total_activities,
        'completed_activities': completed_activities,
        'remaining_activities': remaining_activities,
        'percent_completed': percent_completed,
        'mood_entries': mood_entries,
        'activity_form': form,
        'patient': patient,
        'patient_age': patient_age,
        'patient_last_activity': patient_last_activity,
        'vitals': vitals,
    }

    return render(request, 'dashboard/patient_dashboard.html', context)





@login_required
def daily_activities(request):
    """List and manage today's activities for the logged-in patient, including recurring activities."""
    from .models import DailyActivity
    if not request.user.is_patient:
        messages.error(request, 'Patient access required')
        return redirect('dashboard:home')

    from django.utils import timezone
    today = timezone.localdate()
    all_activities = DailyActivity.objects.filter(user=request.user).order_by('scheduled_for')
    activities_for_today = [a for a in all_activities if a.occurs_on(today)]

    total = len(activities_for_today)
    completed = sum(1 for a in activities_for_today if getattr(a, 'completed', False))
    percent = 0 if total == 0 else int((completed / total) * 100)
    return render(request, 'dashboard/daily_activities.html', {'activities': activities_for_today, 'total_activities': total, 'completed_activities': completed, 'percent_completed': percent})


@login_required
def activity_create(request):
    """Create a DailyActivity. Staff can create for patients (use ?patient=<id> to prefill)."""
    from .forms import DailyActivityForm
    from accounts.models import User

    # Restrict patients from creating activities
    if request.user.is_patient:
        messages.error(request, 'Patients cannot create activities.')
        return redirect('dashboard:daily_activities')

    if request.method == 'POST':
        form = DailyActivityForm(request.POST)
        # If non-staff (patient), remove user field from the form and force activity to belong to them
        if not (request.user.is_doctor or request.user.is_caregiver):
            form.fields.pop('user', None)
            if form.is_valid():
                a = form.save(commit=False)
                a.user = request.user
                a.save()
                return redirect('dashboard:daily_activities')
        else:
            # staff may set user via form
            if form.is_valid():
                form.save()
                return redirect('dashboard:daily_activities')
    else:
        initial = {}
        patient_id = request.GET.get('patient')
        if patient_id and (request.user.is_doctor or request.user.is_caregiver):
            initial['user'] = patient_id
        form = DailyActivityForm(initial=initial)
        if not (request.user.is_doctor or request.user.is_caregiver):
            form.fields.pop('user', None)

    return render(request, 'dashboard/daily_activity_form.html', {'form': form})


@login_required
def toggle_activity(request, activity_id):
    """Toggle activity completion via POST."""
    from .models import DailyActivity
    a = get_object_or_404(DailyActivity, id=activity_id, user=request.user)
    if request.method == 'POST':
        a.completed = not a.completed
        a.save()
        # Redirect back to activities or dashboard depending on where request came from
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'
        return redirect(next_url)
    # If GET, show a simple confirmation
    return render(request, 'dashboard/toggle_activity.html', {'activity': a})





@login_required
def mood_view(request):
    from .models import MoodEntry
    from .forms import MoodForm
    # Support quick mood button POSTs with 'mood' field
    if request.method == 'POST':
        if 'mood' in request.POST and 'note' not in request.POST:
            m = request.POST.get('mood')
            if m:
                MoodEntry.objects.create(user=request.user, mood=m)
                return redirect('dashboard:mood')
        form = MoodForm(request.POST)
        if form.is_valid():
            me = form.save(commit=False)
            me.user = request.user
            me.save()
            return redirect('dashboard:mood')
    else:
        form = MoodForm()

    entries = request.user.mood_entries.order_by('-created_at')[:10]
    return render(request, 'dashboard/mood.html', {'form': form, 'entries': entries})


@login_required
def mood_ajax(request):
    """AJAX endpoint to post a quick mood and return JSON."""
    from django.http import JsonResponse
    from .models import MoodEntry
    if request.method == 'POST':
        mood = request.POST.get('mood') or request.POST.get('mood')
        note = request.POST.get('note', '')
        if mood:
            me = MoodEntry.objects.create(user=request.user, mood=mood, note=note)
            return JsonResponse({'ok': True, 'id': me.id, 'mood': me.mood, 'mood_display': me.get_mood_display(), 'created_at': me.created_at.isoformat()})
    return JsonResponse({'ok': False}, status=400)


@login_required
def toggle_activity_ajax(request, activity_id):
    """AJAX toggle activity completion and return JSON."""
    from django.http import JsonResponse
    from .models import DailyActivity
    a = get_object_or_404(DailyActivity, id=activity_id, user=request.user)
    if request.method == 'POST':
        a.completed = not a.completed
        a.save()
        return JsonResponse({'ok': True, 'id': a.id, 'completed': a.completed})
    return JsonResponse({'ok': False}, status=400)





@login_required
def patient_dashboard_data_ajax(request):
    """Return patient-specific dashboard summary data for charts and live updates."""
    from django.http import JsonResponse
    from django.utils import timezone
    from .models import DailyActivity, MoodEntry
    import datetime

    if not request.user.is_patient:
        return JsonResponse({'ok': False}, status=403)

    today = timezone.localdate()

    # Health score (same heuristic as main view)
    total_reminders = request.user.reminders.count()
    unread_reminders = request.user.reminders.filter(read=False).count()
    if total_reminders:
        health_score = max(0, 100 - int((unread_reminders / total_reminders) * 100))
    else:
        health_score = 80

    # Mood - last 7 days (avg mood mapped to numeric score)
    mood_map = {'very_happy': 5, 'happy': 4, 'neutral': 3, 'sad': 2, 'very_sad': 1, 'anxious': 2}
    mood_labels = []
    mood_data = []
    for i in range(6, -1, -1):
        d = today - datetime.timedelta(days=i)
        mood_labels.append(d.isoformat())
        entries = request.user.mood_entries.filter(created_at__date=d)
        if entries.exists():
            avg = sum(mood_map.get(e.mood, 3) for e in entries) / entries.count()
            mood_data.append(round(avg, 2))
        else:
            mood_data.append(None)



    # Today's activities
    from django.utils import timezone as djtz
    all_activities = DailyActivity.objects.filter(user=request.user)
    activities = [a for a in all_activities if a.occurs_on(today)]
    activities_list = [{'id': a.id, 'name': a.name, 'scheduled_for': a.scheduled_for.isoformat(), 'completed': a.completed, 'type': a.activity_type, 'subtype': a.activity_type} for a in activities]

    # Today's reminders
    reminders_qs = request.user.reminders.filter(scheduled_for__date=today).order_by('scheduled_for')
    reminders_list = [{'id': r.id, 'title': r.title, 'message': r.message, 'scheduled_for': r.scheduled_for.isoformat(), 'read': r.read} for r in reminders_qs]

    # Compute component-based metrics over last 7 days
    start_date = today - datetime.timedelta(days=6)
    recent_acts = DailyActivity.objects.filter(user=request.user, scheduled_for__date__gte=start_date, scheduled_for__date__lte=today)

    def adherence_rate(qs):
        total = qs.count()
        if total == 0:
            return None
        done = qs.filter(completed=True).count()
        return int((done / total) * 100)

    med_rate = adherence_rate(recent_acts.filter(activity_type='medication'))
    exercise_rate = adherence_rate(recent_acts.filter(activity_type='exercise'))
    sleep_rate = adherence_rate(recent_acts.filter(activity_type='rest'))
    social_rate = adherence_rate(recent_acts.filter(activity_type='other'))



    # Mood normalized 1-5 -> 0-100
    mood_vals = [v for v in mood_data if v is not None]
    mood_avg = None
    if mood_vals:
        mood_avg = int(((sum(mood_vals) / len(mood_vals)) - 1) / 4 * 100)

    # Aggregate health score (weighted average of available components)
    components = {
        'medication': med_rate,
        'exercise': exercise_rate,
        'sleep': sleep_rate,
        'social': social_rate,
        'mood': mood_avg,
    }
    weights = {'medication': 0.35, 'exercise': 0.25, 'sleep': 0.20, 'social': 0.1, 'mood': 0.1}
    # Note: mood treated as optional extra; we'll build weighted average from available components
    total_weight = 0.0
    score_accum = 0.0
    for k, v in components.items():
        w = weights.get(k, 0)
        if v is not None:
            score_accum += v * w
            total_weight += w
    computed_health_score = int(score_accum / total_weight) if total_weight > 0 else health_score

    # Generate simple recommendations
    recs = []
    if med_rate is not None and med_rate < 70:
        recs.append('Medication adherence low — try setting reminders or ask your caregiver for help.')
    if exercise_rate is not None and exercise_rate < 50:
        recs.append('Increase light physical activity today (short walk, stretching).')

    if mood_avg is not None and mood_avg < 40:
        recs.append('Mood has been low this week — consider contacting your caregiver or try a relaxation exercise.')
    if sleep_rate is not None and sleep_rate < 50:
        recs.append('Consider improving sleep hygiene (consistent bedtime, reduce naps).')

    # Build today's schedule (merge reminders and activities sorted by time)
    schedule = []
    for r in reminders_list:
        schedule.append({'type': 'reminder', 'id': r['id'], 'title': r['title'], 'time': r['scheduled_for']})
    for a in activities_list:
        schedule.append({'type': 'activity', 'id': a['id'], 'title': a['name'], 'time': a['scheduled_for'], 'completed': a['completed'], 'subtype': a.get('type')})
    # parse iso times for sorting
    def _parse_iso(dt_str):
        try:
            return djtz.datetime.fromisoformat(dt_str)
        except Exception:
            return None
    schedule = sorted([s for s in schedule if _parse_iso(s['time']) is not None], key=lambda s: _parse_iso(s['time']))

    return JsonResponse({
        'ok': True,
        'health_score': computed_health_score,
        'health_components': components,
        'recommendations': recs,
        'mood': {'labels': mood_labels, 'data': mood_data},

        'activities': activities_list,
        'reminders': reminders_list,
        'schedule': schedule,
    })


@login_required
def activity_create_ajax(request):
    """Create a DailyActivity via AJAX and return JSON for immediate UI update."""
    from django.http import JsonResponse
    from .forms import DailyActivityForm

    # Restrict patients from creating activities
    if request.user.is_patient:
        return JsonResponse({'ok': False, 'error': 'Permission denied'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)

    post = request.POST.copy()
    form = DailyActivityForm(post)
    # If patient, don't allow setting user via form
    if not (request.user.is_doctor or request.user.is_caregiver):
        if 'user' in form.fields:
            form.fields.pop('user')

        if form.is_valid():
            a = form.save(commit=False)
            a.user = request.user
            a.save()
            return JsonResponse({'ok': True, 'activity': {'id': a.id, 'name': a.name, 'scheduled_for': a.scheduled_for.isoformat(), 'completed': a.completed, 'type': a.activity_type}})
        else:
            return JsonResponse({'ok': False, 'errors': form.errors}, status=400)

    # Staff may create on behalf of patients
    if form.is_valid():
        a = form.save()
        return JsonResponse({'ok': True, 'activity': {'id': a.id, 'name': a.name, 'scheduled_for': a.scheduled_for.isoformat(), 'completed': a.completed, 'type': a.activity_type}})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


@login_required
def cognitive_tests(request):
    """List available cognitive tests for the patient."""
    if not request.user.is_patient:
        messages.error(request, 'Patient access required')
        return redirect('dashboard:home')
    
    from django.utils import timezone
    from .models import TestResult
    
    today = timezone.now().date()
    # Get tests completed today
    completed_today = TestResult.objects.filter(
        user=request.user, 
        created_at__date=today
    ).values_list('test__name', flat=True)
    
    # Mock tests for display
    tests = [
        {'id': 'memory', 'name': 'Memory Test', 'description': 'Exercise your short-term memory by identifying objects and recalling words.', 'icon': 'fa-puzzle-piece', 'color': 'bg-blue-100 text-blue-600', 'url_name': 'test_memory'},
        {'id': 'color', 'name': 'Color Recognition Test', 'description': 'Identify colors correctly to keep your visual perception sharp.', 'icon': 'fa-eye', 'color': 'bg-yellow-100 text-yellow-600', 'url_name': 'test_color'},
        {'id': 'mixed', 'name': 'Mixed Simple Test', 'description': 'A variety of logic, attention, and memory questions.', 'icon': 'fa-random', 'color': 'bg-green-100 text-green-600', 'url_name': 'test_mixed'},
    ]
    
    # Mark completed
    for t in tests:
        if t['name'] in completed_today:
            t['completed'] = True
    
    return render(request, 'dashboard/cognitive_tests.html', {'tests': tests})


@login_required
def test_memory(request):
    return render(request, 'dashboard/test_memory.html')

@login_required
def test_color(request):
    return render(request, 'dashboard/test_color.html')

@login_required
def test_mixed(request):
    return render(request, 'dashboard/test_mixed.html')

@login_required
def save_test_result(request):
    from django.http import JsonResponse
    from .models import TestResult, CognitiveTest
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            test_name = data.get('test_name')
            score = data.get('score')
            max_score = data.get('max_score')
            
            # Get or create the test definition
            test_def, _ = CognitiveTest.objects.get_or_create(name=test_name)
            
            # Save result
            TestResult.objects.create(
                user=request.user,
                test=test_def,
                score=score,
                max_score=max_score,
                answers=data.get('answers', {})
            )
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)
    return JsonResponse({'ok': False}, status=400)
