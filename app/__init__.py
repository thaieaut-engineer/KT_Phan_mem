from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from config import Config


db = SQLAlchemy()

login_manager = LoginManager()

login_manager.login_view = "auth.login"

login_manager.login_message = "Vui lòng đăng nhập để tiếp tục."


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    login_manager.init_app(app)


    # =========================
    # Models
    # =========================

    from app.models import (
        User,
        Category,
        Product
    )


    # =========================
    # User Loader
    # =========================

    @login_manager.user_loader
    def load_user(user_id):

        return db.session.get(
            User,
            int(user_id)
        )


    # =========================
    # Routes
    # =========================

    from app.routes.home import home_bp
    from app.routes.product import product_bp
    from app.routes.auth import auth_bp
    from app.routes.cart import cart_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)


    @app.context_processor
    def inject_cart_count():

        from flask_login import current_user

        count = 0

        if current_user.is_authenticated:

            from app.models import Cart

            cart = Cart.query.filter_by(
                user_id=current_user.id
            ).first()

            if cart:
                count = sum(
                    item.quantity
                    for item in cart.items
                )

        return {
            "cart_count": count
        }

    return app