#!/usr/bin/env python3
"""
Configuration Settings

Centralized configuration management for the legal practice platform.
Handles environment variables, security settings, and application configuration.
"""

import os
from typing import Optional
from pydantic import BaseSettings


# Language Configuration
LANGUAGES = {
    'nl': 'Nederlands',
    'fr': 'Français',
    'en': 'English',
    'de': 'Deutsch'
}

DEFAULT_LANGUAGE = 'nl'  # Dutch as primary language
SUPPORTED_LANGUAGES = ['nl', 'fr', 'en', 'de']

# Babel Configuration
BABEL_DEFAULT_LOCALE = 'nl'
BABEL_DEFAULT_TIMEZONE = 'Europe/Brussels'
BABEL_TRANSLATION_DIRECTORIES = 'translations'


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application settings
    APP_NAME: str = "Legal Practice Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database settings (for future implementation)
    DATABASE_URL: Optional[str] = None

    # AI and ML settings
    AI_MODEL_PATH: str = "models/"
    ENABLE_AI_FEATURES: bool = True

    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "legal_platform.log"

    # Email settings (for notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None

    # File storage settings
    UPLOAD_DIR: str = "uploads/"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    # CORS settings
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]

    # Feature flags
    ENABLE_TIME_TRACKING: bool = True
    ENABLE_CALENDAR_AI: bool = True
    ENABLE_CRM: bool = True
    ENABLE_DOCUMENT_WORKFLOW: bool = True
    ENABLE_CASE_MANAGEMENT: bool = True
    ENABLE_AI_PERSONALITY: bool = True
    ENABLE_BUSINESS_INTELLIGENCE: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def validate_settings() -> bool:
    """Validate critical settings."""
    required_settings = [
        "SECRET_KEY",
    ]

    for setting in required_settings:
        if not getattr(settings, setting):
            print(f"Warning: {setting} is not set")
            return False

    return True


# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings."""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    ENABLE_AI_FEATURES: bool = True


class ProductionSettings(Settings):
    """Production environment settings."""
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    ENABLE_AI_FEATURES: bool = True

    # Production security requirements
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")

    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///legal_platform.db")

    # Email configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")


class TestSettings(Settings):
    """Test environment settings."""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    ENABLE_AI_FEATURES: bool = False
    DATABASE_URL: str = "sqlite:///test.db"


def get_environment_settings() -> Settings:
    """Get environment-specific settings."""
    environment = os.getenv("ENVIRONMENT", "development").lower()

    if environment == "production":
        return ProductionSettings()
    elif environment == "test":
        return TestSettings()
    else:
        return DevelopmentSettings() 