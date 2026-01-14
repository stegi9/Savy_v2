"""
Application configuration using Pydantic Settings.
Loads environment variables from .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MySQL Database
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str
    mysql_database: str = "savy_db"
    
    # Google Gemini
    gemini_api_key: str
    
    # Application
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # Salt Edge
    saltedge_app_id: str
    saltedge_secret: str
    saltedge_base_url: str = "https://www.saltedge.com/api/v6"
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # API
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000,http://localhost:8080,http://10.0.2.2:8000"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()



