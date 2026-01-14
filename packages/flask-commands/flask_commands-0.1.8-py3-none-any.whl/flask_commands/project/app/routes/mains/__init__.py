from flask import Blueprint

bp = Blueprint('mains', __name__)

from app.routes.mains import routes
