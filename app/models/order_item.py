from app import db


class OrderItem(db.Model):

    __tablename__ = "order_items"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    product_name = db.Column(
        db.String(200),
        nullable=False
    )

    price = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    subtotal = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    order = db.relationship(
        "Order",
        back_populates="items"
    )

    product = db.relationship(
        "Product"
    )