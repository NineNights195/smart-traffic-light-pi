from picamera2 import Picamera2
import cv2

picam2 = Picamera2()

# Create video configure
video_config = picam2.create_video_configuration(
    main={"format": "RGB888"}  # force ISP to output RGB
)
picam2.configure(video_config)

# Enable auto white balance
picam2.set_controls({"AwbEnable": True})

picam2.start()

print("Pi Camera 3 started. Press 'q' to quit.")

try:
    while True:
        # Get ISP-processed RGB frame
        frame = picam2.capture_array("main")

        cv2.imshow("Pi Camera 3 Test", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    picam2.stop()
    cv2.destroyAllWindows()
    print("Camera stopped and window closed.")
