import os
from datetime import timedelta


class BaseConfig:
    """Base configuration shared by all environments."""

    # In production, set SECRET_KEY from environment or a secret manager / key vault
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-not-secure")

    # Example: where your real DB URL would go later
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///bookstore.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security-related defaults
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # In production behind HTTPS you would set this True
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"

    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # App-specific
    ENVIRONMENT_NAME = "base"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENVIRONMENT_NAME = "development"
    # Dev is often HTTP only, so you can override security flags here if needed
    SESSION_COOKIE_SECURE = False


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    ENVIRONMENT_NAME = "testing"
    # Disable CSRF etc. here if you add it later
    SESSION_COOKIE_SECURE = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    ENVIRONMENT_NAME = "production"
    # In real prod you would almost certainly enforce secure cookies:
    SESSION_COOKIE_SECURE = True


CONFIG_BY_NAME = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
