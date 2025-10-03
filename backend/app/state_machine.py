# state_machine.py
import time
from config import (
    YELLOW_DURATION,
)

# UI constants
TRAFFIC_GREEN = "GREEN"
TRAFFIC_YELLOW = "YELLOW"
TRAFFIC_RED = "RED"
PED_WALK = "WALK"
PED_STOP = "STOP"

# ================= Threshold & Timing rules ================= #
# แบ่งช่วงจำนวนคน/รถ
PEDESTRIAN_THRESHOLDS = {
    "small": (1, 3),
    "medium": (4, 6),
    "large": (7, float("inf"))
}

VEHICLE_THRESHOLDS = {
    "small": (1, 3),
    "medium": (4, 6),
    "large": (7, float("inf"))
}

# เวลาสำหรับคน
PEDESTRIAN_GREEN_TIME = {
    "small": 8,
    "medium": 10,
    "large": 12
}

# เวลาสำหรับรถ
VEHICLE_GREEN_TIME = {
    "small": 7,
    "medium": 9,
    "large": 11
}

# เวลาที่รถต้องแดงเพื่อให้คนข้าม
VEHICLE_RED_FOR_PEDESTRIAN = {
    "small": 8,
    "medium": 10,
    "large": 12
}


class StateMachine:
    def __init__(self):
        self.state = "VEHICLE"  # VEHICLE, YELLOW, PERSON
        self.traffic_state = TRAFFIC_GREEN
        self.ped_state = PED_STOP
        self.timer_value = None
        self.phase_start = time.time()
        self.phase_duration = None

    # ---------------- Utility ---------------- #
    def _categorize(self, count, thresholds):
        if count == 0:
            return None
        for key, (low, high) in thresholds.items():
            if low <= count <= high:
                return key
        return None

    # ---------------- Timer calculation ---------------- #
    def calculate_vehicle_timer(self, vehicle_count):
        category = self._categorize(vehicle_count, VEHICLE_THRESHOLDS)
        if category:
            return VEHICLE_GREEN_TIME[category]
        return 0  # ถ้าไม่มีรถเลย

    def calculate_person_timer(self, person_count):
        category = self._categorize(person_count, PEDESTRIAN_THRESHOLDS)
        if category:
            return PEDESTRIAN_GREEN_TIME[category]
        return 0  # ถ้าไม่มีคนเลย

    def calculate_vehicle_red(self, person_count):
        category = self._categorize(person_count, PEDESTRIAN_THRESHOLDS)
        if category:
            return VEHICLE_RED_FOR_PEDESTRIAN[category]
        return 0

    # ---------------- State machine step ---------------- #
    def step(self, vehicle_count, person_count, now=None):
        if now is None:
            now = time.time()

        elapsed = (now - self.phase_start) if self.phase_start else 0

        # --- Special case: only vehicles, no person ---
        if person_count == 0 and vehicle_count > 0 and self.state == "VEHICLE":
            self.traffic_state = TRAFFIC_GREEN
            self.ped_state = PED_STOP
            self.timer_value = None  # แสดง ----
            return self._info()

        # --- VEHICLE state ---
        if self.state == "VEHICLE":
            if self.phase_duration is None:
                self.phase_duration = self.calculate_vehicle_timer(vehicle_count)
                self.phase_start = now
            self.traffic_state = TRAFFIC_GREEN
            self.ped_state = PED_STOP
            self.timer_value = max(0, self.phase_duration - elapsed)

            if elapsed >= self.phase_duration:
                if person_count > 0:
                    # ไป YELLOW ก่อน PERSON
                    self.state = "YELLOW"
                    self.phase_start = now
                    self.phase_duration = YELLOW_DURATION
                    self.timer_value = self.phase_duration
                else:
                    # ถ้าไม่มีคน -> รีเซ็ต VEHICLE ใหม่
                    self.phase_start = now
                    self.phase_duration = self.calculate_vehicle_timer(vehicle_count)
                    self.timer_value = self.phase_duration

        # --- YELLOW state ---
        elif self.state == "YELLOW":
            self.traffic_state = TRAFFIC_YELLOW
            self.ped_state = PED_STOP
            self.timer_value = max(0, self.phase_duration - elapsed)

            if elapsed >= self.phase_duration:
                # ไป PERSON
                self.state = "PERSON"
                self.phase_start = now
                self.phase_duration = self.calculate_person_timer(person_count)
                self.timer_value = self.phase_duration

        # --- PERSON state ---
        elif self.state == "PERSON":
            self.traffic_state = TRAFFIC_RED
            self.ped_state = PED_WALK
            self.timer_value = max(0, self.phase_duration - elapsed)

            if elapsed >= self.phase_duration:
                # กลับไป VEHICLE
                self.state = "VEHICLE"
                self.phase_start = now
                self.phase_duration = self.calculate_vehicle_timer(vehicle_count)
                self.timer_value = self.phase_duration

        return self._info()

    # ---------------- Info dict ---------------- #
    def _info(self):
        return {
            "traffic": self.traffic_state,
            "pedestrian": self.ped_state,
            "remaining": self.timer_value,
            "state": self.state
        }
