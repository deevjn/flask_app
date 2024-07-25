from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    db.init_app(app)

    # Импорт моделей
    from .models import User

    # Импорт маршрутов
    from .routes import routes

    return app