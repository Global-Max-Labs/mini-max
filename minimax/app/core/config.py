import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MQTT Configuration
    MQTT_HOST: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""
    MQTT_CLIENT_ID: str = "python_mqtt_client"
    # Database Configuration
    DB_PATH: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "lancedb")
    
    # Init file configuration - checks environment variable MINIMAX_INIT_FILE first
    INIT_FILE: str = os.getenv(
        'MINIMAX_INIT_FILE',
        os.path.join(os.path.dirname(__file__), "..", "scripts", "test_text.csv")
    )

    # Other application settings can be added here
    APP_NAME: str = "Minimax CORE API"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create a global settings instance
settings = Settings()