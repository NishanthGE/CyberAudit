"""
Anomaly Detection Module — Isolation Forest Inference
"""

import numpy as np
import joblib
import os
from typing import List

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))

_anomaly_model = None
_scaler = None


def _load_models():
    global _anomaly_model, _scaler
    if _anomaly_model is None:
        model_path = os.path.join(MODELS_DIR, "anomaly_model.pkl")
        scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                "anomaly_model.pkl not found. Run: python models/train_models.py"
            )
        _anomaly_model = joblib.load(model_path)
        _scaler = joblib.load(scaler_path)


def detect_anomaly(features: List[float]) -> dict:
    """
    Given a feature vector, return:
      - is_anomaly: bool
      - anomaly_score: float (-1 = anomaly, 1 = normal, continuous in between)
      - normalized_score: float (0.0 = normal, 1.0 = max anomaly)
    """
    _load_models()
    X = np.array(features, dtype=float).reshape(1, -1)
    X_scaled = _scaler.transform(X)

    # decision_function returns negative values for anomalies
    raw_score = float(_anomaly_model.decision_function(X_scaled)[0])
    prediction = int(_anomaly_model.predict(X_scaled)[0])  # -1 or 1

    # Normalize: map raw_score from roughly [-0.5, 0.5] → [0, 1] inverted
    # More negative = more anomalous → higher normalized score
    normalized_score = float(np.clip(1.0 - (raw_score + 0.5) / 1.0, 0.0, 1.0))

    return {
        "is_anomaly": prediction == -1,
        "raw_score": raw_score,
        "normalized_score": normalized_score,
    }
