import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Carrega o .env automaticamente
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = int(os.getenv("DB_PORT", 5432))  # padrão 5432, convertido para int

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT,
        cursor_factory=RealDictCursor
    )

def insert_anomalous_log(log: dict):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO anomalous_logs (
                    user_id, login_time, ip_address, action, location, device, score, top_feature, message
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                log.get("user_id"),
                log.get("timestamp"),
                log.get("ip_address"),
                log.get("action"),
                log.get("location"),
                log.get("device"),
                log.get("score"),
                log.get("top_feature"),
                log.get("message")
            ))
    conn.commit()
    cur.close()
    conn.close()
