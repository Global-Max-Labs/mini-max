import paho.mqtt.client as mqtt

def publish_message(topic: str, message: str, host: str = "localhost", port: int = 1883):
    """
    Publish a message to an MQTT topic
    
    Args:
        topic (str): The MQTT topic to publish to
        message (str): The message to publish
        host (str): MQTT broker host (default: localhost)
        port (int): MQTT broker port (default: 1883)
    """
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(host, port, 60)
    client.publish(topic, message)
    client.disconnect()

if __name__ == "__main__":
    # Example usage
    publish_message("sensors/temp", "35.5")