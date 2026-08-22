# import os
# from dotenv import load_dotenv
# from sqlalchemy.engine import URL

# load_dotenv()


# class Config:
#     SECRET_KEY = os.getenv("SECRET_KEY")

#     database_url = URL.create(
#         drivername="mysql+pymysql",
#         username=os.getenv("DB_USER", "root"),
#         password=os.getenv("DB_PASSWORD", ""),
#         host=os.getenv("DB_HOST", "localhost"),
#         port=int(os.getenv("DB_PORT", "3306")),
#         database=os.getenv("DB_NAME", "petshop_db")
#     )

#     SQLALCHEMY_DATABASE_URI = database_url

#     SQLALCHEMY_TRACK_MODIFICATIONS = False


# SQL trên Aiven
import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL


load_dotenv()


class Config:

    # ==============================
    # Flask
    # ==============================

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "development-secret-key"
    )


    # ==============================
    # Aiven MySQL
    # ==============================

    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername="mysql+pymysql",

        username=os.getenv(
            "DB_USER",
            "avnadmin"
        ),

        password=os.getenv(
            "DB_PASSWORD",
            ""
        ),

        host=os.getenv(
            "DB_HOST"
        ),

        port=int(
            os.getenv(
                "DB_PORT",
                "3306"
            )
        ),

        database=os.getenv(
            "DB_NAME",
            "petshop_db"
        )
    )


    SQLALCHEMY_TRACK_MODIFICATIONS = False