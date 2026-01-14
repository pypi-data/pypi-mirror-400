from app.controllers import MainController
from app.routes.mains import bp

@bp.route('/', methods=['GET'])
def index():
    return MainController.index()
