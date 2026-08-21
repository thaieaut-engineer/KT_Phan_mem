from flask import Blueprint
from sqlalchemy import text
from app import db

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    try:
        db.session.execute(text("SELECT 1"))
        return """
        <h1>🐾 PETSHOP</h1>
        <h2>Flask: OK ✅</h2>
        <h2>MySQL: Connected ✅</h2>
        """
    except Exception as e:
        return f"""
        <h1>🐾 PETSHOP</h1>
        <h2>MySQL: Error ❌</h2>
        <p>{e}</p>
        """