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
    access_token_expire_minutes: int = 1440  # 24 hours (more secure default)
    refresh_token_expire_days: int = 30  # 30 days for refresh tokens
    
    # Affiliate APIs (Optional - falls back to mock if not set)
    amazon_access_key: str = ""
    amazon_secret_key: str = ""
    amazon_partner_tag: str = "savy-21"
    amazon_country: str = "IT"
    
    awin_api_token: str = ""
    awin_publisher_id: str = ""
    
    booking_affiliate_id: str = ""
    booking_api_key: str = ""
    
    # API
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000,http://localhost:8080,http://10.0.2.2:8000"
    frontend_url: str = "http://localhost:3000"  # For email links
    
    # Email (SMTP)
    email_from: str = "noreply@savy.app"
    email_from_name: str = "Savy - Personal Finance Coach"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    
    # Redis (for caching and rate limiting)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0
    
    # Celery (for background jobs)
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    # Sentry (for error monitoring)
    sentry_dsn: str = ""  # Optional
    
    # Firebase (for push notifications)
    firebase_credentials_path: str = ""  # Path to firebase credentials JSON
    
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



