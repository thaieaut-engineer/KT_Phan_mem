from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from app import db

from app.models import (
    Cart,
    CartItem,
    Product
)


cart_bp = Blueprint(
    "cart",
    __name__,
    url_prefix="/gio-hang"
)


# =========================================================
# GET /gio-hang
# =========================================================


def get_cart_count():

    cart = Cart.query.filter_by(
        user_id=current_user.id
    ).first()

    if not cart:
        return 0

    return sum(
        item.quantity
        for item in cart.items
    )

@cart_bp.route("/")
@login_required
def index():

    cart = Cart.query.filter_by(
        user_id=current_user.id
    ).first()

    total = 0

    if cart:

        for item in cart.items:

            price = (
                item.product.sale_price
                if item.product.sale_price is not None
                else item.product.price
            )

            total += price * item.quantity


    return render_template(
        "cart/index.html",
        cart=cart,
        total=total
    )


# =========================================================
# POST /gio-hang/them/<product_id>
# =========================================================

@cart_bp.route(
    "/them/<int:product_id>",
    methods=["POST"]
)
@login_required
def add(product_id):

    product = Product.query.filter_by(
        id=product_id,
        status="active"
    ).first_or_404()


    # Kiểm tra tồn kho

    if product.stock <= 0:

        flash(
            "Sản phẩm đã hết hàng.",
            "danger"
        )

        return redirect(
            url_for(
                "product.detail",
                product_id=product.id
            )
        )


    # Lấy số lượng

    try:

        quantity = int(
            request.form.get(
                "quantity",
                1
            )
        )

    except ValueError:

        quantity = 1


    if quantity < 1:

        quantity = 1


    if quantity > product.stock:

        flash(
            f"Chỉ còn {product.stock} sản phẩm.",
            "danger"
        )

        return redirect(
            url_for(
                "product.detail",
                product_id=product.id
            )
        )


    # =====================================================
    # LẤY / TẠO CART
    # =====================================================

    cart = Cart.query.filter_by(
        user_id=current_user.id
    ).first()


    if not cart:

        cart = Cart(
            user_id=current_user.id
        )

        db.session.add(cart)

        db.session.flush()


    # =====================================================
    # KIỂM TRA SẢN PHẨM ĐÃ CÓ TRONG GIỎ CHƯA
    # =====================================================

    cart_item = CartItem.query.filter_by(
        cart_id=cart.id,
        product_id=product.id
    ).first()


    if cart_item:

        new_quantity = (
            cart_item.quantity + quantity
        )

        if new_quantity > product.stock:

            flash(
                f"Trong giỏ đã có {cart_item.quantity} sản phẩm. "
                f"Chỉ còn {product.stock} sản phẩm.",
                "danger"
            )

            return redirect(
                url_for(
                    "product.detail",
                    product_id=product.id
                )
            )


        cart_item.quantity = new_quantity

    else:

        cart_item = CartItem(

            cart_id=cart.id,

            product_id=product.id,

            quantity=quantity
        )

        db.session.add(cart_item)


    db.session.commit()


    flash(
        "Đã thêm sản phẩm vào giỏ hàng.",
        "success"
    )


    return redirect(
        url_for("cart.index")
    )


# =========================================================
# POST /gio-hang/cap-nhat/<item_id>
# =========================================================

@cart_bp.route(
    "/cap-nhat/<int:item_id>",
    methods=["POST"]
)
@login_required
def update(item_id):

    item = CartItem.query.join(
        Cart
    ).filter(
        CartItem.id == item_id,
        Cart.user_id == current_user.id
    ).first_or_404()


    try:

        quantity = int(
            request.form.get(
                "quantity",
                1
            )
        )

    except ValueError:

        quantity = 1


    if quantity < 1:

        quantity = 1


    if quantity > item.product.stock:

        flash(
            f"Chỉ còn {item.product.stock} sản phẩm.",
            "danger"
        )

        return redirect(
            url_for("cart.index")
        )


    item.quantity = quantity

    db.session.commit()


    flash(
        "Đã cập nhật giỏ hàng.",
        "success"
    )


    return redirect(
        url_for("cart.index")
    )


# =========================================================
# POST /gio-hang/xoa/<item_id>
# =========================================================

@cart_bp.route(
    "/xoa/<int:item_id>",
    methods=["POST"]
)
@login_required
def remove(item_id):

    item = CartItem.query.join(
        Cart
    ).filter(
        CartItem.id == item_id,
        Cart.user_id == current_user.id
    ).first_or_404()


    db.session.delete(item)

    db.session.commit()


    flash(
        "Đã xóa sản phẩm khỏi giỏ hàng.",
        "success"
    )


    return redirect(
        url_for("cart.index")
    )