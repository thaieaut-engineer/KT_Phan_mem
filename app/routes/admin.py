from functools import wraps
import os

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
)

from flask_login import (
    login_required,
    current_user,
)

from werkzeug.utils import secure_filename

from app import db

from app.models import (
    Order,
    Product,
    Category,
    OrderItem,
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


# =========================================================
# QUẢN LÝ SẢN PHẨM
# =========================================================

@admin_bp.route("/products")
@admin_required
def products():

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    category_id = request.args.get(
        "category_id",
        ""
    ).strip()

    query = Product.query


    # =========================
    # TÌM KIẾM
    # =========================

    if keyword:

        query = query.filter(
            Product.name.ilike(
                f"%{keyword}%"
            )
        )


    # =========================
    # LỌC DANH MỤC
    # =========================

    if category_id:

        try:

            category_id = int(category_id)

            query = query.filter(
                Product.category_id == category_id
            )

        except ValueError:

            category_id = ""


    products = query.order_by(
        Product.id.desc()
    ).all()


    categories = Category.query.filter_by(
        status=1
    ).order_by(
        Category.name.asc()
    ).all()


    return render_template(
        "admin/products.html",
        products=products,
        categories=categories,
        keyword=keyword,
        selected_category=category_id
    )

# =========================================================
# KIỂM TRA FILE ẢNH
# =========================================================

ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def allowed_image(filename):

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_IMAGE_EXTENSIONS

# =========================================================
# THÊM SẢN PHẨM
# =========================================================

@admin_bp.route(
    "/products/add",
    methods=["GET", "POST"]
)
@admin_required
def add_product():

    categories = Category.query.filter_by(
        status=1
    ).order_by(
        Category.name.asc()
    ).all()


    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        category_id = request.form.get(
            "category_id",
            ""
        ).strip()

        price = request.form.get(
            "price",
            ""
        ).strip()

        sale_price = request.form.get(
            "sale_price",
            ""
        ).strip()

        stock = request.form.get(
            "stock",
            "0"
        ).strip()

        status = request.form.get(
            "status",
            "active"
        ).strip()


        # =========================
        # VALIDATE TÊN
        # =========================

        if not name:

            flash(
                "Vui lòng nhập tên sản phẩm.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=None,
                categories=categories
            )


        # =========================
        # VALIDATE DANH MỤC
        # =========================

        try:

            category_id = int(category_id)

        except (TypeError, ValueError):

            flash(
                "Danh mục không hợp lệ.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=None,
                categories=categories
            )


        category = Category.query.filter_by(
            id=category_id,
            status=1
        ).first()


        if not category:

            flash(
                "Danh mục không tồn tại hoặc đã bị khóa.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=None,
                categories=categories
            )


        # =========================
        # VALIDATE GIÁ
        # =========================

        try:

            price = float(price)

            if price < 0:
                raise ValueError

        except (TypeError, ValueError):

            flash(
                "Giá sản phẩm không hợp lệ.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=None,
                categories=categories
            )


        # =========================
        # GIÁ KHUYẾN MÃI
        # =========================

        if sale_price:

            try:

                sale_price = float(sale_price)

                if sale_price < 0:
                    raise ValueError

                if sale_price >= price:

                    flash(
                        "Giá khuyến mãi phải nhỏ hơn giá gốc.",
                        "danger"
                    )

                    return render_template(
                        "admin/product_form.html",
                        product=None,
                        categories=categories
                    )

            except (TypeError, ValueError):

                flash(
                    "Giá khuyến mãi không hợp lệ.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=None,
                    categories=categories
                )

        else:

            sale_price = None


        # =========================
        # TỒN KHO
        # =========================

        try:

            stock = int(stock)

            if stock < 0:
                raise ValueError

        except (TypeError, ValueError):

            flash(
                "Tồn kho phải là số nguyên >= 0.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=None,
                categories=categories
            )


        # =========================
        # STATUS
        # =========================

        if status not in [
            "active",
            "inactive"
        ]:

            status = "active"


        # =========================
        # IMAGE
        # =========================

        image_file = request.files.get(
            "image"
        )

        image_name = None


        if image_file and image_file.filename:

            if not allowed_image(
                image_file.filename
            ):

                flash(
                    "Chỉ chấp nhận ảnh PNG, JPG, JPEG hoặc WEBP.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=None,
                    categories=categories
                )


            image_name = secure_filename(
                image_file.filename
            )


            upload_folder = os.path.join(
                current_app.root_path,
                "static",
                "uploads",
                "products"
            )


            os.makedirs(
                upload_folder,
                exist_ok=True
            )


            image_file.save(
                os.path.join(
                    upload_folder,
                    image_name
                )
            )


        # =========================
        # CREATE
        # =========================

        product = Product(

            category_id=category_id,

            name=name,

            description=description,

            price=price,

            sale_price=sale_price,

            stock=stock,

            image=image_name,

            status=status
        )


        db.session.add(product)

        db.session.commit()


        flash(
            "Thêm sản phẩm thành công.",
            "success"
        )


        return redirect(
            url_for(
                "admin.products"
            )
        )


    return render_template(
        "admin/product_form.html",
        product=None,
        categories=categories
    )

# =========================================================
# SỬA SẢN PHẨM
# =========================================================

@admin_bp.route(
    "/products/<int:product_id>/edit",
    methods=["GET", "POST"]
)
@admin_required
def edit_product(product_id):

    product = Product.query.filter_by(
        id=product_id
    ).first_or_404()


    categories = Category.query.filter_by(
        status=1
    ).order_by(
        Category.name.asc()
    ).all()


    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        category_id = request.form.get(
            "category_id",
            ""
        ).strip()

        price = request.form.get(
            "price",
            ""
        ).strip()

        sale_price = request.form.get(
            "sale_price",
            ""
        ).strip()

        stock = request.form.get(
            "stock",
            "0"
        ).strip()

        status = request.form.get(
            "status",
            "active"
        ).strip()


        if not name:

            flash(
                "Vui lòng nhập tên sản phẩm.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=product,
                categories=categories
            )


        try:

            category_id = int(category_id)

        except (TypeError, ValueError):

            flash(
                "Danh mục không hợp lệ.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=product,
                categories=categories
            )


        category = Category.query.filter_by(
            id=category_id,
            status=1
        ).first()


        if not category:

            flash(
                "Danh mục không tồn tại.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=product,
                categories=categories
            )


        try:

            price = float(price)

            if price < 0:
                raise ValueError

        except (TypeError, ValueError):

            flash(
                "Giá sản phẩm không hợp lệ.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=product,
                categories=categories
            )


        if sale_price:

            try:

                sale_price = float(sale_price)

                if sale_price < 0:
                    raise ValueError

                if sale_price >= price:

                    flash(
                        "Giá khuyến mãi phải nhỏ hơn giá gốc.",
                        "danger"
                    )

                    return render_template(
                        "admin/product_form.html",
                        product=product,
                        categories=categories
                    )

            except (TypeError, ValueError):

                flash(
                    "Giá khuyến mãi không hợp lệ.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=product,
                    categories=categories
                )

        else:

            sale_price = None


        try:

            stock = int(stock)

            if stock < 0:
                raise ValueError

        except (TypeError, ValueError):

            flash(
                "Tồn kho không hợp lệ.",
                "danger"
            )

            return render_template(
                "admin/product_form.html",
                product=product,
                categories=categories
            )


        if status not in [
            "active",
            "inactive"
        ]:

            status = "active"


        # =========================
        # UPDATE IMAGE
        # =========================

        image_file = request.files.get(
            "image"
        )


        if image_file and image_file.filename:

            if not allowed_image(
                image_file.filename
            ):

                flash(
                    "Định dạng ảnh không hợp lệ.",
                    "danger"
                )

                return render_template(
                    "admin/product_form.html",
                    product=product,
                    categories=categories
                )


            image_name = secure_filename(
                image_file.filename
            )


            upload_folder = os.path.join(
                current_app.root_path,
                "static",
                "uploads",
                "products"
            )


            os.makedirs(
                upload_folder,
                exist_ok=True
            )


            image_file.save(
                os.path.join(
                    upload_folder,
                    image_name
                )
            )


            product.image = image_name


        # =========================
        # UPDATE DATA
        # =========================

        product.category_id = category_id

        product.name = name

        product.description = description

        product.price = price

        product.sale_price = sale_price

        product.stock = stock

        product.status = status


        db.session.commit()


        flash(
            "Cập nhật sản phẩm thành công.",
            "success"
        )


        return redirect(
            url_for(
                "admin.products"
            )
        )


    return render_template(
        "admin/product_form.html",
        product=product,
        categories=categories
    )

# =========================================================
# XÓA / ẨN SẢN PHẨM
# =========================================================

@admin_bp.route(
    "/products/<int:product_id>/delete",
    methods=["POST"]
)
@admin_required
def delete_product(product_id):

    product = Product.query.filter_by(
        id=product_id
    ).first_or_404()


    # Kiểm tra sản phẩm đã từng xuất hiện trong đơn hàng chưa

    has_order = OrderItem.query.filter_by(
        product_id=product.id
    ).first()


    if has_order:

        product.status = "inactive"

        db.session.commit()


        flash(
            "Sản phẩm đã từng được đặt hàng nên chỉ được chuyển sang trạng thái ẩn.",
            "warning"
        )


    else:

        db.session.delete(product)

        db.session.commit()


        flash(
            "Đã xóa sản phẩm.",
            "success"
        )


    return redirect(
        url_for(
            "admin.products"
        )
    )