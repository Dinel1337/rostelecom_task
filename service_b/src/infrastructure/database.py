from sqlalchemy import create_engine, Column, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
from src.config import settings

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    equipment_id = Column(String, nullable=False)
    status = Column(String, default="pending")
    parameters = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# в проде postgresql, иначе юзаем sqlite
if settings.DEBUG:
    DATABASE_URL = settings.DATABASE_URL_sqlite
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    DATABASE_URL = settings.DATABASE_URL_asyncpg
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Создаёт все таблицы в БД"""
    Base.metadata.create_all(bind=engine)
    print(f"Бдшка поднята: {DATABASE_URL}")

def get_db():
    """DI генератор"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
