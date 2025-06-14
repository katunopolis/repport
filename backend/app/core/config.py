from pydantic_settings import BaseSettings
from typing import Optional, List
import secrets
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Vibe Repport"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://repport:repport@localhost:5432/repport")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", 20))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", 10))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", 30))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", 1800))
    
    # Email (Resend)
    RESEND_API_KEY: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "noreply@yourdomain.com")
    
    # CORS - store as string and process later
    BACKEND_CORS_ORIGINS_STR: str = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
    
    class Config:
        case_sensitive = True
    
    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        """Get list of allowed origins from the string"""
        return self.BACKEND_CORS_ORIGINS_STR.split(",") if self.BACKEND_CORS_ORIGINS_STR else ["http://localhost:3000"]

settings = Settings() 