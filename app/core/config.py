import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # App
    SECRET_KEY: str = "your-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Chat API Configuration
    CHAT_API_URL: str | None = None
    CHAT_API_KEY: str | None = None
    DEFAULT_CHAT_MODEL: str | None = None

    # Database configuration
    DB_ENGINE: str = "sqlite"
    DB_NAME: str = "psychology"
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_HOST: str | None = None
    DB_PORT: str | None = None
    DATABASE_URL: str | None = None

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        if self.DB_ENGINE.lower() == "postgresql" and all([self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_PORT]):
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

        elif self.DB_ENGINE.lower() == "mysql" and all([self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_PORT]):
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

        else:
            # Default to SQLite
            return f"sqlite:///{BASE_DIR / (self.DB_NAME + '.db')}"

    # ✅ Cấu hình để Pydantic tự load file .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# ✅ Khi import module này, Settings sẽ tự đọc .env
settings = Settings()
