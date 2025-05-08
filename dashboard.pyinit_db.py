# init_db.py

import sqlite3

conn = sqlite3.connect("predictions.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    throughput REAL,
    alert TEXT
)
""")

conn.commit()
conn.close()
print("✅ Table predictions créée avec succès.")

