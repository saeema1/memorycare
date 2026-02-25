from sklearn.ensemble import IsolationForest
import numpy as np
import pandas as pd
from .feature_engineering import get_patient_features

def detect_anomalies(user, historical_data=None):
    """
    Detects if the current behavior of the user is an anomaly compared to history.
    If historical_data is provided (a list of feature dicts), it fits the model on it.
    """
    # Get current features
    current_features = get_patient_features(user, days=3) # Short window for current behavior
    
    if historical_data is None or len(historical_data) < 10:
        # Not enough data to fit IsolationForest reliably
        # Fallback to simple statistical threshold
        return {
            'is_anomaly': False,
            'severity': 'Low',
            'reason': 'Insufficient historical data for anomaly detection'
        }

    # Prepare data for IsolationForest
    df = pd.DataFrame(historical_data)
    # Drop non-numeric and label columns if any
    numeric_df = df.select_dtypes(include=[np.number])
    
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(numeric_df)
    
    # Predict on current features
    current_df = pd.DataFrame([current_features]).select_dtypes(include=[np.number])
    prediction = model.predict(current_df)
    
    is_anomaly = prediction[0] == -1
    
    # Calculate severity based on distance from average
    score = model.decision_function(current_df)[0]
    severity = "High" if score < -0.2 else "Moderate" if is_anomaly else "Low"

    reasons = []
    if current_features['missed_med_freq'] > 0.5:
        reasons.append("Frequent missed medications")
    if current_features['meal_skipping_freq'] > 0.5:
        reasons.append("Frequent skipped meals")
    if current_features['cognitive_decline_rate'] < -0.2:
        reasons.append("Sharp cognitive decline detected")

    return {
        'is_anomaly': is_anomaly,
        'severity': severity,
        'score': float(score),
        'reasons': reasons if is_anomaly else []
    }
