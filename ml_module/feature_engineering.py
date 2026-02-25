import pandas as pd
import numpy as np
from django.utils import timezone
from datetime import timedelta
from dashboard.models import TestResult, DailyActivity, MoodEntry

MOOD_MAP = {
    'very_happy': 5,
    'happy': 4,
    'neutral': 3,
    'sad': 2,
    'very_sad': 1,
    'anxious': 2,
}

def get_patient_features(user, days=30):
    """
    Extracts features for a specific patient over the last 'days' days.
    Returns a dictionary of features.
    """
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)

    # 1. Cognitive Test Features
    test_results = TestResult.objects.filter(user=user, created_at__range=(start_date, end_date)).order_by('created_at')
    
    avg_cognitive_score = 0
    cognitive_decline_rate = 0
    
    if test_results.exists():
        scores = [float(r.score) / r.max_score for r in test_results]
        avg_cognitive_score = np.mean(scores)
        
        if len(scores) > 1:
            # Simple slope calculation
            cognitive_decline_rate = scores[-1] - scores[0]
    
    # 2. Activity Features
    activities = DailyActivity.objects.filter(user=user, scheduled_for__range=(start_date, end_date))
    
    total_activities = activities.count()
    completed_activities = activities.filter(completed=True).count()
    activity_consistency = completed_activities / total_activities if total_activities > 0 else 1.0
    
    med_activities = activities.filter(activity_type='medication')
    total_meds = med_activities.count()
    missed_meds = med_activities.filter(completed=False).count()
    missed_med_freq = missed_meds / total_meds if total_meds > 0 else 0
    
    meal_activities = activities.filter(activity_type='meal')
    total_meals = meal_activities.count()
    skipped_meals = meal_activities.filter(completed=False).count()
    meal_skipping_freq = skipped_meals / total_meals if total_meals > 0 else 0

    # 3. Mood Features
    moods = MoodEntry.objects.filter(user=user, created_at__range=(start_date, end_date))
    
    mood_values = [MOOD_MAP.get(m.mood, 3) for m in moods]
    avg_mood = np.mean(mood_values) if mood_values else 3
    mood_instability = np.std(mood_values) if len(mood_values) > 1 else 0

    return {
        'avg_cognitive_score': avg_cognitive_score,
        'cognitive_decline_rate': cognitive_decline_rate,
        'missed_med_freq': missed_med_freq,
        'meal_skipping_freq': meal_skipping_freq,
        'activity_consistency': activity_consistency,
        'avg_mood': avg_mood,
        'mood_instability': mood_instability,
        'total_data_points': total_activities + test_results.count() + moods.count()
    }

def get_training_data(users):
    """
    Generates a DataFrame for training from a list of users.
    In a real scenario, this would include labels (Risk Level).
    For now, we'll generate synthetic labels based on heuristics for demonstration.
    """
    data = []
    for user in users:
        features = get_patient_features(user, days=90)
        
        # Heuristic for demo labels: 
        # High Risk if decline is sharp or med/meal skipping is high
        risk_score = (
            (1 - features['avg_cognitive_score']) * 0.4 +
            abs(features['cognitive_decline_rate']) * 0.3 +
            features['missed_med_freq'] * 0.2 +
            features['meal_skipping_freq'] * 0.1
        )
        
        if risk_score > 0.6:
            label = 'High Risk'
        elif risk_score > 0.3:
            label = 'Moderate Risk'
        else:
            label = 'Low Risk'
            
        features['risk_level'] = label
        data.append(features)
        
    return pd.DataFrame(data)
