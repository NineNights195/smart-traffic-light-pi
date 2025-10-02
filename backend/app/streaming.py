from fastapi import Response
from fastapi.responses import StreamingResponse
import time

def mjpeg_generator(camera_worker):
    boundary = b'--frame\r\n'
    while True:
        jpeg = camera_worker.get_latest_jpeg()
        if jpeg:
            # each chunk must be like: --frame\r\nContent-Type: image/jpeg\r\n\r\n<jpegbytes>\r\n
            chunk = boundary + b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n'
            yield chunk
        else:
            # no frame yet, wait briefly
            time.sleep(0.1)
