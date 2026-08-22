from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app import db
from app.models import User


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


# =========================================================
# REGISTER
# =========================================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        phone = request.form.get(
            "phone",
            ""
        ).strip()


        # =================================================
        # VALIDATE
        # =================================================

        if not full_name:

            flash(
                "Vui lòng nhập họ và tên.",
                "danger"
            )

            return render_template(
                "auth/register.html"
            )


        if not email:

            flash(
                "Vui lòng nhập email.",
                "danger"
            )

            return render_template(
                "auth/register.html"
            )


        if not password:

            flash(
                "Vui lòng nhập mật khẩu.",
                "danger"
            )

            return render_template(
                "auth/register.html"
            )


        if len(password) < 6:

            flash(
                "Mật khẩu phải có ít nhất 6 ký tự.",
                "danger"
            )

            return render_template(
                "auth/register.html"
            )


        # =================================================
        # CHECK EMAIL
        # =================================================

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "Email đã được sử dụng.",
                "danger"
            )

            return render_template(
                "auth/register.html"
            )


        # =================================================
        # CREATE USER
        # =================================================

        user = User(

            full_name=full_name,

            email=email,

            password=generate_password_hash(
                password
            ),

            phone=phone,

            role="user",

            status="active"
        )


        db.session.add(user)

        db.session.commit()


        flash(
            "Đăng ký thành công. Hãy đăng nhập.",
            "success"
        )


        return redirect(
            url_for("auth.login")
        )


    return render_template(
        "auth/register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        # =================================================
        # FIND USER
        # =================================================

        user = User.query.filter_by(
            email=email
        ).first()


        if not user:

            flash(
                "Email hoặc mật khẩu không đúng.",
                "danger"
            )

            return render_template(
                "auth/login.html"
            )


        # =================================================
        # CHECK PASSWORD
        # =================================================

        if not check_password_hash(
            user.password,
            password
        ):

            flash(
                "Email hoặc mật khẩu không đúng.",
                "danger"
            )

            return render_template(
                "auth/login.html"
            )


        # =================================================
        # CHECK STATUS
        # =================================================

        if user.status != "active":

            flash(
                "Tài khoản đã bị khóa.",
                "danger"
            )

            return render_template(
                "auth/login.html"
            )


        # =================================================
        # LOGIN
        # =================================================

        login_user(user)


        next_page = request.args.get(
            "next"
        )

        if next_page:
            return redirect(next_page)


        return redirect(
            url_for("home.index")
        )


    return render_template(
        "auth/login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "Bạn đã đăng xuất.",
        "success"
    )

    return redirect(
        url_for("home.index")
    )

# =========================================================
# PROFILE
# =========================================================

@auth_bp.route("/profile")
@login_required
def profile():

    return render_template(
        "auth/profile.html",
        user=current_user
    )