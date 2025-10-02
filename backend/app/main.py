from fastapi import FastAPI
import sqlite3, os

app = FastAPI()

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data", "traffic.db")

def get_counts():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT object_type, COUNT(*) FROM detections GROUP BY object_type")
    result = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in result}

@app.get("/")
def home():
    return {"message": "Smart Traffic Light API is running 🚦"}

@app.get("/counts")
def counts():
    return get_counts()
