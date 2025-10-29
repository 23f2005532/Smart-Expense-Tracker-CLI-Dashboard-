import os 
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #Session and Cookie Settings
    SESSION_COOKIE_NAME = "session"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7) 

    FRONT_END_BASE = os.getenv("FRONT_END_BASE", "http://localhost:5173")
    CORS_ORIGIN = FRONT_END_BASE

class LocalDevelopmentConfig(Config):
    DEBUG = True
    SQLITE_DB_DIR = os.path.join(basedir, "..", "..", "data")
    if not os.path.exists(SQLITE_DB_DIR):
        os.makedirs(SQLITE_DB_DIR)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(SQLITE_DB_DIR, 'dev_database.db')

    SECRET_KEY = os.getenv("SECRET_KEY", "a_development_secret_key")

    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    