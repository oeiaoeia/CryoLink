"""
CryoLink Configuration
"""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration"""

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cryolink-super-secret-key-change-in-production-2025'

    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'cryolink.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL  # Flask-SQLAlchemy expects this
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Set True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Login
    LOGIN_MESSAGE = "Please log in to access CryoLink."
    LOGIN_MESSAGE_CATEGORY = "info"

    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')

    # Temperature Zones (Celsius)
    TEMP_ZONES = {
        'refrigerated': {'min': 2, 'max': 8, 'label': '2–8°C', 'color': '#0066CC'},
        'frozen': {'min': -25, 'max': -15, 'label': '-20°C', 'color': '#00C853'},
        'ultra_cold': {'min': -80, 'max': -60, 'label': '-70°C', 'color': '#9C27B0'}
    }

    # Risk Thresholds
    RISK_THRESHOLDS = {
        'low': {'min': 0, 'max': 30, 'color': '#00C853', 'label': 'Low'},
        'moderate': {'min': 31, 'max': 60, 'color': '#FFB300', 'label': 'Moderate'},
        'high': {'min': 61, 'max': 100, 'color': '#D32F2F', 'label': 'High'}
    }

    # Alert Settings
    ALERT_CHECK_INTERVAL = 60  # seconds
    EXCURSION_WARNING_MINUTES = 10

    # Pagination
    ITEMS_PER_PAGE = 20

    # API Settings
    API_RATE_LIMIT = "100 per hour"

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    WTF_CSRF_ENABLED = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_ECHO = False
    # NOTE: SysLogHandler removed — it tried to connect to /dev/log,
    # which doesn't exist on Vercel's serverless runtime and crashed
    # every request with FLASK_ENV=production. Vercel's own logging
    # (stdout/stderr) is captured automatically, so no custom handler
    # is needed here.


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
