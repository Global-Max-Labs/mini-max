import paho.mqtt.client as mqtt
import json
from typing import Callable


def create_mqtt_client(broker: str, port: int, on_message_callback: Callable):
    """Creates and configures an MQTT client with a callback function."""

    client = mqtt.Client()

    def on_connect(client, userdata, flags, rc):
        print(f"Connected to MQTT broker with result code {rc}")

    client.on_connect = on_connect
    client.on_message = on_message_callback
    client.connect(broker, port, 60)
    return client


def subscribe(client, topic: str):
    """Subscribes to an MQTT topic."""
    client.subscribe(topic)


def publish(client, topic: str, payload: dict):
    """Publishes a JSON payload to an MQTT topic."""
    client.publish(topic, json.dumps(payload))


def start_loop(client):
    """Starts the MQTT event loop (blocking)."""
    client.loop_forever()
