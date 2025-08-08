# app/plugins/temp_sensor.py
def register(mqtt_client):
    print("Registering temp sensor plugin")
    mqtt_client.subscribe("sensors/temp")
    print("Subscribed to sensors/temp")

    def callback(client, userdata, message):
        print(f"[TempSensor] Received: {message.payload.decode()}")

    mqtt_client.message_callback_add("sensors/temp", callback)
