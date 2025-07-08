import pandas as pd
from pyod.models.hbos import HBOS
import json

def load_and_detect_anomalies(csv_path, output_json_path):
    df = pd.read_csv(csv_path)
    model = HBOS()
    model.fit(df)
    preds = model.predict(df)
    anomalies = df[preds == 1]

    with open(output_json_path, "w") as f:
        json.dump(anomalies.to_dict(orient="records"), f, indent=2)

    print(f"✅ Anomalias salvas em: {output_json_path}")

if __name__ == "__main__":
    load_and_detect_anomalies("data/raw_logs.csv", "data/anomalies_detected.json")
