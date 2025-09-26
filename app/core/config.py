import os
from pydantic_settings import BaseSettings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
class Settings(BaseSettings):
    # Add your config variables here
    SECRET_KEY: str = "your-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Database configuration
    DB_ENGINE: str = os.getenv("DB_ENGINE", "sqlite")
    DB_NAME: str = os.getenv("DB_NAME", "psychology")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "")
    DB_PORT: str = os.getenv("DB_PORT", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
            
        if self.DB_ENGINE.lower() == "postgresql" and all([self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_PORT]):
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        elif self.DB_ENGINE.lower() == "mysql" and all([self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_PORT]):
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            # Default to SQLite if any required configuration is missing
            # return f"sqlite:///{self.DB_NAME}.db"
            return f"sqlite:///{os.path.join(BASE_DIR, self.DB_NAME)}.db"

    class Config:
        env_file = ".env"

settings = Settings()