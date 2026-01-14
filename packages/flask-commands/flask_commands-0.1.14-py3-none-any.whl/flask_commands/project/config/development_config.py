import os
from .base_config import BaseConfig


class DevelopmentConfig(BaseConfig):
    # MySQL DataBase Configuration
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DEVELOPMENT_DATABASE_URI')
