from flask import Blueprint, render_template, request

from app.models import Product, Category


product_bp = Blueprint(
    "product",
    __name__,
    url_prefix="/san-pham"
)


@product_bp.route("/")
def index():

    # =========================
    # Lấy tham số từ URL
    # =========================

    keyword = request.args.get(
        "keyword",
        "",
        type=str
    ).strip()

    category_id = request.args.get(
        "category",
        "",
        type=str
    ).strip()

    sort = request.args.get(
        "sort",
        "",
        type=str
    ).strip()

    page = request.args.get(
        "page",
        1,
        type=int
    )


    # =========================
    # Query sản phẩm
    # =========================

    query = Product.query.filter_by(
        status="active"
    )


    # =========================
    # Tìm kiếm
    # =========================

    if keyword:

        query = query.filter(
            Product.name.ilike(f"%{keyword}%")
        )


    # =========================
    # Lọc danh mục
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
    # Sắp xếp
    # =========================

    if sort == "price_asc":

        query = query.order_by(
            Product.price.asc()
        )

    elif sort == "price_desc":

        query = query.order_by(
            Product.price.desc()
        )

    elif sort == "name_asc":

        query = query.order_by(
            Product.name.asc()
        )

    elif sort == "name_desc":

        query = query.order_by(
            Product.name.desc()
        )

    else:

        query = query.order_by(
            Product.created_at.desc()
        )


    # =========================
    # Phân trang
    # =========================

    pagination = query.paginate(
        page=page,
        per_page=8,
        error_out=False
    )


    # =========================
    # Danh mục
    # =========================

    categories = Category.query.filter_by(
        status=1
    ).all()


    return render_template(
        "product/list.html",
        products=pagination.items,
        pagination=pagination,
        categories=categories,
        keyword=keyword,
        selected_category=category_id,
        selected_sort=sort
    )