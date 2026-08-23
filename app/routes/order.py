from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from app import db

from app.models import (
    Cart,
    Order,
    OrderItem,
    Address
)


order_bp = Blueprint(
    "order",
    __name__,
    url_prefix="/dat-hang"
)


# =========================================================
# CHECKOUT
# =========================================================

@order_bp.route("/", methods=["GET", "POST"])
@login_required
def checkout():

    cart = Cart.query.filter_by(
        user_id=current_user.id
    ).first()


    if not cart or not cart.items:

        flash(
            "Giỏ hàng đang trống.",
            "warning"
        )

        return redirect(
            url_for("cart.index")
        )


    # =====================================================
    # GET ADDRESSES
    # =====================================================

    addresses = Address.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Address.is_default.desc(),
        Address.id.desc()
    ).all()


    # =====================================================
    # CALCULATE TOTAL
    # =====================================================

    total = 0

    for item in cart.items:

        if item.product.sale_price is not None:

            price = item.product.sale_price

        else:

            price = item.product.price


        total += price * item.quantity


    shipping_fee = 0


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        address_id = request.form.get(
            "address_id"
        )

        payment_method = request.form.get(
            "payment_method",
            "cod"
        )

        note = request.form.get(
            "note",
            ""
        ).strip()


        # =================================================
        # CHECK ADDRESS
        # =================================================

        if not address_id:

            flash(
                "Vui lòng chọn địa chỉ nhận hàng.",
                "danger"
            )

            return render_template(
                "order/checkout.html",
                cart=cart,
                addresses=addresses,
                total=total,
                shipping_fee=shipping_fee
            )


        address = Address.query.filter_by(
            id=address_id,
            user_id=current_user.id
        ).first()


        if not address:

            flash(
                "Địa chỉ nhận hàng không hợp lệ.",
                "danger"
            )

            return render_template(
                "order/checkout.html",
                cart=cart,
                addresses=addresses,
                total=total,
                shipping_fee=shipping_fee
            )


        # =================================================
        # CHECK PAYMENT METHOD
        # =================================================

        if payment_method not in [
            "cod",
            "banking"
        ]:

            payment_method = "cod"


        # =================================================
        # CHECK STOCK AGAIN
        # =================================================

        for item in cart.items:

            if item.product.stock < item.quantity:

                flash(
                    f"Sản phẩm '{item.product.name}' "
                    f"không đủ số lượng.",
                    "danger"
                )

                return redirect(
                    url_for("cart.index")
                )


        # =================================================
        # CREATE ORDER
        # =================================================

        order = Order(

            user_id=current_user.id,

            address_id=address.id,

            total_amount=total + shipping_fee,

            shipping_fee=shipping_fee,

            payment_method=payment_method,

            payment_status="unpaid",

            order_status="pending",

            note=note
        )


        db.session.add(order)

        db.session.flush()


        # =================================================
        # CREATE ORDER ITEMS
        # =================================================

        for item in cart.items:

            if item.product.sale_price is not None:

                price = item.product.sale_price

            else:

                price = item.product.price


            subtotal = price * item.quantity


            order_item = OrderItem(

                order_id=order.id,

                product_id=item.product.id,

                product_name=item.product.name,

                price=price,

                quantity=item.quantity,

                subtotal=subtotal
            )


            db.session.add(order_item)


            # =============================================
            # REDUCE STOCK
            # =============================================

            item.product.stock -= item.quantity


        # =================================================
        # DELETE CART ITEMS
        # =================================================

        for item in list(cart.items):

            db.session.delete(item)


        db.session.commit()


        return redirect(
            url_for(
                "order.success",
                order_id=order.id
            )
        )


    return render_template(
        "order/checkout.html",
        cart=cart,
        addresses=addresses,
        total=total,
        shipping_fee=shipping_fee
    )


# =========================================================
# ORDER SUCCESS
# =========================================================

@order_bp.route(
    "/thanh-cong/<int:order_id>"
)
@login_required
def success(order_id):

    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()


    return render_template(
        "order/success.html",
        order=order
    )

# =========================================================
# LỊCH SỬ ĐƠN HÀNG
# =========================================================

@order_bp.route("/lich-su")
@login_required
def history():

    orders = Order.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Order.created_at.desc()
    ).all()

    return render_template(
        "order/history.html",
        orders=orders
    )


# =========================================================
# CHI TIẾT ĐƠN HÀNG
# =========================================================

@order_bp.route("/<int:order_id>")
@login_required
def detail(order_id):

    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "order/detail.html",
        order=order
    )