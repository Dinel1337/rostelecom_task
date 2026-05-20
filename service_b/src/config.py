from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "dinelefox"
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_NAME: str = "tasks"
    
    RABBIT_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    
    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8000
    
    DEBUG: bool = False  # по умолчанию False, переопределяется из env
    
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
        else:
            return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
