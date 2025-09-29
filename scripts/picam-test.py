from picamera2 import Picamera2
import cv2
from time import sleep

picam2 = Picamera2()

# Initialize camera
video_config = picam2.create_video_configuration(main={"format": "RGB888"})
picam2.configure(video_config)

picam2.start()
sleep(2)  # camera warm-up
print("Pi Camera 3 started. Press 'q' to quit.")
try:
    while True:
        frame = picam2.capture_array("main")

        cv2.imshow("Pi Camera 3 Test", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    picam2.stop()
    cv2.destroyAllWindows()
    print("Camera stopped and window closed.")
