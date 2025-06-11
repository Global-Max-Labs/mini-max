from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MQTT Configuration
    MQTT_HOST: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""
    MQTT_CLIENT_ID: str = "python_mqtt_client"
    
    # Other application settings can be added here
    APP_NAME: str = "MQTT Application"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create a global settings instance
settings = Settings()