from datetime import datetime
import pandas as pd
from schema import AuthLog
from datetime import datetime
import pandas as pd
from schema import AuthLog

def preprocess_auth_log(auth_log_input, fit=True) -> pd.DataFrame:
    """
    Pré-processa os dados de autenticação para o modelo HBOS.
    Suporta dados com timestamp (padrão da API) e logs vindos de CSV com coluna `hour`.
    """
    if isinstance(auth_log_input, dict):
        logs = [auth_log_input]
    elif isinstance(auth_log_input, list):
        logs = auth_log_input
    elif isinstance(auth_log_input, AuthLog):
        logs = [auth_log_input.dict()]
    else:
        raise ValueError("Formato de entrada inválido para preprocess_auth_log")

    records = []

    for log in logs:
        # Extrai hora e dia da semana se tiver timestamp
        if "timestamp" in log:
            timestamp = datetime.fromisoformat(log["timestamp"])
            hour_decimal = timestamp.hour + timestamp.minute / 60.0
            day_of_week = timestamp.weekday()
        # Caso contrário, pega direto do log CSV
        else:
            hour_decimal = float(log.get("hour", 0))
            day_of_week = 0  # Pode ajustar se houver coluna

        record = {
            "user_id": hash(log["user_id"]) % 10000,
            "ip_risk_score": hash(log.get("ip_address") or log.get("ip", "")) % 100000,
            "location": hash(log["location"]) % 1000,
            "device": hash(log["device"]) % 1000,
            "hour": hour_decimal,
            "day_of_week": day_of_week,
            "action_weight": hash(log.get("action", "")) % 100
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
