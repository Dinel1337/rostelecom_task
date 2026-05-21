from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    RABBIT_URL: str
    SERVICE_A_URL: str
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 5.0
    CONCURRENT_WORKERS: int = 5
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()