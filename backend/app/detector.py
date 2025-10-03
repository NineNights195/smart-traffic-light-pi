# detector.py
"""
Detector module:
- starts 2 Picamera2 cameras
- loads YOLO model
- provides get_counts() which returns:
    (persons_count, vehicles_count, annotated_frame0, annotated_frame1)
"""

from ultralytics import YOLO
from picamera2 import Picamera2
import time
from pathlib import Path
import config

class Detector:
    def __init__(self,
                 model_path: Path = config.MODEL_PATH,
                 imgsz: int = config.IMG_SZ,
                 conf: float = config.CONFIDENCE,
                 classes = config.TARGET_CLASSES,
                 cam0_index = config.CAM0_INDEX,
                 cam1_index = config.CAM1_INDEX):
        self.model_path = model_path
        self.imgsz = imgsz
        self.conf = conf
        self.classes = classes
        self.cam0_index = cam0_index
        self.cam1_index = cam1_index

        # load model
        print("Loading YOLO model...")
        self.model = YOLO(str(self.model_path))
        print("YOLO loaded.")

        # setup cameras
        print("Initializing cameras...")
        self.cam0 = Picamera2(self.cam0_index)
        self.cam1 = Picamera2(self.cam1_index)
        cfg0 = self.cam0.create_video_configuration(main={"format":"RGB888","size":(640,480)})
        cfg1 = self.cam1.create_video_configuration(main={"format":"RGB888","size":(640,480)})
        self.cam0.configure(cfg0)
        self.cam1.configure(cfg1)
        self.cam0.start()
        self.cam1.start()
        time.sleep(1)
        print("Cameras started.")

    def get_counts(self):
        """
        Capture frames, run detection, return:
        (persons, vehicles, annotated0, annotated1)
        """
        frame0 = self.cam0.capture_array("main")
        frame1 = self.cam1.capture_array("main")

        # run model on each frame
        r0 = self.model(frame0, imgsz=self.imgsz, conf=self.conf, classes=self.classes)[0]
        r1 = self.model(frame1, imgsz=self.imgsz, conf=self.conf, classes=self.classes)[0]

        persons = 0
        vehicles = 0
        for res in (r0, r1):
            if res.boxes is not None and getattr(res.boxes, "cls", None) is not None:
                for cls_v in res.boxes.cls:
                    cid = int(cls_v)
                    if cid == 0:
                        vehicles += 1
                    else:
                        persons += 1

        annotated0 = r0.plot() if (r0.boxes is not None) else frame0
        annotated1 = r1.plot() if (r1.boxes is not None) else frame1

        return persons, vehicles, annotated0, annotated1

    def stop(self):
        try:
            self.cam0.stop()
        except Exception:
            pass
        try:
            self.cam1.stop()
        except Exception:
            pass
