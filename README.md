Học phần: Kiểm thử phần mềm

Đề tài: Kiểm thử website bán đồ thú cưng Petshop

Thành viên
 - Quang Duy Thai (Leader)
 - Truong Hoai Son (Member)
 - Le Nguyen Nam Anh (Member)

# 🐾 PetShop

Website bán đồ thú cưng được xây dựng bằng Python Flask và MySQL.

## Công nghệ

- Python
- Flask
- Flask-SQLAlchemy
- MySQL
- Bootstrap
- JavaScript
- Pytest
- Postman
- JMeter

## Cấu trúc project

PetShop/
│
├── app/
│   ├── __init__.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── category.py
│   │   └── product.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── home.py
│   │   └── product.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   └── product/
│   │       └── list.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── main.js
│       └── images/
│
├── tests/
│
├── venv/
│
├── .env
├── .env.example
├── .gitignore
├── config.py
├── requirements.txt
├── README.md
└── run.py