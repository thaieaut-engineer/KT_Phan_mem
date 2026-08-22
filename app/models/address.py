from app import db


class Address(db.Model):

    __tablename__ = "addresses"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    receiver_name = db.Column(
        db.String(100),
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=False
    )

    address = db.Column(
        db.String(255),
        nullable=False
    )

    is_default = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )