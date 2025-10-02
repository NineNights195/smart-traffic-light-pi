from ultralytics import YOLO
import cv2
import sqlite3
import time
from collections import defaultdict
import config

# ---------------- Config ----------------
VIDEO_PATH = config.TEST_VIDEO_PATH
CONFIDENCE = config.CONFIDENCE
IMG_SZ = config.IMG_SZ
TARGET_CLASSES = config.TARGET_CLASSES
INTERVAL = config.INTERVAL
DB_PATH = config.DB_PATH

# ---------------- Database setup ----------------
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS counts (
    timestamp INTEGER PRIMARY KEY,
    humans INTEGER,
    vehicles INTEGER
)
""")
conn.commit()

# ---------------- Video setup ----------------
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise RuntimeError(f"Cannot open video: {VIDEO_PATH}")

# ---------------- YOLO setup ----------------
model = config.model
print("YOLOv8n loaded ✅")

# ---------------- Counting loop ----------------
start_time = time.time()
acc_counts = defaultdict(int)

print("🚦 Detector running on video...")
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Video ended.")
            break

        results = model(frame, imgsz=IMG_SZ, conf=CONFIDENCE, classes=TARGET_CLASSES, verbose=False)[0]

        humans, vehicles = 0, 0
        if results.boxes is not None and results.boxes.cls is not None:
            for cls_id in results.boxes.cls:
                cls_id = int(cls_id)
                if cls_id == 0:
                    humans += 1
                else:
                    vehicles += 1

        acc_counts["humans"] += humans
        acc_counts["vehicles"] += vehicles

        print(f"[{time.strftime('%H:%M:%S')}] Humans: {humans}, Vehicles: {vehicles}")

        if time.time() - start_time >= INTERVAL:
            timestamp = int(time.time())
            c.execute("INSERT INTO counts (timestamp, humans, vehicles) VALUES (?, ?, ?)",
                      (timestamp, acc_counts["humans"], acc_counts["vehicles"]))
            conn.commit()
            print(f"✅ Saved counts: Humans={acc_counts['humans']} Vehicles={acc_counts['vehicles']}")
            acc_counts = defaultdict(int)
            start_time = time.time()

        cv2.imshow("Video", results.plot())
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    conn.close()
    print("Detector stopped. DB saved.")
