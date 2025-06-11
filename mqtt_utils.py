import socket
import subprocess
import time

def is_port_open(host="localhost", port=1883):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((host, port))
            return True
        except ConnectionRefusedError:
            return False

def ensure_mosquitto_docker():
    if is_port_open():
        print("[MQTT] Broker already running on port 1883.")
        return

    print("[MQTT] Starting Mosquitto via Docker...")
    try:
        subprocess.run([
            "docker", "run", "-d",
            "--name", "iot-mosquitto",
            "-p", "1883:1883",
            "--rm", "eclipse-mosquitto"
        ], check=True)
        time.sleep(2)  # wait for broker to initialize
    except subprocess.CalledProcessError as e:
        print(f"[MQTT] Failed to start Mosquitto: {e}")
        raise
