import os
from datetime import timedelta

# Base directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Base configuration class with default settings.
    Override or extend in subclasses for different environments.
    """
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Folder paths for uploads and templates
    UPLOAD_FOLDER = 'static/uploads'

    # Max upload size (250 MB)
    MAX_CONTENT_LENGTH = 250 * 1024 * 1024

    # Allowed file extensions for uploads
    ALLOWED_EXTENSIONS = {'zip', 'png', "jpg", "jpeg", "gif"}

    # Session and cookie settings
    SESSION_COOKIE_NAME = 'google-login-session'
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=10)
    SEND_FILE_MAX_AGE_DEFAULT = 0

    # Email settings (can be overridden)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True


    #Frontend Base
    FRONT_END_BASE = os.getenv("FRONTEND_BASE","")

    # FRONTEND ALLOWED ORIGINS FOR CORS(BACKEND)
    ORIGINS = os.getenv("FRONTEND_BASE","http://localhost:5173/")


class LocalDevelopmentConfig(Config):
    """
    Configuration for local development environment.
    Use with caution: sensitive keys here should be loaded from environment variables.
    """
    DEBUG = True

    # Local SQLite directory - optional, uncomment if you want to use SQLite
    SQLITE_DB_DIR = os.path.join(basedir, "..", "..", "data")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "database.sqlite3")

    # Example MySQL URI for local dev - replace with your own or set via env var
    # SQLALCHEMY_DATABASE_URI = os.getenv(
    #     "DATABASE_URL",
    #     'mysql+pymysql://flaskuser:Flask%40123@localhost:3306/flask_app_db'
    # )
    

    # Secret key for sessions and security - override via env var in real use
    SECRET_KEY = os.getenv("SECRET_KEY", 'a-super-secret-key')

    # Google OAuth credentials
    # GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "421047947364-l9e9s9uevov3pr1j217oobuvuo4gbbf8.apps.googleusercontent.com")
    # GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your-google-client-secret")


    # Email credentials - override in .env for security
    # MAIL_USERNAME = os.getenv("MAIL_USERNAME", 'ehteshamansari000001@gmail.com')
    # MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "your-email-password")
    # MAIL_DEFAULT_SENDER = ('Forever', MAIL_USERNAME)

    # Cookie security settings for local dev (not secure)
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False

    # Ensure folders exist on startup
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    # os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)


# class ProductionConfig(Config):
#     """
#     Production configuration.
#     Secrets and sensitive info MUST be set via environment variables.
#     Cookie security enabled.
#     """
#     DEBUG = False

#     # Database URI from environment variable (e.g., cloud SQL)
#     SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

#     # Secret key for sessions
#     SECRET_KEY = os.getenv("SECRET_KEY")

#     # Google OAuth
#     GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
#     GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


#     # Email credentials
#     MAIL_USERNAME = os.getenv("MAIL_USERNAME")
#     MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
#     MAIL_DEFAULT_SENDER = ('Forever', MAIL_USERNAME)

#     # Cookie security flags for production
#     SESSION_COOKIE_SECURE = True
#     REMEMBER_COOKIE_SECURE = True

#     # Ensure folders exist on startup
#     os.makedirs(Config.TEMPLATE_UPLOAD_FOLDER, exist_ok=True)
#     os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
