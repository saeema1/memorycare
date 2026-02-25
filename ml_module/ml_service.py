import joblib
import os
import pandas as pd
import numpy as np
from .feature_engineering import get_patient_features
from .anomaly_detection import detect_anomalies
from .model_training import train_risk_model, MODEL_PATH

class MLService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLService, cls).__new__(cls)
        return cls._instance

    def get_model(self):
        if self._model is None:
            if not os.path.exists(MODEL_PATH):
                self._model = train_risk_model()
            else:
                try:
                    self._model = joblib.load(MODEL_PATH)
                except:
                    self._model = train_risk_model()
        return self._model

    def predict_risk(self, user):
        """Returns (Risk Level, Confidence Score, Features)"""
        model = self.get_model()
        features = get_patient_features(user, days=30)
        
        # Prepare for prediction
        X = pd.DataFrame([features]).drop(['total_data_points'], axis=1, errors='ignore')
        X_numeric = X.select_dtypes(include=[np.number])
        
        try:
            prediction = model.predict(X_numeric)[0]
            probs = model.predict_proba(X_numeric)[0]
            confidence = max(probs) * 100
        except Exception:
            # Fallback to heuristic if model fails
            prediction = "Moderate Risk"
            confidence = 50.0
            
        return prediction, confidence, features

    def sync_patient_ml_data(self, user):
        """
        Runs inference and syncs all ML fields to the database.
        Also triggers automated alerts for high risk.
        """
        risk_level, confidence, features = self.predict_risk(user)
        
        # Calculate sub-scores (0-100)
        memory_score = int(features['avg_cognitive_score'] * 100)
        
        # Behavior score: compound of activity compliance and mood stability
        # Weights: consistency (60%), med adherence (20%), mood stability (20%)
        behavior_score = int(
            (features['activity_consistency'] * 60) +
            ((1 - features['missed_med_freq']) * 20) +
            (max(0, 1 - features['mood_instability']/2) * 20)
        )
        
        health_score = self.get_health_score(user)
        
        # Persist to User model
        user.cognitive_risk = risk_level
        user.memory_score = memory_score
        user.behaviour_score = behavior_score
        user.health_score = int(health_score)
        user.save()
        
        # Auto-Alert for High Risk
        if risk_level == 'High Risk':
            from dashboard.models import Alert
            # Check if an unread high-risk alert already exists today to avoid spam
            from django.utils import timezone
            today = timezone.now().date()
            existing = Alert.objects.filter(
                patient=user, 
                alert_type='health', 
                created_at__date=today,
                is_read=False
            ).exists()
            
            if not existing:
                Alert.objects.create(
                    patient=user,
                    caregiver=user.caregiver, # Might be None, that's okay for system alerts
                    alert_type='health',
                    message=f"CRITICAL: High cognitive risk detected for {user.get_full_name()}. Health Score: {health_score}%. Please review immediately."
                )
        
        return {
            'risk_level': risk_level,
            'memory_score': memory_score,
            'behaviour_score': behavior_score,
            'health_score': health_score
        }

    def get_health_score(self, user):
        """Calculates composite cognitive health score (0-100)"""
        f = get_patient_features(user, days=30)
        
        cog_score = min(f['avg_cognitive_score'] * 100, 100) * 0.40
        act_score = min(f['activity_consistency'] * 100, 100) * 0.25
        med_score = min((1 - f['missed_med_freq']) * 100, 100) * 0.15 if 'miss_med_freq' in f else 15
        mood_score = min((f['avg_mood'] / 5) * 100, 100) * 0.10
        stability = max(0, 1 - (f['mood_instability'] / 2)) * 100
        stab_score = stability * 0.10
        
        total_score = cog_score + act_score + med_score + mood_score + stab_score
        return round(total_score, 1)

    def get_recommendations(self, risk_level, anomalies, features):
        """Generates personalized recommendations based on ML output"""
        recs = []
        
        if risk_level == 'High Risk' or risk_level == 'Moderate Risk':
            recs.append("Suggest increasing mental stimulation with more complex cognitive exercises.")
            recs.append("Schedule a dedicated cognitive review session with a doctor.")
            
        if features['missed_med_freq'] > 0.2:
            recs.append("Medication adherence is dropping. Consider setting more prominent alerts.")
            
        if features['meal_skipping_freq'] > 0.2:
            recs.append("Repeatedly skipped meals detected. suggest routine adjustment for nourishment.")

        if features['mood_instability'] > 1.0:
            recs.append("Mood fluctuations are higher than normal. suggest emotional support activities.")
            
        if not recs:
            recs.append("Patient is showing stable patterns. Continue current care plan.")
            
        return recs

# Global singleton
ml_service = MLService()
