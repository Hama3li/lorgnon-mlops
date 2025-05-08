from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
import pickle
import traceback
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime

# Env vars
load_dotenv()
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# Load model + scaler
try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
except Exception as e:
    print("❌ Failed to load model or scaler:", e)
    model = None
    scaler = None

# FastAPI app
app = FastAPI(title="Throughput Prediction API", version="1.0.0")

class InputFeatures(BaseModel):
    lte_rsrp: float
    lte_rsrq: float
    nr_ssRsrp: float
    nr_ssRsrq: float
    nr_ssSinr: float
    mobility_mode: int
    movingSpeed: float
    compassDirection: float
    handoff: int
    pixel_x: int
    pixel_y: int
    throughput_lag_1: float
    throughput_lag_2: float
    throughput_lag_3: float
    throughput_lag_4: float
    throughput_delta: float

def send_alert_email(prediction):
    msg = EmailMessage()
    msg['Subject'] = "🚨 Alerte: Débit très faible détecté"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg.set_content(f"Le débit prédit est de {prediction} Mbps. Ce débit est inférieur à 5 Mbps.")
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print("✅ Email envoyé avec succès.")
    except Exception as e:
        print("❌ Erreur envoi email:", e)

def save_prediction_to_db(prediction, alert_message=None):
    conn = sqlite3.connect("predictions.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO predictions (timestamp, throughput, alert)
        VALUES (?, ?, ?)
    """, (datetime.utcnow().isoformat(), prediction, alert_message))
    conn.commit()
    conn.close()

@app.post("/predict")
def predict(input: InputFeatures):
    if model is None or scaler is None:
        raise HTTPException(status_code=500, detail="Model or scaler not loaded")

    try:
        input_df = pd.DataFrame([input.dict()])
        input_scaled = scaler.transform(input_df)
        prediction = round(float(model.predict(input_scaled)[0]), 2)

        if prediction < 5:
            alert_message = "🚨 ALERTE: Débit très faible (< 5 Mbps)"
            send_alert_email(prediction)
            save_prediction_to_db(prediction, alert_message)
            return {"predicted_throughput": prediction, "alert": alert_message}

        save_prediction_to_db(prediction)
        return {"predicted_throughput": prediction}

    except Exception as e:
        print("🔥 Internal Error:\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Prediction failed")
