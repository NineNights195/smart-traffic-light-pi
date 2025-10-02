import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "traffic.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_latest_counts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT SUM(humans), SUM(vehicles)
        FROM traffic_counts
        WHERE timestamp >= datetime('now', '-5 minutes')
    """)
    row = cur.fetchone()
    conn.close()
    return {"humans": row[0] or 0, "vehicles": row[1] or 0}

def get_history(limit=50):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT timestamp, humans, vehicles
        FROM traffic_counts
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return [
        {"timestamp": r[0], "humans": r[1], "vehicles": r[2]} for r in rows
    ]
