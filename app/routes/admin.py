from functools import wraps
import os
from datetime import date, datetime, timedelta

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
from werkzeug.security import generate_password_hash

from sqlalchemy import or_, func

from app import db

from app.models import (
    Order,
    Product,
    Category,
    OrderItem,
    User,
    Address,
    Cart,
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

    total_users = User.query.count()

    total_products = Product.query.count()

    total_revenue = db.session.query(
        func.coalesce(
            func.sum(Order.total_amount),
            0
        )
    ).filter(
        Order.order_status == "completed"
    ).scalar()

    total_revenue = float(total_revenue or 0)

    days = 14
    today = date.today()
    start_day = today - timedelta(days=days - 1)
    start_dt = datetime.combine(
        start_day,
        datetime.min.time()
    )

    daily_rows = db.session.query(
        func.date(Order.created_at).label("day"),
        func.count(Order.id).label("order_count"),
        func.coalesce(
            func.sum(Order.total_amount),
            0
        ).label("revenue")
    ).filter(
        Order.created_at >= start_dt
    ).group_by(
        func.date(Order.created_at)
    ).all()

    daily_map = {}

    for row in daily_rows:

        day_value = row.day

        if hasattr(day_value, "strftime"):
            day_key = day_value.strftime("%Y-%m-%d")
        else:
            day_key = str(day_value)[:10]

        daily_map[day_key] = {
            "count": int(row.order_count or 0),
            "revenue": float(row.revenue or 0),
        }

    chart_labels = []
    chart_order_counts = []
    chart_revenues = []

    for offset in range(days):

        current_day = start_day + timedelta(days=offset)
        day_key = current_day.strftime("%Y-%m-%d")
        item = daily_map.get(
            day_key,
            {
                "count": 0,
                "revenue": 0,
            }
        )

        chart_labels.append(
            current_day.strftime("%d/%m")
        )
        chart_order_counts.append(item["count"])
        chart_revenues.append(item["revenue"])

    top_product_rows = db.session.query(
        OrderItem.product_name,
        func.sum(OrderItem.quantity).label("qty")
    ).group_by(
        OrderItem.product_name
    ).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(5).all()

    chart_product_labels = [
        row.product_name for row in top_product_rows
    ]
    chart_product_qty = [
        int(row.qty or 0) for row in top_product_rows
    ]

    return render_template(
        "admin/dashboard.html",
        total_orders=total_orders,
        pending_orders=pending_orders,
        confirmed_orders=confirmed_orders,
        shipping_orders=shipping_orders,
        completed_orders=completed_orders,
        cancelled_orders=cancelled_orders,
        total_users=total_users,
        total_products=total_products,
        total_revenue=total_revenue,
        chart_labels=chart_labels,
        chart_order_counts=chart_order_counts,
        chart_revenues=chart_revenues,
        chart_product_labels=chart_product_labels,
        chart_product_qty=chart_product_qty,
        chart_status_counts=[
            pending_orders,
            confirmed_orders,
            shipping_orders,
            completed_orders,
            cancelled_orders,
        ],
    )


# =========================================================
# DANH SÁCH ĐƠN HÀNG
# =========================================================

@admin_bp.route("/orders")
@admin_required
def orders():

    page = request.args.get(
        "page",
        1,
        type=int
    )

    if page < 1:
        page = 1

    # Số đơn hàng / trang
    per_page = 10

    pagination = Order.query.order_by(
        Order.id.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    orders = pagination.items

    return render_template(
        "admin/orders.html",
        orders=orders,
        pagination=pagination
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

    page = request.args.get(
        "page",
        1,
        type=int
    )

    if page < 1:
        page = 1

    # Số sản phẩm / trang
    per_page = 10

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

            category_id_int = int(category_id)

            query = query.filter(
                Product.category_id == category_id_int
            )

        except ValueError:

            category_id = ""

    # =========================
    # PHÂN TRANG
    # =========================

    pagination = query.order_by(
        Product.id.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    products = pagination.items

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
        selected_category=category_id,
        pagination=pagination
    )


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

# =========================================================
# QUẢN LÝ DANH MỤC
# =========================================================

@admin_bp.route("/categories")
@admin_required
def categories():

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    page = request.args.get(
        "page",
        1,
        type=int
    )

    # Không cho page nhỏ hơn 1
    if page < 1:
        page = 1

    # Số danh mục trên mỗi trang
    per_page = 5

    query = Category.query

    # =========================
    # TÌM KIẾM
    # =========================

    if keyword:

        query = query.filter(
            Category.name.ilike(
                f"%{keyword}%"
            )
        )

    # =========================
    # PHÂN TRANG
    # =========================

    pagination = query.order_by(
        Category.id.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    categories = pagination.items

    return render_template(
        "admin/categories.html",
        categories=categories,
        pagination=pagination,
        keyword=keyword
    )


# =========================================================
# THÊM DANH MỤC
# =========================================================

@admin_bp.route(
    "/categories/add",
    methods=["GET", "POST"]
)
@admin_required
def add_category():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        if not name:

            flash(
                "Vui lòng nhập tên danh mục.",
                "danger"
            )

            return render_template(
                "admin/category_form.html",
                category=None
            )

        # Kiểm tra trùng tên

        exists = Category.query.filter(
            db.func.lower(Category.name)
            == name.lower()
        ).first()

        if exists:

            flash(
                "Tên danh mục đã tồn tại.",
                "danger"
            )

            return render_template(
                "admin/category_form.html",
                category=None
            )

        category = Category(
            name=name,
            description=description,
            status=1
        )

        db.session.add(category)
        db.session.commit()

        flash(
            "Thêm danh mục thành công.",
            "success"
        )

        return redirect(
            url_for(
                "admin.categories"
            )
        )

    return render_template(
        "admin/category_form.html",
        category=None
    )


# =========================================================
# SỬA DANH MỤC
# =========================================================

@admin_bp.route(
    "/categories/<int:category_id>/edit",
    methods=["GET", "POST"]
)
@admin_required
def edit_category(category_id):

    category = Category.query.filter_by(
        id=category_id
    ).first_or_404()

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        if not name:

            flash(
                "Vui lòng nhập tên danh mục.",
                "danger"
            )

            return render_template(
                "admin/category_form.html",
                category=category
            )

        # Không cho trùng với danh mục khác

        exists = Category.query.filter(
            db.func.lower(Category.name)
            == name.lower(),
            Category.id != category.id
        ).first()

        if exists:

            flash(
                "Tên danh mục đã tồn tại.",
                "danger"
            )

            return render_template(
                "admin/category_form.html",
                category=category
            )

        category.name = name
        category.description = description

        db.session.commit()

        flash(
            "Cập nhật danh mục thành công.",
            "success"
        )

        return redirect(
            url_for(
                "admin.categories"
            )
        )

    return render_template(
        "admin/category_form.html",
        category=category
    )


# =========================================================
# ẨN / XÓA DANH MỤC
# =========================================================

@admin_bp.route(
    "/categories/<int:category_id>/delete",
    methods=["POST"]
)
@admin_required
def delete_category(category_id):

    category = Category.query.filter_by(
        id=category_id
    ).first_or_404()

    # Kiểm tra sản phẩm thuộc danh mục

    product_count = Product.query.filter_by(
        category_id=category.id
    ).count()

    if product_count > 0:

        category.status = 0

        db.session.commit()

        flash(
            "Danh mục đang có sản phẩm nên đã được chuyển sang trạng thái ẩn.",
            "warning"
        )

    else:

        db.session.delete(category)

        db.session.commit()

        flash(
            "Đã xóa danh mục.",
            "success"
        )

    return redirect(
        url_for(
            "admin.categories"
        )
    )


# =========================================================
# KÍCH HOẠT / ẨN DANH MỤC
# =========================================================

@admin_bp.route(
    "/categories/<int:category_id>/toggle",
    methods=["POST"]
)
@admin_required
def toggle_category(category_id):

    category = Category.query.filter_by(
        id=category_id
    ).first_or_404()

    category.status = 0 if category.status == 1 else 1

    db.session.commit()

    flash(
        "Đã cập nhật trạng thái danh mục.",
        "success"
    )

    return redirect(
        url_for(
            "admin.categories"
        )
    )


# =========================================================
# QUẢN LÝ TÀI KHOẢN
# =========================================================

@admin_bp.route("/users")
@admin_required
def users():

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    selected_role = request.args.get(
        "role",
        ""
    ).strip()

    selected_status = request.args.get(
        "status",
        ""
    ).strip()

    page = request.args.get(
        "page",
        1,
        type=int
    )

    if page < 1:
        page = 1

    per_page = 10

    query = User.query

    if keyword:

        like_keyword = f"%{keyword}%"

        query = query.filter(
            or_(
                User.full_name.ilike(like_keyword),
                User.email.ilike(like_keyword),
                User.phone.ilike(like_keyword)
            )
        )

    if selected_role in ("user", "admin"):

        query = query.filter_by(
            role=selected_role
        )

    if selected_status in ("active", "locked"):

        query = query.filter_by(
            status=selected_status
        )

    pagination = query.order_by(
        User.id.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    users = pagination.items

    return render_template(
        "admin/users.html",
        users=users,
        pagination=pagination,
        keyword=keyword,
        selected_role=selected_role,
        selected_status=selected_status,
    )


# =========================================================
# CHI TIẾT TÀI KHOẢN
# =========================================================

@admin_bp.route("/users/<int:user_id>")
@admin_required
def user_detail(user_id):

    user = User.query.filter_by(
        id=user_id
    ).first_or_404()

    order_count = Order.query.filter_by(
        user_id=user.id
    ).count()

    recent_orders = Order.query.filter_by(
        user_id=user.id
    ).order_by(
        Order.id.desc()
    ).limit(5).all()

    address_count = Address.query.filter_by(
        user_id=user.id
    ).count()

    return render_template(
        "admin/user_detail.html",
        user=user,
        order_count=order_count,
        recent_orders=recent_orders,
        address_count=address_count,
    )


# =========================================================
# THÊM TÀI KHOẢN
# =========================================================

@admin_bp.route(
    "/users/them",
    methods=["GET", "POST"]
)
@admin_required
def add_user():

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

        role = request.form.get(
            "role",
            "user"
        ).strip()

        status = request.form.get(
            "status",
            "active"
        ).strip()

        if not full_name or not email or not password:

            flash(
                "Vui lòng nhập họ tên, email và mật khẩu.",
                "danger"
            )

            return render_template(
                "admin/user_form.html",
                user=None
            )

        if len(password) < 6:

            flash(
                "Mật khẩu phải có ít nhất 6 ký tự.",
                "danger"
            )

            return render_template(
                "admin/user_form.html",
                user=None
            )

        if role not in ("user", "admin"):
            role = "user"

        if status not in ("active", "locked"):
            status = "active"

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "Email đã được sử dụng.",
                "danger"
            )

            return render_template(
                "admin/user_form.html",
                user=None
            )

        user = User(
            full_name=full_name,
            email=email,
            password=generate_password_hash(
                password
            ),
            phone=phone,
            role=role,
            status=status
        )

        db.session.add(user)

        db.session.commit()

        flash(
            "Đã thêm tài khoản.",
            "success"
        )

        return redirect(
            url_for("admin.users")
        )

    return render_template(
        "admin/user_form.html",
        user=None
    )


# =========================================================
# SỬA TÀI KHOẢN
# =========================================================

@admin_bp.route(
    "/users/<int:user_id>/sua",
    methods=["GET", "POST"]
)
@admin_required
def edit_user(user_id):

    user = User.query.filter_by(
        id=user_id
    ).first_or_404()

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        role = request.form.get(
            "role",
            user.role
        ).strip()

        status = request.form.get(
            "status",
            user.status
        ).strip()

        if not full_name:

            flash(
                "Vui lòng nhập họ và tên.",
                "danger"
            )

            return render_template(
                "admin/user_form.html",
                user=user
            )

        if password and len(password) < 6:

            flash(
                "Mật khẩu phải có ít nhất 6 ký tự.",
                "danger"
            )

            return render_template(
                "admin/user_form.html",
                user=user
            )

        if role not in ("user", "admin"):
            role = user.role

        if status not in ("active", "locked"):
            status = user.status

        if user.id == current_user.id:

            if role != "admin" or status != "active":

                flash(
                    "Không thể hạ quyền hoặc khóa tài khoản đang đăng nhập.",
                    "warning"
                )

                return redirect(
                    url_for(
                        "admin.edit_user",
                        user_id=user.id
                    )
                )

        if user.role == "admin" and role != "admin":

            admin_count = User.query.filter_by(
                role="admin"
            ).count()

            if admin_count <= 1:

                flash(
                    "Không thể hạ quyền admin cuối cùng.",
                    "warning"
                )

                return redirect(
                    url_for(
                        "admin.edit_user",
                        user_id=user.id
                    )
                )

        user.full_name = full_name
        user.phone = phone
        user.role = role
        user.status = status

        if password:

            user.password = generate_password_hash(
                password
            )

        db.session.commit()

        flash(
            "Đã cập nhật tài khoản.",
            "success"
        )

        return redirect(
            url_for("admin.users")
        )

    return render_template(
        "admin/user_form.html",
        user=user
    )


# =========================================================
# KHÓA / MỞ KHÓA TÀI KHOẢN
# =========================================================

@admin_bp.route(
    "/users/<int:user_id>/toggle",
    methods=["POST"]
)
@admin_required
def toggle_user(user_id):

    user = User.query.filter_by(
        id=user_id
    ).first_or_404()

    if user.id == current_user.id:

        flash(
            "Không thể khóa tài khoản đang đăng nhập.",
            "warning"
        )

        return redirect(
            url_for("admin.users")
        )

    if user.status == "active":

        if user.role == "admin":

            active_admin_count = User.query.filter_by(
                role="admin",
                status="active"
            ).count()

            if active_admin_count <= 1:

                flash(
                    "Không thể khóa admin đang hoạt động cuối cùng.",
                    "warning"
                )

                return redirect(
                    url_for("admin.users")
                )

        user.status = "locked"

        flash(
            f"Đã khóa tài khoản {user.email}.",
            "success"
        )

    else:

        user.status = "active"

        flash(
            f"Đã mở khóa tài khoản {user.email}.",
            "success"
        )

    db.session.commit()

    return redirect(
        url_for("admin.users")
    )


# =========================================================
# XÓA TÀI KHOẢN
# =========================================================

@admin_bp.route(
    "/users/<int:user_id>/delete",
    methods=["POST"]
)
@admin_required
def delete_user(user_id):

    user = User.query.filter_by(
        id=user_id
    ).first_or_404()

    if user.id == current_user.id:

        flash(
            "Không thể xóa tài khoản đang đăng nhập.",
            "warning"
        )

        return redirect(
            url_for("admin.users")
        )

    if user.role == "admin":

        admin_count = User.query.filter_by(
            role="admin"
        ).count()

        if admin_count <= 1:

            flash(
                "Không thể xóa admin cuối cùng.",
                "warning"
            )

            return redirect(
                url_for("admin.users")
            )

    order_count = Order.query.filter_by(
        user_id=user.id
    ).count()

    if order_count > 0:

        user.status = "locked"

        db.session.commit()

        flash(
            "Tài khoản đã có đơn hàng nên không thể xóa. Đã chuyển sang trạng thái khóa.",
            "warning"
        )

        return redirect(
            url_for("admin.users")
        )

    Address.query.filter_by(
        user_id=user.id
    ).delete()

    cart = Cart.query.filter_by(
        user_id=user.id
    ).first()

    if cart:

        db.session.delete(cart)

    db.session.delete(user)

    db.session.commit()

    flash(
        "Đã xóa tài khoản.",
        "success"
    )

    return redirect(
        url_for("admin.users")
    )