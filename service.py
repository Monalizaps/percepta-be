from datetime import datetime
import pandas as pd
from schema import AuthLog
from datetime import datetime, timedelta
import pandas as pd
from schema import AuthLog

def preprocess_auth_log(auth_log_input, previous_logs=None, fit=True) -> pd.DataFrame:
    # previous_logs: dataframe com logs anteriores para calcular features temporais
    
    if isinstance(auth_log_input, dict):
        logs = [auth_log_input]
    elif isinstance(auth_log_input, list):
        logs = auth_log_input
    elif isinstance(auth_log_input, AuthLog):
        logs = [auth_log_input.dict()]
    else:
        raise ValueError("Formato inválido")

    records = []

    for log in logs:
        # Process timestamp
        ts_str = log.get("timestamp")
        if ts_str and ts_str.endswith("Z"):
            ts_str = ts_str.replace("Z", "+00:00")
        timestamp = datetime.fromisoformat(ts_str) if ts_str else None

        hour_decimal = timestamp.hour + timestamp.minute / 60.0 if timestamp else float(log.get("hour", 0))
        day_of_week = timestamp.weekday() if timestamp else 0

        # Action weight
        action_w = ACTION_WEIGHTS.get(log.get("action", ""), 1)

        # IP risk score - exemplo simples com hash
        ip_risk = hash(log.get("ip_address") or log.get("ip", "")) % 100000

        # Location and device hash
        location_h = hash(log.get("location", "")) % 1000
        device_h = hash(log.get("device", "")) % 1000

        # Tempo desde última ação do usuário (se tiver dados anteriores)
        time_since_last = None
        if previous_logs is not None and timestamp:
            user_logs = previous_logs[previous_logs['user_id'] == log['user_id']]
            if not user_logs.empty:
                last_ts = user_logs['timestamp'].max()
                time_since_last = (timestamp - last_ts).total_seconds() / 60  # minutos
            else:
                time_since_last = -1  # primeira ação

        # Quantidade de ações na última hora
        count_past_hour = 0
        if previous_logs is not None and timestamp:
            one_hour_ago = timestamp - timedelta(hours=1)
            user_logs = previous_logs[(previous_logs['user_id'] == log['user_id']) & 
                                      (previous_logs['timestamp'] >= one_hour_ago) & 
                                      (previous_logs['timestamp'] < timestamp)]
            count_past_hour = len(user_logs)

        record = {
            "user_id": hash(log["user_id"]) % 10000,
            "ip_risk_score": ip_risk,
            "location": location_h,
            "device": device_h,
            "hour": hour_decimal,
            "day_of_week": day_of_week,
            "action_weight": action_w,
            "time_since_last_action": time_since_last if time_since_last is not None else -1,
            "count_actions_past_hour": count_past_hour
        }

        records.append(record)

    return pd.DataFrame(records)


def explain_anomaly(log_df: pd.DataFrame, model) -> str:
    # Calcula os scores individuais
    scores = model.decision_function(log_df)
    max_score_index = scores.argmax()
    feature_names = log_df.columns.tolist()
    values = log_df.iloc[max_score_index]

    # A feature com maior valor normalizado será considerada a mais suspeita
    suspicious_feature = feature_names[values.argmax()]
    return suspicious_feature
