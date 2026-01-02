import os
from dotenv import load_dotenv
from datetime import timedelta

class Config:
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(os.path.join(BASEDIR, ".env"))
    PERMANENT = False #Session expires when user closes browser or not
    WTF_CSRF_ENABLED = True
    SECRET_KEY = os.getenv("SECRET_KEY")
    POOL_RECYCLE = 60

class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    SESSION_COOKIE_SECURE = False
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}