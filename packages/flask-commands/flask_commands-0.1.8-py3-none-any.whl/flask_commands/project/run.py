import os
import time
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'development')

# These are global variable for your jinja2 templates
@app.context_processor
def inject_globals():
    return {
        'time': time}

with app.app_context():
    if not os.path.exists('logs'):
        os.makedirs('logs', exist_ok=True)

    max_bytes = 10 * 1024 * 1024 # 10 MB
    backup_count = 10 # this will create 10 files .log.1 .log.2 .log.3 ...

    # Logging levels to: NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL

    file_handler = RotatingFileHandler(
        f"logs/{app.config['APP_NAME']}-{app.config['FLASK_CONFIG']}.log",
        maxBytes=max_bytes,
        backupCount=backup_count)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    if file_handler not in app.logger.handlers:
        app.logger.addHandler(file_handler)

    # SQL log file (separate from app logs)
    sql_file_handler = RotatingFileHandler(
        f"logs/sql-{app.config['FLASK_CONFIG']}.log",
        maxBytes=max_bytes,
        backupCount=backup_count)
    sql_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    sqlalchemy_logger.propagate = False
    if sql_file_handler not in sqlalchemy_logger.handlers:
        sqlalchemy_logger.addHandler(sql_file_handler)

    if app.config['FLASK_CONFIG'] == 'development':
        # this sets what the application will emit defaults to WARNING
        app.logger.setLevel(logging.DEBUG)
        sqlalchemy_logger.setLevel(logging.INFO)

        # this sets what is writting to the logs
        file_handler.setLevel(logging.DEBUG)
        sql_file_handler.setLevel(logging.INFO)


    if app.config['FLASK_CONFIG'] == 'production':
        app.logger.setLevel(logging.INFO)
        sqlalchemy_logger.setLevel(logging.WARNING)

        file_handler.setLevel(logging.INFO)
        sql_file_handler.setLevel(logging.WARNING)

    app.logger.info(f"{app.config['APP_NAME']} started up in {app.config['FLASK_CONFIG']} mode")
