from picamera2 import Picamera2
import cv2
from ultralytics import YOLO
import time

# Initialize camera
picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"format": "RGB888"})
picam2.configure(video_config)
picam2.start()
time.sleep(2)  # camera warm-up

# Load YOLOv8 model (nano for speed)
model = YOLO("yolov8n.pt")

print("Starting YOLO detection. Press 'q' to quit.")
try:
    while True:
        frame = picam2.capture_array("main")
        
        # YOLO inference
        results = model(frame, verbose=False)[0]  # returns list of detections
        annotated_frame = results.plot() # Draw boxes
        cv2.imshow("YOLO Test", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    picam2.stop()
    cv2.destroyAllWindows()
