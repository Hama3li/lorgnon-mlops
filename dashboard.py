import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="📊 Dashboard Lorgnon", layout="wide")

st.title("📈 Monitoring des Prédictions de Débit")
st.markdown("---")

# Connexion à SQLite
conn = sqlite3.connect("predictions.db")
cursor = conn.cursor()

# Lecture des données
query = "SELECT id, timestamp, throughput, alert FROM predictions ORDER BY timestamp DESC"
df = pd.read_sql_query(query, conn)

# KPI
col1, col2 = st.columns(2)
col1.metric("📦 Total Prédictions", len(df))
col2.metric("🚨 Alertes détectées", df["alert"].notnull().sum())

# Affichage des alertes
st.subheader("🛑 Alertes Récentes")
st.dataframe(df[df["alert"].notnull()], use_container_width=True)

# Toutes les prédictions
st.subheader("📜 Historique complet")
st.dataframe(df, use_container_width=True)
