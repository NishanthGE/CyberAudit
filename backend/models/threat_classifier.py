"""
Threat Classification Module — Random Forest Inference
"""

import numpy as np
import joblib
import os
from typing import List, Dict

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))

LABEL_MAP = {0: "Normal", 1: "Probe", 2: "DoS", 3: "R2L", 4: "U2R"}

_classifier = None
_scaler = None


def _load_models():
    global _classifier, _scaler
    if _classifier is None:
        clf_path = os.path.join(MODELS_DIR, "threat_classifier.pkl")
        scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
        if not os.path.exists(clf_path):
            raise FileNotFoundError(
                "threat_classifier.pkl not found. Run: python models/train_models.py"
            )
        _classifier = joblib.load(clf_path)
        _scaler = joblib.load(scaler_path)


def classify_threat(features: List[float]) -> Dict:
    """
    Classify a network event into threat categories.

    Returns:
      - label: str (Normal / Probe / DoS / R2L / U2R)
      - label_id: int
      - confidence: float (0.0–1.0 for predicted class)
      - probabilities: dict of all class probabilities
    """
    _load_models()
    X = np.array(features, dtype=float).reshape(1, -1)
    X_scaled = _scaler.transform(X)

    label_id = int(_classifier.predict(X_scaled)[0])
    proba = _classifier.predict_proba(X_scaled)[0]

    probabilities = {LABEL_MAP[i]: float(proba[i]) for i in range(len(proba))}
    label = LABEL_MAP[label_id]
    confidence = float(proba[label_id])

    return {
        "label": label,
        "label_id": label_id,
        "confidence": confidence,
        "probabilities": probabilities,
    }
