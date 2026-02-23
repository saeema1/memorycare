def calculate_health_score(user):
    """
    Calculate a health score (0-100) based on:
    1. Reminders adherence (100%)
    """
    score = 0
    
    # 1. Reminders (50%)
    total_reminders = user.reminders.count()
    reminders_score = 80 # Default
    if total_reminders > 0:
        unread = user.reminders.filter(read=False).count()
        reminders_score = int(((total_reminders - unread) / total_reminders) * 100)
    
    final_score = reminders_score
    return final_score

def generate_caregiver_alerts(caregiver):
    """
    Generate dynamic alerts for a caregiver based on their patients' real-time data.
    Returns a list of dicts: {patient, type, message, level, time}
    """
    from .models import DailyActivity, MoodEntry
    from django.utils import timezone
    import datetime
    
    alerts = []
    patients = caregiver.patients_under_caregiver.all()
    now = timezone.now()
    today = now.date()
    
    for patient in patients:
        # 1. Missed Medication (Past due and not completed)
        missed_meds = DailyActivity.objects.filter(
            user=patient, 
            activity_type='medication',
            completed=False,
            scheduled_for__lt=now
        ).order_by('-scheduled_for')
        
        for med in missed_meds:
            if med.scheduled_for.date() >= today - datetime.timedelta(days=1):
                alerts.append({
                    'patient': patient,
                    'type': 'medication', 
                    'title': 'Missed Medication',
                    'message': f"{patient.first_name} missed '{med.name}' scheduled for {med.scheduled_for.strftime('%H:%M')}.",
                    'level': 'critical',
                    'time': med.scheduled_for
                })

        # 2. Missed Activities
        missed_acts = DailyActivity.objects.filter(
            user=patient,
            completed=False,
            scheduled_for__lt=now
        ).exclude(activity_type='medication').order_by('-scheduled_for')
        
        count_missed = 0
        for act in missed_acts:
             if act.scheduled_for.date() == today:
                 count_missed += 1
        
        if count_missed >= 3:
             alerts.append({
                'patient': patient,
                'type': 'activity',
                'title': 'Multiple Missed Activities',
                'message': f"{patient.first_name} has missed {count_missed} activities today.",
                'level': 'warning',
                'time': now
            })

        # 3. Sudden Mood Change
        recent_moods = MoodEntry.objects.filter(user=patient).order_by('-created_at')[:3]
        if len(recent_moods) >= 2:
            if recent_moods[0].mood in ['sad', 'very_sad', 'anxious']:
                alerts.append({
                    'patient': patient,
                    'type': 'mood',
                    'title': 'Negative Mood Detected',
                    'message': f"{patient.first_name} reported feeling '{recent_moods[0].get_mood_display()}' recently.",
                    'level': 'warning',
                    'time': recent_moods[0].created_at
                })



    alerts.sort(key=lambda x: x['time'], reverse=True)
    return alerts




