import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration settings."""
    SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-key-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False

    db_url = os.getenv("DATABASE_URL", "sqlite:///careerpilot.db")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = db_url

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "uploads")
    REPORTS_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "reports")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    WTF_CSRF_ENABLED = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}