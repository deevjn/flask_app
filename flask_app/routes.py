from flask import Blueprint
from . import db

routes = Blueprint('routes', __name__)

# Добавьте здесь свои маршруты (например, для страниц login, register, profile и т.д.)
# Используйте @routes.route('/...')
# Например:
# from . import auth
# routes.register_blueprint(auth.bp)