from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "tasks"
    
    RABBIT_URL: str = "amqp://guest:guest@localhost:5672/"
    
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
    def DATABASE_URL_asyncpg(self) -> str:
        """Асинхронный URL для SQLAlchemy (asyncpg)"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @computed_field
    @property
    def DATABASE_URL_psycopg(self) -> str:
        """Синхронный URL для SQLAlchemy (psycopg)"""
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @computed_field
    @property
    def DATABASE_URL_sqlite(self) -> str:
        """SQLite для разработки (запасной вариант)"""
        return "sqlite:///./tasks.db"

settings = Settings()

if settings.DEBUG:
    print(f"для отладочки")
    print(f"Бдшка: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    print(f"Кролик: {settings.RABBIT_URL}")
