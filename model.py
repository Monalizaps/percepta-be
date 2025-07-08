import pandas as pd
from pyod.models.hbos import HBOS
import joblib
import json
from pathlib import Path
from backend.service import preprocess_auth_log, explain_anomaly

MODEL_PATH = "data/hbos_model.pkl"
LOG_PATH = "data/anomalies_detected.json"

# Carrega modelo treinado
hbos_model: HBOS = joblib.load(MODEL_PATH)

def detect_anomaly(log):
    log_df = preprocess_auth_log(log)
    is_anomaly = hbos_model.predict(log_df)[0]

    if is_anomaly:
        feature = explain_anomaly(log_df, hbos_model)

        # Salva log no JSON
        log_entry = {
            "user_id": log.user_id,
            "timestamp": log.timestamp,
            "ip_address": log.ip_address,
            "location": log.location,
            "device": log.device,
            "reason": f"Possível anomalia detectada na feature: {feature}"
        }

        save_log(log_entry)

        return {
            "is_anomaly": True,
            "message": "Anomalia detectada",
            "feature": feature
        }

    return {
        "is_anomaly": False,
        "message": "Comportamento normal",
        "feature": None
    }

def save_log(entry: dict):
    path = Path(LOG_PATH)
    logs = []

    if path.exists():
        try:
            with open(path, "r") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []

    logs.append(entry)

    with open(path, "w") as f:
        json.dump(logs, f, indent=2)
