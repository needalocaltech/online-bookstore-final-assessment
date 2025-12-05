import os
from datetime import timedelta


class BaseConfig:
    """Base configuration shared by all environments."""

    # In production this MUST come from env or secret manager
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-not-secure")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///bookstore.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # default false, overridden in production
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"

    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    ENVIRONMENT_NAME = "base"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENVIRONMENT_NAME = "development"
    SESSION_COOKIE_SECURE = False  # dev normally over HTTP


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    ENVIRONMENT_NAME = "testing"
    SESSION_COOKIE_SECURE = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    ENVIRONMENT_NAME = "production"
    SESSION_COOKIE_SECURE = True  # enforce secure cookies in prod

    @classmethod
    def validate(cls):
        """Fail fast if insecure defaults are used in production."""
        if cls.SECRET_KEY == "dev-only-not-secure":
            raise RuntimeError("SECRET_KEY must be set via environment in production")


CONFIG_BY_NAME = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///bookstore.db")
