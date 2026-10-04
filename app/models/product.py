from app import db


PRODUCT_IMAGE_BY_NAME = {
    "Royal Canin Adult Dog": "dog-food-bag.jpg",
    "Pedigree Adult": "dog-food-kibble.jpg",
    "SmartHeart Puppy": "dog-food-bag.jpg",
    "Ganador Premium": "dog-food-kibble.jpg",
    "ANF 6 Free Dog": "dog-food-bag.jpg",
    "Me-O Tuna": "cat-food-kibble.jpg",
    "Whiskas Adult": "cat-food-bag.jpg",
    "Royal Canin Kitten": "cat-food-bag.jpg",
    "Cat Eye Tuna": "cat-food-kibble.jpg",
    "Nekko Pouch": "cat-food-bag.jpg",
    "Bóng cao su cho chó": "dog-ball-toy.jpg",
    "Chuột đồ chơi cho mèo": "cat-mouse-toy.jpg",
    "Bóng len cho mèo": "cat-mouse-toy.jpg",
    "Dây thừng đồ chơi": "dog-rope-toy.jpg",
    "Dây dắt chó": "dog-leash.jpg",
    "Vòng cổ thú cưng": "dog-collar.jpg",
    "Áo cho chó": "dog-sweater.jpg",
    "Balo vận chuyển thú cưng": "pet-carrier.jpg",
    "Dung dịch vệ sinh tai": "pet-shampoo.jpg",
    "Khăn lau thú cưng": "pet-towel.jpg",
    "Sữa tắm chó mèo": "pet-shampoo.jpg",
    "Lược chải lông": "cat-grooming.jpg",
    "Ổ nằm cho chó": "dog-bed.jpg",
    "Nhà nhựa cho mèo": "cat-house.jpg",
    "Đệm nằm thú cưng": "dog-bed.jpg",
    "Chuồng thú cưng": "pet-carrier.jpg",
}


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

    category = db.relationship(
        "Category",
        back_populates="products"
    )

    @property
    def image_path(self):
        if self.image:
            if self.image.startswith("products/"):
                return f"images/{self.image}"

            return f"uploads/products/{self.image}"

        filename = PRODUCT_IMAGE_BY_NAME.get(self.name)
        if filename is None:
            category_name = self.category.name.lower() if self.category else ""

            if "mèo" in category_name:
                filename = "cat-food-kibble.jpg"
            elif "đồ chơi" in category_name:
                filename = "dog-ball-toy.jpg"
            elif "phụ kiện" in category_name:
                filename = "dog-collar.jpg"
            elif "chăm sóc" in category_name:
                filename = "pet-shampoo.jpg"
            elif "chuồng" in category_name or "nhà" in category_name:
                filename = "dog-bed.jpg"
            else:
                filename = "dog-food-bag.jpg"

        return f"images/products/{filename}"

    def __repr__(self):
        return f"<Product {self.name}>"