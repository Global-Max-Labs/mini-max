"""TEMPORARY I HOPE HOPE HOPE"""
import multiprocessing
import time
from app.main import app
from app.stt.src.main import run_listener
import uvicorn
import mqtt_worker
from mqtt_utils import ensure_mosquitto_docker, ensure_ffmpeg

def run_api():
    print("[FASTAPI] Starting API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

def run_mqtt():
    print("[MQTT] Ensuring broker is available...")
    ensure_mosquitto_docker()

    print("[FFMPEG] Ensuring FFMPEG is available...")
    ensure_ffmpeg()

    print("[MQTT] Starting MQTT worker...")
    mqtt_worker.start_mqtt()


def run_stt():
    print("[STT] Starting STT worker...")
    run_listener()

if __name__ == "__main__":
    p1 = multiprocessing.Process(target=run_api)
    p2 = multiprocessing.Process(target=run_mqtt)
    p3 = multiprocessing.Process(target=run_stt)

    p1.start()
    time.sleep(1)  # give API a slight head start
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()
