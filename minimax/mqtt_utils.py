import socket
import subprocess
import time
import shutil
import sys


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
        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                "iot-mosquitto",
                "-p",
                "1883:1883",
                "--rm",
                "eclipse-mosquitto:1.6.15",
            ],
            check=True,
        )
        time.sleep(2)  # wait for broker to initialize
    except subprocess.CalledProcessError as e:
        print(f"[MQTT] Failed to start Mosquitto: {e}")
        raise


def ensure_ffmpeg():
    if not shutil.which("ffmpeg"):
        print("[FFMPEG] FFMPEG not found. Please install it.")
        print("Installing FFMPEG...")

        # Check if system is macOS
        if sys.platform == "darwin":
            subprocess.run(["brew", "install", "ffmpeg"], check=True)
        else:
            subprocess.run(["sudo", "apt-get", "install", "-y", "ffmpeg"], check=True)

        print("FFMPEG installed successfully.")
    else:
        print("[FFMPEG] FFMPEG already installed.")
