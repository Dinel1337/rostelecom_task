from pydantic import computed_field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "tasks"
    
    RABBIT_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    
    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8000
    
    DEBUG: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        if self.DEBUG:
            return "sqlite:///./tasks.db"
        return (f"postgresql+psycopg2://{self.DB_USER}:"
                f"{self.DB_PASSWORD.get_secret_value()}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

settings = Settings()