# app/plugins/temp_sensor.py
from actions.vibe_shift import process_vibe_shift


def register(mqtt_client):
    """
    This plugin subscribes to the external/intents/vibe_shift topic and processes the message.
    """
    print("yes it works Registering lights effector plugin")
    mqtt_client.subscribe("external/intents/vibe_shift")
    print("yes it works Subscribed to external/intents/vibe_shift")

    def callback(client, userdata, message):
        print(f"yes it works [TempSensor] Received: {message.payload.decode()}")
        process_vibe_shift(message.payload.decode())

    mqtt_client.message_callback_add("external/intents/vibe_shift", callback)


# todo:
"""
# Commands
internal/commands/<capability>/<unit>/<verb>
external/commands/<system>/<device_or_group>/<verb>

# Effector state
internal/state/<capability>/<unit>/<metric>
external/state/<system>/<device_or_group>/<metric>

# Optional policy/arbitration
internal/policy/<capability>/<unit>/request
internal/policy/<capability>/<unit>/grant

"""
