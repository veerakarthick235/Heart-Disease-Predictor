import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration — reads from environment variables."""
    
    # Flask
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-CHANGE-IN-PRODUCTION')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # MongoDB Atlas
    MONGO_URI = os.environ.get(
        'MONGO_URI',
        'mongodb://localhost:27017/heartdisease'  # Fallback to local for dev
    )
    MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'heartdisease')
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-CHANGE-IN-PRODUCTION')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_HOURS', 24))
    )
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = False     # Set True in production (HTTPS only)
    JWT_COOKIE_CSRF_PROTECT = False  # Enable in production
    
    # Flask-Login
    LOGIN_VIEW = 'auth.login'
    LOGIN_MESSAGE = 'Please log in to access this page.'
    LOGIN_MESSAGE_CATEGORY = 'info'
    
    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URI = "memory://"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
