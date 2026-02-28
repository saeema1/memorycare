from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone

def ensure_patient_activities(user):
    """Seeds default daily activities for a patient if none exist."""
    from .models import DailyActivity
    if not DailyActivity.objects.filter(user=user).exists():
        std_time = timezone.now().replace(minute=0, second=0, microsecond=0)
        # Morning Routine
        DailyActivity.objects.create(user=user, name='Morning Medication', activity_type='medication', scheduled_for=std_time.replace(hour=8), recurrence='daily')
        DailyActivity.objects.create(user=user, name='Breakfast', activity_type='meal', scheduled_for=std_time.replace(hour=8, minute=30), recurrence='daily')
        # Afternoon
        DailyActivity.objects.create(user=user, name='Afternoon Walk', activity_type='exercise', scheduled_for=std_time.replace(hour=14), recurrence='daily')
        DailyActivity.objects.create(user=user, name='Lunch', activity_type='meal', scheduled_for=std_time.replace(hour=13), recurrence='daily')
        # Evening
        DailyActivity.objects.create(user=user, name='Evening Medication', activity_type='medication', scheduled_for=std_time.replace(hour=20), recurrence='daily')
        DailyActivity.objects.create(user=user, name='Dinner', activity_type='meal', scheduled_for=std_time.replace(hour=19, minute=0), recurrence='daily')


def safe_has_role(user, attr_name):
    """Call role-check helpers safely when they may be stored as booleans on the instance.

    Some code may set `user.is_doctor = True` (instance attribute) which shadows
    the class method. This helper returns the boolean either way.
    """
    attr = getattr(user, attr_name, False)
    if isinstance(attr, bool):
        return attr
    try:
        return attr()
    except Exception:
        return False


@login_required
def home(request):
    if safe_has_role(request.user, 'is_doctor'):
        return redirect('dashboard:doctor_dashboard')
    elif safe_has_role(request.user, 'is_caregiver'):
        return redirect('dashboard:doctor_dashboard')
    elif safe_has_role(request.user, 'is_patient'):
        return redirect('dashboard:patient_dashboard')
    else:
        messages.error(request, 'Invalid role')
        return redirect('accounts:login')


@login_required
def doctor_dashboard(request):
    is_doctor = safe_has_role(request.user, 'is_doctor')
    is_caregiver = safe_has_role(request.user, 'is_caregiver')
    
    if not (is_doctor or is_caregiver):
        messages.error(request, 'Access denied')
        return redirect('dashboard:home')
    
    from accounts.models import User
    from ml_module.ml_service import ml_service
    from .models import TestResult

    # Base patient set: all patients under this doctor / caregiver
    if is_doctor:
        patients_base = User.objects.filter(role='PATIENT', doctor=request.user)
    else:
        # Caregivers see patients where they are the assigned caregiver
        patients_base = User.objects.filter(role='PATIENT', caregiver=request.user)

    # --- Apply clinical readiness rules ---
    # 1) Patient must have at least one cognitive test result
    # 2) Patient must be assigned to a caregiver (caregiver is not null)
    tested_ids = TestResult.objects.filter(user__in=patients_base) \
        .values_list('user_id', flat=True).distinct()
    clinical_patients = patients_base.filter(
        id__in=tested_ids,
        caregiver__isnull=False
    ).order_by('last_name', 'first_name')
    
    # Get caregivers under this doctor's network
    if is_doctor:
        # Show all caregivers that were registered by / linked to this doctor,
        # regardless of whether they already have patients assigned.
        caregivers = User.objects.filter(
            role='CAREGIVER',
            doctor=request.user
        ).order_by('last_name', 'first_name')
    else:
        # For caregivers viewing, show all caregivers in the system (could be limited later)
        caregivers = User.objects.filter(role='CAREGIVER').order_by('last_name', 'first_name')

    # Trigger ML Sync only for clinically ready patients (with tests + caregiver)
    for p in clinical_patients:
        try:
            ml_service.sync_patient_ml_data(p)
        except Exception as e:
            # Log error or skip to maintain stability
            pass

    # Metrics: header can show total registered, while averages use only clinical patients
    total_registered_patients = patients_base.count()
    clinical_count = clinical_patients.count()
    
    # Defensive sum for health scores
    health_scores = [getattr(p, 'health_score', 0) or 0 for p in clinical_patients]
    avg_health_score = int(sum(health_scores) / clinical_count) if clinical_count > 0 else 0
    high_risk_count = sum(1 for p in clinical_patients if getattr(p, 'cognitive_risk', '') == 'High Risk')
    
    # Count total evaluations (cognitive tests) completed
    evaluation_count = TestResult.objects.filter(user__in=patients_base).count()

    context = {
        # All registered patients under this doctor/caregiver (for simple name list)
        'patients_all': patients_base.order_by('last_name', 'first_name'),
        # Clinically ready patients (tests completed + caregiver assigned)
        'patients_clinical': clinical_patients,
        'caregivers': caregivers,
        'total_patients_registered': total_registered_patients,
        'total_patients_clinical': clinical_count,
        'avg_health_score': avg_health_score,
        'high_risk_count': high_risk_count,
        'evaluation_count': evaluation_count,
    }

    return render(request, 'dashboard/doctor_dashboard.html', context)


@login_required
@require_POST
def assign_caregiver(request):
    """Handle assigning/removing a caregiver for a patient (form POST from doctor dashboard)."""
    # Only allow doctors (admins) to assign caregivers
    if not safe_has_role(request.user, 'is_doctor'):
        messages.error(request, 'Doctor access required')
        return redirect('dashboard:home')

    patient_id = request.POST.get('patient_id')
    caregiver_id = request.POST.get('caregiver_id')

    from accounts.models import User

    patient = get_object_or_404(User, id=patient_id, doctor=request.user)
    # Ensure patient role matches expectation (tolerant check)
    if getattr(patient, 'role', '').upper() != 'PATIENT':
        messages.error(request, 'Invalid patient selected')
        return redirect('dashboard:doctor_dashboard')

    if caregiver_id:
        caregiver = get_object_or_404(User, id=caregiver_id, doctor=request.user)
        if getattr(caregiver, 'role', '').upper() != 'CAREGIVER':
            messages.error(request, 'Invalid caregiver selected')
            return redirect('dashboard:doctor_dashboard')
        # Use the `caregiver` FK defined on the User model
        patient.caregiver = caregiver
    else:
        patient.caregiver = None

    patient.save()
    messages.success(request, f'Caregiver assignment updated for {patient.get_full_name() or patient.username}')
    return redirect('dashboard:doctor_dashboard')


@login_required
def caregiver_dashboard(request):
    if not safe_has_role(request.user, 'is_caregiver'):
        messages.error(request, 'Caregiver access required')
        return redirect('dashboard:home')

    from accounts.models import User, Reminder
    from ml_module.ml_service import ml_service
    from .models import TestResult, Alert

    # Strict Filtering: Only patients assigned to this caregiver
    patients = User.objects.filter(role='PATIENT', caregiver=request.user).order_by('last_name', 'first_name')
    
    # Trigger ML Sync for these patients to ensure dashboard is fresh
    for p in patients:
        ml_service.sync_patient_ml_data(p)

    total_patients_count = patients.count()

    # Active unread Alerts for assigned patients
    active_alerts_count = Alert.objects.filter(patient__in=patients, is_read=False).count()

    # Recent alerts for these patients
    recent_alerts = Alert.objects.filter(patient__in=patients).order_by('-created_at')[:5]

    # Calculate cohort average health
    health_scores = [getattr(p, 'health_score', 0) or 0 for p in patients]
    avg_health_score = int(sum(health_scores) / total_patients_count) if total_patients_count > 0 else 0

    context = {
        'patients': patients,
        'total_patients': total_patients_count,
        'active_alerts': active_alerts_count,
        'alerts': recent_alerts,
        'avg_health_score': avg_health_score,
    }

    return render(request, 'dashboard/caregiver_dashboard.html', context)


@login_required
def caregiver_patient_detail(request, pk):
    """Secure detailed view for caregivers to monitor assigned patients."""
    if not safe_has_role(request.user, 'is_caregiver'):
        messages.error(request, 'Caregiver access required')
        return redirect('dashboard:home')

    from accounts.models import User
    from .models import TestResult, Alert
    from ml_module.ml_service import ml_service

    # Fetch patient and verify ownership/assignment
    patient = get_object_or_404(User, id=pk, role='PATIENT')
    
    if patient.caregiver != request.user:
        messages.error(request, "Access Denied: This patient is not assigned to you.")
        return redirect('dashboard:caregiver_dashboard')

    # Force a fresh ML sync for the detail page
    ml_data = ml_service.sync_patient_ml_data(patient)

    # History aggregation
    test_history = TestResult.objects.filter(user=patient).order_by('-created_at')
    alert_history = Alert.objects.filter(patient=patient).order_by('-created_at')

    context = {
        'patient': patient,
        'test_history': test_history,
        'alert_history': alert_history,
        'ml_data': ml_data,
        'last_sync': patient.updated_at,
    }
    
    return render(request, 'dashboard/caregiver_patient_detail.html', context)


@login_required
def patient_dashboard(request):
    if not safe_has_role(request.user, 'is_patient'):
        messages.error(request, 'Patient access required')
        return redirect('dashboard:home')

    # Today's reminders/tasks
    from django.utils import timezone
    today = timezone.localdate()
    reminders_today = request.user.reminders.filter(scheduled_for__date=today).order_by('scheduled_for')

    # Machine Learning Integration: Health Score & Recommendations
    from ml_module.ml_service import ml_service
    health_score = ml_service.get_health_score(request.user)
    risk_level, _, features = ml_service.predict_risk(request.user)
    recommendations = ml_service.get_recommendations(risk_level, None, features)[:3]

    if health_score >= 75: health_label = 'Excellent'
    elif health_score >= 50: health_label = 'Good'
    elif health_score >= 30: health_label = 'Fair'
    else: health_label = 'Needs Attention'

    # Fetch available cognitive tests from DB
    from .models import CognitiveTest
    # Seed tests if missing
    if not CognitiveTest.objects.exists():
        # Test 1: Memory Recall (Mixed types)
        CognitiveTest.objects.create(
            name='Memory Recall',
            description='Test your short-term memory with varied questions.',
            questions=[
                {'type': 'choice', 'text': 'Which of these is a fruit?', 'choices': ['Carrot', 'Apple', 'Bread'], 'answer': 'Apple'},
                {'type': 'boolean', 'text': 'Is the sky blue on a clear day?', 'choices': ['True', 'False'], 'answer': 'True'},
                {'type': 'choice', 'text': 'What comes after Monday?', 'choices': ['Sunday', 'Tuesday', 'Wednesday'], 'answer': 'Tuesday'},
                {'type': 'text', 'text': 'Type the number five.', 'answer': '5'}
            ]
        )
        # Test 2: Pattern & Logic
        CognitiveTest.objects.create(
            name='Pattern & Logic',
            description='Simple logic puzzles to keep your mind sharp.',
            questions=[
                {'type': 'choice', 'text': 'Complete the sequence: 2, 4, 6, _', 'choices': ['7', '8', '9'], 'answer': '8'},
                {'type': 'boolean', 'text': 'Is ice hot?', 'choices': ['True', 'False'], 'answer': 'False'},
                {'type': 'choice', 'text': 'Which shape is round?', 'choices': ['Square', 'Circle', 'Triangle'], 'answer': 'Circle'}
            ]
        )
    cognitive_tests = CognitiveTest.objects.all()[:5]

    # Today's scheduled activities (include recurrence)
    ensure_patient_activities(request.user)
    from .models import DailyActivity
    all_activities = DailyActivity.objects.filter(user=request.user).order_by('scheduled_for')
    activities = [a for a in all_activities if a.occurs_on(today)]

    # ... (mood entries logic remains same) ...
    mood_entries = request.user.mood_entries.order_by('-created_at')[:7]

    # ... (form logic remains same) ...
    from .forms import DailyActivityForm
    form = DailyActivityForm()
    if not (safe_has_role(request.user, 'is_doctor') or safe_has_role(request.user, 'is_caregiver')):
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
    latest_test = request.user.test_results.order_by('-created_at').first()
    if latest_test: candidates.append(latest_test.created_at)
    patient_last_activity = max(candidates) if candidates else None

    vitals = {}
    
    # Calculate stats
    from .models import TestResult
    tests_today = TestResult.objects.filter(user=request.user, created_at__date=today).count()

    total_activities = len(activities) + tests_today  # treat each test taken today as an activity
    completed_activities = sum(1 for a in activities if getattr(a, 'completed', False)) + tests_today
    remaining_activities = total_activities - completed_activities

    percent_completed = 0 if total_activities == 0 else int((completed_activities / total_activities) * 100)

    if health_score >= 75: health_label = 'Good'
    elif health_score >= 50: health_label = 'Fair'
    else: health_label = 'Needs attention'

    # Build Schedule (Merge Reminders + Activities + test results, sort by time)
    schedule_items = []
    for r in reminders_today:
        schedule_items.append({'time': r.scheduled_for, 'title': r.title, 'type': 'reminder', 'completed': r.read})
    for a in activities:
        schedule_items.append({'time': a.scheduled_for, 'title': a.name, 'type': 'activity', 'completed': a.completed, 'obj': a})
    # include any cognitive tests taken today
    tests_results_today = TestResult.objects.filter(user=request.user, created_at__date=today)
    for tr in tests_results_today:
        schedule_items.append({'time': tr.created_at, 'title': f"Cognitive Test: {tr.test.name}", 'type': 'test', 'completed': True})
    
    # Sort by time
    schedule_items.sort(key=lambda x: x['time'])

    context = {
        'reminders_today': reminders_today,
        'health_score': health_score,
        'health_label': health_label,
        'cognitive_tests': cognitive_tests,
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
        'recommendations': recommendations,
        'tests_today': tests_today,
    }

    return render(request, 'dashboard/patient_dashboard.html', context)


@login_required
def tests_list(request):
    from .models import CognitiveTest
    tests = CognitiveTest.objects.all()
    return render(request, 'dashboard/tests_list.html', {'tests': tests})


@login_required
def cognitive_tests(request):
    """Simple view to list cognitive tests (alias for tests_list where needed)."""
    from .models import CognitiveTest, TestResult
    tests = CognitiveTest.objects.all()
    # Add status and UI helpers for the professional UI
    for test in tests:
        test.completed = TestResult.objects.filter(user=request.user, test=test).exists()
        # Assign icons and colors based on test name for a premium look
        if 'Memory' in test.name:
            test.icon = 'fa-brain'
            test.color_style = 'background: var(--primary-light); color: var(--primary-color);'
        elif 'Logic' in test.name or 'Pattern' in test.name:
            test.icon = 'fa-puzzle-piece'
            test.color_style = 'background: #fef3c7; color: #d97706;'
        else:
            test.icon = 'fa-notes-medical'
            test.color_style = 'background: #dcfce7; color: #166534;'
    return render(request, 'dashboard/cognitive_tests.html', {'tests': tests})


@login_required
def daily_activities(request):
    """List and manage today's activities for the logged-in patient, including recurring activities."""
    from .models import DailyActivity, TestResult
    from accounts.models import Reminder
    if not safe_has_role(request.user, 'is_patient'):
        messages.error(request, 'Patient access required')
        return redirect('dashboard:home')

    from django.utils import timezone
    today = timezone.localdate()
    
    # 1. Activities
    ensure_patient_activities(request.user)
    all_activities = DailyActivity.objects.filter(user=request.user).order_by('scheduled_for')
    activities_for_today = [a for a in all_activities if a.occurs_on(today)]

    # 2. Reminders
    reminders_today = Reminder.objects.filter(patient=request.user, scheduled_for__date=today)
    
    # 3. Tests
    tests_results_today = TestResult.objects.filter(user=request.user, created_at__date=today)
    tests_today = tests_results_today.count()

    # Build Unified Schedule
    schedule_items = []
    for r in reminders_today:
        schedule_items.append({'time': r.scheduled_for, 'title': r.title, 'type': 'reminder', 'completed': r.read})
    for a in activities_for_today:
        schedule_items.append({'time': a.scheduled_for, 'title': a.name, 'type': 'activity', 'completed': a.completed, 'obj': a})
    for tr in tests_results_today:
        schedule_items.append({'time': tr.created_at, 'title': f"Cognitive Test: {tr.test.name}", 'type': 'test', 'completed': True})
    
    # Sort by time
    schedule_items.sort(key=lambda x: x['time'])

    total = len(activities_for_today) + tests_today
    completed = sum(1 for a in activities_for_today if getattr(a, 'completed', False)) + tests_today
    percent = 0 if total == 0 else int((completed / total) * 100)
    
    context = {
        'schedule': schedule_items,
        'activities': activities_for_today, # keep for legacy if needed
        'total_activities': total,
        'completed_activities': completed,
        'percent_completed': percent,
        'tests_today': tests_today,
    }
    return render(request, 'dashboard/daily_activities.html', context)


@login_required
def activity_create(request):
    """Create a DailyActivity. Staff can create for patients (use ?patient=<id> to prefill)."""
    from .forms import DailyActivityForm
    from accounts.models import User

    # Restrict patients from creating activities
    if safe_has_role(request.user, 'is_patient'):
        messages.error(request, 'Patients cannot create activities.')
        return redirect('dashboard:daily_activities')

    if request.method == 'POST':
        form = DailyActivityForm(request.POST)
        # If non-staff (patient), remove user field from the form and force activity to belong to them
        if not (safe_has_role(request.user, 'is_doctor') or safe_has_role(request.user, 'is_caregiver')):
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
        if patient_id and (safe_has_role(request.user, 'is_doctor') or safe_has_role(request.user, 'is_caregiver')):
            initial['user'] = patient_id
        form = DailyActivityForm(initial=initial)
        if not (safe_has_role(request.user, 'is_doctor') or safe_has_role(request.user, 'is_caregiver')):
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
def take_test(request, test_id):
    """Dispatch view: either per-question flow or specialized game template."""
    from .models import CognitiveTest, TestResult
    test = CognitiveTest.objects.get(id=test_id)

    # Dispatch to specialized templates based on name
    if 'Memory' in test.name:
        return render(request, 'dashboard/test_memory.html', {'test': test})
    elif 'Color' in test.name:
        return render(request, 'dashboard/test_color.html', {'test': test})
    elif 'Mixed' in test.name:
        return render(request, 'dashboard/test_mixed.html', {'test': test})

    # Default per-question flow
    questions = test.questions or []
    total = len(questions)

    # determine current question index from GET or POST
    if request.method == 'POST':
        # get current index from hidden field
        idx = int(request.POST.get('idx', 0))
        key = f'q{idx}'
        answers = request.session.get(f'test_{test_id}_answers', {})
        answers[key] = request.POST.get(key)
        request.session[f'test_{test_id}_answers'] = answers

        # move to next question
        next_idx = idx + 1
        if next_idx >= total:
            # finalize and score
            score = 0
            max_score = total
            for i, q in enumerate(questions):
                user_ans = answers.get(f'q{i}')
                correct = q.get('answer')
                if correct is not None and user_ans is not None and str(user_ans).strip() == str(correct).strip():
                    score += 1
            result = TestResult.objects.create(
                user=request.user,
                test=test,
                score=score,
                max_score=max_score,
                answers=answers,
            )
            # clear session answers
            try:
                del request.session[f'test_{test_id}_answers']
            except KeyError:
                pass
            return redirect('dashboard:test_result', test_id=test.id, result_id=result.id)
        else:
            # redirect to same view with next question index
            return redirect(f"{request.path}?q={next_idx}")

    # GET
    q_index = request.GET.get('q')
    try:
        idx = int(q_index) if q_index is not None else 0
    except ValueError:
        idx = 0
    if idx < 0 or (total and idx >= total):
        idx = 0

    question = questions[idx] if total else None
    answers = request.session.get(f'test_{test_id}_answers', {})
    progress = 0 if total == 0 else int(((idx + 1) / total) * 100) if total else 0
    current_answer = answers.get(f'q{idx}')
    prev_idx = idx - 1 if idx > 0 else None
    is_last = (idx + 1 == total)

    return render(request, 'dashboard/take_test.html', {
        'test': test,
        'question': question,
        'idx': idx,
        'total': total,
        'progress': progress,
        'answers': answers,
        'current_answer': current_answer,
        'prev_idx': prev_idx,
        'is_last': is_last,
    })


@require_POST
@login_required
def save_test_result(request):
    """AJAX view to save results from specialized interactive tests."""
    from django.http import JsonResponse
    import json
    from .models import CognitiveTest, TestResult

    try:
        data = json.loads(request.body)
        test_name = data.get('test_name')
        score = data.get('score', 0)
        max_score = data.get('max_score', 1)

        test = CognitiveTest.objects.filter(name__icontains=test_name).first()
        if not test:
            # Create a placeholder test object if it doesn't exist
            test = CognitiveTest.objects.create(name=test_name, description=f"Specialized {test_name}")

        result = TestResult.objects.create(
            user=request.user,
            test=test,
            score=score,
            max_score=max_score,
            answers={'specialized': True}
        )
        return JsonResponse({'status': 'success', 'result_id': result.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def test_result(request, test_id, result_id):
    from .models import TestResult
    result = TestResult.objects.get(id=result_id, user=request.user, test_id=test_id)
    percent = int((result.score / result.max_score) * 100) if result.max_score > 0 else 0
    return render(request, 'dashboard/test_result.html', {
        'result': result,
        'percent': percent
    })


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
def test_ajax_question(request, test_id):
    """Return rendered HTML for a question (partial) for AJAX insertion."""
    from django.http import JsonResponse
    from .models import CognitiveTest
    test = get_object_or_404(CognitiveTest, id=test_id)
    q_index = int(request.GET.get('q', 0))
    questions = test.questions or []
    total = len(questions)
    if q_index < 0 or (total and q_index >= total):
        return JsonResponse({'ok': False}, status=400)
    question = questions[q_index]
    progress = 0 if total == 0 else int(((q_index + 1) / total) * 100)
    html = render(request, 'dashboard/partials/test_question.html', {'question': question, 'idx': q_index, 'total': total, 'progress': progress}).content.decode('utf-8')
    return JsonResponse({'ok': True, 'html': html, 'progress': progress})


@login_required
def test_ajax_answer(request, test_id):
    """Accept answer via AJAX, store in session, return next question html or final result."""
    from django.http import JsonResponse
    from .models import CognitiveTest, TestResult
    test = get_object_or_404(CognitiveTest, id=test_id)
    questions = test.questions or []
    total = len(questions)
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)
    try:
        idx = int(request.POST.get('idx', 0))
    except (TypeError, ValueError):
        idx = 0
    answer_val = request.POST.get('answer')
    answers = request.session.get(f'test_{test_id}_answers', {})
    answers[f'q{idx}'] = answer_val
    request.session[f'test_{test_id}_answers'] = answers

    next_idx = idx + 1
    if next_idx >= total:
        # finalize
        score = 0
        max_score = total
        for i, q in enumerate(questions):
            user_ans = answers.get(f'q{i}')
            correct = q.get('answer')
            if correct is not None and user_ans is not None and str(user_ans).strip() == str(correct).strip():
                score += 1
        result = TestResult.objects.create(user=request.user, test=test, score=score, max_score=max_score, answers=answers)
        try:
            del request.session[f'test_{test_id}_answers']
        except KeyError:
            pass
        return JsonResponse({'ok': True, 'finished': True, 'score': score, 'max_score': max_score, 'result_id': result.id})
    else:
        # return next question html
        question = questions[next_idx]
        progress = int(((next_idx + 1) / total) * 100)
        html = render(request, 'dashboard/partials/test_question.html', {'question': question, 'idx': next_idx, 'total': total, 'progress': progress}).content.decode('utf-8')
        return JsonResponse({'ok': True, 'finished': False, 'html': html, 'progress': progress})


@login_required
def patient_dashboard_data_ajax(request):
    """Return patient-specific dashboard summary data for charts and live updates."""
    from django.http import JsonResponse
    from django.utils import timezone
    from .models import DailyActivity, MoodEntry, TestResult
    import datetime

    if not safe_has_role(request.user, 'is_patient'):
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

    # Cognitive progress - last 10 test results (score percentage)
    results = list(request.user.test_results.order_by('-created_at')[:10])[::-1]
    cog_labels = [r.created_at.date().isoformat() for r in results]
    cog_data = [round((r.score / r.max_score) * 100, 2) if r.max_score else 0 for r in results]

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

    # Cognitive performance (average of last 10 results)
    cog_values = [round((r.score / r.max_score) * 100, 2) for r in request.user.test_results.order_by('-created_at')[:10] if r.max_score]
    cognitive_avg = int(sum(cog_values) / len(cog_values)) if cog_values else None

    # Mood normalized 1-5 -> 0-100
    mood_vals = [v for v in mood_data if v is not None]
    mood_avg = None
    if mood_vals:
        mood_avg = int(((sum(mood_vals) / len(mood_vals)) - 1) / 4 * 100)

    # Aggregate health score (weighted average of available components)
    components = {
        'medication': med_rate,
        'exercise': exercise_rate,
        'cognitive': cognitive_avg,
        'sleep': sleep_rate,
        'social': social_rate,
        'mood': mood_avg,
    }
    weights = {'medication': 0.25, 'exercise': 0.2, 'cognitive': 0.3, 'sleep': 0.15, 'social': 0.1, 'mood': 0.2}
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
    if cognitive_avg is not None and cognitive_avg < 60:
        recs.append('Try short cognitive exercises to improve memory and attention.')
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
        'cognitive': {'labels': cog_labels, 'data': cog_data},
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
    if safe_has_role(request.user, 'is_patient'):
        return JsonResponse({'ok': False, 'error': 'Permission denied'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)

    post = request.POST.copy()
    form = DailyActivityForm(post)
    # If patient, don't allow setting user via form
    if not (safe_has_role(request.user, 'is_doctor') or safe_has_role(request.user, 'is_caregiver')):
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


# --- Machine Learning API Endpoints ---

from django.http import JsonResponse
from ml_module.ml_service import ml_service
from ml_module.anomaly_detection import detect_anomalies
from .models import Alert
import json


@login_required
def predict_risk_api(request, patient_id=None):
    """
    POST /api/predict-risk/
    Predicts cognitive decline risk for the patient.
    """
    user = request.user
    if patient_id and (safe_has_role(user, 'is_doctor') or safe_has_role(user, 'is_caregiver')):
        from accounts.models import User
        target_user = get_object_or_404(User, id=patient_id)
    else:
        target_user = user

    risk_level, confidence, features = ml_service.predict_risk(target_user)
    recommendations = ml_service.get_recommendations(risk_level, None, features)

    # Trigger Alert if Risk is High
    if risk_level == 'High Risk' and getattr(target_user, 'caregiver', None):
        Alert.objects.get_or_create(
            caregiver=target_user.caregiver,
            patient=target_user,
            alert_type='health',
            message=f"CRITICAL: High cognitive decline risk predicted for {target_user.get_full_name()} (Confidence: {confidence:.1f}%)",
            is_read=False
        )

    return JsonResponse({
        'status': 'success',
        'patient_id': target_user.id,
        'risk_level': risk_level,
        'confidence': round(confidence, 1),
        'recommendations': recommendations,
        'trend': 'Stable' # Placeholder for trend logic
    })


@login_required
def detect_anomaly_api(request, patient_id=None):
    """
    POST /api/detect-anomaly/
    Detects unusual behavioral patterns.
    """
    user = request.user
    if patient_id and (safe_has_role(user, 'is_doctor') or safe_has_role(user, 'is_caregiver')):
        from accounts.models import User
        target_user = get_object_or_404(User, id=patient_id)
    else:
        target_user = user

    # In a real system, we'd pull historical data for the Isolation Forest
    # For now, we use the detect_anomalies function which has a heuristic fallback
    anomaly_result = detect_anomalies(target_user)

    if anomaly_result['is_anomaly'] and getattr(target_user, 'caregiver', None):
        Alert.objects.get_or_create(
            caregiver=target_user.caregiver,
            patient=target_user,
            alert_type='other',
            message=f"ANOMALY DETECTED: {', '.join(anomaly_result['reasons'])} for {target_user.get_full_name()}",
            is_read=False
        )

    return JsonResponse({
        'status': 'success',
        'patient_id': target_user.id,
        'is_anomaly': anomaly_result['is_anomaly'],
        'severity': anomaly_result['severity'],
        'reasons': anomaly_result['reasons']
    })


@login_required
def health_score_api(request, patient_id=None):
    """
    GET /api/health-score/
    Returns the composite cognitive health score.
    """
    user = request.user
    if patient_id and (safe_has_role(user, 'is_doctor') or safe_has_role(user, 'is_caregiver')):
        from accounts.models import User
        target_user = get_object_or_404(User, id=patient_id)
    else:
        target_user = user

    score = ml_service.get_health_score(target_user)
    
    return JsonResponse({
        'status': 'success',
        'patient_id': target_user.id,
        'health_score': score,
        'components': {
            'cognitive': '40%',
            'activity': '25%',
            'medication': '15%',
            'mood': '10%',
            'stability': '10%'
        }
    })
