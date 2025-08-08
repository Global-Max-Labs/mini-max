# mqtt_worker.py
import paho.mqtt.client as mqtt
import importlib
import pkgutil
from minimax.app.core.config import settings
import time


def load_plugins(client):
    print("[MQTT] Loading plugins...")
    import minimax.app.plugins

    found_plugins = False

    for _, module_name, _ in pkgutil.iter_modules(minimax.app.plugins.__path__):
        found_plugins = True
        mod = importlib.import_module(f"minimax.app.plugins.{module_name}")
        print(f"[MQTT] Module: {mod} found")
        if hasattr(mod, "register"):
            print(f"[MQTT] Loading plugin: {module_name}")
            mod.register(client)

    if not found_plugins:
        print("[MQTT] No plugins found in app.plugins package")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[MQTT] Connected successfully to broker")
        # Subscribe to topics after successful connection
        load_plugins(client)
    else:
        print(f"[MQTT] Failed to connect, return code: {rc}")
        # Connection return codes:
        # 0: Connection successful
        # 1: Connection refused - incorrect protocol version
        # 2: Connection refused - invalid client identifier
        # 3: Connection refused - server unavailable
        # 4: Connection refused - bad username or password
        # 5: Connection refused - not authorized


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"[MQTT] Unexpected disconnection, return code: {rc}")
    else:
        print("[MQTT] Disconnected successfully")


def start_mqtt():
    print("[MQTT] Initializing MQTT client...")
    client = mqtt.Client(client_id=settings.MQTT_CLIENT_ID)

    # Set callbacks
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # Set credentials if provided
    if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
        client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

    print(f"[MQTT] Connecting to {settings.MQTT_HOST}:{settings.MQTT_PORT}...")

    try:
        client.connect(settings.MQTT_HOST, settings.MQTT_PORT)
        # Use loop_start() instead of loop_forever() for better error handling
        client.loop_start()

        # Keep the main thread alive
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"[MQTT] Connection error: {e}")
        raise
    finally:
        print("[MQTT] Stopping MQTT client...")
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    start_mqtt()
