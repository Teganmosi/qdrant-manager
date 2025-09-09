import os
from dotenv import load_dotenv

load_dotenv()

def _int(env_name: str, default: int):
    try:
        return int(os.getenv(env_name, default))
    except (TypeError, ValueError):
        return default

class Settings:
    # Database
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = _int("DB_PORT", 3306)
    DB_NAME = os.getenv("DB_NAME", "qdrant_manager")

    # Qdrant
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-to-a-long-random-string")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_SECONDS = _int("ACCESS_TOKEN_EXPIRE_SECONDS", 1800)
    REFRESH_TOKEN_EXPIRE_SECONDS = _int("REFRESH_TOKEN_EXPIRE_SECONDS", 2592000)

    # App
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    APP_NAME = os.getenv("APP_NAME", "Qdrant Admin API")

settings = Settings()