import joblib
import os
import django
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memorycare.settings')
django.setup()

from sklearn.ensemble import RandomForestClassifier
from ml_module.feature_engineering import get_training_data
from accounts.models import User

MODEL_PATH = os.path.join('ml_models', 'cognitive_model.pkl')

def train_risk_model():
    """
    Simulates training of the cognitive decline risk model.
    In a real system, this would use labeled historical data.
    """
    patients = User.objects.filter(role='PATIENT')
    if patients.count() < 3:
        # Not enough data to train, create a dummy model for demo
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        # Dummy data: [avg_score, decline, med_freq, meal_freq, activity, mood, mood_std]
        X = [
            [0.9, 0.0, 0.0, 0.0, 1.0, 4.5, 0.1], # Low
            [0.4, -0.3, 0.6, 0.4, 0.5, 2.0, 1.5], # High
            [0.6, -0.1, 0.2, 0.2, 0.8, 3.5, 0.5], # Moderate
        ]
        y = ['Low Risk', 'High Risk', 'Moderate Risk']
        model.fit(X, y)
    else:
        df = get_training_data(patients)
        X = df.drop(['risk_level', 'total_data_points'], axis=1)
        y = df['risk_level']
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return model

if __name__ == "__main__":
    train_risk_model()
