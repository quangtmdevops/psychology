import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # Database configuration
    DB_ENGINE = os.getenv('DB_ENGINE', 'sqlite')
    DB_NAME = os.getenv('DB_NAME', 'psychology_db')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')

    @classmethod
    def get_database_url(cls):
        if cls.DB_ENGINE.lower() == 'mysql':
            return f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        else:
            # Default to SQLite
            return f"sqlite:///{cls.DB_NAME}.db"
