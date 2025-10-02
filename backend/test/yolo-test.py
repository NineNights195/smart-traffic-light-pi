from picamera2 import Picamera2
import cv2
from ultralytics import YOLO
import time

# Initialize two cameras
picam2_0 = Picamera2(0)
picam2_1 = Picamera2(1)

video_config_0 = picam2_0.create_video_configuration(main={"format": "RGB888"})
video_config_1 = picam2_1.create_video_configuration(main={"format": "RGB888"})

picam2_0.configure(video_config_0)
picam2_1.configure(video_config_1)

picam2_0.start()
picam2_1.start()
time.sleep(2)  # camera warm-up

# Load YOLOv8 model (nano for speed)
model = YOLO("yolov8n.pt")

# COCO class IDs
# Vehicles: 0 = person, 1 = bicycle, 2 = car, 3 = motorcycle, 5 = bus, 7 = truck
target_classes = [0,1,2,3,5,7]

print("Starting YOLO detection on both cameras. Press 'q' to quit.")
try:
    while True:
        frame0 = picam2_0.capture_array("main")
        frame1 = picam2_1.capture_array("main")
        
        # YOLO inference
        results0 = model(frame0, classes=target_classes)[0]
        results1 = model(frame1, classes=target_classes)[0]
        annotated_frame0 = results0.plot()
        annotated_frame1 = results1.plot()
        
        cv2.imshow("YOLO Test Camera 0", annotated_frame0)
        cv2.imshow("YOLO Test Camera 1", annotated_frame1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    picam2_0.stop()
    picam2_1.stop()
    cv2.destroyAllWindows()
