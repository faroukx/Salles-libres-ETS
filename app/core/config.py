import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Salles libres ÉTS"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./ets_rooms.db"
    UPLOAD_DIR: str = "./data/uploads"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# S'assurer que les dossiers nécessaires existent
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)
