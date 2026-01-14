from config import config
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Logging a user's authentication state handler
login_manager = LoginManager()

# ORM Database handler
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name) -> Flask:
    """Creates a Flask application Instance."""
    app = Flask(__name__)

    # apply configuration
    app.config.from_object(config[config_name])

    # initialize extensions: order matters
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    from app.routes.mains import bp as mains_blueprint
    app.register_blueprint(mains_blueprint)

    return app
