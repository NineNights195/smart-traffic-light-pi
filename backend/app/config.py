from pathlib import Path
from ultralytics import YOLO

# ---------------- Config ----------------
CONFIDENCE = 0.1
IMG_SZ = 640

# COCO class IDs (0 = person, 1 bicycle, 2 car, 3 motorcycle, 5 bus, 7 truck)
TARGET_CLASSES = [0, 2]

# YOLO model path (using nano model)
model = YOLO(Path(__file__).resolve().parent.parent.parent / "models" / "yolov8n.pt")

# How often to save counts into the database (in seconds)
INTERVAL = 5 * 60  # 5 minutes

# Database path (points to project-root/data/traffic.db)
DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "traffic.db"

# Test video path (for detector_video.py)
TEST_VIDEO_PATH = Path(__file__).resolve().parent.parent / "test" / "test_video.mp4"
