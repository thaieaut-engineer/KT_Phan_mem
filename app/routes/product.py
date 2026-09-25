from flask import Blueprint, render_template, request
from sqlalchemy import or_

from app.models import Product, Category


product_bp = Blueprint(
    "product",
    __name__,
    url_prefix="/san-pham"
)


SECTION_META = {
    "cho": {
        "title": "Sản phẩm cho chó",
        "subtitle": "Thức ăn, đồ chơi và phụ kiện dành cho chó.",
    },
    "meo": {
        "title": "Sản phẩm cho mèo",
        "subtitle": "Thức ăn, đồ chơi và phụ kiện dành cho mèo.",
    },
    "phu-kien": {
        "title": "Phụ kiện thú cưng",
        "subtitle": "Dây dắt, vòng cổ, đồ chơi và đồ dùng chăm sóc.",
    },
    "khuyen-mai": {
        "title": "Khuyến mãi",
        "subtitle": "Những sản phẩm đang giảm giá hấp dẫn.",
    },
}


def _render_catalog(section=None, list_endpoint="product.index"):

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

    query = Product.query.filter_by(
        status="active"
    )

    if section in ("cho", "meo", "phu-kien"):
        query = query.join(Category)

    if section == "cho":
        query = query.filter(
            or_(
                Category.name.ilike("%chó%"),
                Product.name.ilike("%chó%"),
                Product.description.ilike("%chó%"),
            )
        )

    elif section == "meo":
        query = query.filter(
            or_(
                Category.name.ilike("%mèo%"),
                Product.name.ilike("%mèo%"),
                Product.description.ilike("%mèo%"),
            )
        )

    elif section == "phu-kien":
        query = query.filter(
            or_(
                Category.name.ilike("%phụ kiện%"),
                Category.name.ilike("%đồ chơi%"),
                Category.name.ilike("%chăm sóc%"),
                Category.name.ilike("%chuồng%"),
            )
        )

    elif section == "khuyen-mai":
        query = query.filter(
            Product.sale_price.isnot(None),
            Product.sale_price > 0,
        )

    if keyword:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{keyword}%"),
                Product.description.ilike(f"%{keyword}%"),
            )
        )

    if category_id:
        try:
            category_id_int = int(category_id)

            query = query.filter(
                Product.category_id == category_id_int
            )

        except ValueError:
            category_id = ""

    if sort == "price_asc":
        query = query.order_by(Product.price.asc())

    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())

    elif sort == "name_asc":
        query = query.order_by(Product.name.asc())

    elif sort == "name_desc":
        query = query.order_by(Product.name.desc())

    else:
        query = query.order_by(Product.created_at.desc())

    if section in ("cho", "meo", "phu-kien"):
        query = query.distinct()

    pagination = query.paginate(
        page=page,
        per_page=8,
        error_out=False
    )

    categories = Category.query.filter_by(
        status=1
    ).all()

    meta = SECTION_META.get(section, {})

    page_title = meta.get("title", "Tất cả sản phẩm")
    page_subtitle = meta.get(
        "subtitle",
        "Khám phá các sản phẩm dành cho thú cưng"
    )

    return render_template(
        "product/list.html",
        products=pagination.items,
        pagination=pagination,
        categories=categories,
        keyword=keyword,
        selected_category=category_id,
        selected_sort=sort,
        page_title=page_title,
        page_subtitle=page_subtitle,
        list_endpoint=list_endpoint,
    )


@product_bp.route("/")
def index():
    return _render_catalog()


@product_bp.route("/cho")
def dogs():
    return _render_catalog(
        section="cho",
        list_endpoint="product.dogs"
    )


@product_bp.route("/meo")
def cats():
    return _render_catalog(
        section="meo",
        list_endpoint="product.cats"
    )


@product_bp.route("/phu-kien")
def accessories():
    return _render_catalog(
        section="phu-kien",
        list_endpoint="product.accessories"
    )


@product_bp.route("/khuyen-mai")
def promotions():
    return _render_catalog(
        section="khuyen-mai",
        list_endpoint="product.promotions"
    )


@product_bp.route("/<int:product_id>")
def detail(product_id):

    product = Product.query.filter_by(
        id=product_id,
        status="active"
    ).first_or_404()

    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.status == "active"
    ).limit(4).all()

    return render_template(
        "product/detail.html",
        product=product,
        related_products=related_products
    )
