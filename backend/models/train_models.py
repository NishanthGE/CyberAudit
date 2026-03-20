"""
ML Model Training Script — AI Blockchain Audit Log System

Trains:
  1. Isolation Forest — anomaly detection (unsupervised)
  2. Random Forest Classifier — threat classification (Normal/Probe/DoS/R2L/U2R)

Uses a synthetic NSL-KDD-style dataset with realistic network traffic features.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
import random

# ─── Seed ───────────────────────────────────────────────────────────────────
np.random.seed(42)
random.seed(42)

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Feature Columns (NSL-KDD inspired) ─────────────────────────────────────
FEATURES = [
    "duration",          # seconds
    "src_bytes",         # bytes from src to dst
    "dst_bytes",         # bytes from dst to src
    "count",             # connections to same host in 2s window
    "srv_count",         # connections to same service in 2s window
    "serror_rate",       # % connections with SYN errors
    "srv_serror_rate",   # % connections to same service with SYN errors
    "rerror_rate",       # % connections with REJ errors
    "same_srv_rate",     # % connections to same service
    "diff_srv_rate",     # % connections to different services
    "dst_host_count",    # connections to same dst host
    "dst_host_srv_count",# connections to same dst host and service
    "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate",
    "dst_host_serror_rate",
    "hour_of_day",       # 0-23
    "failed_logins",     # number of failed login attempts
    "is_root_shell",     # 0/1 — whether root shell obtained
    "num_file_creations",
    "num_access_files",
]

LABEL_MAP = {0: "Normal", 1: "Probe", 2: "DoS", 3: "R2L", 4: "U2R"}
LABEL_REVERSE = {v: k for k, v in LABEL_MAP.items()}


def generate_normal_samples(n=4000):
    """Normal traffic — business hours, low error rates, moderate traffic."""
    hours = np.random.choice(range(8, 18), n)  # business hours
    return pd.DataFrame({
        "duration":                  np.random.exponential(2, n),
        "src_bytes":                 np.random.lognormal(8, 1.5, n),
        "dst_bytes":                 np.random.lognormal(7, 1.5, n),
        "count":                     np.random.randint(1, 15, n),
        "srv_count":                 np.random.randint(1, 12, n),
        "serror_rate":               np.random.beta(1, 20, n),
        "srv_serror_rate":           np.random.beta(1, 20, n),
        "rerror_rate":               np.random.beta(1, 15, n),
        "same_srv_rate":             np.random.beta(8, 2, n),
        "diff_srv_rate":             np.random.beta(1, 8, n),
        "dst_host_count":            np.random.randint(1, 30, n),
        "dst_host_srv_count":        np.random.randint(1, 25, n),
        "dst_host_same_srv_rate":    np.random.beta(7, 2, n),
        "dst_host_diff_srv_rate":    np.random.beta(1, 7, n),
        "dst_host_serror_rate":      np.random.beta(1, 25, n),
        "hour_of_day":               hours,
        "failed_logins":             np.random.choice([0, 1], n, p=[0.95, 0.05]),
        "is_root_shell":             np.zeros(n),
        "num_file_creations":        np.random.randint(0, 3, n),
        "num_access_files":          np.random.randint(0, 5, n),
        "label":                     0,
    })


def generate_probe_samples(n=1000):
    """Probe attacks — port scanning, high connection counts, many services."""
    return pd.DataFrame({
        "duration":                  np.random.exponential(0.5, n),
        "src_bytes":                 np.random.lognormal(4, 1, n),
        "dst_bytes":                 np.random.lognormal(3, 1, n),
        "count":                     np.random.randint(200, 512, n),
        "srv_count":                 np.random.randint(100, 512, n),
        "serror_rate":               np.random.beta(3, 2, n),
        "srv_serror_rate":           np.random.beta(3, 2, n),
        "rerror_rate":               np.random.beta(2, 3, n),
        "same_srv_rate":             np.random.beta(1, 3, n),
        "diff_srv_rate":             np.random.beta(5, 2, n),
        "dst_host_count":            np.random.randint(200, 256, n),
        "dst_host_srv_count":        np.random.randint(1, 20, n),
        "dst_host_same_srv_rate":    np.random.beta(2, 5, n),
        "dst_host_diff_srv_rate":    np.random.beta(5, 2, n),
        "dst_host_serror_rate":      np.random.beta(3, 2, n),
        "hour_of_day":               np.random.randint(0, 24, n),
        "failed_logins":             np.random.choice([0, 1], n, p=[0.6, 0.4]),
        "is_root_shell":             np.zeros(n),
        "num_file_creations":        np.random.randint(0, 2, n),
        "num_access_files":          np.random.randint(0, 3, n),
        "label":                     1,
    })


def generate_dos_samples(n=1500):
    """DoS attacks — huge src_bytes, very high count, high error rates."""
    return pd.DataFrame({
        "duration":                  np.random.exponential(0.1, n),
        "src_bytes":                 np.random.lognormal(12, 2, n),
        "dst_bytes":                 np.random.exponential(10, n),
        "count":                     np.random.randint(400, 512, n),
        "srv_count":                 np.random.randint(400, 512, n),
        "serror_rate":               np.random.beta(8, 1, n),
        "srv_serror_rate":           np.random.beta(8, 1, n),
        "rerror_rate":               np.random.beta(5, 2, n),
        "same_srv_rate":             np.random.beta(9, 1, n),
        "diff_srv_rate":             np.random.beta(1, 9, n),
        "dst_host_count":            np.random.randint(200, 256, n),
        "dst_host_srv_count":        np.random.randint(200, 256, n),
        "dst_host_same_srv_rate":    np.random.beta(9, 1, n),
        "dst_host_diff_srv_rate":    np.random.beta(1, 9, n),
        "dst_host_serror_rate":      np.random.beta(8, 1, n),
        "hour_of_day":               np.random.randint(0, 24, n),
        "failed_logins":             np.random.randint(0, 5, n),
        "is_root_shell":             np.zeros(n),
        "num_file_creations":        np.zeros(n),
        "num_access_files":          np.zeros(n),
        "label":                     2,
    })


def generate_r2l_samples(n=500):
    """R2L — unauthorized remote access, failed logins, off-hours activity."""
    hours = np.concatenate([
        np.random.choice(range(0, 6), n // 2),
        np.random.choice(range(22, 24), n // 2),
    ])
    np.random.shuffle(hours)
    return pd.DataFrame({
        "duration":                  np.random.exponential(5, n),
        "src_bytes":                 np.random.lognormal(6, 1.5, n),
        "dst_bytes":                 np.random.lognormal(5, 1.5, n),
        "count":                     np.random.randint(1, 20, n),
        "srv_count":                 np.random.randint(1, 15, n),
        "serror_rate":               np.random.beta(2, 5, n),
        "srv_serror_rate":           np.random.beta(2, 5, n),
        "rerror_rate":               np.random.beta(4, 3, n),
        "same_srv_rate":             np.random.beta(5, 3, n),
        "diff_srv_rate":             np.random.beta(2, 5, n),
        "dst_host_count":            np.random.randint(1, 30, n),
        "dst_host_srv_count":        np.random.randint(1, 20, n),
        "dst_host_same_srv_rate":    np.random.beta(4, 3, n),
        "dst_host_diff_srv_rate":    np.random.beta(2, 4, n),
        "dst_host_serror_rate":      np.random.beta(2, 5, n),
        "hour_of_day":               hours[:n],
        "failed_logins":             np.random.randint(3, 20, n),
        "is_root_shell":             np.zeros(n),
        "num_file_creations":        np.random.randint(0, 5, n),
        "num_access_files":          np.random.randint(5, 50, n),
        "label":                     3,
    })


def generate_u2r_samples(n=200):
    """U2R — privilege escalation, root shell obtained, file creation."""
    return pd.DataFrame({
        "duration":                  np.random.exponential(10, n),
        "src_bytes":                 np.random.lognormal(7, 1, n),
        "dst_bytes":                 np.random.lognormal(6, 1, n),
        "count":                     np.random.randint(1, 10, n),
        "srv_count":                 np.random.randint(1, 8, n),
        "serror_rate":               np.random.beta(1, 10, n),
        "srv_serror_rate":           np.random.beta(1, 10, n),
        "rerror_rate":               np.random.beta(1, 10, n),
        "same_srv_rate":             np.random.beta(6, 3, n),
        "diff_srv_rate":             np.random.beta(1, 6, n),
        "dst_host_count":            np.random.randint(1, 20, n),
        "dst_host_srv_count":        np.random.randint(1, 15, n),
        "dst_host_same_srv_rate":    np.random.beta(6, 3, n),
        "dst_host_diff_srv_rate":    np.random.beta(1, 6, n),
        "dst_host_serror_rate":      np.random.beta(1, 10, n),
        "hour_of_day":               np.random.randint(0, 24, n),
        "failed_logins":             np.random.randint(0, 3, n),
        "is_root_shell":             np.ones(n),
        "num_file_creations":        np.random.randint(10, 50, n),
        "num_access_files":          np.random.randint(10, 100, n),
        "label":                     4,
    })


def train_models():
    print("=" * 60)
    print("  AI Threat Detection — Model Training")
    print("=" * 60)

    # 1. Generate synthetic dataset
    print("\n[1/5] Generating synthetic NSL-KDD-style dataset...")
    df = pd.concat([
        generate_normal_samples(4000),
        generate_probe_samples(1000),
        generate_dos_samples(1500),
        generate_r2l_samples(500),
        generate_u2r_samples(200),
    ], ignore_index=True).sample(frac=1, random_state=42)

    print(f"      Dataset size: {len(df)} samples")
    print(f"      Class distribution:\n{df['label'].map(LABEL_MAP).value_counts().to_string()}")

    X = df[FEATURES].values
    y = df["label"].values

    # 2. Feature scaling
    print("\n[2/5] Fitting StandardScaler...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))
    print("      Saved: scaler.pkl")

    # 3. Train Isolation Forest on normal traffic only
    print("\n[3/5] Training Isolation Forest (anomaly detection)...")
    X_normal = X_scaled[y == 0]
    iso_forest = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        max_samples="auto",
        random_state=42,
        n_jobs=-1,
    )
    iso_forest.fit(X_normal)
    joblib.dump(iso_forest, os.path.join(MODELS_DIR, "anomaly_model.pkl"))
    
    # Evaluate on full dataset
    predictions = iso_forest.predict(X_scaled)
    anomaly_rate = float((predictions == -1).mean())
    print(f"      Saved: anomaly_model.pkl")
    print(f"      Anomaly rate on full dataset: {anomaly_rate:.2%}")

    # 4. Train Random Forest classifier
    print("\n[4/5] Training Random Forest classifier (threat classification)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    rf_classifier = RandomForestClassifier(
        n_estimators=300,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    rf_classifier.fit(X_train, y_train)
    joblib.dump(rf_classifier, os.path.join(MODELS_DIR, "threat_classifier.pkl"))

    y_pred = rf_classifier.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"      Saved: threat_classifier.pkl")
    print(f"      Test accuracy: {accuracy:.4f}")
    print("\n      Classification Report:")
    target_names = [LABEL_MAP[i] for i in sorted(LABEL_MAP.keys())]
    print(classification_report(y_test, y_pred, target_names=target_names))

    # 5. Save feature metadata
    print("[5/5] Saving feature metadata...")
    import json
    metadata = {
        "features": FEATURES,
        "label_map": LABEL_MAP,
        "n_features": len(FEATURES),
    }
    with open(os.path.join(MODELS_DIR, "model_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    print("      Saved: model_metadata.json")

    print("\n" + "=" * 60)
    print("  All models trained and saved successfully!")
    print("=" * 60)


if __name__ == "__main__":
    train_models()
