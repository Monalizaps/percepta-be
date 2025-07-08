from fastapi import APIRouter, HTTPException
from schema import AuthLog
from service import preprocess_auth_log
from pyod.models.hbos import HBOS
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import os
from db import get_connection



router = APIRouter()

# 🔧 Modelo HBOS global para reuso simples
model = HBOS()
trained = False
features_used = ['hour', 'day_of_week', 'ip_risk_score', 'action_weight']

@router.post("/detect")
def detect(log: AuthLog):
    global trained

    df_input = preprocess_auth_log([log.dict()], fit=False)

    if not trained:
        df_train = pd.read_csv(os.path.join("data", "normal_logs_csv__simulado_.csv"))
        df_train_proc = preprocess_auth_log(df_train.to_dict(orient="records"), fit=True)
        model.fit(df_train_proc[features_used])
        trained = True

    score = model.decision_function(df_input[features_used])[0]
    label = model.predict(df_input[features_used])[0]

    feature_weights = abs(df_input[features_used].iloc[0] - model.decision_scores_.mean())
    top_feature = feature_weights.idxmax()

    result = {
        "user_id": log.user_id,
        "timestamp": log.timestamp,
        "is_anomaly": bool(label),
        "score": float(score),
        "top_feature": top_feature,
        "message": "Anomalia detectada" if label else "Comportamento normal"
    }

    if label:
        db_log = {
            "user_id": log.user_id,
            "timestamp": log.timestamp,
            "ip_address": log.ip_address,
            "action": log.action,
            "location": log.location,
            "device": log.device,
            "score": float(score),
            "top_feature": top_feature,
            "message": "Anomalia detectada"
        }
        insert_anomalous_log(db_log)

    return result

@router.get("/anomalies")
def get_anomalies():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM anomalous_logs ORDER BY login_time DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Mapear os resultados para dicts
        columns = ["id", "user_id", "login_time", "ip_address", "action", "location", "device", "score", "top_feature", "message"]
        anomalies = [dict(zip(columns, row)) for row in rows]

        return anomalies

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/simulate")
def simulate_detection():
    global trained

    path = Path("data/raw_logs.csv")
    df_raw = pd.read_csv(path)

    if not trained:
        df_train = pd.read_csv("data/normal_logs_csv__simulado_.csv")
        df_train_proc = preprocess_auth_log(df_train.to_dict(orient="records"), fit=True)
        model.fit(df_train_proc[features_used])
        trained = True

    simulated_logs = []

    for _, row in df_raw.iterrows():
        log = AuthLog(
            user_id=row["user_id"],
            timestamp=row["timestamp"],
            ip_address=row["ip_address"],
            action=row["action"],
            location=row["location"],
            device=row["device"]
        )
        df_input = preprocess_auth_log([log.dict()], fit=False)
        score = model.decision_function(df_input[features_used])[0]
        label = model.predict(df_input[features_used])[0]

        feature_weights = abs(df_input[features_used].iloc[0] - model.decision_scores_.mean())
        top_feature = feature_weights.idxmax()

        result = {
            "user_id": log.user_id,
            "timestamp": log.timestamp,
            "is_anomaly": bool(label),
            "score": float(score),
            "top_feature": top_feature,
            "message": "Anomalia detectada" if label else "Comportamento normal"
        }

        simulated_logs.append(result)

    return simulated_logs
