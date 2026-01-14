from .base_config import BaseConfig
from .development_config import DevelopmentConfig
from .production_config import ProductionConfig

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
