import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    def __init__(self) -> None:
        # Database Configuration
        self.DATABASE_PATH: str = os.getenv("DATABASE_PATH", "shorturl.db")

        # Server Configuration
        self.HOST: str = os.getenv("HOST", "0.0.0.0")
        self.PORT: int = int(os.getenv("PORT", "8000"))
        self._base_url: str = os.getenv("BASE_URL", "http://127.0.0.1:8000")

        # Application Configuration
        self.ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
        self.DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
        self.CODE_LENGTH: int = int(os.getenv("CODE_LENGTH", "6"))

        # API Configuration
        self.API_TITLE: str = os.getenv("API_TITLE", "URL Shortener")
        self.API_DESCRIPTION: str = os.getenv("API_DESCRIPTION", "Simple URL shortener service with SQLite storage")
        self.API_VERSION: str = os.getenv("API_VERSION", "1.0.0")

    @staticmethod
    def _ensure_scheme(value: str) -> str:
        if not value:
            return value
        if value.startswith(("http://", "https://")):
            return value
        return f"http://{value}"

    @property
    def BASE_URL(self) -> str:
        return self._ensure_scheme(self._base_url)

    # Environment-based properties
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

# Create a global settings instance
settings = Settings()
