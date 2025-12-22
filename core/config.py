from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Farm Web"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DEVICE_TOKEN_EXPIRE_HOURS: int = 1
    ALLOWED_HOSTS: List[str] = ["*"]
    DATABASE_URL: str
    REDIS_URL: str = "redis://redis:6379/0"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()