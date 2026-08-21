from app import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    name = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(db.Text)

    price = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    sale_price = db.Column(
        db.Numeric(12, 2),
        nullable=True
    )

    stock = db.Column(
        db.Integer,
        default=0
    )

    image = db.Column(
        db.String(255)
    )

    status = db.Column(
        db.String(20),
        default="active"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    def __repr__(self):
        return f"<Product {self.name}>"