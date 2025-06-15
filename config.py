import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # Database configuration
    DB_ENGINE = os.getenv('DB_ENGINE', 'postgresql')
    DB_NAME = os.getenv('DB_NAME', 'psychology')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DB_HOST = os.getenv('DB_HOST', 'db')
    DB_PORT = os.getenv('DB_PORT', '5432')

    @classmethod
    def get_database_url(cls):
        if cls.DB_ENGINE.lower() == 'mysql':
            return f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        elif cls.DB_ENGINE.lower() == 'postgresql':
            return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        else:
            # Default to SQLite
            return f"sqlite:///{cls.DB_NAME}.db"
