import os
from .base_config import BaseConfig


class ProductionConfig(BaseConfig):
    # MySQL DataBase Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_PRODUCTION_DATABASE_URI')
