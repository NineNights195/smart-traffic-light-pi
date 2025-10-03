# config.py
from pathlib import Path

# SIMULATION mode: if True, hardware GPIO won't be used (canvas only)
SIMULATION = False

# ---------------- YOLO / Camera ----------------
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "yolov8n.pt"
IMG_SZ = 640
CONFIDENCE = 0.15
TARGET_CLASSES = [0, 2]  # person + vehicles of interest

# Camera indices (Picamera2)
CAM0_INDEX = 0
CAM1_INDEX = 1

# ---------------- GPIO pins ---------------- (update to your wiring if different)
GPIO_RED = 17
GPIO_YELLOW = 27
GPIO_GREEN = 22

GPIO_PED_RED1 = 24
GPIO_PED_GREEN1 = 23
GPIO_PED_RED2 = 6
GPIO_PED_GREEN2 = 5

# TM1637 pins
TM_CLK = 18
TM_DIO = 25

# ---------------- Timing (seconds) ----------------
# Dynamic timer parameters
MIN_GREEN = 5           # minimum green seconds
MAX_GREEN = 20          # maximum green seconds
TIME_PER_VEHICLE = 3    # seconds per vehicle (when converting count -> time)
TIME_PER_PERSON = 4     # seconds per pedestrian
VEHICLE_WEIGHT = 1.0
PEDESTRIAN_WEIGHT = 1.0
PERSON_CONFIRM = 3    # seconds of continuous detection to trigger vehicle->person
VEHICLE_CONFIRM = 3   # seconds of continuous detection to trigger person->vehicle
MIN_GREEN = 5           # already present, minimum green for either side


# Transition durations
YELLOW_DURATION = 3     # vehicle -> person: yellow fixed
FLASH_DURATION = 3      # person -> vehicle: flashing pedestrian
FLASH_INTERVAL = 0.5    # pedestrian light flash interval

# Database logging
INTERVAL_DB = 5 * 60    # seconds to aggregate before writing to DB

# Path to DB (project-root/backend/data/traffic.db)
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "traffic.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
