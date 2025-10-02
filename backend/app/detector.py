from picamera2 import Picamera2
from ultralytics import YOLO
import cv2
import time
import sqlite3
from collections import defaultdict
import config

# ---------------- Config ----------------
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

# ---------------- Camera setup ----------------
print("Initializing cameras...")
cam0 = Picamera2(0)
cam1 = Picamera2(1)

config0 = cam0.create_video_configuration(main={"format": "RGB888","size": (640,480)})
config1 = cam1.create_video_configuration(main={"format": "RGB888","size": (640,480)})
cam0.configure(config0)
cam1.configure(config1)
cam0.start()
cam1.start()
time.sleep(2)
print("Cameras ready ✅")

# ---------------- YOLO setup ----------------
model = config.model
print("YOLOv8n loaded ✅")

# ---------------- Counting loop ----------------
start_time = time.time()
acc_counts = defaultdict(int)

print("🚦 Detector running... Press 'q' to stop")
try:
    while True:
        frame0 = cam0.capture_array("main")
        frame1 = cam1.capture_array("main")

        results0 = model(frame0, imgsz=IMG_SZ, conf=CONFIDENCE, classes=TARGET_CLASSES, verbose=False)[0]
        results1 = model(frame1, imgsz=IMG_SZ, conf=CONFIDENCE, classes=TARGET_CLASSES, verbose=False)[0]

        humans, vehicles = 0, 0
        for res in [results0, results1]:
            if res.boxes is not None and res.boxes.cls is not None:
                for cls_id in res.boxes.cls:
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

        # Optional display
        cv2.imshow("Camera 0", results0.plot())
        cv2.imshow("Camera 1", results1.plot())
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cam0.stop()
    cam1.stop()
    cv2.destroyAllWindows()
    conn.close()
    print("Detector stopped. Cameras closed, DB saved.")
