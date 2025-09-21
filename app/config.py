import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Database Configuration
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "shorturl.db")

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    BASE_URL: str = os.getenv("BASE_URL", "127.0.0.1:8000")

    # Application Configuration
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    CODE_LENGTH: int = int(os.getenv("CODE_LENGTH", "6"))

    # API Configuration
    API_TITLE: str = os.getenv("API_TITLE", "URL Shortener")
    API_DESCRIPTION: str = os.getenv("API_DESCRIPTION", "Simple URL shortener service with SQLite storage")
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")

# Create a global settings instance
settings = Settings()