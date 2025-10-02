import threading, time
from datetime import datetime, timezone
from .database import insert_count

def aggregator_loop(camera_worker, interval_minutes=5):
    while True:
        # sleep until next 5-min boundary (optional) or simple sleep for interval
        time.sleep(interval_minutes * 60)
        samples = camera_worker.pop_and_clear_buffer()
        if not samples:
            cars = 0; persons = 0
        else:
            # choose aggregation strategy: max, median, sum, etc.
            vehicles_list = [s[0] for s in samples]
            persons_list = [s[1] for s in samples]
            cars = int(max(vehicles_list))
            persons = int(max(persons_list))
        ts = datetime.now(timezone.utc).astimezone().isoformat(timespec='minutes')
        insert_count(ts, cars, persons)
