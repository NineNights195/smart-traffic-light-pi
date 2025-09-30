from picamera2 import Picamera2
import cv2
from time import sleep

picam2_0 = Picamera2(0)
picam2_1 = Picamera2(1)

# Initialize camera
video_config_0 = picam2_0.create_video_configuration(main={"format": "RGB888","size": (640, 480)})
video_config_1 = picam2_1.create_video_configuration(main={"format": "RGB888","size": (640, 480)})
picam2_0.configure(video_config_0)
picam2_1.configure(video_config_1)
picam2_0.start()
picam2_1.start()
sleep(2)  # camera warm-up

print("Pi Camera 3 started. Press 'q' to quit.")
try:
    while True:
        frame0 = picam2_0.capture_array("main")
        frame1 = picam2_1.capture_array("main")
        cv2.imshow("Camera 0 Test", frame0)
        cv2.imshow("Camera 1 Test", frame1)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    picam2_0.stop()
    picam2_1.stop()
    cv2.destroyAllWindows()
    print("All camera stopped and window closed.")
