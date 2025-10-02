import uvicorn
from app.api import app
from backend.app.detector import CameraWorker
import threading

def start_system():
    cam0 = CameraWorker(cam_id=0)
    cam1 = CameraWorker(cam_id=1)
    cam0.start()
    cam1.start()
    app.state.cams = {0: cam0, 1: cam1}
    # start aggregator threads
    t0 = threading.Thread(target=lambda: __import__('app.aggregator').aggregator_loop(cam0), daemon=True)
    t1 = threading.Thread(target=lambda: __import__('app.aggregator').aggregator_loop(cam1), daemon=True)
    t0.start(); t1.start()

if __name__ == "__main__":
    start_system()
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=False)