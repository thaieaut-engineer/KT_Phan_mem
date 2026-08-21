from app import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Integer, default=1)

    products = db.relationship(
        "Product",
        backref="category",
        lazy=True
    )

    def __repr__(self):
        return f"<Category {self.name}>"