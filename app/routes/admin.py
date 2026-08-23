from functools import wraps

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    abort,
)

from flask_login import (
    login_required,
    current_user,
)

from app import db

from app.models import (
    Order,
)


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# =========================================================
# ADMIN CHECK
# =========================================================

def admin_required(view):

    @wraps(view)
    @login_required
    def wrapped_view(*args, **kwargs):

        if not current_user.is_authenticated:
            return redirect(
                url_for("auth.login")
            )

        if current_user.role != "admin":

            flash(
                "Bạn không có quyền truy cập trang quản trị.",
                "danger"
            )

            return redirect(
                url_for("home.index")
            )

        return view(*args, **kwargs)

    return wrapped_view


# =========================================================
# DASHBOARD
# =========================================================

@admin_bp.route("/")
@admin_required
def dashboard():

    total_orders = Order.query.count()

    pending_orders = Order.query.filter_by(
        order_status="pending"
    ).count()

    confirmed_orders = Order.query.filter_by(
        order_status="confirmed"
    ).count()

    shipping_orders = Order.query.filter_by(
        order_status="shipping"
    ).count()

    completed_orders = Order.query.filter_by(
        order_status="completed"
    ).count()

    cancelled_orders = Order.query.filter_by(
        order_status="cancelled"
    ).count()

    return render_template(
        "admin/dashboard.html",
        total_orders=total_orders,
        pending_orders=pending_orders,
        confirmed_orders=confirmed_orders,
        shipping_orders=shipping_orders,
        completed_orders=completed_orders,
        cancelled_orders=cancelled_orders,
    )


# =========================================================
# DANH SÁCH ĐƠN HÀNG
# =========================================================

@admin_bp.route("/orders")
@admin_required
def orders():

    orders = Order.query.order_by(
        Order.created_at.desc()
    ).all()

    return render_template(
        "admin/orders.html",
        orders=orders
    )


# =========================================================
# CHI TIẾT ĐƠN HÀNG
# =========================================================

@admin_bp.route("/orders/<int:order_id>")
@admin_required
def order_detail(order_id):

    order = Order.query.filter_by(
        id=order_id
    ).first_or_404()

    return render_template(
        "admin/order_detail.html",
        order=order
    )


# =========================================================
# XÁC NHẬN ĐƠN
# =========================================================

@admin_bp.route(
    "/orders/<int:order_id>/confirm",
    methods=["POST"]
)
@admin_required
def confirm_order(order_id):

    order = Order.query.filter_by(
        id=order_id
    ).first_or_404()

    if order.order_status != "pending":

        flash(
            "Chỉ đơn hàng đang chờ xác nhận mới có thể xác nhận.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.order_detail",
                order_id=order.id
            )
        )

    order.order_status = "confirmed"

    db.session.commit()

    flash(
        f"Đã xác nhận đơn hàng #{order.id}.",
        "success"
    )

    return redirect(
        url_for(
            "admin.order_detail",
            order_id=order.id
        )
    )


# =========================================================
# CHUYỂN SANG ĐANG GIAO
# =========================================================

@admin_bp.route(
    "/orders/<int:order_id>/shipping",
    methods=["POST"]
)
@admin_required
def shipping_order(order_id):

    order = Order.query.filter_by(
        id=order_id
    ).first_or_404()

    if order.order_status != "confirmed":

        flash(
            "Đơn hàng phải được xác nhận trước khi giao.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.order_detail",
                order_id=order.id
            )
        )

    order.order_status = "shipping"

    db.session.commit()

    flash(
        f"Đơn hàng #{order.id} đang được giao.",
        "success"
    )

    return redirect(
        url_for(
            "admin.order_detail",
            order_id=order.id
        )
    )


# =========================================================
# HOÀN THÀNH
# =========================================================

@admin_bp.route(
    "/orders/<int:order_id>/complete",
    methods=["POST"]
)
@admin_required
def complete_order(order_id):

    order = Order.query.filter_by(
        id=order_id
    ).first_or_404()

    if order.order_status != "shipping":

        flash(
            "Chỉ đơn hàng đang giao mới có thể hoàn thành.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.order_detail",
                order_id=order.id
            )
        )

    order.order_status = "completed"

    # Nếu COD thì khi hoàn thành mới xem là đã thanh toán
    if order.payment_method == "cod":

        order.payment_status = "paid"

    db.session.commit()

    flash(
        f"Đơn hàng #{order.id} đã hoàn thành.",
        "success"
    )

    return redirect(
        url_for(
            "admin.order_detail",
            order_id=order.id
        )
    )


# =========================================================
# HỦY ĐƠN
# =========================================================

@admin_bp.route(
    "/orders/<int:order_id>/cancel",
    methods=["POST"]
)
@admin_required
def cancel_order(order_id):

    order = Order.query.filter_by(
        id=order_id
    ).first_or_404()

    if order.order_status in [
        "completed",
        "cancelled"
    ]:

        flash(
            "Không thể hủy đơn hàng này.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.order_detail",
                order_id=order.id
            )
        )

    order.order_status = "cancelled"

    # =====================================================
    # HOÀN LẠI TỒN KHO
    # =====================================================

    for item in order.items:

        if item.product:

            item.product.stock += item.quantity

    db.session.commit()

    flash(
        f"Đã hủy đơn hàng #{order.id} và hoàn lại tồn kho.",
        "success"
    )

    return redirect(
        url_for(
            "admin.order_detail",
            order_id=order.id
        )
    )