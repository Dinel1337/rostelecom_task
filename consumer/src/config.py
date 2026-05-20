from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    RABBIT_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    SERVICE_A_URL: str = "http://service_a:8001/api/v1/equipment/cpe"
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 5.0
    CONCURRENT_WORKERS: int = 5
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
