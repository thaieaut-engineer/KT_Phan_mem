from flask import Blueprint, render_template

from app.models import Product


home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():

    products = Product.query.filter_by(
        status="active"
    ).limit(8).all()

    return render_template(
        "home.html",
        products=products
    )
