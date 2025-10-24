# app/plugins/temp_sensor.py
def register(mqtt_client):
    print("Registering lights effector plugin")
    mqtt_client.subscribe("external/intents/vibe_shift")
    print("Subscribed to external/intents/vibe_shift")

    def callback(client, userdata, message):
        print(f"[LightsEffector] Received: {message.payload.decode()}")

    mqtt_client.message_callback_add("external/intents/vibe_shift", callback)
