from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from app import db
from app.models import Address


address_bp = Blueprint(
    "address",
    __name__,
    url_prefix="/dia-chi"
)


# =========================================================
# DANH SÁCH ĐỊA CHỈ
# =========================================================

@address_bp.route("/")
@login_required
def index():

    addresses = Address.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Address.is_default.desc(),
        Address.id.desc()
    ).all()

    return render_template(
        "address/index.html",
        addresses=addresses
    )


# =========================================================
# THÊM ĐỊA CHỈ
# =========================================================

@address_bp.route("/them", methods=["GET", "POST"])
@login_required
def add():

    if request.method == "POST":

        receiver_name = request.form.get(
            "receiver_name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        is_default = request.form.get(
            "is_default"
        ) == "1"


        # =========================
        # VALIDATE
        # =========================

        if not receiver_name:

            flash(
                "Vui lòng nhập tên người nhận.",
                "danger"
            )

            return redirect(
                url_for("address.add")
            )


        if not phone:

            flash(
                "Vui lòng nhập số điện thoại.",
                "danger"
            )

            return redirect(
                url_for("address.add")
            )


        if not address:

            flash(
                "Vui lòng nhập địa chỉ.",
                "danger"
            )

            return redirect(
                url_for("address.add")
            )


        # =========================
        # NẾU LÀ ĐỊA CHỈ ĐẦU TIÊN
        # → TỰ ĐỘNG MẶC ĐỊNH
        # =========================

        existing_count = Address.query.filter_by(
            user_id=current_user.id
        ).count()

        if existing_count == 0:

            is_default = True


        # =========================
        # BỎ MẶC ĐỊNH CŨ
        # =========================

        if is_default:

            Address.query.filter_by(
                user_id=current_user.id
            ).update(
                {
                    "is_default": False
                }
            )


        # =========================
        # TẠO ĐỊA CHỈ
        # =========================

        new_address = Address(

            user_id=current_user.id,

            receiver_name=receiver_name,

            phone=phone,

            address=address,

            is_default=is_default
        )


        db.session.add(new_address)

        db.session.commit()


        flash(
            "Thêm địa chỉ thành công.",
            "success"
        )


        return redirect(
            url_for("address.index")
        )


    return render_template(
        "address/add.html"
    )


# =========================================================
# ĐẶT ĐỊA CHỈ MẶC ĐỊNH
# =========================================================

@address_bp.route(
    "/mac-dinh/<int:address_id>",
    methods=["POST"]
)
@login_required
def set_default(address_id):

    selected_address = Address.query.filter_by(
        id=address_id,
        user_id=current_user.id
    ).first_or_404()


    Address.query.filter_by(
        user_id=current_user.id
    ).update(
        {
            "is_default": False
        }
    )


    selected_address.is_default = True

    db.session.commit()


    flash(
        "Đã thay đổi địa chỉ mặc định.",
        "success"
    )


    return redirect(
        url_for("address.index")
    )