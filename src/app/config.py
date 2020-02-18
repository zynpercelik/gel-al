import os
import datetime


class BaseConfig:

    SQLALCHEMY_DATABASE_URI = 'postgresql://test:123456789@localhost/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRATION_DELTA = datetime.timedelta(days=25)

    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL',
                                  'redis://localhost:6379')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND',
                                      'redis://localhost:6379')



class ProductionConfig(BaseConfig):
    DEBUG = False
    Testing = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
