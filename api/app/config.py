from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Default to SQLite for local development if PostgreSQL is not available
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./test.db"
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()
