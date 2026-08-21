from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Config


db = SQLAlchemy()


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)


    # =========================
    # Import Models
    # =========================

    from app.models import Category, Product


    # =========================
    # Register Routes
    # =========================

    from app.routes.home import home_bp
    from app.routes.product import product_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(product_bp)


    return app