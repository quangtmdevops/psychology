import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Add your config variables here
    SECRET_KEY: str = "your-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "sqlite:///./test.db" 

    class Config:
        SQLALCHEMY_DATABASE_URI = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://postgres:postgres@db:5432/psychology"
        )
        env_file = ".env"


settings = Settings()