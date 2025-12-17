import time
import cv2
import numpy as np
import sqlite3
from collections import defaultdict

import config
from detector import Detector
from state_machine import StateMachine, TRAFFIC_GREEN, TRAFFIC_YELLOW, TRAFFIC_RED, PED_WALK, PED_STOP

# optionally import hardware modules only if not simulation
if not config.SIMULATION:
    from gpiozero import LED, TrafficLights
    import tm1637

# --- Setup detector and state machine ---
det = Detector(model_path=config.MODEL_PATH,
               imgsz=config.IMG_SZ,
               conf=config.CONFIDENCE,
               classes=config.TARGET_CLASSES,
               cam0_index=config.CAM0_INDEX,
               cam1_index=config.CAM1_INDEX)

sm = StateMachine()

# --- Setup hardware if needed ---
if not config.SIMULATION:
    lights = TrafficLights(red=config.GPIO_RED, amber=config.GPIO_YELLOW, green=config.GPIO_GREEN)
    ped_red1 = LED(config.GPIO_PED_RED1)
    ped_green1 = LED(config.GPIO_PED_GREEN1)
    ped_red2 = LED(config.GPIO_PED_RED2)
    ped_green2 = LED(config.GPIO_PED_GREEN2)
    try:
        display = tm1637.TM1637(clk=config.TM_CLK, dio=config.TM_DIO)
        display.brightness(2)
    except Exception as e:
        print("TM1637 init failed:", e)
        display = None
else:
    lights = ped_red1 = ped_green1 = ped_red2 = ped_green2 = display = None

# --- Database setup ---
conn = sqlite3.connect(config.DB_PATH)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS counts (
    timestamp INTEGER PRIMARY KEY,
    humans INTEGER,
    vehicles INTEGER
)
""")
conn.commit()

acc_counts = defaultdict(int)
db_start = time.time()

# --- UI drawing helpers ---
def draw_ui(right_w, traffic_state, pedestrian_state, remaining):
    """
    Build a UI canvas (height matches frames) with traffic/pedestrian lights and timer
    right_w = width for UI (e.g. 600)
    """
    h = 480
    canvas = np.zeros((h, right_w, 3), dtype=np.uint8)
    # traffic light
    x, y, w, hbox = 20, 20, 120, 320
    cx = x + w // 2
    cy_red, cy_yellow, cy_green = y+60, y+160, y+260
    cv2.rectangle(canvas, (x,y),(x+w,y+hbox), (30,30,30), -1)
    cv2.circle(canvas, (cx, cy_red), 40, (0,0,255) if traffic_state==TRAFFIC_RED else (50,50,50), -1)
    cv2.circle(canvas, (cx, cy_yellow), 40, (0,255,255) if traffic_state==TRAFFIC_YELLOW else (50,50,50), -1)
    cv2.circle(canvas, (cx, cy_green), 40, (0,255,0) if traffic_state==TRAFFIC_GREEN else (50,50,50), -1)
    cv2.putText(canvas, f"TRAFFIC : {traffic_state}", (10,y+hbox+30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255),2)

    # timer (below traffic light)
    ttxt = "----" if remaining is None else f"{int(remaining)}s"
    cv2.putText(canvas, f"TIMER : {ttxt}", (10, y+hbox+70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)

    # pedestrian
    x2, y2, w2, h2 = 180, 80, 240, 160
    left = (x2+60, y2+h2//2)
    right = (x2+180, y2+h2//2)
    cv2.rectangle(canvas, (x2, y2),(x2+w2, y2+h2),(30,30,30), -1)
    cv2.circle(canvas, left, 40, (0,0,255) if pedestrian_state==PED_STOP else (50,50,50), -1)
    cv2.circle(canvas, right, 40, (0,255,0) if pedestrian_state==PED_WALK else (50,50,50), -1)
    # Move pedestrian teller below its sign
    cv2.putText(canvas, f"PEDESTRIAN : {pedestrian_state}", (x2, y2+h2+30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255),2)

    return canvas

# --- Helper to update hardware safely ---
def set_hardware(traffic_state, pedestrian_state, remaining):
    if config.SIMULATION:
        return
    # TrafficLights: use .on/.off
    if traffic_state == TRAFFIC_RED:
        lights.red.on(); lights.amber.off(); lights.green.off()
    elif traffic_state == TRAFFIC_YELLOW:
        lights.red.off(); lights.amber.on(); lights.green.off()
    else:  # GREEN
        lights.red.off(); lights.amber.off(); lights.green.on()

    # Pedestrian LEDs (STOP means red on left; WALK means green on right in this UI)
    ped_red1.value = ped_red2.value = (pedestrian_state == PED_STOP)
    ped_green1.value = ped_green2.value = (pedestrian_state == PED_WALK)

    # TM1637 display
    if display:
        try:
            if remaining is None:
                # show dashes
                display.show("----")
            else:
                # format mmss if you want; for simplicity show seconds as two-digit or more
                s = int(max(0, remaining))
                # Show as two digits seconds (if >99 shows last two digits)
                if s < 100:
                    display.show(f"{s:02d}")
                else:
                    display.show(f"{s%100:02d}")
        except Exception:
            pass

# --- Main loop ---
print("Starting Smart Traffic Light. Press 'q' to quit.")
try:
    while True:
        now = time.time()
        # get counts + frames
        persons, vehicles, ann0, ann1 = det.get_counts()

        # step state machine
        info = sm.step(persons, vehicles, now)
        traffic = info["traffic"]
        pedestrian = info["pedestrian"]
        remaining = info["remaining"]

        # aggregate counts for DB
        acc_counts["humans"] += persons
        acc_counts["vehicles"] += vehicles

        # update hardware
        set_hardware(traffic, pedestrian, remaining)

        # draw UI
        ui_canvas = draw_ui(420, traffic, pedestrian, remaining)
        # align heights
        # annotated frames may differ in height; standardize to 480
        def fit_h(img, h=480):
            if img.shape[0] == h: return img
            return cv2.resize(img, (int(img.shape[1]*h/img.shape[0]), h))
        a0 = fit_h(ann0, 480)
        a1 = fit_h(ann1, 480)

        # combine horizontally (keep total width manageable)
        combined = np.hstack((a0, a1, ui_canvas))
        cv2.imshow("Smart Traffic Light", combined)

        # write DB periodically
        if now - db_start >= config.INTERVAL_DB:
            ts = int(now)
            cur.execute("INSERT INTO counts (timestamp, humans, vehicles) VALUES (?, ?, ?)",
                        (ts, acc_counts["humans"], acc_counts["vehicles"]))
            conn.commit()
            acc_counts = defaultdict(int)
            db_start = now

        # user quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    pass

finally:
    print("Shutting down...")
    try:
        det.stop()
    except Exception:
        pass

    cv2.destroyAllWindows()

    if not config.SIMULATION:
        try:
            lights.off()
        except Exception:
            pass
        try:
            ped_red1.off(); ped_red2.off()
            ped_green1.off(); ped_green2.off()
        except Exception:
            pass
        if display:
            try:
                display.show("----")
            except Exception:
                pass
            try:
                display.cleanup()
            except Exception:
                pass

    try:
        conn.close()
    except Exception:
        pass

    print("Stopped.")
