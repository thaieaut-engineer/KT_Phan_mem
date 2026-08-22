from app import db


class Order(db.Model):

    __tablename__ = "orders"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    address_id = db.Column(
        db.Integer,
        db.ForeignKey("addresses.id"),
        nullable=True
    )

    total_amount = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    shipping_fee = db.Column(
        db.Numeric(12, 2),
        default=0
    )

    payment_method = db.Column(
        db.String(20),
        default="cod"
    )

    payment_status = db.Column(
        db.String(20),
        default="unpaid"
    )

    order_status = db.Column(
        db.String(30),
        default="pending"
    )

    note = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    items = db.relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    address = db.relationship(
        "Address"
    )