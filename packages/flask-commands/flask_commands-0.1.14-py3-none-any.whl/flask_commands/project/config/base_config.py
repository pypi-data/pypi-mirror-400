import os
from datetime import timedelta
from dotenv import load_dotenv

# Import Environment variables

load_dotenv()  # reads variables from a .env file and sets them in os.environ

class BaseConfig():
    FLASK_CONFIG = os.environ.get('FLASK_CONFIG')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    APP_NAME = os.environ.get('APP_NAME')
